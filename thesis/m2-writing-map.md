# Current M2 evidence-to-writing map

Status: draft for review, 2026-10-07. This map records the current evidence and authorized scope amendments. It does not change the protected proposal, source plan or claim ledger.

## Exact approved research questions

### RQ-01

چگونه می‌توان با تلفیق بردارهای معنایی و کدهای هش ادراکی، امضایی برای تصویر تولید کرد که همزمان با حفظ یکتایی، در برابر ویرایش‌های مجاز پایدار باقی بماند؟

Operational reading: Test a combined semantic and perceptual signature for instance distinction and stability under explicitly permitted edits.

### RQ-02

آیا انتقال محل جاسازی واترمارک از فضای پیکسل به فضای پنهان در مدل‌های انتشار، تأثیر معناداری بر افزایش نرخ بقای واترمارک در برابر حملات بازتولید خواهد داشت؟

Operational reading: Compare latent-space embedding with a pixel-space comparator on watermark survival under regeneration.

### RQ-03

چگونه می‌توان با تحلیل آماری ضرایب فرکانسی میانی، وجود و صحت واترمارک را با دقتی قابل رقابت با دیکودرهای عصبی اما با سرعت بیشتر تشخیص داد؟

Operational reading: Compare mid-band DCT detection with neural decoders on detection quality and inference time.

### RQ-04

آیا معماری پیشنهادی توانایی تفکیک میان تصویر اصلی و تصویر جعلی که دارای واترمارک کپی‌شده است را دارا می‌باشد؟

Operational reading: Measure discrimination between a valid original and different content carrying a copied watermark.

## Relationship to the earlier outline

The earlier `thesis/outline.md` and `format-checklist.md` are copied verbatim from worktree `b6-thesis-outline`, commit `0e184241b27a29f0bb46f17f1ab470792984b8fb`. They remain a historical working outline, not a current frozen method or institutional template. This map supplies the current bridge rather than silently rewriting that source.

| Area | Current draft treatment |
|---|---|
| Question order | Chapter 5 and Chapter 6 answer RQ1–RQ4; untested questions retain their places |
| Method | Frozen F5 r2: pixel perturbation optimized through SD1.5 VAE; encoder-latent DCT plus fragile image tier. Initial-noise and image-only 8×8 DCT commitments are explicitly different |
| Threats | Current user scope is T3 regeneration, T4 copy-paste, T5 collision. Older T1/T2/T6 entries in the outline do not authorize new experiments |
| Data | Narrowed approved 300-source COCO512 run; original 1,000 COCO, DIV2K and DiffusionDB commitments are not represented as completed |
| Results | Reviewed frozen run and its quality failures; no fresh held-out tuning |
| Statistics | Frozen bounds, source/pair units and unadjusted paired sign tests. No new bootstrap or Holm analysis |
| Acceptance | Draft writing authorized; no formal human M2 acceptance, chapter finalization or institutional acceptance recorded |
| Language and format | English working prose per project instruction; exact approved Persian questions preserved above. University format is unresolved |

## Deliverables and unresolved evidence

Chapter 5 reports inventory, all primary clean controls, quality failures, T3 total/checked outcomes, paired tests, T4 delivery/rejection and T5 exclusions. Chapter 6 treats each question, causal/security/provenance limits, and proposed follow-up work. The separate writing claim inventory traces every claim block to the exact retained run and source paths.

TODO:EVIDENCE markers identify unresolved experiments or assessments. A limitation such as “no neural comparison exists” can be verified while the missing positive efficiency claim remains untested. No external paper is cited for a new performance comparison here; the existing bibliography is preserved for later source-checked assembly.

Remaining documentary work includes aligning introduction/method/design chapters with this bounded evidence and the actual implementation, and later applying the authenticated university template. These drafts do not rewrite the approved title or decide its dynamic-ownership scope for the institution.
