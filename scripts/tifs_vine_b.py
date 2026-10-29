"""VINE-B bound-carrier comparator; importable with the standard library alone.

The public-derived HMAC is check redundancy, not cryptographic authentication.
Only the server adapter imports science libraries. Original q/h are evaluator
references and are never inputs to the operational reader.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import hmac
from itertools import combinations
import struct
import time

DOMAIN = b"tifs-vine-b/v1/q-tag"
MASK_DOMAIN = b"tifs-vine-b/v1/h-mask"
RADIUS = 4
PAYLOAD_BITS = 100


def _word(value):
    if type(value) is not int or not 0 <= value < 2**32:
        raise ValueError("q and h must be unsigned 32-bit integers")
    return value


def _context(key, config, owner):
    if not isinstance(key, bytes) or not key:
        raise ValueError("Nonempty resolved profile key required")
    if not isinstance(config, bytes) or len(config) != 32:
        raise ValueError("32-byte detector configuration ID required")
    if not isinstance(owner, bytes) or not owner:
        raise ValueError("Canonical nonempty owner bytes required")


def frame(q, config, owner, *, domain=DOMAIN):
    """Length-prefix every field (unsigned 32-bit big endian)."""
    fields = (domain, config, owner, _word(q).to_bytes(4,"big"))
    return b"".join(struct.pack(">I",len(part))+part for part in fields)


def tag36(q, key, config, owner):
    _context(key,config,owner)
    return int.from_bytes(hmac.new(key,frame(q,config,owner),hashlib.sha256).digest()[:5],"big") >> 4


def mask32(q, key, config, owner):
    _context(key,config,owner)
    return int.from_bytes(hmac.new(key,frame(q,config,owner,domain=MASK_DOMAIN),hashlib.sha256).digest()[:4],"big")


def _codeword(q, key, config, owner, tagger=tag36):
    return (_word(q) << 36) | tagger(q,key,config,owner)


def encode_payload(q, h, key, config, owner):
    """q32 || tag36 || (h XOR mask32(owner,q)), most-significant bit first."""
    word = (_codeword(q,key,config,owner) << 32) | (_word(h)^mask32(q,key,config,owner))
    return [(word >> i)&1 for i in range(99,-1,-1)]


def _bits(bits):
    try:
        bits = tuple(bits)
    except TypeError as exc:
        raise ValueError("Expected exactly 100 integer binary bits") from exc
    if len(bits) != PAYLOAD_BITS or any(type(b) is not int or b not in (0,1) for b in bits):
        raise ValueError("Expected exactly 100 integer binary bits")
    return bits


def _decode_uncached(bits, key, config, owner, *, tagger=tag36):
    """Exhaust all q32 candidates within radius4 of observed q.

    The injectable tagger is private and permits collision/ambiguity unit tests.
    Every production call uses the fixed domain-separated HMAC above.
    """
    _context(key,config,owner)
    bits = _bits(bits)
    raw100 = int("".join(map(str,bits)),2)
    raw = raw100 >> 32
    data = raw >> 36
    # All candidates share the framed domain/config/owner and q length.
    # Copy the HMAC prefix state rather than rebuilding it 41,449 times.
    tag_context = hmac.new(key,frame(0,config,owner)[:-4],hashlib.sha256) if tagger is tag36 else None
    matches, candidate, examined = 0, None, 0
    for errors in range(RADIUS+1):
        for positions in combinations(range(32),errors):
            delta = 0
            for position in positions:
                delta |= 1 << position
            value = data ^ delta
            q = value
            if tag_context is not None:
                candidate_context=tag_context.copy()
                candidate_context.update(q.to_bytes(4,"big"))
                tag=int.from_bytes(candidate_context.digest()[:5],"big") >> 4
            else:
                tag=tagger(q,key,config,owner)
            distance = (raw ^ ((q << 36)|tag)).bit_count()
            examined += 1
            if distance <= RADIUS:
                matches += 1
                candidate = (q,distance)
    result = dict(unique=matches==1, candidates=matches, candidates_examined=examined,
                  radius=RADIUS, q=None,h=None,distance=None,
                  status="unique" if matches==1 else "ambiguous" if matches else "no_codeword")
    if matches == 1:
        q,distance=candidate
        h=(raw100 & 0xffffffff)^mask32(q,key,config,owner)
        result.update(q=f"{q:08x}",h=f"{h:08x}",distance=distance)
    result["h_recovery"]="unmasked observed field; no error correction or independent presence test"
    return result


@lru_cache(maxsize=256)
def _cached_decode(bits, key, config, owner):
    return tuple(_decode_uncached(bits,key,config,owner).items())


def decode_payload(bits, key, config, owner):
    return dict(_cached_decode(_bits(bits),key,config,owner))


def delivery_diagnostics(raw_bits, decoding, payload):
    """Evaluator-only comparison, after operational reading is complete."""
    if payload is None:
        return None
    target = _bits(payload["bits"])
    raw_bits = _bits(raw_bits)
    errors = sum(a!=b for a,b in zip(raw_bits,target))
    parts = {name:sum(a!=b for a,b in zip(raw_bits[lo:hi],target[lo:hi]))
             for name,lo,hi in (("q",0,32),("tag",32,68),("masked_h",68,100))}
    return dict(raw_payload_bit_errors=errors,raw_payload_accuracy=1-errors/100,
                raw_payload_exact=errors==0,
                raw_q_bit_errors=parts["q"],raw_q_accuracy=1-parts["q"]/32,
                raw_tag_bit_errors=parts["tag"],raw_tag_accuracy=1-parts["tag"]/36,
                raw_masked_h_bit_errors=parts["masked_h"],raw_masked_h_accuracy=1-parts["masked_h"]/32,
                decoded_h_bit_errors=(int(decoding["h"],16)^int(payload["h"],16)).bit_count() if decoding["unique"] else None,
                corrected_payload_exact=bool(decoding["unique"] and decoding["q"]==payload["q"] and decoding["h"]==payload["h"]))


class VineB:
    """Server-only VINE adapter plus seven-view CPU CLIP; no reader VAE."""
    def __init__(self, assets, base, encoding=False):
        import encoder_transfer_runtime as rt
        import f5_latent_codec as f5
        import revised_watermark_v5 as v5
        import three_threat_models as models
        from a6_clip_visual import load_visual_encoder
        from f5_gate import semantic_feature
        self.vine = rt.Vine(assets,encoding=encoding)
        self.f5,self.v5,self.models,self.semantic_feature=f5,v5,models,semantic_feature
        self.clip,self.transform=load_visual_encoder(assets/"a6/clip/ViT-B-32.pt",device="cpu")
        self.profile=rt.read(rt.ROOT/base["profile_file"])
        self.checked,self.key,self.config=v5._resolve(self.profile,None)
        if self.checked["security"] != "public-derived":
            raise ValueError("VINE-B protocol requires the frozen public-derived profile")

    def features(self,rgb):
        return self.semantic_feature(self.models,self.clip,self.transform,rgb,7)

    def codes(self,rgb,features,*,binding=False):
        luma=self.v5.luminance_from_rgb(rgb.tolist())
        base=self.v5.base
        base._check_image(luma,int(self.checked["minimum_side"]))
        # _Fragile.analysis starts with these exact hash-detail planes; the
        # later carrier planes are not consumed by _perceptual_hash.
        means,coefficients=base._analyse(luma,base._DETAIL_PLANES)
        return (self.v5._semantic(means,self.checked,self.key,self.config,features,binding=binding),
                base._perceptual_hash(means,coefficients,self.key,self.config))

    def embed(self,rgb,owner):
        q,h=self.codes(rgb,self.features(rgb),binding=True)
        bits=encode_payload(q,h,self.key,self.config,self.v5.canonical_owner(owner))
        marked=self.vine.embed(rgb,bits)
        payload=dict(q=f"{q:08x}",h=f"{h:08x}",bits=bits,h_target_basis="original before VINE embedding; never replaced")
        return marked,payload,dict(family="vine-b",layout="q32-public-check36-masked-h32",binding="soft",
            security="public-derived check redundancy; no cryptographic authentication",semantic_views=7)

    def blind(self,rgb):
        # Dummy presence is discarded: the target is never given to the reader.
        result=self.vine.detect(rgb,[0]*100)
        return dict(raw=result["raw"],native=result.get("native"))

    def read(self,rgb,owner,*,blind=None,features=None):
        tick=time.monotonic()
        if blind is None: blind=self.blind(rgb)
        if features is None: features=self.features(rgb)
        q_now,h_now=self.codes(rgb,features)
        owner_bytes=self.v5.canonical_owner(owner)
        decoded=decode_payload(blind["raw"]["decoded_message"],self.key,self.config,owner_bytes)
        found=decoded["unique"]
        semantic=dict(found=found,read=found,decoded_code=decoded["q"],
            corrected_distance=(int(decoded["q"],16)^q_now).bit_count() if found else None,
            decoding_error_rate=0.0 if found else None)
        instance=dict(found=found,read=found,decoded_code=decoded["h"],
            corrected_distance=(int(decoded["h"],16)^h_now).bit_count() if found else None,
            decoding_error_rate=None,independent_carrier_evidence=False,
            recovery="unmasked observed h; no h error correction or separate presence test")
        decision=self.checked["decision"]
        s_status=i_status=soft_distance=None
        base=self.v5.base
        if found:
            s_status,soft_distance=self.f5._semantic_status(semantic,features,self.key,self.config,
                (int(decision["semantic_radius"]),int(decision["semantic_mismatch_distance"])),True,"soft")
            i_status=max(base._content_status(instance["corrected_distance"],int(decision["instance_radius"]),
                int(decision["instance_mismatch_distance"]),True),s_status,key=base._STATUS_RANK.get)
        outcome,state=base._decide(found,s_status,found,i_status)
        for channel,status in ((semantic,s_status),(instance,i_status)):
            channel.update(content_status=status,content_match=bool(found and base._STATUS_RANK[status]==0))
        semantic["soft_distance"]=soft_distance
        return dict(family="vine-b",revision=1,outcome=outcome,proposal_state=state,watermark_found=found,
            semantic=semantic,instance=instance,semantic_code=f"{q_now:08x}",perceptual_hash=f"{h_now:08x}",
            owner_id=owner_bytes.decode("utf-8"),binding="soft",binding_mode="combined",detector_config_id=self.config.hex(),
            carrier_decode=decoded,native=blind,seconds=time.monotonic()-tick,
            carrier_detection="unique radius-4 q32+tag36 codeword; h unmasked conditional on q-read; not F5 carrier key tests",
            security="public-derived check redundancy; no cryptographic authentication",
            side_information=["public OwnerID","profile","pinned CLIP weights","pinned VINE decoder weights"])
