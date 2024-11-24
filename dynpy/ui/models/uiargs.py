import tkinter as tk
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, NotRequired, TypedDict, Unpack


@dataclass
class UiPadding:
    @classmethod
    def args_from_dict(cls, ui_args: Dict[str, Any]) -> Dict[str, Any]:
        return {attr: ui_args.pop(attr) for attr in cls.__annotations__}

    @classmethod
    def from_dict(cls, ui_args: Dict[str, Any]) -> "UiPadding":
        return UiPadding(**cls.args_from_dict(ui_args))

    padx: int = 2
    pady: int = 2
    ipadx: int = 2
    ipady: int = 2

    @property
    def padx_e(self):
        return 3 * self.padx

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GridArgs(TypedDict):
    row: NotRequired[int]
    column: NotRequired[int]
    columnspan: NotRequired[int]
    sticky: NotRequired[str]
    padx: NotRequired[int]
    pady: NotRequired[int]
    ipadx: NotRequired[int]
    ipady: NotRequired[int]


class ConfigArgs(TypedDict):
    index: NotRequired[int]
    weight: NotRequired[int]
    minsize: NotRequired[int]


@dataclass
class UiArgs:
    @classmethod
    def from_dict(cls, args: Dict[str, Any]) -> "UiArgs":
        if 'padding' not in args:
            args['padding'] = UiPadding.from_dict(args)
        return UiArgs(**args)

    row: int = 0
    column: int = 0
    columnspan: int = 1
    sticky: str = tk.EW
    padding: UiPadding = field(default_factory=UiPadding)
    west_min: int = 140
    east_min: int = 150

    def add_row(self):
        self.column = 0
        self.row += 1

    def add_column(self):
        self.column += 1

    def as_dict(self, *args: str) -> Dict[str, Any]:
        attr_dict = asdict(self)
        attr_dict.pop('padding')
        attr_dict.update(self.padding.as_dict())
        if len(args) == 0:
            return attr_dict
        return {key: attr_dict[key] for key in args}

    def to_dict(self, *args: str, **kwargs: Unpack[GridArgs]) -> Dict[str, Any]:
        attr_dict = self.as_dict(*args)
        attr_dict.update(kwargs)
        return attr_dict

    def _clean_grid_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        for key in ('padx_e', 'west_min', 'east_min'):
            args.pop(key, None)
        return args

    def grid_args(self, **kwargs: Unpack[GridArgs]) -> Dict[str, Any]:
        args = self.as_dict()
        args = self._clean_grid_args(args)
        args.update(kwargs)
        return args

    def _get_config_args(
        self, name: str, **kwargs: Unpack[ConfigArgs]
    ) -> ConfigArgs:
        args = self.as_dict(*(name,))
        args["index"] = args.pop(name, 0)
        if "weight" not in kwargs:
            kwargs["weight"] = 1
        args.update(kwargs)
        return ConfigArgs(**args)

    def row_args(self, **kwargs: Unpack[ConfigArgs]) -> ConfigArgs:
        return self._get_config_args("row", **kwargs)

    def column_args(self, **kwargs: Unpack[ConfigArgs]) -> ConfigArgs:
        return self._get_config_args("column", **kwargs)

    def create(self, **kwargs: Unpack[GridArgs]) -> "UiArgs":
        args = self.to_dict()
        args.update(kwargs)
        args["row"] = args.pop("row", 0)
        args["column"] = args.pop("column", 0)
        args["sticky"] = args.pop("sticky", tk.EW)
        return UiArgs.from_dict(args)
