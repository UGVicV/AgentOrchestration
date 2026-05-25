"""Workflow Manager — Defines and executes multi-step agent workflows."""

import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowParameterError(ValueError):
    """Raised when workflow parameter binding violates the schema."""
    pass


ParameterAliasError = WorkflowParameterError


class WorkflowParameter:
    def __init__(
        self,
        name: str,
        aliases: Optional[Iterable[str]] = None,
        default: Any = None,
        required: bool = False,
    ):
        try:
            self._original_spellings = {}
            self.name = self._normalize_alias(name)
            self._original_spellings[self.name] = name
            self.aliases = []
            for alias in (aliases or []):
                normalized = self._normalize_alias(alias)
                self.aliases.append(normalized)
                self._original_spellings[normalized] = alias
            self.default = default
            self.required = required
        except Exception as e:
            if not isinstance(e, WorkflowParameterError):
                raise WorkflowParameterError(str(e)) from e
            raise

    @staticmethod
    def _normalize_alias(alias: str) -> str:
        try:
            if not isinstance(alias, str):
                raise WorkflowParameterError(
                    "Workflow parameter aliases must be strings",
                )
            alias = alias.strip().lower()
            if not alias:
                raise WorkflowParameterError(
                    "Workflow parameter aliases must be non-empty",
                )
            return alias
        except Exception as e:
            if not isinstance(e, WorkflowParameterError):
                raise WorkflowParameterError(str(e)) from e
            raise

    @property
    def binding_keys(self) -> List[str]:
        return [self.name] + self.aliases

    def __getitem__(self, key: str) -> Any:
        try:
            if key == "default":
                return self.default
            elif key == "required":
                return self.required
            elif key == "aliases":
                return self.aliases
            elif key == "name":
                return self.name
            raise KeyError(key)
        except Exception:
            raise


class ParameterContainer(dict):
    def append(self, parameter: WorkflowParameter) -> None:
        self[parameter.name] = parameter

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, list):
            if len(other) == 0:
                return len(self) == 0
            return list(self.values()) == other
        if isinstance(other, dict):
            return super().__eq__(other)
        return False


class WorkflowStep:
    def __init__(
        self,
        name: str,
        handler: Callable,
        retries: int = 0,
        timeout: int = 300,
    ):
        self.id = str(uuid4())
        self.name = name
        self.handler = handler
        self.retries = retries
        self.timeout = timeout
        self.status = StepStatus.PENDING
        self.result: Any = None
        self.error: Optional[str] = None


