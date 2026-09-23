# SEAL v4 inspection record

Inspected 2026-09-23 (UTC) by /root using public arXiv HTML.
Source: https://arxiv.org/html/2503.12172v4
Identity: Kasra Arabi; R. Teal Witter; Chinmay Hegde; Niv Cohen.
Title: SEAL: Semantic Aware Image Watermarking.
First submitted 2025; inspected revision v4 dated 2026-05-18.
DOI: 10.48550/arXiv.2503.12172 (record-level, not revision-specific).

## Exact excerpt

Section 3.2, Semantic Patterns with SimHash:
> For cryptographic security, we also use a user-specific secret salt.

## Inspection notes

Section 3.2, Algorithms 1–3: generation captions a proxy image with BLIP-2, embeds its caption with Paraphrase Mpnet Base V2, and uses SimHash-derived noise patches. Detection compares reconstructed noise from inverse diffusion with expected patches. This is not an image-domain DCT detector.

## Limits

Targeted full-text inspection, not a complete paper or code audit. No experiment reproduced. This short excerpt and observer notes are not a redistributed full-text snapshot; their checksum protects this record only, not the remote paper. The proposal's unversioned 2025 reference must not be treated as identical to this later revision. No claim that the proposed thesis method is infeasible follows from this record.
