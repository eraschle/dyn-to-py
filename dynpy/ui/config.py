import tkinter as tk
from tkinter.ttk import Notebook

from dynpy.ui.action import ConvertActionView
from dynpy.ui.interface import IConvertService
from dynpy.ui.source import SourceListView
from dynpy.ui.utils import widget as ui


class ConvertConfigFrame(tk.Frame):
    def __init__(self, master: tk.Misc, service: IConvertService):
        super().__init__(master)
        args = ui.UiArgs()
        self.service = service
        self.grid_columnconfigure(args.column_index, weight=1)
        self.grid_rowconfigure(args.row_index, weight=1)
        self.grid(cnf=args.to_dict())
        self.tab_frame = Notebook(self)
        args = args.create()
        self.tab_frame.grid_columnconfigure(args.column_index, weight=1)
        self.tab_frame.grid_rowconfigure(args.row_index, weight=1)
        self.tab_frame.grid(cnf=args.to_dict())
        self.source = SourceListView(self.tab_frame)
        self.actions = ConvertActionView(self.tab_frame)
        self.tab_frame.add(self.source, text="Source")
        self.tab_frame.add(self.actions, text="Actions")