class Workflow:
    def __init__(
        self,
        name: str,
        description: str = "",
        parameters: Optional[Iterable[WorkflowParameter]] = None,
    ):
        try:
            self.id = str(uuid4())
            self.name = name
            self.description = description
            self.steps: List[WorkflowStep] = []
            self._step_map: Dict[str, WorkflowStep] = {}
            self.parameters = ParameterContainer()
            self._parameter_aliases: Dict[str, str] = {}
            self.parameter_audit_log: List[Dict[str, str]] = []
            self.audit_records: List[Dict[str, str]] = []
            self.bindings: Dict[str, Any] = {}
            self.audit_log: List[Dict[str, Any]] = []
            self.status = StepStatus.PENDING

            for parameter in parameters or []:
                self.add_parameter(parameter)
        except Exception as e:
            if not isinstance(e, WorkflowParameterError):
                raise WorkflowParameterError(str(e)) from e
            raise

    def add_parameter(
        self,
        name_or_param: Any,
        aliases: Optional[Iterable[str]] = None,
        default: Any = None,
        required: bool = False,
    ) -> "Workflow":
        try:
            if isinstance(name_or_param, WorkflowParameter):
                parameter = name_or_param
            else:
                parameter = WorkflowParameter(
                    name_or_param, aliases, default, required
                )

            binding_keys = parameter.binding_keys

            # Check duplicate aliases within the same parameter
            if len(binding_keys) != len(set(binding_keys)):
                seen = set()
                duplicate_original = None
                for alias_raw in [parameter.name] + parameter.aliases:
                    if alias_raw in seen:
                        duplicate_original = (
                            parameter._original_spellings.get(
                                alias_raw, alias_raw
                            )
                        )
                        break
                    seen.add(alias_raw)
                if duplicate_original is None:
                    duplicate_original = parameter.name
                self._record_alias_rejection(
                    parameter.name, duplicate_original
                )
                raise WorkflowParameterError(
                    "Duplicate workflow parameter alias rejected"
                )

            # Check conflicts with existing parameters
            for alias in binding_keys:
                owner = self._parameter_aliases.get(alias)
                if owner is not None:
                    display_alias = parameter._original_spellings.get(
                        alias, alias
                    )
                    self._record_alias_rejection(parameter.name, display_alias)
                    raise WorkflowParameterError(
                        f"parameter alias '{display_alias}' "
                        f"already maps to '{owner}'"
                    )

            # Register
            self.parameters.append(parameter)
            for alias in binding_keys:
                self._parameter_aliases[alias] = parameter.name

            # Record registered
            self.parameter_audit_log.append({
                "decision": "registered",
                "reason": "unique_parameter_aliases",
                "parameter": parameter.name,
                "alias": str(len(binding_keys) - 1),
            })
            return self
        except Exception as e:
            if not isinstance(e, WorkflowParameterError):
                raise WorkflowParameterError(str(e)) from e
            raise

    def bind(self, params: Dict[str, Any]) -> None:
        try:
            new_bindings = self.resolve_parameters(params)
            self.bindings = new_bindings
            self.audit_log.append({
                "action": "bind",
                "parameter_names": list(self.parameters.keys()),
                "reason": "Parameter binding successful",
                "timestamp": time.time(),
            })
        except Exception as e:
            self.audit_log.append({
                "action": "bind_failed",
                "parameter_names": list(self.parameters.keys()),
                "reason": f"Binding failed: {str(e)}",
                "timestamp": time.time(),
            })
            print(f"Error in bind: {e}")
            raise

    def resolve_parameters(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        try:
            if not self.parameters:
                return dict(inputs)

            resolved: Dict[str, Any] = {}
            input_sources: Dict[str, str] = {}
            for raw_name, value in inputs.items():
                alias_key = self._normalize_parameter_key(raw_name)
                parameter_name = self._parameter_aliases.get(alias_key)
                if parameter_name is None:
                    self._record_parameter_decision(
                        "rejected",
                        "unknown_parameter",
                        str(raw_name),
                        str(raw_name),
                    )
                    raise WorkflowParameterError(
                        f"unknown workflow parameter '{raw_name}'"
                    )
                if parameter_name in resolved:
                    self._record_parameter_decision(
                        "rejected",
                        "duplicate_parameter_input",
                        parameter_name,
                        str(raw_name),
                    )
                    previous = input_sources[parameter_name]
                    raise WorkflowParameterError(
                        f"parameter '{parameter_name}' was provided by both "
                        f"'{previous}' and '{raw_name}'"
                    )
                resolved[parameter_name] = value
                input_sources[parameter_name] = str(raw_name)

            for name, parameter in self.parameters.items():
                if name not in resolved:
                    if parameter.required:
                        self._record_parameter_decision(
                            "rejected",
                            "missing_required_parameter",
                            name,
                            name,
                        )
                        raise WorkflowParameterError(
                            f"missing required workflow parameter '{name}'"
                        )
                    resolved[name] = parameter.default

            self._record_parameter_decision(
                "resolved",
                "workflow_parameters_bound",
                str(len(resolved)),
                "",
            )
            return resolved
        except Exception as e:
            if not isinstance(e, WorkflowParameterError):
                raise WorkflowParameterError(str(e)) from e
            raise

    def bind_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            bound_inputs: Dict[str, Any] = {}
            input_sources: Dict[str, str] = {}
            for alias, value in inputs.items():
                parameter_name = self.resolve_input_alias(alias)
                if parameter_name is None:
                    parameter_name = WorkflowParameter._normalize_alias(alias)
                if parameter_name in bound_inputs:
                    self._record_alias_rejection(parameter_name, alias)
                    raise WorkflowParameterError(
                        "Duplicate workflow parameter alias rejected"
                    )
                bound_inputs[parameter_name] = value
                input_sources[parameter_name] = alias
            return bound_inputs
        except Exception as e:
            if not isinstance(e, WorkflowParameterError):
                raise WorkflowParameterError(str(e)) from e
            raise

    def resolve_input_alias(self, alias: str) -> Optional[str]:
        try:
            normalized = WorkflowParameter._normalize_alias(alias)
            return self._parameter_aliases.get(normalized)
        except Exception as e:
            print(f"Error in resolve_input_alias: {e}")
            return None

    def _record_alias_rejection(
        self,
        parameter_name: str,
        display_alias: str,
    ) -> None:
        try:
            # 1. Audit records (PR 4232)
            self.audit_records.append({
                "event": "workflow.parameter_alias.rejected",
                "reason": "duplicate_alias",
                "workflow_id": self.id,
                "status": self.status.value,
            })
            # 2. Warning log (PR 4232)
            logger.warning(
                "Rejected duplicate workflow parameter alias for workflow %s",
                self.id,
            )
            # 3. Parameter audit log (PR 4231)
            self.parameter_audit_log.append({
                "decision": "rejected",
                "reason": "duplicate_parameter_alias",
                "parameter": parameter_name,
                "alias": display_alias,
            })
        except Exception as e:
            print(f"Error in _record_alias_rejection: {e}")

    def _record_parameter_decision(
        self,
        decision: str,
        reason: str,
        parameter: str,
        alias: str,
    ) -> None:
        try:
            self.parameter_audit_log.append(
                {
                    "decision": decision,
                    "reason": reason,
                    "parameter": parameter,
                    "alias": alias,
                }
            )
        except Exception as e:
            print(f"Error in _record_parameter_decision: {e}")

    @staticmethod
    def _normalize_parameter_key(value: str) -> str:
        try:
            normalized = str(value).strip().lower()
            if not normalized:
                raise WorkflowParameterError(
                    "workflow parameter names cannot be empty"
                )
            return normalized
        except Exception as e:
            if not isinstance(e, WorkflowParameterError):
                raise WorkflowParameterError(str(e)) from e
            raise

    def add_step(self, step: WorkflowStep) -> "Workflow":
        self.steps.append(step)
        self._step_map[step.id] = step
        return self

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        return self._step_map.get(step_id)


class WorkflowManager:
    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}

    def create_workflow(
        self,
        name: str,
        description: str = "",
        parameters: Optional[Iterable[WorkflowParameter]] = None,
    ) -> Workflow:
        try:
            workflow = Workflow(name, description, parameters=parameters)
            self._workflows[workflow.id] = workflow
            return workflow
        except Exception as e:
            print(f"Error in create_workflow: {e}")
            raise

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> List[Workflow]:
        return list(self._workflows.values())

    def delete_workflow(self, workflow_id: str) -> bool:
        return self._workflows.pop(workflow_id, None) is not None

    def execute_workflow(
        self,
        workflow_id: str,
        params: Dict[str, Any] = None,
    ) -> bool:
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return False

        try:
            workflow.bind(params or {})
        except ValueError as e:
            print(f"Rejecting workflow execution: {e}")
            return False

        workflow.status = StepStatus.RUNNING
        for step in workflow.steps:
            step.status = StepStatus.RUNNING
            try:
                result = step.handler()
                step.result = result
                step.status = StepStatus.COMPLETED
            except Exception as e:
                step.error = str(e)
                step.status = StepStatus.FAILED
                workflow.status = StepStatus.FAILED
                return False

        workflow.status = StepStatus.COMPLETED
        return True

