import pytest
import logging
from src.orchestrator.workflow import (
    WorkflowManager,
    WorkflowStep,
    StepStatus,
)
from src.common.metrics import metrics

logger = logging.getLogger(__name__)


class TestWorkflowParameters:
    def setup_method(self):
        try:
            self.manager = WorkflowManager()
            metrics._counters.clear()  # Reset metrics counters
        except Exception as e:
            logger.error(f"Error in setup_method: {str(e)}")
            raise

    def test_parameter_binding_success(self):
        try:
            wf = self.manager.create_workflow("test_wf")
            wf.add_parameter("param_bool_default_false", default=False)
            wf.add_parameter("param_str_default", default="hello")
            wf.add_parameter("param_required", required=True)
            wf.add_parameter("param_override_false", default=True)

            run_params = {
                "param_required": "world",
                "param_override_false": False
            }

            # Handler kiểm tra params được truyền vào
            received_params = {}

            def dummy_handler(**kwargs):
                received_params.update(kwargs)
                return "success"

            step = WorkflowStep("step1", dummy_handler)
            wf.add_step(step)

            success = self.manager.execute_workflow(wf.id, run_params)

            assert success is True
            assert wf.status == StepStatus.COMPLETED
            assert wf.parameters["param_bool_default_false"] is False
            assert wf.parameters["param_str_default"] == "hello"
            assert wf.parameters["param_required"] == "world"
            assert wf.parameters["param_override_false"] is False

            # Đảm bảo handler nhận đúng params đã merge
            assert received_params["param_bool_default_false"] is False
            assert received_params["param_str_default"] == "hello"
            assert received_params["param_required"] == "world"
            assert received_params["param_override_false"] is False

            bind_success = metrics._counters.get(
                "workflow.parameters.bind_success", 0
            )
            assert bind_success == 1
        except Exception as e:
            logger.error(f"Error in test_parameter_binding_success: {str(e)}")
            raise

    def test_parameter_binding_unknown_param(self):
        try:
            wf = self.manager.create_workflow("test_wf")
            wf.add_parameter("param_a", default="value_a")

            # Handler
            def dummy_handler():
                return "success"

            step = WorkflowStep("step1", dummy_handler)
            wf.add_step(step)

            with pytest.raises(ValueError) as exc_info:
                self.manager.execute_workflow(wf.id, {"param_unknown": "val"})

            assert "Unknown parameter: param_unknown" in str(exc_info.value)
            val_failed = metrics._counters.get(
                "workflow.parameters.validation_failed", 0
            )
            assert val_failed == 1
            # Trạng thái workflow không đổi
            assert wf.status == StepStatus.PENDING
        except Exception as e:
            logger.error(
                f"Error in test_parameter_binding_unknown_param: {str(e)}"
            )
            raise

    def test_parameter_binding_missing_required(self):
        try:
            wf = self.manager.create_workflow("test_wf")
            wf.add_parameter("param_required", required=True)

            def dummy_handler():
                return "success"

            step = WorkflowStep("step1", dummy_handler)
            wf.add_step(step)

            with pytest.raises(ValueError) as exc_info:
                self.manager.execute_workflow(wf.id, {})

            assert (
                "Missing required parameter: param_required"
                in str(exc_info.value)
            )
            val_failed = metrics._counters.get(
                "workflow.parameters.validation_failed", 0
            )
            assert val_failed == 1
            assert wf.status == StepStatus.PENDING
        except Exception as e:
            logger.error(
                f"Error in test_parameter_binding_missing_required: {str(e)}"
            )
            raise

    def test_parameter_binding_lifecycle_state_rebind(self):
        try:
            wf = self.manager.create_workflow("test_wf")
            wf.add_parameter("param_a", default="val")

            # Chạy trước một lần để status thành COMPLETED
            wf.status = StepStatus.COMPLETED

            with pytest.raises(ValueError) as exc_info:
                self.manager.execute_workflow(wf.id, {"param_a": "new_val"})

            assert (
                "Cannot bind parameters when workflow status is completed"
                in str(exc_info.value)
            )
            val_failed = metrics._counters.get(
                "workflow.parameters.validation_failed", 0
            )
            assert val_failed == 1
        except Exception as e:
            logger.error(
                f"Error in test_parameter_binding_lifecycle_state_rebind: "
                f"{str(e)}"
            )
            raise

    def test_pre_dispatch_validation_preserves_state(self):
        try:
            wf = self.manager.create_workflow("test_wf")
            wf.add_parameter("param_required", required=True)

            handler_called = False

            def dummy_handler():
                nonlocal handler_called
                handler_called = True
                return "success"

            step = WorkflowStep("step1", dummy_handler)
            wf.add_step(step)

            # Cố ý trigger validation failure bằng cách không truyền params
            with pytest.raises(ValueError):
                self.manager.execute_workflow(wf.id, {})

            # Đảm bảo handler không hề chạy
            assert handler_called is False
            # Đảm bảo trạng thái của step và workflow vẫn giữ là PENDING
            assert wf.status == StepStatus.PENDING
            assert step.status == StepStatus.PENDING
        except Exception as e:
            logger.error(
                f"Error in test_pre_dispatch_validation_preserves_state: "
                f"{str(e)}"
            )
            raise
