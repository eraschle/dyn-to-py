import logging
import tkinter as tk
from tkinter.ttk import Treeview
from typing import Callable, List, Optional, Tuple

from dynpy.core.models import SourceConfig
from dynpy.ui.models.entries import LabelEntry, LabelEntryOptions
from dynpy.ui.models.views import IView
from dynpy.ui.utils import widget as ui

log = logging.getLogger(__name__)


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


class SourceListView(tk.Frame, IView[List[SourceConfig]]):
    # https://stackoverflow.com/questions/18562123/how-to-make-ttk-treeviews-rows-editable
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        # style = Style()
        # style.configure("Treeview.Heading", font=("Calibri", 10, "bold"))
        args = ui.UiArgs(sticky=tk.NSEW)
        self.view_models: List[SourceViewModel] = []
        self.grid_rowconfigure(**args.row_args(weight=0))
        self._add_buttons(args)
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=1))
        self.tbl_tree = self._setup_table(args)

    def _get_buttons_args(self) -> List[Tuple[str, Callable[[], None]]]:
        return [
            ("Add", lambda: self.create_source()),
            ("Edit", lambda: self.edit_selected()),
            ("Remove", lambda: self.delete_selected()),
        ]

    def _add_buttons(self, args: ui.UiArgs) -> None:
        frm_buttons = tk.Frame(self)
        frm_buttons.grid(cnf=args.grid_args(sticky=tk.NSEW))
        btn_args = args.create()
        frm_buttons.grid_rowconfigure(**btn_args.row_args(weight=0))
        for idx, name_n_command in enumerate(self._get_buttons_args()):
            name, command = name_n_command
            button = tk.Button(master=frm_buttons, text=name, command=command)
            if idx > 0:
                btn_args.add_column()
            frm_buttons.grid_columnconfigure(**btn_args.column_args(weight=0))
            button.grid(cnf=btn_args.grid_args())
        btn_args.add_column()
        frm_buttons.grid_columnconfigure(**btn_args.column_args(weight=1))

    def horizontal_scrollbar(
        self, frame: tk.Frame, table: Treeview, args: ui.UiArgs
    ) -> tk.Scrollbar:
        if args.row_index < 1:
            args.add_row()
        scroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=table.xview)
        scroll.grid(cnf=args.grid_args(sticky=tk.EW))
        return scroll

    def vertical_scrollbar(self, frame: tk.Frame, table: Treeview, args: ui.UiArgs) -> tk.Scrollbar:
        if args.column_index < 1:
            args.add_column()
        scroll = tk.Scrollbar(frame, orient=tk.VERTICAL, command=table.yview)
        scroll.grid(cnf=args.grid_args(sticky=tk.NS))
        return scroll

    def _setup_table(self, args: ui.UiArgs) -> Treeview:
        frame = tk.Frame(self)
        frame.grid(cnf=args.grid_args())

        tbl_args = args.create()
        frame.grid_columnconfigure(**tbl_args.column_args())
        frame.grid_rowconfigure(**tbl_args.row_args())
        table = Treeview(frame, style="Treeview")
        table.grid(cnf=tbl_args.grid_args(sticky=tk.NSEW))
        v_scroll = self.vertical_scrollbar(frame, table, tbl_args)
        h_scroll = self.horizontal_scrollbar(frame, table, tbl_args)
        table.configure(
            selectmode=tk.BROWSE,
            show="headings",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
        )
        return table

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

    def show(self, model: Optional[List[SourceConfig]] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()
