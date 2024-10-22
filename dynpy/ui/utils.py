import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Union


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


def get_okay_button(frame: tk.Frame) -> Optional[tk.Button]:
    for child in frame.children.values():
        if not isinstance(child, tk.Button) or child['text'] != 'Okay':
            continue
        return child
    return None


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
