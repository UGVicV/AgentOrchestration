import pytest
from src.orchestrator.workflow import Workflow, WorkflowStep, WorkflowManager, StepStatus


class TestWorkflowParameters:
    def test_preserve_false_defaults_and_overrides(self):
        try:
            workflow = Workflow("test_wf")
            workflow.add_parameter("param_false_default", default=False, required=False)
            workflow.add_parameter("param_true_default", default=True, required=False)
            workflow.add_parameter("param_override", default=True, required=False)
            
            # Bind parameters
            # override param_override to False, leave others to use defaults
            workflow.bind({"param_override": False})
            
            assert workflow.bindings["param_false_default"] is False
            assert workflow.bindings["param_true_default"] is True
            assert workflow.bindings["param_override"] is False
        except Exception as e:
            print(f"Error in test_preserve_false_defaults_and_overrides: {e}")
            raise

    def test_required_parameter_check(self):
        try:
            manager = WorkflowManager()
            workflow = manager.create_workflow("test_wf")
            workflow.add_parameter("required_param", required=True)
            workflow.add_step(WorkflowStep("step1", lambda: "ok"))
            
            # Try to execute workflow without the required parameter
            result = manager.execute_workflow(workflow.id, {})
            assert result is False
            assert workflow.status == StepStatus.PENDING
            
            # Execute with required parameter
            result = manager.execute_workflow(workflow.id, {"required_param": "value"})
            assert result is True
            assert workflow.status == StepStatus.COMPLETED
        except Exception as e:
            print(f"Error in test_required_parameter_check: {e}")
            raise

    def test_sanitized_audit_log(self):
        try:
            workflow = Workflow("test_wf")
            workflow.add_parameter("secret_param", default="my-secret-key", required=False)
            
            workflow.bind({"secret_param": "overridden-secret"})
            
            assert len(workflow.audit_log) == 1
            log_entry = workflow.audit_log[0]
            
            assert log_entry["action"] == "bind"
            assert "secret_param" in log_entry["parameter_names"]
            
            # Ensure the raw value is NOT in the audit log
            # Convert log_entry to string to check all fields recursively
            log_str = str(log_entry)
            assert "my-secret-key" not in log_str
            assert "overridden-secret" not in log_str
        except Exception as e:
            print(f"Error in test_sanitized_audit_log: {e}")
            raise
