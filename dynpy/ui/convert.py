import tkinter as tk
from pathlib import Path
from typing import List

from dynpy.service.convert import ConvertHandler
from dynpy.ui.interface import IView
from dynpy.ui.utils import widget as ui


class SourceFileListBox(tk.LabelFrame):
    def __init__(self, master: tk.Misc, text: str):
        super().__init__(master=master, text=text)
        args = ui.UiArgs()
        self.files: List[Path] = []
        self.grid_rowconfigure(**args.row_args())
        self.grid_columnconfigure(**args.column_args())
        self.lst_files = tk.Listbox(self)
        self.add_file_lists(args)

    def add_file_lists(self, args: ui.UiArgs):
        args = args.create(row=0, column=0, sticky=tk.NSEW)
        self.lst_files.grid_rowconfigure(**args.row_args())
        self.lst_files.grid_columnconfigure(**args.column_args())
        self.lst_files.grid(cnf=args.grid_args())

    def clean_values(self):
        self.lst_files.delete(0, self.lst_files.size() - 1)

    def _sub_path_of(self, file: Path, root: Path) -> str:
        return str(file.resolve()).removeprefix(str(root.resolve()))

    def update_files(self, files: List[Path], root_path: Path):
        self.files = files
        self.clean_values()
        file_names = [self._sub_path_of(file, root_path) for file in files]
        self.lst_files.insert("end", *file_names)


class ConvertionView(tk.Frame, IView[ConvertHandler]):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        args = ui.UiArgs()
        self.grid_rowconfigure(**args.row_args())
        self.grid_columnconfigure(**args.column_args())

        self.lst_source = SourceFileListBox(self, "Source Files")
        self.lst_source.grid(cnf=args.grid_args(sticky=tk.NSEW))
        args.add_column()

        self.grid_columnconfigure(**args.column_args())
        self.lst_export = SourceFileListBox(self, "Export Files")
        self.lst_export.grid(cnf=args.grid_args(sticky=tk.NSEW))

    def get_model(self) -> ConvertHandler:
        raise NotImplementedError

    def update_view(self, model: ConvertHandler):
        source = model.source
        self.lst_source.update_files(source.source_files(), source.source_path)
        self.lst_export.update_files(source.export_files(), source.export_path)

    def show(self, model: ConvertHandler | None = None):
        if model is not None:
            self.update_view(model)
        self.grid()

    def hide(self):
        self.grid_remove()
