#!/usr/bin/env python3

import tkinter as tk
from dataclasses import asdict, dataclass, field
from tkinter import ttk
from tkinter.constants import EW, GROOVE, NSEW, W
from typing import Any, Callable, Dict, Optional, Self, Tuple, Union

UiElement = Union[tk.Button, tk.Label, tk.Entry]
UiWidget = Union[UiElement, tk.Frame, tk.LabelFrame, ttk.Treeview]


@dataclass
class UiPadding:
    padx: int = 2
    pady: int = 2
    ipadx: int = 2
    ipady: int = 2

    @property
    def padx_e(self):
        return 3 * self.padx

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UiMatrix:
    index: int
    weight: int = 1

    def as_tuple(self) -> Tuple[int, int]:
        return self.index, self.weight

    def as_dict(self) -> Dict[str, int]:
        return asdict(self)

    def __iter__(self):
        return iter(self.as_tuple())


@dataclass
class UiArgs:
    row: int = 0
    column: int = 0
    columnspan: int = 1
    sticky: str = EW
    padding: UiPadding = field(default_factory=UiPadding)
    west_min: int = 140
    east_min: int = 150

    def add_row(self):
        self.column = 0
        self.row += 1

    def add_column(self):
        self.column += 1

    def as_dict(self) -> Dict[str, Any]:
        attr_dict = asdict(self)
        attr_dict.pop('padding')
        attr_dict.update(self.padding.as_dict())
        return attr_dict

    def to_dict(self, *args: str, **kwargs) -> Dict[str, Any]:
        attr_dict = self.as_dict()
        attr_dict = {key: attr_dict[key] for key in args}
        attr_dict.update(kwargs)
        return attr_dict

    def grid_args(self, **kwargs) -> Dict[str, Any]:
        grid_args = self.as_dict()
        for key in ('padx_e', 'west_min', 'east_min'):
            if key not in grid_args:
                continue
            grid_args.pop(key)
        grid_args.update(kwargs)
        return grid_args

    def create(self, *, column: int = 0, row: int = 0, sticky: str = EW, **kwargs) -> "UiArgs":
        return UiArgs(**self.to_dict(column=column, row=row, sticky=sticky, **kwargs))


def get_sticky(element: UiWidget) -> str:
    """
    Get sticky value of the ui element

    Parameters:
    element (UiElement) the ui element
    """
    if isinstance(element, (tk.Frame, tk.LabelFrame)) or (
        isinstance(element, tk.Label) and element['relief'] == GROOVE
    ):
        return NSEW
    return EW


def setup_grid(element: UiWidget, args: UiArgs) -> None:
    """
    Configures the grid option for an ui element

    Parameters:
    element (UiElement) the ui element
    """
    names = ["row", "column", "columnspan", "padx", "pady"]
    if not isinstance(element, (tk.Button, tk.Frame, tk.LabelFrame)):
        names.append("ipady")
    attr_dict = args.to_dict(*names, sticky=get_sticky(element))
    element.grid(cnf=attr_dict)


def setup_label(label: tk.Label, text: str | tk.Variable) -> tk.Label:
    """
    Configures the label with the default options

    Parameters:
    label (Label) the label to hide
    text (str) the text of label if its not empty
    """
    label.configure(anchor=W)
    if isinstance(text, str):
        label.configure(text=text)
    elif isinstance(text, tk.Variable):
        label.configure(textvariable=text)
    return label


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
        row=args.row,
        column=args.column,
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
    args.sticky = EW
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
