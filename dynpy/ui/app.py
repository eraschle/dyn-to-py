import tkinter as tk

from dynpy.ui.utils import widget as ui
from dynpy.ui.source import SourceFrame


class AppView(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.args = ui.UiArgs()
        self.app_frame = tk.Frame(self)
        source_frame = SourceFrame(self.app_frame)
        source_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.args.add_row()

        self.app_frame.grid_columnconfigure(0, weight=1)
        self.app_frame.grid_rowconfigure(0, weight=1)
        self.app_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
