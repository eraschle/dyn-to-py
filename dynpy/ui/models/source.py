import logging
import tkinter as tk
from pathlib import Path
from tkinter import messagebox as msg
from typing import Callable, List, Optional, cast

from dynpy.core.models import SourceConfig
from dynpy.ui.models.uiargs import UiArgs
from dynpy.ui.models.views import IView
from dynpy.ui.widget.entries import LabelEntry, LabelEntryOptions, LabelPathEntry

log = logging.getLogger(__name__)


def is_valid_path(current_path: str) -> bool:
    path = Path(current_path)
    return path.exists() and path.is_dir()


class SourceViewModel:
    def __init__(self, parent: tk.Misc, is_valid_name_callback: Callable[[str], bool]):
        self.is_valid_name_cb = is_valid_name_callback
        self.model = SourceConfig(name="", source="", export="")
        self.name_value = tk.StringVar(master=parent, value=self.model.name)
        self.source_value = tk.StringVar(master=parent, value=self.model.source)
        self.export_value = tk.StringVar(master=parent, value=self.model.export)
        self.name_label = "Name"
        self.source_label = "Source Path"
        self.export_label = "Export Path"

    def get_model(self) -> SourceConfig:
        return SourceConfig(
            name=self.name_value.get(),
            source=self.source_value.get(),
            export=self.export_value.get(),
        )

    @property
    def is_valid_name(self) -> bool:
        return self.is_valid_name_cb(self.name_value.get())

    @property
    def name_invalid_message(self) -> str:
        return "Name already exists"

    @property
    def is_valid_source(self) -> bool:
        return is_valid_path(self.source_value.get())

    @property
    def source_invalid_message(self) -> str:
        return f"{self.source_value.get()} does not exist"

    @property
    def is_valid_export(self) -> bool:
        return is_valid_path(self.export_value.get())

    @property
    def export_invalid_message(self) -> str:
        return f"{self.export_value.get()} does not exist"

    @property
    def is_valid(self) -> bool:
        return self.is_valid_name and self.is_valid_source and self.is_valid_export

    @property
    def invalid_messages(self) -> List[str]:
        messages = []
        if not self.is_valid_name:
            messages.append(self.name_invalid_message)
        if not self.is_valid_source:
            messages.append(self.source_invalid_message)
        if not self.is_valid_export:
            messages.append(self.export_invalid_message)
        return messages

    def update_model(self, model: SourceConfig):
        self.model = model
        self.name_value.set(model.name)
        self.source_value.set(model.source)
        self.export_value.set(model.export)

    def name_options(self, args: UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.name_label,
            value=self.name_value,
            validate=lambda: self.is_valid_name_cb(self.name_value.get()),
            args=args,
        )

    def source_options(self, args: UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.source_label,
            value=self.source_value,
            validate=lambda: is_valid_path(self.source_value.get()),
            args=args,
        )

    def export_options(self, args: UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.export_label,
            value=self.export_value,
            validate=lambda: is_valid_path(self.export_value.get()),
            args=args,
        )


