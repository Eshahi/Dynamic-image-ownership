# C2 synthesis

The retained thesis tests establish survival under particular image-to-image regenerators. They do not cover the full regeneration threat. Three distinctions from the inspected literature should organize the article.

First, attack strength is not a common unit. Zhao's removal curves, WAVES performance-quality analysis and CtrlRegen's semantic/spatial conditioning all show why a strength number alone is insufficient. Fresh-noise regeneration can retain recognizable semantics while changing pixels substantially. The thesis must define the permissible same-instance relation before evaluating the detector, then report quality and detection together. The 18.126 dB boundary is an operational classification rule, not a general perceptual or legal boundary.

Second, access differs. Repeated regeneration, query-free spectral disruption, known-encoder optimization, paired-payload VAE training and leaderboard-adapted attacks require different information and resources. A reviewer can reasonably ask for a public-encoder adaptive T3 attack against F5 because F5 optimizes through that encoder. However, the current session found no direct evidence that a particular robustified encoder already defeats this exact system. Such a test is a future hypothesis, with costs and conditions to be specified.

Third, the target outcome matters. Local watermark localization, detector-bit survival, identifying a processing trace and returning a registered record are not interchangeable. The 2026 local benchmark shows that nominally local inpainting can reconstruct an entire image; this matters to the exact T4 implementation. The forensic-stealth study shows that watermark removal can leave detectable traces; it does not recover the owner pointer. A successful forensic classifier cannot be substituted for a registry authentication result.

The highest-value future T3 additions are therefore an independent encoder family, controlled fresh-noise regeneration, and a declared adaptive known-encoder removal attack, all with a fixed instance relation and a matched quality budget. No such test was run here. Scope-expanding attacks such as cropping remain a short limitation unless separately authorized.

The source cards preserve version and threshold differences. None of their rates is a valid head-to-head baseline for the frozen thesis results without a matched protocol. The Q-VAE note further establishes that SD2.1 is an unseen diffusion checkpoint but does not by itself test an independent VAE encoder family.
