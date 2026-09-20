"""Deterministic Telegram transport for Spec Kit status and gate decisions."""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from . import control
from .common import ContractError, contained, parser, redact, write

TOKEN_ENV = "THESIS_TELEGRAM_BOT_TOKEN"
USER_ENV = "THESIS_TELEGRAM_ALLOWED_USER_ID"
CHAT_ENV = "THESIS_TELEGRAM_ALLOWED_CHAT_ID"
STATE_DEFAULT = ".thesis-notify/telegram-state.json"
COMMAND = re.compile(
    r"^/(status)\s+([A-Za-z0-9][A-Za-z0-9_-]{0,127})$|"
    r"^/(approve|reject)\s+([A-Za-z0-9][A-Za-z0-9_-]{0,127})\s+"
    r"([A-Za-z0-9][A-Za-z0-9_-]{0,127})$"
)
HELP = (
    "Accepted commands:\n"
    "/status <run-id>\n"
    "/approve <run-id> <step-id>\n"
    "/reject <run-id> <step-id>"
)


def _positive_id(value: str | None, name: str) -> int:
    try:
        result = int(value or "")
    except ValueError:
        raise ContractError(f"{name} must be a positive integer") from None
    if result <= 0:
        raise ContractError(f"{name} must be a positive integer")
    return result


def token_configuration(env=None):
    env = os.environ if env is None else env
    token = env.get(TOKEN_ENV, "")
    if not re.fullmatch(r"[0-9]+:[A-Za-z0-9_-]{20,}", token):
        raise ContractError(f"Set {TOKEN_ENV} to the BotFather token outside source control")
    return token


def configuration(env=None):
    env = os.environ if env is None else env
    return {
        "token": token_configuration(env),
        "user_id": _positive_id(env.get(USER_ENV), USER_ENV),
        "chat_id": _positive_id(env.get(CHAT_ENV), CHAT_ENV),
    }


