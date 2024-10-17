import logging
from pathlib import Path
from typing import List, Mapping

from dynpy.core import factory
from dynpy.core.actions import ActionType, ConvertAction
from dynpy.core.convert import ConvertHandler, Direction
from dynpy.core.models import ConvertConfig, SourceConfig

log = logging.getLogger(__name__)


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
        return ConvertConfig.extension

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
