# Superseded quality-model attempt

This first diagnostic fit used a linear beta schedule for the R0 logSNR covariate in D3. The frozen R0 DDIM scheduler uses scaled_linear betas: (sqrt(0.00085) + i/999 * (sqrt(0.012)-sqrt(0.00085)))^2. D0-D2 and data extraction were unaffected, but D3 scores and coefficients require rerunning. This copy is retained for provenance.
