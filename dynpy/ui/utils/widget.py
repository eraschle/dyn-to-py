import tkinter as tk
from dataclasses import asdict, dataclass, field
from tkinter import ttk
from typing import (
    Any,
    Callable,
    Dict,
    NotRequired,
    Optional,
    TypedDict,
    Union,
    Unpack,
)

UiElement = Union[tk.Button, tk.Label, tk.Entry]
UiWidget = Union[UiElement, tk.Frame, tk.LabelFrame, ttk.Treeview]


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


@dataclass
class UiArgs:
    @classmethod
    def from_dict(cls, args: Dict[str, Any]) -> "UiArgs":
        if 'padding' not in args:
            args['padding'] = UiPadding.from_dict(args)
        return UiArgs(**args)

    row_index: int = 0
    row_weight: int = 1
    column_index: int = 0
    column_weight: int = 1
    columnspan: int = 1
    sticky: str = tk.EW
    padding: UiPadding = field(default_factory=UiPadding)
    west_min: int = 140
    east_min: int = 150

    def add_row(self, weight: int = 1):
        self.column_index = 0
        self.column_weight = 1
        self.row_index += 1
        self.row_weight = weight

    def add_column(self, weight: int = 1):
        self.column_weight = weight
        self.column_index += 1

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
        for key in ('padx_e', 'west_min', 'east_min', 'row_weight', 'column_weight'):
            args.pop(key, None)
        return {key.removesuffix("_index"): value for key, value in args.items()}

    def grid_args(self, **kwargs: Unpack[GridArgs]) -> Dict[str, Any]:
        args = self.as_dict()
        args = self._clean_grid_args(args)
        args.update(kwargs)
        return args

    def _get_config_args(self, name: str, **kwargs: Unpack[ConfigArgs]) -> ConfigArgs:
        prefix = f"{name}_"
        args = self.as_dict(*(f"{prefix}index", f"{prefix}weight"))
        args = {key.removeprefix(prefix): value for key, value in args.items()}
        args.update(kwargs)
        return ConfigArgs(**args)

    def row_args(self, **kwargs: Unpack[ConfigArgs]) -> ConfigArgs:
        return self._get_config_args("row", **kwargs)

    def column_args(self, **kwargs: Unpack[ConfigArgs]) -> ConfigArgs:
        return self._get_config_args("column", **kwargs)

    def create(self, **kwargs: Unpack[GridArgs]) -> "UiArgs":
        args = self.to_dict()
        args.update(kwargs)
        args["row_index"] = args.pop("row", 0)
        args["column_index"] = args.pop("column", 0)
        args["sticky"] = args.pop("sticky", tk.EW)
        return UiArgs.from_dict(args)


def get_sticky(element: UiWidget) -> str:
    """
    Get sticky value of the ui element

    Parameters:
    element (UiElement) the ui element
    """
    if isinstance(element, (tk.Frame, tk.LabelFrame)) or (
        isinstance(element, tk.Label) and element['relief'] == tk.GROOVE
    ):
        return tk.NSEW
    return tk.EW


def setup_grid(element: UiWidget, args: UiArgs) -> None:
    """
    Configures the grid option for an ui element

    Parameters:
    element (UiElement) the ui element
    """
    names = ["row_index", "column_index", "columnspan", "padx", "pady"]
    if not isinstance(element, (tk.Button, tk.Frame, tk.LabelFrame)):
        names.append("ipady")
    attr_dict = args.to_dict(*names, sticky=get_sticky(element))
    element.grid(cnf=attr_dict)


def get_okay_button(frame: tk.Frame) -> Optional[tk.Button]:
    for child in frame.children.values():
        if not isinstance(child, tk.Button) or child['text'] != 'Okay':
            continue
        return child
    return None


def _create_button(
    frame: tk.Frame, name: str, args: UiArgs, command: Callable[[], None]
) -> tk.Frame:
    button = tk.Button(frame, text=name, command=command)
    button.grid(
        row=args.row_index,
        column=args.column_index,
        sticky=args.sticky,
        padx=args.padding.padx,
        pady=args.padding.pady,
        ipady=args.padding.ipady,
    )
    return frame


def create_okay_button(frame: tk.Frame, args: UiArgs, command: Callable[[], None]) -> tk.Frame:
    return _create_button(frame, 'Okay', args, command)


def create_cancel_button(frame: tk.Frame, args: UiArgs, command: Callable[[], None]) -> tk.Frame:
    return _create_button(frame, 'Cancel', args, command)


def get_button_frame(
    master: tk.Misc,
    args: UiArgs,
    okay_cmd: Callable,
    cancel_cmd: Optional[Callable],
) -> tk.Frame:
    frame = tk.Frame(master)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, minsize=args.east_min)
    frame.grid_columnconfigure(2, minsize=args.west_min)
    args.sticky = tk.EW
    if cancel_cmd is not None:
        btn_cancel = create_cancel_button(frame, args, cancel_cmd)
        add_okay_cancel_key_event(btn_cancel, okay_cmd, cancel_cmd)
    args.add_column()
    btn_okay = create_okay_button(frame, args, okay_cmd)
    add_okay_cancel_key_event(btn_okay, okay_cmd, cancel_cmd)
    return frame


def add_okay_cancel_key_event(
    widget: tk.Widget,
    okay_cmd: Callable[[], None],
    cancel_cmd: Optional[Callable[[], None]],
):
    def okay_key_command(_):
        return okay_cmd()

    widget.bind('<Return>', okay_key_command)
    if cancel_cmd is None:
        return

    def cancel_key_cmd(_):
        return cancel_cmd()

    widget.bind('<Escape>', cancel_key_cmd)


def center_on_screen(window: tk.Tk, width: float = 900, height: float = 800):
    # get screen width and height
    scr_width = window.winfo_screenwidth()
    scr_height = window.winfo_screenheight()

    # calculate position x and y coordinates
    x_center = int((scr_width / 2) - (width / 2))
    y_center = int((scr_height / 2) - (height / 2))
    window.geometry(f'{width}x{height}+{x_center}+{y_center}')
