from dataclasses import dataclass
import tkinter as tk
from typing import Callable, Optional

from dynpy.ui.utils import widget as ui


@dataclass
class LabelEntryOptions:
    label_text: str | tk.Variable
    entry_text: tk.Variable
    args: ui.UiArgs
    key_event: Optional[Callable[[], None]] = None


class LabelEntry:
    def __init__(self, parent: tk.Misc, options: LabelEntryOptions):
        self.label = tk.Label(parent)
        self.entry = tk.Entry(parent)
        ui.set_label_entry(
            label=self.label,
            label_text=options.label_text,
            entry=self.entry,
            entry_value=options.entry_text,
            args=options.args,
        )
