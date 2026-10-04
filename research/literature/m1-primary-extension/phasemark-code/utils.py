import torch
from PIL import Image, ImageEnhance
import io
import random
import numpy as np
import cv2
import torchvision.transforms as tforms
from bm3d import bm3d_rgb

from skimage.metrics import structural_similarity as ssim
import lpips
from pytorch_fid.fid_score import *
from compressai.zoo import bmshj2018_hyperprior, cheng2020_anchor #bmshj2018_factorized

def transform_img(image, resolution=512):
    tform = tforms.Compose([tforms.Resize((resolution,resolution)), tforms.ToTensor()])
    image = tform(image)
    return 2.0 * image - 1.0

@torch.no_grad()
def decode_vae_to_pil(output_tensor):
    # 1. VAE 디코딩된 텐서 후처리: [-1, 1] 범위의 텐서를 [0, 1] 범위로 변환
    output_tensor = (output_tensor + 1.0) / 2.0
    output_tensor = torch.clamp(output_tensor, min=0.0, max=1.0)
    # 2. 텐서를 PIL 이미지로 변환
    image_tensor = output_tensor.squeeze(0).permute(1, 2, 0).cpu() # (B, C, H, W) -> (C, H, W)
    # 3. NumPy 배열로 변환 및 0-255 범위로 조정
    image_numpy = (image_tensor.numpy() * 255).astype('uint8')
    # 4. PIL 이미지 생성
    pil_image = Image.fromarray(image_numpy)
    return pil_image

#######################################################
# [DFT] Phase Embedding 방식 임베딩 및 검출 함수
#######################################################
@torch.no_grad()
def embed_dft_phase(dft, watermark_bits, multi_bit, alphas):
    num_bits = len(watermark_bits)
    dft = dft.clone()
    # mid_band = dft[8:16, 8:16]
    mid_band = dft[12:16, 12:16]
    magnitude = torch.abs(mid_band)
    phase = torch.angle(mid_band)
    plus_phase = 0
    for i in range(num_bits):
        # 워터마크 비트에 따라 위상 조정
        plus_phase += alphas[i] * multi_bit[i] * watermark_bits[i]
    phase_embed = phase + plus_phase # (8,8)
    epsilon = 1e-2  # 경계값에서 여유를 두는 작은 소수
    phase_embed = torch.clip(phase_embed, -3.1416 + epsilon, 3.1416 - epsilon)  # Clipping
    mid_band = magnitude * torch.exp(1j * phase_embed)
    # dft[8:16, 8:16] = mid_band
    dft[12:16, 12:16] = mid_band
    return dft
@torch.no_grad()
def detect_dft_phase(dft, watermark_bits):
    num_bits = len(watermark_bits)
    # mid_band = dft[8:16, 8:16]
    mid_band = dft[12:16, 12:16]
    phase = torch.angle(mid_band)
    extracted_bits = []
    for i in range(num_bits):
        # 위상 차이를 이용한 상관 검출
        corr = torch.sum(phase * watermark_bits[i])
        extracted_bits.append(corr)
    return torch.sign(torch.tensor(extracted_bits))

# 0 : phase QIM
@torch.no_grad()
def embed_dft_qim(dft, multi_bit, blocks):
    dft = dft.clone()
    for bit_i, rect in zip(multi_bit, blocks):
        x1, y1, x2, y2 = rect
        mid_band = dft[x1:x2, y1:y2]
        magnitude = torch.abs(mid_band)
        phase = torch.angle(mid_band)
        if bit_i == 1:
            phase = np.pi / 2 * torch.ones_like(phase)
        else:
            phase = -np.pi / 2 * torch.ones_like(phase)
        mid_band = magnitude * torch.exp(1j * phase)
        dft[x1:x2, y1:y2] = mid_band
    return dft

@torch.no_grad()
def detect_dft_qim(dft, blocks):
    extracted_bits = []
    for rect in blocks:
        x1, y1, x2, y2 = rect
        mid_band = dft[x1:x2, y1:y2]
        phase = torch.angle(mid_band)
        if phase.sum() > 0:
            extracted_bits.append(1)
        else:
            extracted_bits.append(-1)
    return torch.tensor(extracted_bits, dtype=dft.dtype, device=dft.device)

