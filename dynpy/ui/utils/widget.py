#!/usr/bin/env python3

from dataclasses import asdict, dataclass
from tkinter import (
    Button,
    Entry,
    Frame,
    Label,
    Misc,
    Scale,
    StringVar,
    Text,
    Tk,
    Toplevel,
    Variable,
    Widget,
)
from tkinter.constants import DISABLED, EW, GROOVE, NORMAL, NSEW, W
from tkinter.ttk import Checkbutton, Combobox, LabelFrame, Treeview
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union


UiElement = Union[Button, Combobox, Text, Label, Entry, Scale, Checkbutton]
UiWidget = Union[UiElement, Frame, LabelFrame, Widget, Treeview]


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
class UiArgs:
    row: int = 0
    column: int = 0
    columnspan: int = 1
    sticky: str = EW
    padding: UiPadding = UiPadding()
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


def enable(element: UiElement) -> None:
    """
    Activates the ui element

    Parameters:
    element(UiElement) the element to enable
    """
    if isinstance(element, Combobox):
        element.configure(state='readonly')
    else:
        element.configure(state=NORMAL)


def disable(element: UiElement) -> None:
    """
    Deactivates the ui element

    Parameters:
    element(UiElement) the element to disable
    """
    element.configure(state=DISABLED)


def is_disabled(element: UiElement) -> bool:
    """
    Checks if the ui element is deactivated

    Parameters:
    element(UiElement) the element to disable
    """
    return element['state'] == DISABLED


def combobox_add(combobox: Combobox, names: Sequence[str]) -> None:
    current = combobox.get()
    combobox['values'] = names
    if len(names) == 0:
        return
    index = 0
    if current in names:
        index = names.index(current)
    combobox.current(index)


def visible(element: UiElement) -> None:
    """
    Shows ui element visible in the grid

    Parameters:
    element(UiElement) the element to show
    """
    element.grid()


def hide(element: UiElement) -> None:
    """
    Hides the ui element in the grid but remembers the configuration

    Parameters:
    element(UiElement) the element to hide
    """
    element.grid_remove()


def get_sticky(element: UiWidget) -> str:
    """
    Get sticky value of the ui element

    Parameters:
    element (UiElement) the ui element
    """
    if isinstance(element, (Frame, LabelFrame)) or (isinstance(element, Label) and element['relief'] == GROOVE):
        return NSEW
    return EW


def setup_grid(element: UiWidget, args: UiArgs) -> None:
    """
    Configures the grid option for an ui element

    Parameters:
    element (UiElement) the ui element
    """
    names = ["row", "column", "columnspan", "padx", "pady"]
    if not isinstance(element, (Button, Frame, LabelFrame)):
        names.append("ipady")
    attr_dict = args.to_dict(*names, sticky=get_sticky(element))
    element.grid(cnf=attr_dict)


def setup_change_button(button: Button, command: Callable, label: Optional[Label] = None) -> None:
    """
    Configures the "Change" button with the default options
    and adds the click command

    Parameters:
    button (Button) button to configure
    args (Dict[str, Any]) default gui args
    command (Callable) click command
    label (Label) if the label is not None, a mouse-click event with the command will be added
    """
    setup_button(button, 'Change', command, label)


def setup_button(button: Button, text: Union[str, Variable], command: Callable, label: Optional[Label] = None) -> None:
    """
    Configures the button with the default options
    and adds the click command

    Parameters:
    button (Button) button to configure
    text (str) button text
    args (Dict[str, Any]) default gui args
    command (Callable) click command
    label (Label) if the label is not None, a mouse-click event with the command will be added
    """
    button.configure(command=command)
    if isinstance(text, Variable):
        button.configure(textvariable=text)
    elif isinstance(text, str):
        button.configure(text=text)
    if label is None:
        return
    add_label_button_1(label, command)


def add_label_button_1(label: Label, command: Callable) -> None:
    label.bind('<Button-1>', lambda event: command())


def setup_combobox(combobox: Combobox, selected: Callable) -> None:
    """
    Configures the combobox with the default options
    and adds the selected function if any

    Parameters:
    combobox (Combobox) the label to hide
    """
    combobox.configure(state='readonly')
    combobox.bind("<<ComboboxSelected>>", selected)


def setup_label(label: Label, text: str | Variable) -> Label:
    """
    Configures the label with the default options

    Parameters:
    label (Label) the label to hide
    text (str) the text of label if its not empty
    """
    label.configure(anchor=W)
    if isinstance(text, str):
        label.configure(text=text)
    elif isinstance(text, Variable):
        label.configure(textvariable=text)
    return label


def setup_read_only(label: Label, variable: Optional[StringVar] = None) -> Label:
    """
    Configures the read only label with the default options

    Parameters:
    label(Label) the label to hide
    """
    setup_label(label, '')
    label.configure(relief=GROOVE)
    if variable is not None:
        label.configure(textvariable=variable)
    return label


def widget_text(widget: Widget, text: str) -> None:
    """
    Changes the widget text

    Parameters:
    widget (Widget) the widget
    text (str) the text of widget
    """
    widget['text'] = text


