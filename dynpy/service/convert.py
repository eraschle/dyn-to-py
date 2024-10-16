from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
from typing import Callable, List, Mapping

from dynpy.core.actions import ActionType, ConvertAction
from dynpy.core.models import ConvertConfig, SourceConfig
from dynpy.service import factory

log = logging.getLogger(__name__)


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


class ConvertService:
    def __init__(self):
        self._handler: ConvertHandler | None = None

    @property
    def handler(self) -> ConvertHandler:
        if self._handler is None:
            raise ValueError("No convert config loaded")
        return self._handler

    @property
    def direction(self) -> Direction:
        return self.handler.direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        if direction == Direction.UNKNOWN:
            raise ValueError("Unknown direction")
        self.handler.direction = direction

    @property
    def convert_config(self) -> ConvertConfig:
        return self.handler.convert

    @property
    def config_extension(self) -> str:
        return "dynpy"

    def load_config(self, file_path: Path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist")
        self._handler = ConvertHandler(
            source_name=None,
            convert=factory.convert_config(file_path.resolve()),
            direction=Direction.UNKNOWN,
        )

    def create_config(self, directory_path: Path) -> Path:
        if not directory_path.exists():
            raise FileNotFoundError(f"{directory_path} does not exist")
        file_path = directory_path / f"config.{self.config_extension}"
        config = factory.default_convert_config()
        config.save(file_path)
        return file_path

    @property
    def config(self) -> ConvertConfig:
        return self.handler.convert

    @property
    def source_files(self) -> List[Path]:
        return self.current_source.source_files()

    @property
    def export_files(self) -> List[Path]:
        return self.current_source.export_files()

    @property
    def current_source(self) -> SourceConfig:
        return self.handler.source

    def source_by(self, source_name: str) -> SourceConfig:
        self.handler.source_name = source_name
        return self.handler.source

    @property
    def source_configs(self) -> List[SourceConfig]:
        return self.config.sources

    @property
    def actions(self) -> Mapping[ActionType, List[ConvertAction]]:
        return self.config.actions

    def add_source(self, source: SourceConfig) -> None:
        self.config.add_source(source)

    def update_source(self, source: SourceConfig) -> None:
        self.config.update(source)