# 2 : phase quantization
@torch.no_grad()
def get_min_angle_diff(a, b):
    """ 두 각도 사이의 최소 차이를 계산 (-pi ~ pi) """
    return torch.atan2(torch.sin(a - b), torch.cos(a - b))

@torch.no_grad()
def embed_latent_fft_quantization(dft, multi_bit, blocks):
    """ 제안 2: Phase Quantization을 이용한 워터마크 임베딩 """
    dft = dft.clone()
    
    # 비트 1과 -1에 대한 위상 양자화 집합 정의
    quant_set_A = torch.tensor([0, np.pi/2, np.pi, 3*np.pi/2], device=dft.device)
    quant_set_B = torch.tensor([np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4], device=dft.device)

    for bit_i, rect in zip(multi_bit, blocks):
        x1, y1, x2, y2 = rect
        mid_band = dft[x1:x2, y1:y2]
        
        magnitude = torch.abs(mid_band)
        phase_orig = torch.angle(mid_band)
        phase_new = torch.zeros_like(phase_orig)

        target_set = quant_set_A if bit_i == 1 else quant_set_B
        
        # 각 위상 값을 target_set에서 가장 가까운 값으로 양자화
        # phase_orig.unsqueeze(-1) -> [H, W, 1]
        # target_set -> [N_quant]
        # Broadcast를 통해 [H, W, N_quant] 차원에서 각도 차이 계산
        angle_diffs = torch.abs(get_min_angle_diff(phase_orig.unsqueeze(-1), target_set))
        best_indices = torch.argmin(angle_diffs, dim=-1)
        phase_new = target_set[best_indices]

        mid_band_new = magnitude * torch.exp(1j * phase_new)
        dft[x1:x2, y1:y2] = mid_band_new
        
    return dft

@torch.no_grad()
def detect_latent_fft_quantization(dft, blocks):
    """ 제안 2: Phase Quantization 워터마크 검출 """
    extracted_bits = []
    
    quant_set_A = torch.tensor([0, np.pi/2, np.pi, 3*np.pi/2], device=dft.device)
    quant_set_B = torch.tensor([np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4], device=dft.device)

    for rect in blocks:
        x1, y1, x2, y2 = rect
        mid_band = dft[x1:x2, y1:y2]
        phase = torch.angle(mid_band)

        # 각 위성 집합까지의 총 거리 계산
        # unsqueeze와 broadcasting을 활용하여 효율적으로 계산
        dist_A = torch.sum(torch.min(torch.abs(get_min_angle_diff(phase.unsqueeze(-1), quant_set_A)), dim=-1)[0])
        dist_B = torch.sum(torch.min(torch.abs(get_min_angle_diff(phase.unsqueeze(-1), quant_set_B)), dim=-1)[0])

        if dist_A < dist_B:
            extracted_bits.append(1)
        else:
            extracted_bits.append(-1)
            
    return torch.tensor(extracted_bits, dtype=torch.float32, device=dft.device)

# 3 : spread spectrum
def generate_pn_sequence(key, size, device):
    """
    주어진 key로부터 재현 가능한 PN 시퀀스(-1, +1)를 생성합니다.
    """
    generator = torch.Generator(device=device)
    generator.manual_seed(key)
    # 0 또는 1을 생성 -> 2 곱하고 1 빼서 -1 또는 +1로 변환
    pn = (torch.rand(size, generator=generator, device=device) > 0.5) * 2.0 - 1.0
    return pn

def generate_balanced_pn_sequence(key, size, device):
    """
    (개선) +1과 -1의 개수가 항상 절반씩 유지되는 '균형 잡힌' PN 시퀀스를 생성합니다.
    - size: (H, W) 튜플. H*W는 짝수여야 합니다.
    """
    h, w = size
    assert (h * w) % 2 == 0, "블록의 총 픽셀 수는 짝수여야 합니다."
    
    num_elements = h * w
    num_ones = num_elements // 2
    num_minus_ones = num_elements - num_ones
    
    # +1과 -1이 절반씩 있는 기본 시퀀스 생성
    base_sequence = torch.cat([
        torch.ones(num_ones),
        -torch.ones(num_minus_ones)
    ]).to(device)
    
    # key를 이용해 재현 가능한 무작위 순열(permutation) 생성
    generator = torch.Generator(device=device)
    generator.manual_seed(key)
    # randperm: 0부터 n-1까지의 정수를 무작위로 섞어 반환
    indices = torch.randperm(num_elements, generator=generator, device=device)
    
    # 기본 시퀀스를 무작위로 섞음
    shuffled_sequence = base_sequence[indices]
    
    # 2x2 형태로 reshape
    return shuffled_sequence.view(h, w)

