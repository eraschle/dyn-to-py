from pathlib import Path
from typing import List, Mapping, Protocol

from dynpy.core.actions import ActionType, ConvertAction
from dynpy.core.convert import ConvertHandler, Direction
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

    def set_convert_direction(self, direction: str) -> Direction:
        """Set the convert direction

        Set the convert direction to the given value.
        If the direction is not valid, a ValueError is raised.

        Parameters
        ----------
        direction : str
            The convert direction"""
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

    def update_sources(self, configs: List[SourceConfig]) -> None:
        """Update the source configurations

        Update the source configurations with the given list.

        Parameters
        ----------
        configs : List[SourceConfig]
            The source configurations"""
        ...

    def actions(self) -> Mapping[ActionType, List[ConvertAction]]:
        """Return the actions

        Returns
        -------
        Mapping[ActionType, List[ConvertAction]]
            The actions"""
        ...

    def update_actions(self, actions: Mapping[ActionType, List[ConvertAction]]):
        """Update the actions

        Update the actions with the given mapping.

        Parameters
        ----------
        actions : Mapping[ActionType, List[ConvertAction]]
            The actions"""
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
