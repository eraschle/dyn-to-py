import tkinter as tk
from typing import Iterable, List, Mapping, Optional, Type

from dynpy.core.actions import (
    ActionType,
    ConvertAction,
    RemoveLineAction,
    TypeIgnoreAction,
)
from dynpy.service import factory
from dynpy.ui.models.entries import LabelEntry, LabelEntryOptions
from dynpy.ui.models.views import IView
from dynpy.ui.utils import widget as ui
from dynpy.ui.widget.editable import EditableListboxFrame


def _editable_listbox_frame(master: tk.Misc, text: str, args: ui.UiArgs) -> EditableListboxFrame:
    frm_label = tk.LabelFrame(master=master, text=text)
    frm_label.grid(cnf=args.grid_args(sticky=tk.NSEW))
    edit_args = args.create(row=0, column=0, sticky=tk.NSEW)
    frm_label.grid_rowconfigure(**edit_args.row_args())
    frm_label.grid_columnconfigure(**edit_args.column_args())
    lst_edit = EditableListboxFrame(frm_label)
    lst_edit.grid(cnf=edit_args.grid_args())
    return lst_edit


class RemoveActionLabelFrame(tk.LabelFrame, IView[RemoveLineAction]):
    def __init__(self, master: tk.Misc, text: str):
        super().__init__(master=master, text=text)
        args = ui.UiArgs(sticky=tk.NSEW)
        self.action = factory.default_remove_action()
        self.grid_rowconfigure(**args.row_args())
        self.grid_columnconfigure(**args.column_args())
        self.edt_values = _editable_listbox_frame(self, "Values", args)

    def get_model(self) -> RemoveLineAction:
        self.action.contains = self.edt_values.get_values()
        return self.action

    def update_view(self, model: RemoveLineAction):
        self.action = model
        self.edt_values.update_values(model.contains)

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
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args())
        self.replace = self._add_replace_value(args)
        args.add_row()
        self.grid_rowconfigure(**args.row_args())
        self.edt_regex = _editable_listbox_frame(self, "Regex", args)
        args.add_column()
        self.grid_columnconfigure(**args.column_args())
        self.edt_contain = _editable_listbox_frame(self, "Contains", args)

    def _add_replace_value(self, args: ui.UiArgs) -> LabelEntry:
        frame = tk.Frame(self)
        frame.grid(cnf=args.grid_args(columnspan=2, sticky=tk.EW))
        value_var = tk.StringVar(frame, self.action.value)
        options = LabelEntryOptions(
            name="Replace Value",
            value=value_var,
            args=args.create(sticky=tk.NSEW),
            validate=lambda: len(value_var.get().strip()) > 0,
        )
        return LabelEntry(frame, options=options)

    def get_model(self) -> TypeIgnoreAction:
        self.action.value = self.replace.value
        self.action.contains = self.edt_contain.get_values()
        self.action.regex = self.edt_regex.get_values()
        return self.action

    def update_view(self, model: TypeIgnoreAction):
        self.action = model
        self.replace.value = model.value
        self.edt_regex.update_values(model.regex)
        self.edt_contain.update_values(model.contains)

    def show(self, model: Optional[TypeIgnoreAction] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()


class ConvertActionView(tk.Frame, IView[Mapping[ActionType, List[ConvertAction]]]):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        args = ui.UiArgs(sticky=tk.NSEW)
        config = factory.default_convert_config()
        self.actions = config.actions
        self.grid_rowconfigure(**args.row_args())
        self.grid_columnconfigure(**args.column_args())
        self.replace = ReplaceActionLabelFrame(self, "Replace Action")
        self.replace.grid(cnf=args.grid_args())
        args.add_column()
        self.grid_columnconfigure(**args.column_args())
        self.remove = RemoveActionLabelFrame(self, "Remove Action")
        self.remove.grid(cnf=args.grid_args())

    def _get_action[T](self, actions: Iterable[ConvertAction], action: Type[T]) -> List[T]:
        return [act for act in actions if isinstance(act, action)]

    def _replace_actions(self) -> List[TypeIgnoreAction]:
        return self._get_action(
            actions=self.actions.get(ActionType.REPLACE, []),
            action=TypeIgnoreAction,
        )

    def _update_replace_view(self):
        actions = self._replace_actions()
        if len(actions) == 0:
            return
        self.replace.update_view(actions[0])

    def _get_replace_actions(self) -> List[ConvertAction]:
        if len(self._replace_actions()) == 0:
            return []
        return [self.replace.get_model()]

    def _remove_actions(self) -> List[RemoveLineAction]:
        return self._get_action(
            actions=self.actions.get(ActionType.REMOVE, []),
            action=RemoveLineAction,
        )

    def _update_remove_view(self):
        actions = self._remove_actions()
        if len(actions) == 0:
            self.remove.hide()
        else:
            self.remove.update_view(actions[0])

    def _get_remove_actions(self) -> List[ConvertAction]:
        if len(self._remove_actions()) == 0:
            return []
        return [self.remove.get_model()]

    def get_model(self) -> Mapping[ActionType, List[ConvertAction]]:
        return {
            ActionType.REPLACE: self._get_replace_actions(),
            ActionType.REMOVE: self._get_remove_actions(),
        }

    def update_view(self, model: Mapping[ActionType, List[ConvertAction]]):
        self.models = model
        self._update_remove_view()
        self._update_replace_view()

    def show(self, model: Mapping[ActionType, List[ConvertAction]] | None = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()
