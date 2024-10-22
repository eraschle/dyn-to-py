from pathlib import Path
from typing import Iterable, List, Mapping, Protocol, Optional, Tuple

from dynpy.core.actions import AConvertAction, ActionType
from dynpy.core.handler import ConvertHandler, Direction
from dynpy.core.models import SourceConfig


class IConvertService(Protocol):
    @property
    def config_extension(self) -> str:
        """Return the configuration extension

        Returns
        -------
        str
            The configuration extension"""
        ...

    @property
    def config_loaded(self) -> bool:
        """Return whether a configuration is loaded

        Returns
        -------
        bool
            Whether a configuration is loaded"""
        ...

    def source_exists(self, name: str) -> bool:
        """Return whether a source exists.

        Returns
        -------
        bool
            Whether a source exists"""
        ...

    def convert_handle_by(self, source_name: str) -> ConvertHandler:
        """Return the convert handler.

        Return the convert handler for the given source name.

        Parameters
        ----------
        source_name : str
            The source name

        Returns
        -------
        ConvertHandler
            The convert handler"""
        ...

    @property
    def source_name(self) -> Optional[str]:
        """Return the source configuration name

        Returns
        -------
        str
            The source configuration name"""
        ...

    @property
    def direction(self) -> Direction:
        """Return the convert direction

        Returns
        -------
        Direction
            The convert direction"""
        ...

    @direction.setter
    def direction(self, direction: Direction) -> None:
        """Set the convert direction

        Set the convert direction to the given direction.

        Parameters
        ----------
        direction : Direction
            The convert direction"""
        ...

    @property
    def has_direction(self) -> bool:
        """Return whether a direction is set

        Returns
        -------
        bool
            Whether a direction is set"""
        ...

    @property
    def can_convert(self) -> bool:
        """Return whether a conversion can be performed

        Returns
        -------
        bool
            Whether a conversion can be performed"""
        ...

    def convert(self) -> None:
        """Perform the conversion"""
        ...

    def sources(self) -> List[SourceConfig]:
        """Return the source configurations

        Returns
        -------
        List[SourceConfig]
            The source configurations"""
        ...

    def update_sources(self, configs: List[SourceConfig]) -> bool:
        """Update the source configurations

        Update the source configurations with the given list.

        Parameters
        ----------
        configs : List[SourceConfig]
            The source configurations

        Returns
        -------
        bool
            True if the source configurations were updated successfully"""
        ...

    def actions(self) -> Mapping[ActionType, List[AConvertAction]]:
        """Return the actions

        Returns
        -------
        Mapping[ActionType, List[ConvertAction]]
            The actions"""
        ...

    def update_actions(self, actions: Mapping[ActionType, List[AConvertAction]]) -> bool:
        """Update the actions

        Update the actions with the given mapping.

        Parameters
        ----------
        actions : Mapping[ActionType, List[ConvertAction]]
            The actions

        Returns
        -------
        bool
            True if the actions were updated successfully"""
        ...

    def load_config(self, file_path: Path) -> None:
        """Load source configuration

        Load the source configuration from the given file path.
        If the file does not exist, a FileNotFoundError is raised.

        Parameters
        ----------
        file_path : Path
            The path of the configuration file"""
        ...

    def create_config(self, directory_path: Path) -> Path:
        """Create new source configuration

        Create a new source configuration in the given directory.
        If the directory does not exist, a FileNotFoundError is raised.
        If the configuration file already exists, it is overwritten.

        Parameters
        ----------
        directory_path : Path
            The directory in which the configuration should be created

        Returns
        -------
        Path
            The path of the created configuration"""
        ...

    @property
    def can_save_config(self) -> bool:
        """Return whether the source configuration can be saved

        Returns
        -------
        bool
            Whether the source configuration can be saved"""
        ...

    def config_save(self) -> None:
        """Save the source configuration"""
        ...

    def config_save_as(self, file_path: Path) -> None:
        """Save the source configuration as

        Save the source configuration to the given file path.

        Parameters
        ----------
        file_path : Path
            The path of the configuration file"""
        ...

    def code_diff(self, source: Tuple[str, List[str]], other: Tuple[str, List[str]]) -> Iterable[str]:
        """Return the code difference between source and export code.

        Return the code difference between the dynamo python code
        and the export python code.

        Parameters
        ----------
        source: Tuple[str, List[str]]
            Source file name and python code
        other: Tuple[str, List[str]]
            Other file name and python code

        Returns
        -------
        Iterable[str]
            The code difference"""
        ...