def set_label_entry(
    label: Label,
    label_text: str | Variable,
    entry: Entry,
    entry_value: Variable,
    args: UiArgs,
    key_event: Optional[Callable[[Any], None]] = None,
) -> None:
    """Setup a label with an entry user input

    :param label: The label object
    :type label: Label
    :param label_text: The label text
    :type label_text: str
    :param entry: The entry object
    :type entry: Entry
    :param string_var: The Variable for the entry value
    :type string_var: Variable
    :param grid_args: Dictionary with grid values
    :type grid_args: Dict[str, Any]
    :param key_event: A key event function for the entry, defaults to None
    :type key_event: Optional[Callable[[Any], None]], optional
    """
    setup_label(label, label_text)
    label.grid(cnf=get_grid_args(args))
    if isinstance(entry_value, str):
        entry_value = StringVar(value=entry_value)
    entry.configure(textvariable=entry_value)
    args.add_column()
    entry.grid(cnf=get_grid_args(args))
    if key_event is None:
        return
    entry.bind("<KeyRelease>", key_event)


def get_combobox(event) -> Optional[Combobox]:
    # pylint: disable=missing-function-docstring
    combobox = event.widget
    if not isinstance(combobox, Combobox):
        return None
    return combobox


def get_entry(event) -> Optional[Entry]:
    # pylint: disable=missing-function-docstring
    entry = event.widget
    if not isinstance(entry, Entry):
        return None
    return entry


def get_grid_args(args: UiArgs) -> Dict[str, Any]:
    grid_args = args.as_dict()
    if 'padx_e' in grid_args:
        grid_args.pop('padx_e')
    if 'west_min' in grid_args:
        grid_args.pop('west_min')
    if 'east_min' in grid_args:
        grid_args.pop('east_min')
    if 'sticky' not in grid_args:
        grid_args['sticky'] = EW
    return grid_args


def forgot_children(widget: UiWidget, clean_weight: bool = False):
    """Forgot all children of the widget in the grid layout.

    :param widget: The widget to forgot children.
    :type widget: UiWidget
    """
    for child in widget.children.values():
        if clean_weight:
            clean_grid_weight(widget, 'column')
            clean_grid_weight(widget, 'row')
        child.grid_forget()


def clean_grid_weight(widget: Widget, config: str, weight: int = 0):
    """Sets the grid weight for column and row to the given weight.

    :param widget: The widget location in the grid to be cleaned.
    :type widget: Widget
    :param config: The name of the config. Allowed are 'column' and 'row'
    :type config: str
    :param weight: The weight value to be set, defaults to 0
    :type weight: int, optional
    """
    grid_info = widget.grid_info()
    if config not in grid_info:
        return
    widget_config = grid_info[config]  # type: ignore
    widget.master.grid_columnconfigure(widget_config, weight=weight)


def get_okay_button(frame: Frame) -> Optional[Button]:
    for child in frame.children.values():
        if not isinstance(child, Button) or child['text'] != 'Okay':
            continue
        return child
    return None


def get_button_frame(
    master: Misc,
    args: Dict[str, Any],
    okay_command: Callable,
    cancel_command: Optional[Callable],
) -> Frame:
    frame = Frame(master)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, minsize=args['east_min'])
    frame.grid_columnconfigure(2, minsize=args['east_min'])
    grid_args = get_grid_args(args)
    if cancel_command is not None:
        btn_cancel = Button(frame, text='Cancel', command=cancel_command)
        btn_cancel.grid(
            row=0,
            column=1,
            sticky=EW,
            padx=grid_args['padx'],
            pady=grid_args['pady'],
            ipady=grid_args['ipady'],
        )
        add_okay_cancel_key_event(btn_cancel, okay_command, cancel_command)
    btn_okay = Button(frame, text='Okay', command=okay_command)
    btn_okay.grid(
        row=0,
        column=2,
        sticky=EW,
        padx=grid_args['padx'],
        pady=grid_args['pady'],
        ipady=grid_args['ipady'],
    )
    add_okay_cancel_key_event(btn_okay, okay_command, cancel_command)
    return frame


def add_okay_cancel_key_event(
    widget: Widget,
    okay_command: Callable[[], None],
    cancel_command: Optional[Callable[[], None]],
):
    def okay_key_command(_):
        return okay_command()

    widget.bind('<Return>', okay_key_command)
    if cancel_command is None:
        return

    def cancel_key_command(_):
        return cancel_command()

    widget.bind('<Escape>', cancel_key_command)


def center_on_screen(window: Tk, width=900, height=800):
    # get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # calculate position x and y coordinates
    x_coord = int((screen_width / 2) - (width / 2))
    y_coord = int((screen_height / 2) - (height / 2))
    window.geometry(f'{width}x{height}+{x_coord}+{y_coord}')


def center_on_frame(frame: Misc, dialog: Toplevel):
    points = center_points(frame)
    dialog.update_idletasks()
    top_width = dialog.winfo_width()
    top_height = dialog.winfo_height()
    top_x = int(points[0] - (top_width / 2))
    top_y = int(points[1] - (top_height / 2))
    dialog.geometry(f'+{int(top_x)}+{int(top_y)}')


def center_points(frame: Misc) -> Tuple:
    top = frame.winfo_toplevel()
    width = top.winfo_width()
    height = top.winfo_height()
    middle_x = int(top.winfo_x() + (width / 2))
    middle_y = int(top.winfo_y() + (height / 2))
    return (middle_x, middle_y)
