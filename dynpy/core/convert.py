from dataclasses import dataclass
from enum import Enum
from typing import Callable, List

from dynpy.core.actions import ActionType
from dynpy.core.models import ConvertConfig, SourceConfig


class Direction(str, Enum):
    UNKNOWN = "UNKNOWN"
    TO_PYTHON = "TO_PYTHON"
    TO_DYNAMO = "TO_DYNAMO"


@dataclass
class ConvertHandler:
    convert: ConvertConfig
    direction: Direction
    source_name: str | None = None

    @property
    def source(self) -> SourceConfig:
        if self.source_name is None:
            raise ValueError("No source name provided")
        return self.convert.source_by(self.source_name)

    def _apply_action(self, action_type: ActionType, lines: List[str]) -> List[str]:
        for action in self.convert.actions_by(action_type):
            lines = action.apply(lines)
        return lines

    def _restore_action(self, action_type: ActionType, lines: List[str]) -> List[str]:
        for action in self.convert.actions_by(action_type):
            lines = action.restore(lines)
        return lines

    @property
    def action_func(self) -> Callable[[ActionType, List[str]], List[str]]:
        if self.direction == Direction.UNKNOWN:
            raise ValueError("Unknown direction")
        if self.direction == Direction.TO_PYTHON:
            return self._apply_action
        return self._restore_action

    def apply_action(self, lines: List[str]) -> List[str]:
        for action_type in ActionType:
            lines = self.action_func(action_type, lines)
        return lines
