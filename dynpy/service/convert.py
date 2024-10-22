import difflib
import logging
from pathlib import Path
from typing import Callable, Iterable, List, Mapping, Optional, Tuple

from dynpy.core import factory
from dynpy.core import handler as hdl
from dynpy.core.actions import AConvertAction, ActionType
from dynpy.core.handler import ConvertHandler, Direction
from dynpy.core.models import ConvertConfig, SourceConfig
from dynpy.service import dynamo, python

log = logging.getLogger(__name__)


class ConvertService:
    def __init__(self):
        self._handler: ConvertHandler | None = None
        self._convert_func: Mapping[Direction, Callable[[ConvertHandler], None]] = {
            Direction.TO_PYTHON: dynamo.to_python,
            Direction.TO_DYNAMO: python.to_dynamo,
        }

    @property
    def config_extension(self) -> str:
        return ConvertConfig.extension

    @property
    def config_loaded(self) -> bool:
        return self._handler is not None

    def load_config(self, file_path: Path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist")
        self.config_path = file_path
        self._handler = ConvertHandler(
            source_name=None,
            convert=factory.convert_config(file_path.resolve()),
            direction=Direction.UNKNOWN,
        )

    @property
    def can_save_config(self) -> bool:
        if self._handler is None:
            return False
        return self.config.can_save()

    def config_save(self):
        self.config.save()

    def config_save_as(self, file_path: Path):
        self.config.save_as(file_path)

    def create_config(self, directory_path: Path) -> Path:
        if not directory_path.exists():
            raise FileNotFoundError(f"{directory_path} does not exist")
        return hdl.create_config(directory_path)

    @property
    def handler(self) -> ConvertHandler:
        if self._handler is None:
            raise ValueError("No convert config loaded")
        return self._handler

    def convert_handle_by(self, source_name: str) -> ConvertHandler:
        self.handler.source_name = source_name
        return self.handler

    @property
    def source_name(self) -> Optional[str]:
        return self.handler.source_name

    @property
    def direction(self) -> Direction:
        return self.handler.direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        self.handler.direction = direction

    @property
    def has_direction(self) -> bool:
        return self.handler.direction != Direction.UNKNOWN

    def source_exists(self, name: str) -> bool:
        config = self.handler.convert
        return any(src.name == name for src in config.sources)

    @property
    def can_convert(self) -> bool:
        if self._handler is None:
            return False
        if self.handler.source_name is None:
            return False
        source = self.handler.source
        if not source.source_path.exists():
            return False
        return self.handler.direction in self._convert_func

    def convert(self) -> None:
        callback = self._convert_func.get(self.direction, None)
        if callback is None:
            raise ValueError(f"Cannot convert {self.handler.direction}")
        callback(self.handler)

    @property
    def config(self) -> ConvertConfig:
        return self.handler.convert

    def sources(self) -> List[SourceConfig]:
        return self.config.sources

    def _same_sources(self, configs: List[SourceConfig]) -> bool:
        existing = self.sources()
        return all(src in existing for src in configs)

    def update_sources(self, configs: List[SourceConfig]) -> bool:
        changed = not self._same_sources(configs)
        self.config.set_sources(configs)
        return changed

    def actions(self) -> Mapping[ActionType, List[AConvertAction]]:
        return self.config.actions

    def _action_equal(self, action_type: ActionType, actions: List[AConvertAction]) -> bool:
        existing = self.actions().get(action_type, [])
        return all(act in existing for act in actions)

    def _same_actions(self, actions: Mapping[ActionType, List[AConvertAction]]) -> bool:
        return all(self._action_equal(act, acts) for act, acts in actions.items())

    def update_actions(self, actions: Mapping[ActionType, List[AConvertAction]]) -> bool:
        changed = not self._same_actions(actions)
        self.config.set_actions(actions)
        return changed

    def code_diff(
        self, source: Tuple[str, List[str]], other: Tuple[str, List[str]]
    ) -> Iterable[str]:
        source_name, source_code = source
        other_name, other_code = other
        count = max(len(source_code), len(other_code))
        diff = list(
            # To display the result after conversion,
            # - source must be b
            # - other must be a
            difflib.unified_diff(
                a=other_code,
                fromfile=other_name,
                b=source_code,
                tofile=source_name,
                n=count,
            )
        )
        if len(diff) == 0:
            return source_code
        return diff