@torch.no_grad()
def embed_latent_fft_spread_spectrum(dft, multi_bit, blocks, key=42, alpha=np.pi / 8):
    """
    제안 3: Spread Spectrum을 이용한 워터마크 임베딩
    - key: PN 시퀀스 생성을 위한 시드값
    - alpha: 워터마크 강도
    (개선) 위상 랩핑을 해결한 Spread Spectrum 임베딩
    - 복소수 곱셈을 통해 위상을 더합니다.
    """
    dft = dft.clone()
    for i, (bit_i, rect) in enumerate(zip(multi_bit, blocks)):
        x1, y1, x2, y2 = rect
        mid_band = dft[x1:x2, y1:y2]
        
        # 각 블록마다 고유한 PN 시퀀스 생성을 위해 key와 블록 인덱스(i)를 조합
        pn_sequence = generate_balanced_pn_sequence(key + i, (x2-x1, y2-y1), dft.device)

        # 위상 변화량을 복소수 회전 연산자(rotator)로 변환
        phase_change = (bit_i * alpha) * pn_sequence
        rotator = torch.exp(1j * phase_change)

        # 복소수 곱셈으로 위상 랩핑 없이 안전하게 위상을 더함
        mid_band_new = mid_band * rotator
        dft[x1:x2, y1:y2] = mid_band_new
    return dft

@torch.no_grad()
def detect_latent_fft_spread_spectrum(dft, blocks, key=42, alpha=np.pi / 8):
    """
    (개선) 위상 랩핑을 해결한 Spread Spectrum 검출 (Matched Filter)
    - 복소수 내적(상관관계)을 이용합니다.
    (최종 수정) 크기 정규화를 추가하여 지배적인 계수 문제를 해결한 검출기
    """
    extracted_bits = []
    # 부동소수점 연산에서 0으로 나누는 것을 방지하기 위한 작은 값
    epsilon = 1e-12 
    for i, rect in enumerate(blocks):
        x1, y1, x2, y2 = rect
        z_received = dft[x1:x2, y1:y2]
        
        pn_sequence = generate_balanced_pn_sequence(key + i, (x2-x1, y2-y1), dft.device)
        
        # 가설 H1 (비트 '1' 패턴)
        pattern_1 = torch.exp(1j * alpha * pn_sequence)
        # 가설 H-1 (비트 '-1' 패턴)
        pattern_minus1 = torch.exp(1j * -alpha * pn_sequence)

        # 각 가설로 신호를 복원(demodulate)
        demod_for_1 = z_received * torch.conj(pattern_1)
        demod_for_minus1 = z_received * torch.conj(pattern_minus1)
        # print(torch.abs(demod_for_1))

        # ======================================================================
        # ✨ 핵심 수정: 각 벡터를 더하기 전에 크기를 1로 정규화 ✨
        # ======================================================================
        # 이제 모든 벡터는 크기에 상관없이 동등한 "투표권"을 가집니다.
        norm_demod_1 = demod_for_1 / (torch.abs(demod_for_1) + epsilon)
        norm_demod_minus1 = demod_for_minus1 / (torch.abs(demod_for_minus1) + epsilon)
        
        # 복원된 벡터들의 합의 크기(절대값)를 계산
        # torch.abs()는 복소수의 크기(magnitude)를 반환합니다.
        mag_1 = torch.abs(torch.sum(norm_demod_1))
        mag_minus1 = torch.abs(torch.sum(norm_demod_minus1))

        # 크기가 더 큰 쪽의 가설을 채택
        if mag_1 > mag_minus1:
            extracted_bits.append(1)
        else:
            extracted_bits.append(-1)
            
    return torch.tensor(extracted_bits, dtype=torch.float32, device=dft.device)

