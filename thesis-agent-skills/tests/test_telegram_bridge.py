"""Offline tests for the deterministic Telegram transport."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from thesis_agents.common import ContractError
from thesis_agents.telegram_bridge import (
    CHAT_ENV,
    TOKEN_ENV,
    USER_ENV,
    authorized_message,
    configuration,
    load_state,
    poll_once,
    process_command,
    watch_workflows,
)


CONFIG = {"token": "123456:abcdefghijklmnopqrstuvwxyz_ABCD", "user_id": 42, "chat_id": 42}


def update(text, update_id=10, user_id=42, chat_id=42, chat_type="private"):
    return {
        "update_id": update_id,
        "message": {
            "message_id": 7,
            "from": {"id": user_id},
            "chat": {"id": chat_id, "type": chat_type},
            "text": text,
        },
    }


class FakeAPI:
    def __init__(self, updates=None, fail_send=False):
        self.pending = list(updates or [])
        self.sent = []
        self.fail_send = fail_send

    def updates(self, offset, timeout):
        return [item for item in self.pending if item["update_id"] >= offset]

    def send(self, chat_id, message):
        if self.fail_send:
            raise ContractError("offline send failure")
        self.sent.append((chat_id, message))
        return {"message_id": len(self.sent)}


class TelegramBridgeTests(unittest.TestCase):
    def test_configuration_never_accepts_missing_or_malformed_values(self):
        valid = {TOKEN_ENV: CONFIG["token"], USER_ENV: "42", CHAT_ENV: "42"}
        self.assertEqual(configuration(valid), CONFIG)
        for broken in ({}, {**valid, TOKEN_ENV: "bad"}, {**valid, USER_ENV: "0"}):
            with self.subTest(broken=broken), self.assertRaises(ContractError):
                configuration(broken)

    def test_authorization_requires_exact_private_user_and_chat(self):
        self.assertEqual(authorized_message(update("/help"), CONFIG), "/help")
        self.assertIsNone(authorized_message(update("/help", user_id=41), CONFIG))
        self.assertIsNone(authorized_message(update("/help", chat_id=41), CONFIG))
        self.assertIsNone(authorized_message(update("/help", chat_type="group"), CONFIG))

    def test_command_parser_rejects_free_form_text(self):
        with tempfile.TemporaryDirectory() as directory:
            reply = process_command(Path(directory), update("approve it"), "approve it", CONFIG)
        self.assertIn("Command rejected", reply)

    def test_exact_approval_is_bound_to_current_gate(self):
        package = {"run_id": "run-1", "step_id": "gate-1", "state_sha256": "a" * 64}
        result = {"status": "paused", "current_step_id": "gate-2"}
        with tempfile.TemporaryDirectory() as directory, \
             patch("thesis_agents.telegram_bridge.control.status", return_value={}), \
             patch("thesis_agents.telegram_bridge.control.gate_package", return_value=package), \
             patch("thesis_agents.telegram_bridge.control.resume", return_value=result) as resume:
            reply = process_command(Path(directory), update("/approve run-1 gate-1"), "/approve run-1 gate-1", CONFIG)
            decision = resume.call_args.args[2]
        self.assertEqual(decision["run_id"], "run-1")
        self.assertEqual(decision["step_id"], "gate-1")
        self.assertEqual(decision["verdict"], "approve")
        self.assertEqual(decision["actor"], "telegram-user:42")
        self.assertIn("Decision recorded", reply)

    def test_poll_advances_offset_for_unauthorized_updates(self):
        api = FakeAPI([update("/help", user_id=99)])
        with tempfile.TemporaryDirectory() as directory:
            path, state = load_state(directory, ".thesis-notify/state.json")
            result = poll_once(Path(directory), api, CONFIG, path, state)
            _, persisted = load_state(directory, ".thesis-notify/state.json")
        self.assertEqual(result, {"updates_processed": 1, "responses_sent": 0})
        self.assertEqual(persisted["next_update_id"], 11)
        self.assertEqual(api.sent, [])

    def test_delivery_cursor_moves_only_after_successful_notification(self):
        status = {"run_id": "run-1", "workflow_id": "thesis-smoke"}
        listed = {"runs": [status]}
        notice = {"notification": "changed", "token": "token-1"}
        with tempfile.TemporaryDirectory() as directory:
            path, state = load_state(directory, ".thesis-notify/state.json")
            with patch("thesis_agents.telegram_bridge.control.invoke", return_value=listed), \
                 patch("thesis_agents.telegram_bridge.control.status", return_value=status), \
                 patch("thesis_agents.telegram_bridge.control.watch_once", return_value=notice):
                with self.assertRaises(ContractError):
                    watch_workflows(Path(directory), FakeAPI(fail_send=True), CONFIG, path, state)
                self.assertNotIn("run-1", state["workflow_tokens"])
                result = watch_workflows(Path(directory), FakeAPI(), CONFIG, path, state)
        self.assertEqual(result["notifications_sent"], 1)
        self.assertEqual(state["workflow_tokens"]["run-1"], "token-1")


if __name__ == "__main__":
    unittest.main()
