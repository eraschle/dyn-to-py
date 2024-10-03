import tkinter as tk
from typing import List, Optional

from dynpy.core.models import SourceConfig
from dynpy.ui.interface import IView
from dynpy.ui.models.entries import LabelEntry, LabelEntryOptions
from dynpy.ui.utils import widget as ui


class SourceViewModel:
    def __init__(self, model: Optional[SourceConfig] = None):
        if model is None:
            model = SourceConfig(name='', source='', export='')
        self.model = model
        self.name = tk.StringVar(value=model.name)
        self.source = tk.StringVar(value=model.source)
        self.export = tk.StringVar(value=model.export)

    def update_model(self, model: SourceConfig):
        self.model = model
        self.name.set(model.name)
        self.source.set(model.source)
        self.export.set(model.export)

    def name_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(label_text='Name', entry_text=self.name, args=args)

    def source_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(label_text='Source Path', entry_text=self.source, args=args)

    def export_options(self, args: ui.UiArgs) -> LabelEntryOptions:
        return LabelEntryOptions(label_text='Export Path', entry_text=self.export, args=args)


class SourceView(tk.Frame, IView[SourceConfig]):
    def __init__(self, master: tk.Misc, view_model: SourceViewModel, args: Optional[ui.UiArgs] = None):
        super().__init__(master)
        args = args or ui.UiArgs()
        self.view_model = view_model
        self.grid_columnconfigure(1, weight=1, minsize=350)
        self.grid_rowconfigure(args.row, weight=1)
        self.name = LabelEntry(self, self.view_model.name_options(args))
        args.add_row()
        self.grid_rowconfigure(args.row, weight=1)
        self.source = LabelEntry(self, self.view_model.source_options(args))
        args.add_row()
        self.grid_rowconfigure(args.row, weight=1)
        self.export = LabelEntry(self, self.view_model.export_options(args))

    def update_view(self, model: SourceConfig):
        self.view_model.update_model(model)

    def show(self):
        pass

    def hide(self):
        pass


class SourceListView(tk.Frame, IView[List[SourceConfig]]):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        args = ui.UiArgs()
        self.view_models: List[SourceViewModel] = []
        self.grid_columnconfigure(1, weight=1, minsize=350)
        self.grid_rowconfigure(args.row, weight=1)

    def update_view(self, model: List[SourceConfig]):
        self.view_models = [SourceViewModel(mdl) for mdl in model]

    def show(self):
        pass

    def hide(self):
        pass


class SourceFrame(tk.Frame):
    def __init__(self, master: tk.Misc, args: Optional[ui.UiArgs] = None):
        super().__init__(master)
        args = args or ui.UiArgs()
        self.grid_columnconfigure(args.column, weight=1)
        self.grid_rowconfigure(args.row, weight=1)
        self.model_view = SourceView(self, SourceViewModel(), args)
        self.model_view.grid(cnf=ui.get_grid_args(args))
        args.add_row()
        self.grid_columnconfigure(args.column, weight=1)
        self.grid_rowconfigure(args.row, weight=1)
        self.list_view = SourceListView(self)
        self.list_view.grid(cnf=ui.get_grid_args(args))
