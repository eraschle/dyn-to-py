import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as dialog
from typing import Callable, List, Optional, Tuple

from dynpy.core.models import SourceConfig
from dynpy.ui.models.entries import LabelEntry, LabelEntryOptions
from dynpy.ui.models.views import IView
from dynpy.ui.utils import widget as ui

log = logging.getLogger(__name__)


def ask_for_folder(title: str, current_path: str) -> str:
    dir_path = dialog.askdirectory(
        title=f"Select '{title.upper()}' directory.",
        initialdir=current_path,
    )
    if dir_path is None:
        return current_path
    return dir_path


class SourceViewModel:
    def __init__(self, parent: tk.Misc, model: Optional[SourceConfig] = None):
        if model is None:
            model = SourceConfig(name="", source="", export="")
        self.model = model
        self.name_value = tk.StringVar(master=parent, value=model.name)
        self.source_value = tk.StringVar(master=parent, value=model.source)
        self.export_value = tk.StringVar(master=parent, value=model.export)
        self.name_label = "Name"
        self.source_label = "Source Path"
        self.export_label = "Export Path"

    @property
    def tree_id(self) -> str:
        return self.model.name

    def get_model(self) -> SourceConfig:
        return SourceConfig(
            name=self.name_value.get(),
            source=self.source_value.get(),
            export=self.export_value.get(),
        )

    def update_model(self, model: SourceConfig):
        self.model = model
        self.name_value.set(model.name)
        self.source_value.set(model.source)
        self.export_value.set(model.export)

    def name_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.name_label,
            value=self.name_value,
            args=args,
        )

    def source_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.source_label,
            value=self.source_value,
            args=args,
        )

    def export_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.export_label,
            value=self.export_value,
            args=args,
        )


class SourceView(tk.Frame, IView[SourceConfig]):
    def __init__(self, master: tk.Misc, args: Optional[ui.UiArgs] = None):
        super().__init__(master)
        args = args or ui.UiArgs()
        self.model = SourceViewModel(self)
        self.name = LabelEntry(self, self.model.name_options(args))
        args.add_row()
        self.source = LabelEntry(self, self.model.source_options(args))
        args.add_row()
        self.export = LabelEntry(self, self.model.export_options(args))

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


class SourceButtonFrame(tk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.create_name = tk.StringVar(self, "Create")
        self.create_command: Callable[[], None] = lambda: None
        self.edit_name = tk.StringVar(self, "Edit")
        self.edit_command: Callable[[], None] = lambda: None
        self.delete_name = tk.StringVar(self, "Delete")
        self.delete_command: Callable[[], None] = lambda: None

    def _get_buttons_args(self) -> List[Tuple[tk.StringVar, Callable[[], None]]]:
        return [
            (self.create_name, lambda: self.create_command()),
            (self.edit_name, lambda: self.edit_command()),
            (self.delete_name, lambda: self.delete_command()),
        ]

    def _create_button_frame(self, args: ui.UiArgs) -> tk.Frame:
        frame = tk.Frame(self)
        args = args.create()
        frame.grid_rowconfigure(**args.row_args(weight=0))
        for idx, name_n_command in enumerate(self._get_buttons_args()):
            name, command = name_n_command
            button = tk.Button(master=frame, textvariable=name, command=command)
            if idx > 0:
                args.add_column()
            frame.grid_columnconfigure(**args.column_args(weight=0))
            button.grid(cnf=args.grid_args())
        # Expand column
        args.add_column()
        frame.grid_columnconfigure(**args.column_args(weight=1))
        return frame


class EntryPopup(ttk.Entry):
    def __init__(self, tree: ttk.Treeview, iid: str, column: int, text: str, **kw):
        ttk.Style().configure('pad.TEntry', padding='1 1 1 1')
        super().__init__(tree, style='pad.TEntry', **kw)
        self.tree = tree
        self.iid = iid
        self.column = column

        self.insert(0, text)
        # self['state'] = 'readonly'
        # self['readonlybackground'] = 'white'
        # self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False

        self.focus_force()
        self.select_all()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda *ignore: self.destroy())

    def on_return(self, event):
        rowid = self.tree.focus()
        values = list(self.tree.item(rowid, 'values'))
        values[self.column] = self.get()
        self.tree.item(rowid, values=values)
        self.destroy()

    def select_all(self, *ignore):
        '''Set selection on the whole text'''
        self.selection_range(0, 'end')

        # returns 'break' to interrupt default key-bindings
        return 'break'