class SourceView(tk.Frame, IView[SourceConfig]):
    def __init__(self, master: "SourceListView"):
        super().__init__(master)
        args = UiArgs(sticky=tk.NSEW)
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args())
        self.frm_buttons = tk.Frame(self)
        self.frm_buttons.grid(cnf=args.grid_args(sticky=tk.EW))
        btn_args = args.create()
        self.frm_buttons.grid_columnconfigure(
            **btn_args.column_args(weight=0), minsize=btn_args.east_min
        )
        self.btn_create = tk.Button(self.frm_buttons, text="Create", command=self.on_create)
        self.btn_create.grid(cnf=btn_args.grid_args())
        self.btn_save = tk.Button(self.frm_buttons, text="Save", command=self.on_save)
        self.btn_save.grid(cnf=btn_args.grid_args())
        btn_args.add_column()
        self.frm_buttons.grid_columnconfigure(
            **btn_args.column_args(weight=0), minsize=btn_args.east_min
        )
        self.btn_cancel = tk.Button(self.frm_buttons, text="Cancel", command=self.on_cancel)
        self.btn_cancel.grid(cnf=btn_args.grid_args())
        btn_args.add_column()
        self.frm_buttons.grid_columnconfigure(**btn_args.column_args(weight=1))
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.model = SourceViewModel(self, self.list_view.is_unique_by)
        self.name = LabelEntry(self, self.model.name_options(args))
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.source = LabelPathEntry(self, self.model.source_options(args))
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.export = LabelPathEntry(self, self.model.export_options(args))
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=1))
        self._toggle_buttons(to_normal=True)

    def _toggle_buttons(self, to_normal: bool):
        if to_normal:
            self.btn_create.grid()
            self.btn_save.grid_remove()
            self.btn_cancel.grid_remove()
        else:
            self.btn_create.grid_remove()
            self.btn_save.grid()
            self.btn_cancel.grid()

    @property
    def list_view(self) -> "SourceListView":
        return cast(SourceListView, self.master)

    def _show_invalid_warning(self):
        messages = self.model.invalid_messages
        messages = [f" - {msg}" for msg in messages]
        message = "\n".join(messages)
        message = f"Invalid model:\n{message}"
        msg.showwarning("Invalid model", message)

    def on_create(self):
        model = SourceConfig(name="<Source Name>", source="<Source Path>", export="<Export Path>")
        self._toggle_buttons(to_normal=False)
        self.update_view(model)

    def on_save(self):
        if self.model.is_valid:
            model = self.get_model()
            self.list_view.add_model(model)
            self._toggle_buttons(to_normal=True)
        else:
            self._show_invalid_warning()

    def on_cancel(self):
        self._toggle_buttons(to_normal=True)
        self.list_view.show_selected_model()

    def get_model(self) -> SourceConfig:
        return self.model.get_model()

    def update_view(self, model: SourceConfig):
        self.model.update_model(model)

    def show(self, model: Optional[SourceConfig] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()


class SourceListView(tk.Frame, IView[List[SourceConfig]]):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        args = UiArgs(sticky=tk.NSEW)
        self.models: List[SourceConfig] = []
        self.current_idx: Optional[int] = None
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args(weight=1))
        self.lst_sources = self._create_listbox(args)
        args.add_column()
        self.grid_columnconfigure(**args.column_args(weight=1))
        self.viw_model = SourceView(self)
        self.viw_model.grid(cnf=args.grid_args(sticky=tk.NSEW))

    def _create_listbox(self, args: UiArgs) -> tk.Listbox:
        frame = tk.LabelFrame(self, text="Source configurations")
        frame.grid(cnf=args.grid_args())

        lst_args = args.create()
        frame.grid_columnconfigure(**lst_args.column_args())
        frame.grid_rowconfigure(**lst_args.row_args())
        list_box = tk.Listbox(frame)
        list_box.bind('<<ListboxSelect>>', self.on_selection_changed)
        list_box.grid(cnf=lst_args.grid_args(sticky=tk.NSEW))
        return list_box

    def is_unique_by(self, name: str) -> bool:
        if len(self.models) == 0:
            return True
        if len(self.models) == 1:
            return self.models[0].name != name
        for idx, model in enumerate(self.models):
            if model.name != name:
                continue
            if self.current_idx is not None and idx == self.current_idx:
                continue
            return False
        return True

    def is_unique(self, other: SourceConfig) -> bool:
        return self.is_unique_by(other.name)

    def update_model_at(self, index: int):
        view_model = self.viw_model.model
        if not view_model.is_valid:
            return
        model = view_model.get_model()
        if self.models[index].name != model.name:
            self.lst_sources.delete(index)
            self.lst_sources.insert(index, model.name)
        self.models[index] = model

    def on_selection_changed(self, event: tk.Event):
        log.debug(f"Selection changed: {event}")
        selected_indices = self.lst_sources.curselection()
        log.debug(f"Selected indices: {selected_indices}")
        if len(selected_indices) != 1:
            return
        index = selected_indices[0]
        if not isinstance(index, int) or index == self.current_idx:
            return
        if self.current_idx is not None:
            self.update_model_at(self.current_idx)
        self.current_idx = index
        model = self.models[self.current_idx]
        self.viw_model.update_view(model)

    def show_selected_model(self):
        index = 0 if self.current_idx is None else self.current_idx
        self.current_idx = None
        self.lst_sources.selection_set(index)

    def add_model(self, model: SourceConfig):
        if not self.is_unique(model):
            return
        self.models.append(model)
        self.lst_sources.insert(tk.END, model.name)
        self.lst_sources.selection_set(tk.END)

    def get_model(self) -> List[SourceConfig]:
        return self.models

    def update_listbox(self):
        self.lst_sources.delete(0, tk.END)
        for model in self.models:
            self.lst_sources.insert(tk.END, model.name)
        if self.current_idx is not None:
            self.lst_sources.selection_set(self.current_idx)

    def update_view(self, model: List[SourceConfig]):
        self.models = model
        self.current_idx = None
        self.update_listbox()

    def show(self, model: Optional[List[SourceConfig]] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()