class TelegramAPI:
    def __init__(self, token, opener=urlopen):
        self.token = token
        self.opener = opener

    def call(self, method, values, timeout=40):
        request = Request(
            f"https://api.telegram.org/bot{self.token}/{method}",
            data=urlencode(values).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with self.opener(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ContractError(f"Telegram API request failed with HTTP status {exc.code}") from None
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ContractError("Telegram API request failed: " + type(exc).__name__) from None
        if not isinstance(payload, dict) or not payload.get("ok"):
            description = payload.get("description", "invalid response") if isinstance(payload, dict) else "invalid response"
            raise ContractError("Telegram API rejected request: " + redact(description))
        return payload.get("result")

    def send(self, chat_id, message):
        text = str(message).strip()
        if not text:
            raise ContractError("Refusing to send an empty Telegram message")
        result = None
        for start in range(0, len(text), 3500):
            result = self.call("sendMessage", {"chat_id": chat_id, "text": text[start:start + 3500]})
        return result

    def updates(self, offset, timeout):
        result = self.call(
            "getUpdates",
            {
                "offset": offset,
                "timeout": timeout,
                "allowed_updates": json.dumps(["message"]),
            },
            timeout=max(40, timeout + 10),
        )
        if not isinstance(result, list):
            raise ContractError("Telegram getUpdates returned a non-list result")
        return result


def load_state(project, relative_path):
    path = contained(project, relative_path)
    if not path.exists():
        return path, {"schema_version": "1.0", "next_update_id": 0, "workflow_tokens": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("Invalid Telegram bridge state: " + redact(exc)) from None
    if (
        not isinstance(state, dict)
        or state.get("schema_version") != "1.0"
        or not isinstance(state.get("next_update_id"), int)
        or state["next_update_id"] < 0
        or not isinstance(state.get("workflow_tokens"), dict)
    ):
        raise ContractError("Invalid Telegram bridge state contract")
    return path, state


def save_state(path, state):
    write(path, state, force=True)


def authorized_message(update, config):
    if not isinstance(update, dict) or not isinstance(update.get("update_id"), int):
        raise ContractError("Telegram update lacks an integer update_id")
    message = update.get("message")
    if not isinstance(message, dict):
        return None
    sender = message.get("from") or {}
    chat = message.get("chat") or {}
    if (
        sender.get("id") != config["user_id"]
        or chat.get("id") != config["chat_id"]
        or chat.get("type") != "private"
    ):
        return None
    text = message.get("text")
    if not isinstance(text, str):
        return HELP
    return text.strip()


def identity_candidates(updates):
    candidates = set()
    for update in updates:
        if not isinstance(update, dict):
            continue
        message = update.get("message")
        if not isinstance(message, dict) or message.get("text") not in ("/start", "/help"):
            continue
        sender = message.get("from") or {}
        chat = message.get("chat") or {}
        if (
            isinstance(sender.get("id"), int)
            and sender["id"] > 0
            and isinstance(chat.get("id"), int)
            and chat["id"] > 0
            and chat.get("type") == "private"
        ):
            candidates.add((sender["id"], chat["id"]))
    return [{"user_id": user_id, "chat_id": chat_id} for user_id, chat_id in sorted(candidates)]


def _decision(update, package, verdict, config):
    current = datetime.now(timezone.utc)
    message = update["message"]
    return {
        "run_id": package["run_id"],
        "step_id": package["step_id"],
        "state_sha256": package["state_sha256"],
        "verdict": verdict,
        "timestamp": current.isoformat(),
        "expires_at": (current + timedelta(minutes=10)).isoformat(),
        "actor": f"telegram-user:{config['user_id']}",
        "source_ref": f"telegram:update:{update['update_id']}:message:{message.get('message_id', 'unknown')}",
    }


def process_command(project, update, text, config):
    if text in ("/start", "/help"):
        return HELP
    match = COMMAND.fullmatch(text)
    if not match:
        return "Command rejected.\n" + HELP
    if match.group(1) == "status":
        data = control.status(project, match.group(2))
        return control.summarize(data)

    verdict, run_id, step_id = match.group(3), match.group(4), match.group(5)
    data = control.status(project, run_id)
    package = control.gate_package(project, data)
    if package["step_id"] != step_id:
        raise ContractError("Decision step does not match the current human gate")
    result = control.resume(
        project,
        run_id,
        _decision(update, package, verdict, config),
        execute=True,
        stop=verdict == "reject",
    )
    current_step = result.get("current_step_id")
    suffix = f"\nCurrent step: {current_step}" if current_step else ""
    return f"Decision recorded: {verdict}\nRun: {run_id}\nStatus: {result.get('status')}" + suffix


def poll_once(project, api, config, state_path, state, timeout=0):
    processed = 0
    responses = 0
    updates = sorted(api.updates(state["next_update_id"], timeout), key=lambda item: item.get("update_id", -1))
    for update in updates:
        update_id = update.get("update_id")
        if not isinstance(update_id, int) or update_id < state["next_update_id"]:
            continue
        processed += 1
        response = None
        try:
            text = authorized_message(update, config)
            if text is not None:
                response = process_command(project, update, text, config)
        except ContractError as exc:
            response = "Request rejected: " + redact(exc)
        state["next_update_id"] = update_id + 1
        # A consumed Telegram update must not be replayed if acknowledgement delivery fails.
        save_state(state_path, state)
        if response:
            api.send(config["chat_id"], response)
            responses += 1
    return {"updates_processed": processed, "responses_sent": responses}


def watch_workflows(project, api, config, state_path, state):
    listed = control.invoke(project, ["status"])
    runs = [run for run in listed.get("runs", []) if run.get("workflow_id") in control.WORKFLOWS]
    sent = 0
    for item in runs:
        run_id = item.get("run_id")
        if not isinstance(run_id, str):
            continue
        data = control.status(project, run_id)
        notice = control.watch_once(data, state["workflow_tokens"].get(run_id))
        if notice is None:
            continue
        api.send(config["chat_id"], notice["notification"])
        state["workflow_tokens"][run_id] = notice["token"]
        save_state(state_path, state)
        sent += 1
    return {"runs_checked": len(runs), "notifications_sent": sent}


def main():
    cli = parser("Deterministic Telegram bridge for thesis Spec Kit workflows")
    cli.add_argument("--project", required=True)
    cli.add_argument("--state-file", default=STATE_DEFAULT)
    actions = cli.add_subparsers(dest="action", required=True)
    identify = actions.add_parser("identify")
    identify.add_argument("--timeout", type=int, default=20, choices=range(0, 31), metavar="0..30")
    actions.add_parser("check")
    send = actions.add_parser("send")
    send.add_argument("message")
    actions.add_parser("watch-once")
    poll = actions.add_parser("poll-once")
    poll.add_argument("--timeout", type=int, default=0, choices=range(0, 31), metavar="0..30")
    run = actions.add_parser("run")
    run.add_argument("--poll-timeout", type=int, default=25, choices=range(1, 31), metavar="1..30")
    run.add_argument("--workflow-check-seconds", type=int, default=30)
    args = cli.parse_args()

    project = Path(args.project).resolve()
    if not project.is_dir():
        raise ContractError("Project directory does not exist")
    token = token_configuration()
    api = TelegramAPI(token)
    if args.action == "identify":
        return {
            "candidates": identity_candidates(api.updates(0, args.timeout)),
            "instruction": "Set the allowlisted user/chat IDs only after verifying they belong to you.",
            "token_exposed": False,
        }
    config = configuration()
    state_path, state = load_state(project, args.state_file)
    if args.action == "check":
        return {
            "configured": True,
            "allowed_user_id": config["user_id"],
            "allowed_chat_id": config["chat_id"],
            "state_file": str(state_path),
            "token_exposed": False,
        }
    if args.action == "send":
        result = api.send(config["chat_id"], args.message)
        return {"sent": True, "message_id": result.get("message_id") if isinstance(result, dict) else None}
    if args.action == "watch-once":
        return watch_workflows(project, api, config, state_path, state)
    if args.action == "poll-once":
        return poll_once(project, api, config, state_path, state, args.timeout)

    if args.workflow_check_seconds < 5:
        raise ContractError("workflow-check-seconds must be at least 5")
    next_workflow_check = 0.0
    while True:
        current = time.monotonic()
        if current >= next_workflow_check:
            watch_workflows(project, api, config, state_path, state)
            next_workflow_check = current + args.workflow_check_seconds
        poll_once(project, api, config, state_path, state, args.poll_timeout)


if __name__ == "__main__":
    from .common import cli_entry
    raise SystemExit(cli_entry(main))
