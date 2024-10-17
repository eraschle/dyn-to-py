from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional

from dynpy.core import factory
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


def get_config_path(dir_path: Optional[Path]) -> Path:
    dir_path = Path.cwd() if dir_path is None else dir_path
    file_path = dir_path / f"config.{ConvertConfig.extension}"
    file_path = file_path.with_suffix(f".{ConvertConfig.extension}")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def create_config(dir_path: Optional[Path]) -> Path:
    file_path = get_config_path(dir_path=dir_path)
    config = factory.default_convert_config()
    config.save(file_path)
    return file_path


def read_config(file_path: Optional[Path]) -> ConvertConfig:
    if file_path is None:
        path = get_config_path(dir_path=Path.cwd())
    else:
        path = file_path
    if not path.exists():
        raise FileNotFoundError(f"Config '{path}' does not exist")
    if path.is_dir():
        raise FileNotFoundError(f"Config '{path}' is directory")
    return factory.convert_config(path.resolve())


def get_direction(do_import: bool, do_export: bool) -> Direction:
    if not do_export and not do_import:
        raise Exception("Please provide either --do-export or --do-import")
    if do_export and not do_import:
        return Direction.TO_PYTHON
    elif do_import and not do_export:
        return Direction.TO_DYNAMO
    raise Exception("Can not export and import at the same time")


def create_handler(path: Path, name: str, do_import: bool, do_export: bool) -> ConvertHandler:
    direction = get_direction(do_import=do_import, do_export=do_export)
    return ConvertHandler(
        convert=read_config(path),
        source_name=name,
        direction=direction,
    )
