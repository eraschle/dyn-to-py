import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from dynpy.ui.utils import widget as ui

EntryEvent = Callable[[tk.Event], None]


@dataclass(kw_only=True)
class LabelEntryOptions:
    name: str | tk.Variable
    value: tk.Variable
    columns: Iterable[ui.UiMatrix]
    rows: Iterable[ui.UiMatrix]
    args: ui.UiArgs
    key_event: Optional[EntryEvent] = None


class LabelEntry:
    def __init__(self, parent: tk.Misc, options: LabelEntryOptions):
        self.label = tk.Label(parent)
        self.entry = tk.Entry(parent)
        self.set_options(options)
        self.set_parent(parent, options)

    def set_parent(self, parent: tk.Misc, options: LabelEntryOptions) -> None:
        for col in options.columns:
            parent.grid_columnconfigure(index=col.index, weight=col.weight)
        for col in options.rows:
            parent.grid_rowconfigure(index=col.index, weight=col.weight)

    def set_options(self, options: LabelEntryOptions) -> None:
        ui.setup_label(self.label, options.name)
        self.label.grid(cnf=options.args.grid_args())
        options.args.add_column()
        self.entry.configure(textvariable=options.value)
        self.entry.grid(cnf=options.args.grid_args())
        options.args.add_row()
        if options.key_event is None:
            return
        self.entry.bind("<KeyRelease>", options.key_event)
