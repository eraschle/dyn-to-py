import tkinter as tk
from typing import Iterable, Optional

from dynpy.core import factory
from dynpy.core.actions import (
    ActionType,
    ConvertAction,
    RemoveLineAction,
    TypeIgnoreAction,
)
from dynpy.core.models import ConvertConfig
from dynpy.ui.interface import IView
from dynpy.ui.utils import widget as ui
from dynpy.ui.utils.editable import EditableListbox


def _editable_listbox(master: tk.Misc, text: str, args: ui.UiArgs) -> EditableListbox:
    frm_label = tk.LabelFrame(master=master, text=text)
    args_lbl = args.create(row=0, column=0, sticky=tk.NSEW)
    frm_label.grid_rowconfigure(index=args_lbl.row, weight=1)
    frm_label.grid_columnconfigure(index=args_lbl.column, weight=1)
    frm_label.grid(cnf=args.grid_args())
    lst_edit = EditableListbox(frm_label)
    args_edt = args_lbl.create(row=0, column=0, sticky=tk.NSEW)
    lst_edit.grid_rowconfigure(index=args_edt.row, weight=1)
    lst_edit.grid_columnconfigure(index=args_edt.column, weight=1)
    lst_edit.grid(cnf=args_edt.grid_args())
    return lst_edit


class RemoveActionLabelFrame(tk.LabelFrame, IView[RemoveLineAction]):
    def __init__(self, master: tk.Misc, text: str):
        super().__init__(master=master, text=text)
        args = ui.UiArgs(sticky=tk.NSEW)
        self.action = factory.default_remove_action()
        self.grid_rowconfigure(index=args.row, weight=1)
        self.grid_columnconfigure(index=args.column, weight=1)
        self.lst_values = _editable_listbox(self, "Values", args)

    def update_view(self, model: RemoveLineAction):
        self.action = model
        self.lst_values.update_values(model.contains)

    def show(self, model: Optional[RemoveLineAction] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()


class ReplaceActionLabelFrame(tk.LabelFrame, IView[TypeIgnoreAction]):
    def __init__(self, master: tk.Misc, text: str):
        super().__init__(master=master, text=text)
        args = ui.UiArgs()
        self.action = factory.default_type_ignore_action()
        self.grid_rowconfigure(index=args.row, weight=1)
        self.grid_columnconfigure(index=args.column, weight=1)
        self.lst_regex = _editable_listbox(self, "Regex", args)
        args.add_column()
        self.grid_columnconfigure(index=args.column, weight=1)
        self.lst_contain = _editable_listbox(self, "Contains", args)

    def update_view(self, model: TypeIgnoreAction):
        self.action = model
        self.lst_regex.update_values(model.regex)
        self.lst_contain.update_values(model.contains)

    def show(self, model: Optional[TypeIgnoreAction] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()


class ConvertActionFrame(tk.Frame, IView[ConvertConfig]):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        args = ui.UiArgs()
        self.model = factory.default_convert_config()
        self.grid_rowconfigure(index=args.row, weight=1)
        self.grid_columnconfigure(index=args.column, weight=1)
        self.replace = ReplaceActionLabelFrame(self, "Replace Value")
        args.add_column()
        self.grid_columnconfigure(index=args.column, weight=1)
        self.remove = RemoveActionLabelFrame(self, "Remove Line")
        self.remove.grid(cnf=args.grid_args())

    def update_replace(self, actions: Iterable[ConvertAction]):
        actions = [act for act in actions if isinstance(act, TypeIgnoreAction)]
        if len(actions) == 0:
            return
        self.replace.update_view(actions[0])

    def update_remove(self, actions: Iterable[ConvertAction]):
        actions = [act for act in actions if isinstance(act, RemoveLineAction)]
        if len(actions) == 0:
            return
        self.remove.update_view(actions[0])

    def update_view(self, model: ConvertConfig):
        self.model = model
        self.update_remove(model.get_actions(ActionType.REMOVE))
        self.update_replace(model.get_actions(ActionType.REPLACE))

    def show(self, model: ConvertConfig | None = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()
