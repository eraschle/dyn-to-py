from typing import Optional, Protocol, TypeVar


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
