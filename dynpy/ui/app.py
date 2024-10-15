import tkinter as tk
from tkinter.ttk import Notebook

from dynpy.ui.action import ConvertActionView
from dynpy.ui.convert import ConvertionView
from dynpy.ui.interface import IConvertService
from dynpy.ui.source import SourceListView
from dynpy.ui.utils import widget as ui


class ConvertAppFrame(tk.Frame):
    def __init__(self, master: tk.Misc, service: IConvertService):
        super().__init__(master)
        args = ui.UiArgs()
        self.service = service
        self.grid_columnconfigure(**args.column_args())
        self.grid_rowconfigure(**args.row_args())
        args = args.create()
        self.tab_frame = Notebook(self)
        self.tab_frame.grid_columnconfigure(**args.column_args())
        self.tab_frame.grid_rowconfigure(**args.row_args())
        self.tab_frame.grid(cnf=args.grid_args(sticky=tk.NSEW))
        self.add_sources()
        self.add_actions()
        self.add_convert()

    def add_sources(self):
        self.source = SourceListView(self.tab_frame)
        self.tab_frame.add(self.source, text="Source")

    def add_actions(self):
        self.actions = ConvertActionView(self.tab_frame)
        self.tab_frame.add(self.actions, text="Actions")

    def add_convert(self):
        self.convert = ConvertionView(self.tab_frame)
        self.tab_frame.add(self.convert, text="Convert")


class ConvertApp(tk.Tk):
    def __init__(self, service: IConvertService) -> None:
        super().__init__()
        args = ui.UiArgs()
        self.grid_columnconfigure(**args.column_args())
        self.grid_rowconfigure(**args.row_args())
        self.frame = ConvertAppFrame(self, service)
        self.frame.grid(cnf=args.grid_args(sticky=tk.NSEW))
