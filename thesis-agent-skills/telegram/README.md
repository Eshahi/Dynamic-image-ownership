# Telegram bridge

This bridge is a deterministic transport for Spec Kit. It does not use Hermes, an LLM, or a
second workflow engine. It sends meaningful workflow changes and accepts only exact commands
from one allowlisted private Telegram user and chat.

Set these values in the process environment, using the BotFather token and your numeric private
Telegram user/chat ID. Never write real values into this repository.

```text
THESIS_TELEGRAM_BOT_TOKEN
THESIS_TELEGRAM_ALLOWED_USER_ID
THESIS_TELEGRAM_ALLOWED_CHAT_ID
```

Validate local configuration without contacting Telegram:

```text
python skills/thesis-workflow-control/scripts/telegram_bridge.py --project <project> check
```

Send a live test message:

```text
python skills/thesis-workflow-control/scripts/telegram_bridge.py --project <project> send "Bridge test"
```

Start local long polling and meaningful-state notifications:

```text
python skills/thesis-workflow-control/scripts/telegram_bridge.py --project <project> run
```

Do not run Hermes, another long poller, or a webhook for the same bot token at the same time.

The only state-changing chat commands are exact, authenticated gate decisions:

```text
/approve <run-id> <step-id>
/reject <run-id> <step-id>
```

Status is read-only:

```text
/status <run-id>
```

Unknown commands and free-form text are never executed. The bridge records its delivery cursor
under `.thesis-notify/`, which must remain outside Git. Workflow state continues to belong only
to Spec Kit. If the bridge is offline, the workflow remains paused at a gate.
