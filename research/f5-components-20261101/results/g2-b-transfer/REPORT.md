# G2-B saved-mark residual-transfer panel

MEASURED: Exploratory development results. Fixed 8 DESIGN donors x 30 EVALUATE recipients x 2 scales.

MEASURED: 480/480 successful reads; 480 meet PSNR > 35 dB and SSIM > .9. B-and-not-C strict-quality events: 2. G2-B status: KILL.

| Endpoint | All successful reads | Strict PSNR/SSIM |
|---|---:|---:|
| C | 0 | 0 |
| O | 14 | 14 |
| O_U | 8 | 8 |
| Bs | 0 | 0 |
| Bi | 2 | 2 |
| B | 2 | 2 |

MEASURED: Per-donor and per-recipient counts, including scales and missingness, are in by-donor.csv and by-recipient.csv. Every successful raw detector call and quality result is preserved in batch JSONL; exact input and run hashes are in inventory.json and batch run files.

DERIVED: With zero events in 480 independent trials, the one-sided 95% binomial upper bound would be 0.622%. These images are dependent through repeated donors and recipients, so that interpretation does not apply.

JUDGMENT: Any strict-quality B accept rejected by C kills B promotion under the fixed ruling. Zero G2-B events establish neither adaptive security nor satisfaction of the separate G2-A conditions. No human visual verdict was supplied.