# 4 : relative pattern
@torch.no_grad()
def embed_latent_fft_relative_pattern(dft, multi_bit, blocks):
    dft = dft.clone()
    for bit_i, rect in zip(multi_bit, blocks):
        x1, y1, x2, y2 = rect
        # 2x2 블록이 아닐 경우를 대비하여 flatten해서 처리
        mid_band = dft[x1:x2, y1:y2].flatten()
        
        # 4개의 픽셀 p1, p2, p3, p4
        p1, p2, p3, p4 = mid_band
        
        # p1, p3의 크기와 위상은 유지
        mag2, mag4 = torch.abs(p2), torch.abs(p4)
        phase1, phase3 = torch.angle(p1), torch.angle(p3)
        
        if bit_i == 1: # In-phase
            new_phase2 = phase1
            new_phase4 = phase3
        else: # Anti-phase
            new_phase2 = phase1 + np.pi
            new_phase4 = phase3 + np.pi
            
        # p2, p4를 새로운 위상으로 업데이트
        mid_band[1] = mag2 * torch.exp(1j * new_phase2)
        mid_band[3] = mag4 * torch.exp(1j * new_phase4)
        
        dft[x1:x2, y1:y2] = mid_band.view(x2-x1, y2-y1)     
    return dft

@torch.no_grad()
def detect_latent_fft_relative_pattern(dft, blocks):
    extracted_bits = []
    for rect in blocks:
        x1, y1, x2, y2 = rect
        mid_band = dft[x1:x2, y1:y2].flatten()
        
        p1, p2, p3, p4 = mid_band
        phase1, phase2 = torch.angle(p1), torch.angle(p2)
        phase3, phase4 = torch.angle(p3), torch.angle(p4)

        # 각 쌍의 위상 차이를 계산 (랩핑 문제 해결)
        diff1 = get_min_angle_diff(phase1, phase2)
        diff2 = get_min_angle_diff(phase3, phase4)
        
        # cos 값을 이용해 상관 점수 계산
        score = torch.cos(diff1) + torch.cos(diff2)
        
        if score > 0:
            extracted_bits.append(1)
        else:
            extracted_bits.append(-1)
    return torch.tensor(extracted_bits, dtype=torch.float32, device=dft.device)

# 5 : relative pulling
@torch.no_grad()
def embed_latent_fft_relative_pulling(dft, multi_bit, blocks, gamma=0.8):
    """
    (품질 개선) 복소수 보간을 이용해 부드럽게 상대 위상 패턴을 형성합니다.
    - gamma: 워터마크 강도. 클수록 패턴이 강해지고 왜곡이 커짐. (0.1 ~ 0.5 추천)
    """
    dft = dft.clone()
    for bit_i, rect in zip(multi_bit, blocks):
        x1, y1, x2, y2 = rect
        mid_band = dft[x1:x2, y1:y2].flatten()
        
        p1_orig, p2_orig, p3_orig, p4_orig = mid_band
        
        # 목표 위상 설정
        phase1, phase3 = torch.angle(p1_orig), torch.angle(p3_orig)
        if bit_i == 1: # In-phase 목표
            target_phase2 = phase1
            target_phase4 = phase3
        else: # Anti-phase 목표
            target_phase2 = phase1 + np.pi
            target_phase4 = phase3 + np.pi
            
        # p2와 p4에 대한 목표 벡터(Target Vector) 생성
        p2_target = torch.abs(p2_orig) * torch.exp(1j * target_phase2)
        p4_target = torch.abs(p4_orig) * torch.exp(1j * target_phase4)
        
        # 복소 평면에서 gamma 비율로 보간(pulling)
        p2_new = (1 - gamma) * p2_orig + gamma * p2_target
        p4_new = (1 - gamma) * p4_orig + gamma * p4_target
        
        mid_band[1] = p2_new
        mid_band[3] = p4_new
        
        dft[x1:x2, y1:y2] = mid_band.view(x2-x1, y2-y1)
        
    return dft

detect_latent_fft_relative_pulling = detect_latent_fft_relative_pattern

