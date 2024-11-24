import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable, Optional

from dynpy.ui.models.uiargs import UiArgs


@dataclass(kw_only=True)
class LabelEntryOptions:
    name: str
    value: Any
    validate: Callable[[], bool]
    args: UiArgs
    invalidate: Optional[Callable[[], None]] = None

    def label_name(self, parent: tk.Misc) -> tk.StringVar:
        return tk.StringVar(master=parent, value=self.name)

    def entry_value(self, parent: tk.Misc) -> tk.StringVar:
        if self.value is None:
            return tk.StringVar(parent, value="")
        if isinstance(self.value, tk.StringVar):
            return self.value
        return tk.StringVar(master=parent, value=str(self.value))


class LabelEntry:
    def __init__(self, parent: tk.Misc, options: LabelEntryOptions):
        parent.grid_rowconfigure(**options.args.row_args(weight=0))
        self.label_name = self._add_label(parent, options)
        options.args.add_column()
        self.entry_value = self._add_entry(parent, options)

    @property
    def name(self) -> str:
        return self.label_name.get()

    @name.setter
    def name(self, name: str):
        self.label_name.set(name)

    @property
    def value(self) -> str:
        return self.entry_value.get()

    @value.setter
    def value(self, value: Any):
        if value is None:
            return
        self.entry_value.set(str(value))

    def _add_label(
        self, parent: tk.Misc, options: LabelEntryOptions
    ) -> tk.StringVar:
        variable = options.label_name(parent)
        self._label = tk.Label(parent, textvariable=variable)
        parent.grid_columnconfigure(
            **options.args.column_args(weight=0, minsize=options.args.west_min)
        )
        self._label.grid(cnf=options.args.grid_args(sticky=tk.W))
        return variable

    def _add_entry(
        self, parent: tk.Misc, options: LabelEntryOptions
    ) -> tk.StringVar:
        variable = options.entry_value(parent)
        self._entry = tk.Entry(
            parent,
            textvariable=variable,
            validate="all",
            validatecommand=(parent.register(options.validate), "%P"),
            # invalidcommand=parent.register(options.invalidate),
        )
        parent.grid_columnconfigure(**options.args.column_args(weight=1))
        self._entry.grid(cnf=options.args.grid_args(sticky=tk.EW))
        return variable


class LabelPathEntry(LabelEntry):
    last_path: str = str(Path.home())

    def __init__(self, parent: tk.Misc, options: LabelEntryOptions):
        super().__init__(parent, options)
        self._add_button(parent, options)

    def _add_button(self, parent: tk.Misc, options: LabelEntryOptions) -> None:
        self._button = tk.Button(
            parent, text="...", command=self._on_button_click
        )
        options.args.add_column()
        parent.grid_columnconfigure(**options.args.column_args(weight=0))
        self._button.grid(cnf=options.args.grid_args(sticky=tk.EW))

    def _is_path(self, path: Optional[str]) -> bool:
        return path is not None and path != ""

    def _on_button_click(self):
        path = self.value
        if not self._is_path(path):
            path = self.last_path
        path = filedialog.askdirectory(
            initialdir=path, title="Select Directory"
        )
        if not self._is_path(path):
            return
        self.value = path
        self.last_path = path