class SourceTreeview(tk.Frame):
    # https://stackoverflow.com/questions/18562123/how-to-make-ttk-treeviews-rows-editable
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        args = ui.UiArgs(sticky=tk.NSEW)
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args(weight=1))
        self.buttons = SourceButtonFrame(self)
        self.buttons.create_command = self.create_source
        self.buttons.edit_command = self.edit_selected
        self.buttons.delete_command = self.delete_selected
        self.buttons.grid(cnf=args.grid_args(columnspan=2))
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=1))
        self.tbl_tree = self._create_treeview(args)
        args.add_column()
        self.grid_columnconfigure(**args.column_args(weight=1))
        self.frm_model = SourceView(self)
        self.frm_model.grid(cnf=args.grid_args(sticky=tk.NSEW))

    def _horizontal_scroll(self, frame: tk.Frame, args: ui.UiArgs) -> tk.Scrollbar:
        if args.row_index < 1:
            args.add_row()
        scroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tbl_tree.xview)
        scroll.grid(cnf=args.grid_args(sticky=tk.EW))
        return scroll

    def _vertical_scroll(self, frame: tk.Frame, args: ui.UiArgs) -> tk.Scrollbar:
        if args.column_index < 1:
            args.add_column()
        scroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tbl_tree.yview)
        scroll.grid(cnf=args.grid_args(sticky=tk.NS))
        return scroll

    def _create_treeview(self, args: ui.UiArgs) -> ttk.Treeview:
        frame = tk.Frame(self)
        frame.grid(cnf=args.grid_args())

        tree_args = args.create()
        frame.grid_columnconfigure(**tree_args.column_args())
        frame.grid_rowconfigure(**tree_args.row_args())
        table = ttk.Treeview(frame, style="Treeview")
        table.bind("<Double-1>", self.on_left_double_click)
        table.bind("<Double-3>", self.on_middle_double_click)
        table.grid(cnf=tree_args.grid_args(sticky=tk.NSEW))
        table.configure(
            selectmode=tk.BROWSE,
            show="headings",
            yscrollcommand=self._vertical_scroll(frame, tree_args).set,
            xscrollcommand=self._horizontal_scroll(frame, tree_args).set,
        )
        return table

    def on_left_double_click(self, event):
        '''Executed, when a row is double-clicked. Opens
        read-only EntryPopup above the item's column, so it is possible
        to select text'''

        # close previous popups
        try:  # in case there was no previous popup
            self.entryPopup.destroy()
        except AttributeError:
            pass

        # what row and column was clicked on
        rowid = self.tbl_tree.identify_row(event.y)
        column = self.tbl_tree.identify_column(event.x)

        # handle exception when header is double click
        if not rowid:
            return

        # get column position info
        x, y, width, height = self.tbl_tree.bbox(rowid, column)

        # y-axis offset
        pady = int(height) // 2

        # place Entry popup properly
        column_idx = int(column[1:]) - 1
        text = self.tbl_tree.item(rowid, 'values')[column_idx]
        self.entryPopup = EntryPopup(self.tbl_tree, rowid, column_idx, text)
        self.entryPopup.place(x=x, y=int(y) + pady, width=width, height=height, anchor='w')

    def on_middle_double_click(self, event):
        # what row and column was clicked on
        rowid = self.tbl_tree.identify_row(event.y)
        column = self.tbl_tree.identify_column(event.x)

        # handle exception when header is double click
        if not rowid:
            return

        column_idx = int(column[1:]) - 1
        if column_idx < 1:
            return
        column_name = self.tbl_tree.heading(column, "text")
        values = list(self.tbl_tree.item(rowid, 'values'))
        values[column_idx] = ask_for_folder(values[column_idx], column_name)
        self.tbl_tree.item(rowid, values=values)

    def _model_by(self, tree_id: str) -> SourceViewModel:
        for view_model in self.view_models:
            if view_model.tree_id != tree_id:
                continue
            return view_model
        raise ValueError(f"Model not found: {tree_id}")

    def _get_selected_model(self) -> Optional[SourceViewModel]:
        selected_ids = self.tbl_tree.selection()
        if len(selected_ids) == 0:
            return None
        tree_id = selected_ids[0]
        return self._model_by(tree_id)

    def create_source(self) -> None:
        pass

    def edit_selected(self) -> None:
        model = self._get_selected_model()
        if model is None:
            return
        pass

    def delete_selected(self) -> None:
        view_model = self._get_selected_model()
        if view_model is None:
            return
        self.view_models.remove(view_model)
        self.tbl_tree.delete(view_model.model.name)
        # self._update_tree()

    def _column_names(self) -> List[str]:
        model = SourceViewModel(self)
        return [model.name_label, model.source_label, model.export_label]

    def _add_columns(self) -> None:
        names = self._column_names()
        self.tbl_tree.configure(columns=names)
        for idx, name in enumerate(names, start=1):
            col_index = f"#{idx}"
            self.tbl_tree.column(
                col_index,
                anchor=tk.W,
                stretch=True,
            )
            self.tbl_tree.heading(
                col_index,
                text=name,
                anchor=tk.CENTER,
            )

    def _remove_all_rows(self):
        for row in self.tbl_tree.get_children():
            self.tbl_tree.delete(row)

    def _update_sources(self):
        for view_model in self.view_models:
            model = view_model.model
            values = [model.name, model.source, model.export]
            self.tbl_tree.insert("", "end", id=view_model.tree_id, values=values)

    def get_model(self) -> List[SourceConfig]:
        return [mdl.get_model() for mdl in self.view_models]

    def _update_tree(self):
        self._remove_all_rows()
        self._add_columns()
        self._update_sources()

    def update_view(self, model: List[SourceConfig]):
        self.view_models = [SourceViewModel(self, mdl) for mdl in model]
        self._update_tree()
