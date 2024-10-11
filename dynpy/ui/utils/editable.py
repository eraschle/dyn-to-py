import tkinter as tk
from typing import Iterable


class EditableListbox(tk.Listbox):
    """A listbox where you can directly edit an item via double-click
    listbox-text-edit-in-gui"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.edit_index: int | None = None
        self.bind("<Double-1>", self._start_edit)

    def clean_values(self):
        self.delete(0, self.size() - 1)

    def update_values(self, models: Iterable[str]):
        self.clean_values()
        self.insert("end", *models)

    def _start_edit(self, event):
        index = self.index(f"@{event.x},{event.y}")
        self.start_edit(index)
        return "break"

    def start_edit(self, index):
        if self.bbox(index) is None:
            self.see(index)

        self.edit_index = index
        bbox = self.bbox(index)
        if bbox is None:
            return
        y_index = bbox[1]
        entry = tk.Entry(self, borderwidth=0, highlightthickness=1)
        entry.bind("<Return>", self.accept_edit)
        entry.bind("<Escape>", self.cancel_edit)

        text = self.get(index)
        entry.insert(0, text)
        entry.selection_from(0)
        entry.selection_to("end")
        entry.place(relx=0, y=y_index, relwidth=1, width=-1)
        entry.focus_set()
        entry.grab_set()

    def cancel_edit(self, event):
        event.widget.destroy()

    def accept_edit(self, event):
        new_data = event.widget.get()
        if self.edit_index is None:
            return
        self.delete(self.edit_index)
        self.insert(self.edit_index, new_data)
        event.widget.destroy()
