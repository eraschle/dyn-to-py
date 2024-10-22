import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Union

from dynpy.ui.models.uiargs import UiArgs

UiElement = Union[tk.Button, tk.Label, tk.Entry]
UiWidget = Union[UiElement, tk.Frame, tk.LabelFrame, ttk.Treeview]


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