#
# TBD
#

@torch.no_grad()
# SFW - Symmetric Fourier Watermark Enforcement
@torch.no_grad()
def enforce_hermitian_symmetry(freq_tensor):
    B, C, H, W = freq_tensor.shape # fftshifted frequency (complex tensor) - center (32,32)
    assert H == W, "H != W"
    freq_tensor = freq_tensor.clone()
    freq_tensor_tmp = freq_tensor.clone()
    # DC point (no imaginary)
    freq_tensor[:, :, H//2, W//2] = torch.real(freq_tensor_tmp[:, :, H//2, W//2])
    if H % 2 == 0: # Even
        # Nyquist Points (no imaginary)
        freq_tensor[:, :, 0, 0] = torch.real(freq_tensor_tmp[:, :, 0, 0])
        freq_tensor[:, :, H//2, 0] = torch.real(freq_tensor_tmp[:, :, H//2, 0])  # (32, 0)
        freq_tensor[:, :, 0, W//2] = torch.real(freq_tensor_tmp[:, :, 0, W//2])  # (0, 32)
    
        # Nyquist axis - conjugate
        freq_tensor[:, :, 0, 1:W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, 0, W//2+1:], dims=[2]))
        freq_tensor[:, :, H//2, 1:W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, H//2, W//2+1:], dims=[2]))
        freq_tensor[:, :, 1:H//2, 0] = torch.conj(torch.flip(freq_tensor_tmp[:, :, H//2+1:, 0], dims=[2]))
        freq_tensor[:, :, 1:H//2, W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, H//2+1:, W//2], dims=[2]))
        # Square quadrants - conjugate
        freq_tensor[:, :, 1:H//2, 1:W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, H//2+1:, W//2+1:], dims=[2, 3]))
        freq_tensor[:, :, H//2+1:, 1:W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, 1:H//2, W//2+1:], dims=[2, 3]))
    else: # Odd
        # Nyquist axis - conjugate
        freq_tensor[:, :, H//2, 0:W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, H//2, W//2+1:], dims=[2]))
        freq_tensor[:, :, 0:H//2, W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, H//2+1:, W//2], dims=[2]))
        # Square quadrants - conjugate
        freq_tensor[:, :, 0:H//2, 0:W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, H//2+1:, W//2+1:], dims=[2, 3]))
        freq_tensor[:, :, H//2+1:, 0:W//2] = torch.conj(torch.flip(freq_tensor_tmp[:, :, 0:H//2, W//2+1:], dims=[2, 3]))
    return freq_tensor

#######################################################
# Multi-Band DFT 관련 함수
#######################################################
def in_mid_band(x, y, r_min=10, r_max=23):
    r = np.sqrt(x**2 + y**2)
    return (r >= r_min) and (r <= r_max)

def block_in_mid_band(x, y, block_size=2, r_min=10, r_max=23):
    for i in range(block_size):
        for j in range(block_size):
            if not in_mid_band(x+i, y+j, r_min, r_max):
                return False
    return True

def blocks_overlap(b1, b2):
    x11, y11, x12, y12 = b1
    x21, y21, x22, y22 = b2
    if x12 <= x21 or x22 <= x11 or y12 <= y21 or y22 <= y11:
        return False
    return True

def get_bit_blocks(shape, num_bits=15, block_size=2, r_min=10, r_max=23, axis_offset=1):
    """
    대각선 영역을 포함한 대칭 블록 배치 함수
    """
    # max_h, max_w = 32, 32
    max_h, max_w = shape
    candidates = []

    # 가능한 모든 블록 위치 확인 (대각선 포함)
    for x in range(axis_offset, max_h - block_size + 1):
        for y in range(axis_offset, max_w - block_size + 1):
            if block_in_mid_band(x, y, block_size, r_min, r_max):
                cx = x + block_size // 2
                cy = y + block_size // 2
                r = np.sqrt(cx**2 + cy**2)
                manhattan_dist = x + y

                if x == y:  # 대각선 상의 블록
                    candidates.append((x, y, x+block_size, y+block_size, r, manhattan_dist, True))
                elif y > x and block_in_mid_band(y, x, block_size, r_min, r_max):  # 대각선 위쪽 영역
                    candidates.append((x, y, x+block_size, y+block_size, r, manhattan_dist, False))

    # 후보들 정렬
    candidates.sort(key=lambda c: c[4]) # radius가 작은 순서대로 정렬
    # candidates.sort(key=lambda c: c[5]) # 축에 가까운 순서대로 정렬

    selected_blocks = []
    for c in candidates:
        b1 = (c[0], c[1], c[2], c[3])

        if c[6]:  # 대각선 상의 블록
            # 기존 블록들과 겹치지 않는지 확인
            overlap = False
            for existing_block in selected_blocks:
                if blocks_overlap(existing_block, b1):
                    overlap = True
                    break
            if not overlap:
                selected_blocks.append(b1)
        else:  # 대칭쌍
            b2 = (c[1], c[0], c[3], c[2])  # 대칭 블록

            # 기존 블록들과 겹치지 않는지 확인
            overlap = False
            for existing_block in selected_blocks:
                if blocks_overlap(existing_block, b1) or blocks_overlap(existing_block, b2):
                    overlap = True
                    break

            # 대칭 블록끼리도 겹치지 않는지 확인
            if not overlap and not blocks_overlap(b1, b2):
                selected_blocks.append(b1)
                selected_blocks.append(b2)

        if len(selected_blocks) >= num_bits:
            selected_blocks = selected_blocks[:num_bits]
            break

    return selected_blocks

# ====================================================================================================
# For generate mode
@torch.no_grad()
def get_random_latents(pipe, batch_size=1, gen_seed=None, resolution=512):
    if gen_seed:
        g = torch.Generator(device=pipe.device).manual_seed(gen_seed)
        return pipe.prepare_latents(batch_size, pipe.unet.in_channels, resolution, resolution, pipe.unet.dtype, pipe.device, g) # (1,4,64,64)
    return pipe.prepare_latents(batch_size, pipe.unet.in_channels, resolution, resolution, pipe.unet.dtype, pipe.device, None) # (1,4,64,64)

# ====================================================================================================
# [Metrics] image quality : PSNR, SSIM, LPIPS
def path_to_pil(img_path):
    if isinstance(img_path, str) and os.path.isfile(img_path):
        return Image.open(img_path)
    elif isinstance(img_path, Image.Image):   
        return img_path
    else:
        raise ValueError("유효한 파일 경로나 Pillow 이미지 객체를 입력하세요.")

def get_psnr(img1, img2, eps=1e-10):
    # caluclate psnr
    img1 = np.array(path_to_pil(img1).convert('RGB'))
    img2 = np.array(path_to_pil(img2).convert('RGB'))
    mse = np.mean((img1 - img2) ** 2)
    mse = max(mse, eps)
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

def get_ssim(img1, img2):
    # caluclate ssim
    img1 = np.array(path_to_pil(img1).convert('L')) # 흑백으로 변환
    img2 = np.array(path_to_pil(img2).convert('L')) # 흑백으로 변환
    ssim_value, _ = ssim(img1, img2, full=True)
    return ssim_value

loss_fn = lpips.LPIPS(net="vgg").to("cuda")
@torch.no_grad()
def get_lpips(img1, img2, device="cuda"):
    # caluclate LPIPS(VGG): image should be RGB, normalized to [-1,1]
    img1 = transform_img(path_to_pil(img1).convert('RGB'), resolution=224).unsqueeze(0).to(torch.float32).to(device)
    img2 = transform_img(path_to_pil(img2).convert('RGB'), resolution=224).unsqueeze(0).to(torch.float32).to(device)
    lpips_value = loss_fn(img1, img2)
    return lpips_value.item()

# [Metrics] generation quality : CLIP score, FID
@torch.no_grad() 
def get_clip_score(image_batch, prompt_batch, model, clip_preprocess, tokenizer, device="cuda"):
    image_batch = [image_batch] if isinstance(image_batch, Image.Image) else image_batch    # N_i : image num_batch
    prompt_batch = [prompt_batch] if isinstance(prompt_batch, str) else prompt_batch        # N_p : prompt num_batch
    assert len(image_batch) == len(prompt_batch)
    # image features
    img_batch = [clip_preprocess(image).unsqueeze(0) for image in image_batch]
    img_batch = torch.concatenate(img_batch).to(device) # (N_i,3,224,224)
    image_features = model.encode_image(img_batch) # (N_i,1024)
    # text features
    text = tokenizer(prompt_batch).to(device) # (N_p,77)
    text_features = model.encode_text(text) # (N_p,1024)
    # normalize
    image_features /= image_features.norm(dim=-1, keepdim=True) # (N_i,1024)
    text_features /= text_features.norm(dim=-1, keepdim=True) # (N_p,1024)
    # return (image_features @ text_features.T).mean(-1) # (N_i,1024)@(1024,N_p)=(N_i,N_p) -> mean(-1) -> (N_i,)
    return (image_features * text_features).sum(-1) # (N_i,)=(N_p,)

# FID : Folder-based measurement (total image distribution)
def get_FID(gt_folder, target_folder, device="cuda"):
    return calculate_fid_given_paths([gt_folder, target_folder], batch_size=64, device=device, dims=2048, num_workers=16)

#######################################################
# Distort
#######################################################
class RandomCropWithOriginalPosition:
    def __init__(self, crop_size, original_size, fill=0):
        self.crop_size = crop_size
        self.original_size = original_size
        self.fill = fill

    def __call__(self, img):
        w, h = img.size
        top = random.randint(0, h - self.crop_size)
        left = random.randint(0, w - self.crop_size)
        cropped_img = img.crop((left, top, left + self.crop_size, top + self.crop_size))
        padded_img = Image.new(img.mode, (self.original_size, self.original_size), self.fill)
        padded_img.paste(cropped_img, (left, top))
        return padded_img

vaeb = bmshj2018_hyperprior(quality=3, pretrained=True).to("cuda").eval()
vaec = cheng2020_anchor(quality=3, pretrained=True).to("cuda").eval()
@torch.no_grad()
def image_distortion(img1, img2, seed, 
                     brightness_factor = None, 
                     contrast_factor = None, 
                     jpeg_ratio = None, 
                     gaussian_blur_r = None, 
                     gaussian_std = None, 
                     bm3d_sigma = None,
                     vaeb_quality = None,
                     vaec_quality = None,
                     center_crop_area_ratio = None,
                     random_crop_area_ratio = None,
                     ):
    if brightness_factor is not None:
        if img1 is not None:
            img1 = tforms.ColorJitter(brightness=brightness_factor)(img1)
        img2 = tforms.ColorJitter(brightness=brightness_factor)(img2)
    if contrast_factor is not None:
        if img1 is not None:
            img1 = ImageEnhance.Contrast(img1).enhance(contrast_factor)
        img2 = ImageEnhance.Contrast(img2).enhance(contrast_factor)
    if jpeg_ratio is not None:
        if img1 is not None:
            buf = io.BytesIO()
            img1.save(buf, format='JPEG', quality=jpeg_ratio)
            img1 = Image.open(buf)
        buf2 = io.BytesIO()
        img2.save(buf2, format='JPEG', quality=jpeg_ratio)
        img2 = Image.open(buf2)
    if gaussian_blur_r is not None:
        if img1 is not None:
            img1 = Image.fromarray(cv2.GaussianBlur(np.array(img1), (gaussian_blur_r, gaussian_blur_r), 1))
        img2 = Image.fromarray(cv2.GaussianBlur(np.array(img2), (gaussian_blur_r, gaussian_blur_r), 1))
    if gaussian_std is not None:
        img_shape = np.array(img1).shape
        g_noise = np.random.normal(0, gaussian_std, img_shape) * 255
        g_noise = g_noise.astype(np.uint8)
        if img1 is not None:
            img1 = Image.fromarray(np.clip(np.array(img1) + g_noise, 0, 255))
        img2 = Image.fromarray(np.clip(np.array(img2) + g_noise, 0, 255))
    if bm3d_sigma is not None:
        if img1 is not None:
            img1 = Image.fromarray((np.clip(bm3d_rgb(np.array(img1) / 255, bm3d_sigma), 0, 1) * 255).astype(np.uint8))
        img2 = Image.fromarray((np.clip(bm3d_rgb(np.array(img2) / 255, bm3d_sigma), 0, 1) * 255).astype(np.uint8))
    if vaeb_quality is not None:
        assert vaeb_quality == 3, "Only quality 3 is supported for VAE-B"
        img_transforms = tforms.Compose([tforms.Resize((512,512)), tforms.ToTensor()])
        if img1 is not None:
            enc1 = vaeb.compress(img_transforms(img1).unsqueeze(0).to("cuda"))
            dec1 = vaeb.decompress(enc1['strings'], enc1['shape'])
            img1 = tforms.ToPILImage()(dec1['x_hat'].squeeze())
        enc2 = vaeb.compress(img_transforms(img2).unsqueeze(0).to("cuda"))
        dec2 = vaeb.decompress(enc2['strings'], enc2['shape'])
        img2 = tforms.ToPILImage()(dec2['x_hat'].squeeze())
    if vaec_quality is not None:
        assert vaec_quality == 3, "Only quality 3 is supported for VAE-C"
        img_transforms = tforms.Compose([tforms.Resize((512,512)), tforms.ToTensor()])
        if img1 is not None:
            enc1 = vaec.compress(img_transforms(img1).unsqueeze(0).to("cuda"))
            dec1 = vaec.decompress(enc1['strings'], enc1['shape'])
            img1 = tforms.ToPILImage()(dec1['x_hat'].squeeze())
        enc2 = vaec.compress(img_transforms(img2).unsqueeze(0).to("cuda"))
        dec2 = vaec.decompress(enc2['strings'], enc2['shape'])
        img2 = tforms.ToPILImage()(dec2['x_hat'].squeeze())
    if center_crop_area_ratio is not None:
        crop_len = int(512 * (center_crop_area_ratio ** 0.5))
        padding_left = (512 - crop_len) // 2
        padding_right = (512 - crop_len) - padding_left
        center_crop_transforms = tforms.Compose([
            tforms.CenterCrop(size=(crop_len, crop_len)),
            tforms.Pad(padding=(padding_left, padding_left, padding_right, padding_right), fill=0),])
        if img1 is not None:
            img1 = center_crop_transforms(img1)
        img2 = center_crop_transforms(img2)
    if random_crop_area_ratio is not None:
        crop_len = int(512 * (random_crop_area_ratio ** 0.5))
        random_crop_transforms = RandomCropWithOriginalPosition(crop_len, 512, fill=0)
        if img1 is not None:
            img1 = random_crop_transforms(img1)
        img2 = random_crop_transforms(img2)
    return [img1, img2]

# ====================================================================================================
# [Watermark Verification Thresholds]
def compute_verification_thresholds(marklength, fpr, user_number):
    """
    Compute bit-accuracy thresholds for watermark verification and user attribution
    via one-sided binomial hypothesis testing.

    Under H0 (no watermark), each bit matches with p=0.5, so correct ~ Binomial(marklength, 0.5).
    - tau_onebit : smallest threshold where P(X > i | H0)             <= fpr
    - tau_bits   : smallest threshold where P(X > i | H0)*user_number <= fpr  (Bonferroni)

    Returns (tau_onebit, tau_bits) as bit-accuracy fractions in [0, 1].
    """
    from scipy.special import betainc
    tau_onebit = None
    tau_bits = None
    for i in range(marklength + 1):
        fpr_val = betainc(i + 1, marklength - i, 0.5)  # P(X > i | H0)
        if fpr_val <= fpr and tau_onebit is None:
            tau_onebit = i / marklength
        if fpr_val * user_number <= fpr and tau_bits is None:
            tau_bits = i / marklength
    if tau_onebit is None:
        tau_onebit = 1.0
    if tau_bits is None:
        tau_bits = 1.0
    return tau_onebit, tau_bits


# ====================================================================================================
# [Random Seed]
def set_random_seed(seed=0):
    torch.manual_seed(seed + 0)
    torch.cuda.manual_seed(seed + 1)
    torch.cuda.manual_seed_all(seed + 2)
    np.random.seed(seed + 3)
    torch.cuda.manual_seed_all(seed + 4)
    random.seed(seed + 5)