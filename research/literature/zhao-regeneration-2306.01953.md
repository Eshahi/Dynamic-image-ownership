# Zhao et al. — Invisible Image Watermarks Are Provably Removable Using Generative AI (arXiv 2306.01953, v3 2024-10-31)

- URL: https://arxiv.org/abs/2306.01953
- Access: B1 targeted inspection Thms 4.3-4.4, Alg.1, App.E.

## Claim
Regeneration x = A(phi(x_w)+N(0,sigma^2 I)) removes invisible marks; bound f(e1)=Phi(Phi^{-1}(1-e1)-L*Delta/sigma).

## Mechanism
Theory with phi embedding map, A reconstruction. Practical: VAE/diffusion img2img.

## Threat model
Black-box regeneration without detector queries. Exactly F5 T3 SD1.5 img2img .4/.5/.6.

## Numbers
Theorem only. F5 probe: encoder-amplified 20-27x latent gain at equal PSNR, keep-rate .34 -> .57 at .4.

## Relevance to F5
Design equation. F5 exploits by maximizing L through encoder. Current diagnostic: carrier never lost at .4, binding is bottleneck.
