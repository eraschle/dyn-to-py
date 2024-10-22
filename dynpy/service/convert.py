import logging
from pathlib import Path
from typing import Callable, List, Mapping

from dynpy.core import convert as hdl
from dynpy.core import factory
from dynpy.core.actions import ActionType, ConvertAction
from dynpy.core.convert import ConvertHandler, Direction
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
        self._handler = ConvertHandler(
            source_name=None,
            convert=factory.convert_config(file_path.resolve()),
            direction=Direction.UNKNOWN,
        )

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

    def set_convert_direction(self, direction: str) -> Direction:
        self.handler.direction = Direction(direction)
        return self.handler.direction

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
        callback = self._convert_func.get(self.handler.direction, None)
        if callback is None:
            raise ValueError(f"Cannot convert {self.handler.direction}")
        callback(self.handler)

    @property
    def config(self) -> ConvertConfig:
        return self.handler.convert

    def sources(self) -> List[SourceConfig]:
        return self.config.sources

    def update_sources(self, configs: List[SourceConfig]) -> None:
        self.config.set_sources(configs)

    def actions(self) -> Mapping[ActionType, List[ConvertAction]]:
        return self.config.actions

    def update_actions(self, actions: Mapping[ActionType, List[ConvertAction]]):
        self.config.set_actions(actions)
