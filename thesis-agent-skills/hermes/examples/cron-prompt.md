# Disabled example: status inspection only

This is a prompt example, not a registered job or HEARTBEAT.md. Nothing is scheduled.
After explicit user activation, use Hermes's supported `cronjob` tool or `hermes cron` CLI
to create a job in the intended profile. Do not edit Hermes's cron store directly.

Suggested job prompt:

> Inspect only the user's explicitly selected thesis Spec Kit project and exact workflow run.
> Use thesis-workflow-control watch-once with the last successfully delivered token. If there
> is no output, stay silent. On a meaningful transition, deliver the bounded message through
> Hermes. At a human gate, prepare the review package and request an explicit decision; never
> resume from cron. Do not create, approve, retry or spend. Record a delivery token only after
> a successful send. If no run is configured, stay silent and leave the job disabled.

Hermes may start each cron execution with a fresh agent session. Persist delivery tokens
through a reviewed Hermes-managed storage mechanism when enabling the job; do not assume
conversation memory survives. Delivery acknowledgement remains outside the read-only helper.