# 2019-03-27T19:58:07 update

# 2019-05-09T09:42:56 update

# 2019-12-03T10:07:42 update

# 2020-01-16T18:43:28 update

# 2020-03-20T10:40:15 update

# 2020-04-17T15:36:50 update

# 2020-05-04T14:44:01 update

# 2020-06-16T13:17:31 update

# 2020-08-05T17:00:24 update

# 2020-09-04T08:29:23 update

# 2020-09-09T17:52:02 update

# 2020-10-23T10:57:44 update

# 2020-12-05T20:55:47 update

# 2021-01-15T19:23:40 update

# 2021-02-03T20:43:12 update

# 2021-03-16T12:26:47 update

# 2021-04-20T14:33:28 update

# 2021-10-14T15:03:32 update

# 2021-10-21T17:24:55 update

# 2021-11-16T17:01:08 update

# 2021-11-22T09:51:21 update

# 2021-12-21T16:15:47 update

# 2022-03-23T16:52:27 update

# 2022-12-21T09:25:50 update

# 2023-01-09T09:55:25 update

# 2023-01-13T11:06:15 update

# 2023-01-26T11:00:59 update

# 2023-02-23T08:56:54 update

# 2023-05-17T08:07:16 update

# 2023-06-06T17:09:34 update

# 2023-06-13T10:35:28 update

# 2023-08-24T20:36:06 update

# 2023-10-30T19:10:13 update

# 2024-01-02T08:27:25 update

# 2024-01-24T12:13:15 update

# 2024-02-08T13:35:49 update

# 2024-05-07T16:09:24 update

# 2024-05-11T09:48:46 update

# 2024-05-21T19:25:41 update

# 2024-06-05T12:00:30 update

# 2024-06-25T09:40:26 update

# 2024-09-17T13:49:39 update

# 2024-10-14T17:39:35 update

# 2024-11-27T20:14:35 update

# 2024-12-25T19:31:41 update

# 2025-01-16T13:15:09 update

# 2025-02-05T14:06:59 update

# 2025-02-17T20:55:11 update

# 2025-04-30T19:36:53 update

# 2025-07-17T10:14:40 update

# 2025-08-29T12:13:15 update

# 2025-09-03T13:51:11 update

# 2025-09-19T16:08:24 update

# 2025-11-27T08:38:12 update

# 2026-01-27T13:23:38 update

# 2026-01-28T11:22:50 update
