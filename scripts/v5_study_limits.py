"""User-requested 45-minute ceiling; inner deadlines leave time for cleanup."""

MAX_SECONDS = 2700
WORKER_SECONDS = 2500
WSL_SECONDS = 2600
KILL_GRACE_SECONDS = 30
LAUNCHER_SECONDS = 2650
BUDGET = {"max_seconds": MAX_SECONDS, "max_usd": 0, "hourly_usd": 0}
