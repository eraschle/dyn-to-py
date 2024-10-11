import tkinter as tk
from tkinter.ttk import Notebook
from typing import Optional, Protocol

from dynpy.core import factory
from dynpy.core.models import ConvertConfig
from dynpy.ui.action import ConvertActionFrame
from dynpy.ui.interface import IView
from dynpy.ui.utils import widget as ui


class IConvertConfigService(Protocol):
    config: ConvertConfig

    def get(self) -> ConvertConfig: ...

    def update(self, source: ConvertConfig) -> None: ...


class ConvertConfigFrame(tk.Frame, IView[ConvertConfig]):
    def __init__(self, master: tk.Misc, args: Optional[ui.UiArgs] = None):
        super().__init__(master)
        self.config = factory.default_convert_config()
        args = args or ui.UiArgs()
        self.tab_frame = Notebook(self)
        self.source = ConvertConfigFrame(self.tab_frame)
        self.actions = ConvertActionFrame(self.tab_frame)
        self.tab_frame.add(self.source, text="Source")
        self.tab_frame.add(self.actions, text="Actions")
        self.grid_columnconfigure(args.column, weight=1)
        self.grid_rowconfigure(args.row, weight=1)

    def update_view(self, model: ConvertConfig):
        self.source.show(model)
        self.actions.show(model)

    def show(self, model: Optional[ConvertConfig] = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        for view in self.tab_frame.tabs():
            view.hide()
        self.grid_remove()
