import tkinter as tk
from tkinter.ttk import Style, Treeview
from typing import List, Optional

from dynpy.core.models import ConvertConfig, SourceConfig
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

    def update_model(self, model: SourceConfig):
        self.model = model
        self.name_value.set(model.name)
        self.source_value.set(model.source)
        self.export_value.set(model.export)

    def name_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.name_label,
            value=self.name_value,
            columns=(ui.UiMatrix(0, 0), ui.UiMatrix(1, 1)),
            rows=(ui.UiMatrix(0, 0),),
            args=args,
            key_event=None,
        )

    def source_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.source_label,
            value=self.source_value,
            columns=(ui.UiMatrix(0, 0), ui.UiMatrix(1, 1)),
            rows=(ui.UiMatrix(1, 0),),
            args=args,
            key_event=None,
        )

    def export_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(
            name=self.export_label,
            value=self.export_value,
            columns=(ui.UiMatrix(0, 0), ui.UiMatrix(1, 1)),
            rows=(ui.UiMatrix(2, 0),),
            args=args,
            key_event=None,
        )


class SourceView(tk.Frame, IView[SourceConfig]):
    def __init__(self, master: tk.Misc, args: Optional[ui.UiArgs] = None):
        super().__init__(master)
        args = args or ui.UiArgs()
        self.model = SourceViewModel(self)
        self.name = LabelEntry(self, self.model.name_options(args))
        self.source = LabelEntry(self, self.model.source_options(args))
        self.export = LabelEntry(self, self.model.export_options(args))

    def update_view(self, model: SourceConfig):
        self.model.update_model(model)

    def show(self, model: Optional[SourceConfig] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()


def _horizontal_scrollbar(parent: tk.Misc, content: Treeview) -> tk.Scrollbar:
    horizontal = tk.Scrollbar(
        parent,
        orient=tk.HORIZONTAL,
        command=content.xview,
    )
    horizontal.grid(row=1, column=0, sticky=tk.EW)
    return horizontal


def _vertical_scrollbar(parent: tk.Misc, content: Treeview) -> tk.Scrollbar:
    vertical = tk.Scrollbar(
        parent,
        orient=tk.VERTICAL,
        command=content.yview,  # type: ignore
    )
    vertical.grid(row=0, column=1, sticky=tk.NS)
    return vertical


class SourceListView(tk.Frame, IView[List[SourceConfig]]):
    def __init__(self, master: tk.Misc, args: Optional[ui.UiArgs] = None):
        super().__init__(master)
        args = args or ui.UiArgs()
        style = Style()
        style.configure("Treeview.Heading", font=("Calibri", 10, "bold"))
        self.tbl_tree = Treeview(self, style="Treeview")
        self.view_models: List[SourceViewModel] = []
        self.grid_columnconfigure(1, weight=1, minsize=350)
        self.grid_rowconfigure(args.row, weight=1)
        self._setup_grid(args)
        self._setup_table()

    def _setup_grid(self, args: ui.UiArgs):
        ui.setup_grid(self, args)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky=tk.NSEW)

    def _setup_table(self):
        scb_vertical = _vertical_scrollbar(self, self.tbl_tree)
        scb_horizontal = _horizontal_scrollbar(self, self.tbl_tree)
        self.tbl_tree.configure(
            selectmode=tk.BROWSE,
            show="headings",
            yscrollcommand=scb_vertical.set,
            xscrollcommand=scb_horizontal.set,
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


class ConvertConfigFrame(tk.Frame, IView[ConvertConfig]):
    def __init__(self, master: tk.Misc, args: Optional[ui.UiArgs] = None):
        super().__init__(master)
        args = args or ui.UiArgs()
        self.grid_columnconfigure(args.column, weight=1)
        self.grid_rowconfigure(args.row, weight=1)
        self.list_view = SourceListView(self)
        self.list_view.grid(cnf=args.grid_args())
        args.add_row()
        self.grid_columnconfigure(args.column, weight=1)
        self.grid_rowconfigure(args.row, weight=1)
        self.model_view = SourceView(self, args)
        self.model_view.grid(cnf=args.grid_args())
        self.model_view.hide()

    def update_view(self, model: ConvertConfig):
        self.list_view.update_view(model.configs)

    def show(self, model: Optional[ConvertConfig] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def _hide_views(self):
        self.list_view.hide()
        self.model_view.hide()

    def hide(self):
        self._hide_views()
        self.grid_remove()
