import tkinter as tk
from dataclasses import dataclass
from typing import Any

from dynpy.ui.utils import widget as ui


@dataclass(kw_only=True)
class LabelEntryOptions:
    name: str
    value: Any
    args: ui.UiArgs

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
        parent.grid_rowconfigure(**options.args.row_args())
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

    def _add_label(self, parent: tk.Misc, options: LabelEntryOptions) -> tk.StringVar:
        variable = options.label_name(parent)
        self._label = tk.Label(parent, textvariable=variable)
        parent.grid_columnconfigure(
            **options.args.column_args(weight=0), minsize=options.args.west_min
        )
        self._label.grid(cnf=options.args.grid_args(sticky=tk.W))
        return variable

    def _add_entry(self, parent: tk.Misc, options: LabelEntryOptions) -> tk.StringVar:
        variable = options.entry_value(parent)
        self._entry = tk.Entry(parent, textvariable=variable)
        parent.grid_columnconfigure(**options.args.column_args(weight=1))
        self._entry.grid(cnf=options.args.grid_args())
        return variable
