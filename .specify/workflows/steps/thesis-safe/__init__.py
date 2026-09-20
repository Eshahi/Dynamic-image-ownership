"""Spec Kit extension: fixed deterministic smoke stages, never a shell."""
from specify_cli.workflows.base import StepBase, StepResult, StepStatus

class ThesisSafeStep(StepBase):
    type_key="thesis-safe"
    actions={"research","design","execute","analysis","audit","complete"}

    def validate(self,config):
        errors=super().validate(config)
        if set(config)-{"id","type","action"}: errors.append("Unknown thesis-safe field")
        if config.get("action") not in self.actions: errors.append("Unknown thesis-safe action")
        return errors

    def execute(self,config,context):
        errors=self.validate(config)
        if errors: return StepResult(status=StepStatus.FAILED,error="; ".join(errors))
        from thesis_agents.smoke import stage
        try:
            return StepResult(output=stage(config["action"],context.project_root,context.run_id))
        except Exception as exc:
            from thesis_agents.common import redact
            return StepResult(status=StepStatus.FAILED,error=redact(exc))
