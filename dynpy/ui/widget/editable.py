import tkinter as tk
from typing import Callable, Iterable, List, Literal, Tuple

from dynpy.ui.models.uiargs import UiArgs


class EditableListbox(tk.Listbox):
    """A listbox where you can directly edit an item via double-click
    listbox-text-edit-in-gui"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.edit_index: int | None = None
        self.bind("<Double-1>", self._edit_event)
        self.bind("<Delete>", self._delete_event)
        self.bind("<Insert>", self._add_event)
        self.edit_started_hook: Callable[[], None] = lambda: None
        self.edit_finished_hook: Callable[[], None] = lambda: None

    def clean_values(self):
        self.delete(0, self.size() - 1)

    def update_values(self, models: Iterable[str]):
        self.clean_values()
        self.insert("end", *models)

    def _add_event(self, event: tk.Event):
        if self != event.widget:
            return
        self.add_item()
        return "break"

    def add_item(self):
        index = self.size()
        self.insert(index, "New Item")
        self.edit_item(index)

    def _delete_event(self, event: tk.Event):
        if self != event.widget:
            return
        self.delete_selected()
        return "break"

    @property
    def selected_index(self) -> int:
        indices = self.curselection()
        index = -1
        if isinstance(indices, (list, tuple)):
            index = indices[0] if len(indices) > 0 else -1
        else:
            index = indices
        print(f"Current selection TK: {indices} App: {index}")
        return index

    def delete_selected(self):
        self.delete(self.selected_index)

    def _edit_event(self, event: tk.Event):
        if self != event.widget:
            return
        index = self.index(f"@{event.x},{event.y}")
        self.edit_item(index)
        return "break"

    def edit_selected(self):
        self.edit_item(self.selected_index)

    def edit_item(self, index):
        if self.bbox(index) is None:
            self.see(index)

        self.edit_index = index
        bbox = self.bbox(index)
        if bbox is None:
            return
        self.edit_started_hook()
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
        self.edit_finished_hook()

    def accept_edit(self, event):
        new_data = event.widget.get()
        if self.edit_index is not None:
            self.delete(self.edit_index)
            self.insert(self.edit_index, new_data)
            event.widget.destroy()
        self.edit_finished_hook()


class EditableListboxFrame(tk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master=master)
        args = UiArgs()
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args())
        self.editable = EditableListbox(self)
        self.editable.edit_started_hook = lambda: self._edit_hook(tk.DISABLED)
        self.editable.edit_finished_hook = lambda: self._edit_hook(tk.NORMAL)
        self.buttons = self._add_buttons(args)
        args.add_row()
        self.grid_rowconfigure(**args.row_args())
        args.columnspan = len(self.buttons) + 1
        self.editable.grid(cnf=args.grid_args(sticky=tk.NSEW))

    def update_values(self, models: Iterable[str]):
        self.editable.update_values(models)

    def get_values(self) -> List[str]:
        return self.editable.get(0, self.editable.size())

    def _edit_hook(self, state: Literal["normal", "disabled"]):
        for button in self.buttons:
            button.config(state=state)

    def _get_buttons_args(self) -> List[Tuple[str, Callable[[], None]]]:
        return [
            ("Add", lambda: self.editable.add_item()),
            ("Edit", lambda: self.editable.edit_selected()),
            ("Remove", lambda: self.editable.delete_selected()),
        ]

    def _add_buttons(self, args: UiArgs) -> List[tk.Button]:
        buttons = []
        for name, command in self._get_buttons_args():
            if len(buttons) > 0:
                args.add_column()
            self.grid_columnconfigure(
                **args.column_args(weight=0, minsize=args.east_min)
            )
            button = tk.Button(master=self, text=name, command=command)
            button.grid(cnf=args.grid_args())
            buttons.append(button)
        args.add_column()
        self.grid_columnconfigure(**args.column_args(weight=1))
        return buttons
