# ROBIN: Robust and Invisible Watermarks for Diffusion Models with Adversarial Optimization

Primary source: https://arxiv.org/html/2411.03862v2

Inspected: Sec.3.1-3.4; Sec.4.1/Table1; Table3. Full-text artifact/checksum in paper JSON and inventory.

Injects a strong frequency watermark into an intermediate diffusion state (training timestep200-300), jointly optimizes watermark and reusable hiding prompt; remaining denoising conceals it. Detector uses null prompt CFG1 and partial inversion to injection state, then L1 reference matching. Main SD2 uses50-step DPM-Solver; watermark optimization50 images/1000 rounds. Table1 SD average attack AUC .983 versus Tree-Ring .975; verification .531s versus2.599s on RTX3090. Table3 stacked attacks reduce ROBIN AUC from .973 to .556 (last listed setting).

Limitations: Still needs diffusion model, inversion, injection point and watermark key; .531s is hardware-specific. Main table ordinary transformations is not a regeneration sweep. Hiding prompt during inversion hurts recovery.
