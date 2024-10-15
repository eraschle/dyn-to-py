import tkinter as tk
from tkinter.ttk import Treeview
from typing import List, Optional

from dynpy.core.models import SourceConfig
from dynpy.ui.interface import IView
from dynpy.ui.models.entries import LabelEntry, LabelEntryOptions
from dynpy.ui.utils import widget as ui


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
    def __init__(self, master: tk.Misc, args: Optional[ui.UiArgs] = None):
        super().__init__(master)
        # style = Style()
        # style.configure("Treeview.Heading", font=("Calibri", 10, "bold"))
        args = args or ui.UiArgs()
        self.view_models: List[SourceViewModel] = []
        self.tbl_tree = Treeview(self, style="Treeview")
        self.tbl_tree.grid_columnconfigure(**args.column_args(), minsize=350)
        self.tbl_tree.grid_rowconfigure(**args.row_args())
        self._setup_table(args)
        self.grid(cnf=args.grid_args())

    def horizontal_scrollbar(self, args: ui.UiArgs) -> tk.Scrollbar:
        if args.row_index < 1:
            args.add_row()
        scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tbl_tree.xview)
        scroll.grid(cnf=args.grid_args(sticky=tk.EW))
        return scroll

    def vertical_scrollbar(self, args: ui.UiArgs) -> tk.Scrollbar:
        if args.column_index < 1:
            args.add_column()
        scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.tbl_tree.yview)
        scroll.grid(cnf=args.grid_args(sticky=tk.NS))
        return scroll

    def _setup_table(self, args: ui.UiArgs):
        self.grid_columnconfigure(**args.column_args())
        self.grid_rowconfigure(**args.row_args())
        self.tbl_tree.grid(cnf=args.grid_args(sticky=tk.NSEW))
        v_scroll = self.vertical_scrollbar(args)
        h_scroll = self.horizontal_scrollbar(args)
        self.tbl_tree.configure(
            selectmode=tk.BROWSE,
            show="headings",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
        )

    def _get_name(self, option: LabelEntryOptions) -> str:
        if isinstance(option.name, str):
            return option.name
        return option.name.get()

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
                anchor=tk.E,
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
        for view in self.view_models:
            model = view.model
            values = [model.name, model.source, model.export]
            self.tbl_tree.insert("", "end", values=values)

    def get_model(self) -> List[SourceConfig]:
        return [mdl.get_model() for mdl in self.view_models]

    def update_view(self, model: List[SourceConfig]):
        self.view_models = [SourceViewModel(self, mdl) for mdl in model]
        self._remove_all_rows()
        self._add_columns()
        self._update_sources()

    def show(self, model: Optional[List[SourceConfig]] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()
