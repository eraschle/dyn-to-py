from typing import Protocol, TypeVar

TModel = TypeVar('TModel', contravariant=True)


class IView(Protocol[TModel]):
    def update_view(self, model: TModel) -> None: ...

    def show(self) -> None: ...

    def hide(self) -> None: ...
