import logging
import pytest

from src.orchestrator.workflow import (
    ParameterAliasError,
    StepStatus,
    Workflow,
    WorkflowManager,
    WorkflowParameter,
    WorkflowParameterError,
    WorkflowStep,
)


class TestWorkflowParameters:
    def test_preserve_false_defaults_and_overrides(self):
        try:
            workflow = Workflow("test_wf")
            workflow.add_parameter(
                "param_false_default", default=False, required=False
            )
            workflow.add_parameter(
                "param_true_default", default=True, required=False
            )
            workflow.add_parameter(
                "param_override", default=True, required=False
            )

            # Bind parameters
            # override param_override to False, leave others to use defaults
            workflow.bind({"param_override": False})

            assert workflow.bindings["param_false_default"] is False
            assert workflow.bindings["param_true_default"] is True
            assert workflow.bindings["param_override"] is False
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

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
            result = manager.execute_workflow(
                workflow.id, {"required_param": "value"}
            )
            assert result is True
            assert workflow.status == StepStatus.COMPLETED
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_sanitized_audit_log(self):
        try:
            workflow = Workflow("test_wf")
            workflow.add_parameter(
                "secret_param", default="my-secret-key", required=False
            )

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
            pytest.fail(f"Unexpected exception: {e}")


def test_duplicate_aliases_are_rejected_before_registration():
    try:
        workflow = Workflow("daily-refresh")

        with pytest.raises(WorkflowParameterError):
            workflow.add_parameter(
                "account_id", aliases=["account", "ACCOUNT"]
            )

        assert workflow.parameters == {}
        assert workflow.status is StepStatus.PENDING
        assert workflow.parameter_audit_log[-1] == {
            "decision": "rejected",
            "reason": "duplicate_parameter_alias",
            "parameter": "account_id",
            "alias": "ACCOUNT",
        }
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_alias_collision_with_existing_parameter_is_rejected():
    try:
        workflow = Workflow("daily-refresh")
        workflow.add_parameter("account_id", aliases=["account"])

        with pytest.raises(WorkflowParameterError):
            workflow.add_parameter("workspace_id", aliases=["account"])

        assert list(workflow.parameters) == ["account_id"]
        assert workflow.status is StepStatus.PENDING
        assert (
            workflow.parameter_audit_log[-1]["reason"]
            == "duplicate_parameter_alias"
        )
        assert workflow.parameter_audit_log[-1]["alias"] == "account"
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_resolve_parameters_binds_aliases_to_canonical_names():
    try:
        workflow = Workflow("daily-refresh")
        workflow.add_parameter("account_id", aliases=["account"])
        workflow.add_parameter("limit", aliases=["page_size"], default=100)

        resolved = workflow.resolve_parameters({"account": "acct_123"})

        assert resolved == {"account_id": "acct_123", "limit": 100}
        assert workflow.parameter_audit_log[-1] == {
            "decision": "resolved",
            "reason": "workflow_parameters_bound",
            "parameter": "2",
            "alias": "",
        }
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_resolve_parameters_rejects_duplicate_canonical_input():
    try:
        workflow = Workflow("daily-refresh")
        workflow.add_parameter("limit", aliases=["page_size"])

        with pytest.raises(WorkflowParameterError):
            workflow.resolve_parameters({"limit": 25, "page_size": 50})

        assert workflow.status is StepStatus.PENDING
        assert workflow.parameter_audit_log[-1] == {
            "decision": "rejected",
            "reason": "duplicate_parameter_input",
            "parameter": "limit",
            "alias": "page_size",
        }
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_manager_registers_parameters_before_publishing_workflow():
    try:
        manager = WorkflowManager()
        workflow = manager.create_workflow(
            "daily-refresh",
            parameters=[WorkflowParameter("region", aliases=["cloud_region"])],
        )

        assert manager.get_workflow(workflow.id) is workflow
        assert workflow.resolve_parameters({"cloud_region": "us-east-1"}) == {
            "region": "us-east-1"
        }
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_manager_does_not_publish_invalid_parameter_schema():
    try:
        manager = WorkflowManager()

        with pytest.raises(WorkflowParameterError):
            manager.create_workflow(
                "daily-refresh",
                parameters=[WorkflowParameter("region", aliases=["region"])],
            )

        assert manager.list_workflows() == []
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_parameter_helpers_are_public_exports():
    try:
        from src.orchestrator import WorkflowParameter as ExportedParameter
        from src.orchestrator import WorkflowParameterError as ExportedError

        assert ExportedParameter is WorkflowParameter
        assert ExportedError is WorkflowParameterError
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_create_workflow_rejects_duplicate_parameter_aliases():
    try:
        manager = WorkflowManager()

        with pytest.raises(ParameterAliasError):
            manager.create_workflow(
                "duplicate-aliases",
                parameters=[
                    WorkflowParameter("source", aliases=["owner"]),
                    WorkflowParameter("assignee", aliases=["OWNER"]),
                ],
            )

        assert manager.list_workflows() == []
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_input_binding_rejects_duplicate_aliases_without_state_change():
    try:
        workflow = Workflow(
            "input-binding",
            parameters=[WorkflowParameter("owner", aliases=["assignee"])],
        )
        workflow.status = StepStatus.RUNNING

        with pytest.raises(ParameterAliasError):
            workflow.bind_inputs({"owner": "alice", "ASSIGNEE": "bob"})

        assert workflow.status == StepStatus.RUNNING
        assert workflow.resolve_input_alias("assignee") == "owner"
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_parameter_rejects_duplicate_aliases_within_same_parameter():
    try:
        workflow = Workflow("duplicate-local-alias")

        with pytest.raises(ParameterAliasError):
            workflow.add_parameter(
                WorkflowParameter("owner", aliases=["OWNER"])
            )

        assert workflow.parameters == []
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_duplicate_alias_rejection_is_sanitized(caplog):
    try:
        workflow = Workflow(
            "sanitized",
            parameters=[WorkflowParameter("token", aliases=["safe"])],
        )

        with caplog.at_level(
            logging.WARNING, logger="src.orchestrator.workflow"
        ):
            with pytest.raises(ParameterAliasError):
                workflow.add_parameter(
                    WorkflowParameter(
                        "secret_value",
                        aliases=["safe", "do-not-log-this-secret"],
                    ),
                )

        log_output = caplog.text
        assert "do-not-log-this-secret" not in log_output
        assert "secret_value" not in log_output
        assert workflow.audit_records[-1]["reason"] == "duplicate_alias"
        assert "alias" not in workflow.audit_records[-1]
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
