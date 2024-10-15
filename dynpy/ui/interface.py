from typing import List, Mapping, Optional, Protocol, TypeVar

from dynpy.core.actions import ActionType, ConvertAction
from dynpy.core.models import ConvertConfig, SourceConfig
from dynpy.service.convert import ConvertHandler

TModel = TypeVar("TModel")


class IView(Protocol[TModel]):
    def get_model(self) -> TModel:
        """Return model with values from view component

        Returns
        -------
        TModel
            The updated model
        """
        ...

    def update_view(self, model: TModel) -> None:
        """Update view with model values

        Update the view components with the values from model.

        Parameters
        ----------
        model : TModel
            the model
        """
        ...

    def show(self, model: Optional[TModel] = None) -> None:
        """Show the view

        Show the view and update the view with the model values if provided.

        Parameters
        ----------
        model : Optional[TModel]
            the model to show
        """
        ...

    def hide(self) -> None:
        """Hide the view"""
        ...


class IConvertService(Protocol):
    @property
    def convert_config(self) -> ConvertConfig: ...

    @property
    def actions(self) -> Mapping[ActionType, List[ConvertAction]]: ...

    @property
    def source_configs(self) -> List[SourceConfig]: ...

    @property
    def current_source(self) -> SourceConfig: ...

    @property
    def handler(self) -> ConvertHandler: ...

    def source_by(self, source_name: str) -> SourceConfig: ...

    def add_source(self, source: SourceConfig) -> None: ...

    def update_source(self, source: SourceConfig) -> None: ...
