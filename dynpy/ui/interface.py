from typing import Optional, Protocol, TypeVar

TModel = TypeVar("TModel", contravariant=True)


class IView(Protocol[TModel]):
    def update_view(self, model: TModel) -> None: ...

    def show(self, model: Optional[TModel] = None) -> None: ...

    def hide(self) -> None: ...
