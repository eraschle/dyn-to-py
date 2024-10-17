import tkinter as tk
import traceback
from pathlib import Path
from tkinter import filedialog as dialog
from tkinter import messagebox as msg
from tkinter.ttk import Notebook
from typing import Callable, Optional

from dynpy.service import IConvertService
from dynpy import ressources as res
from dynpy.ui.models.action import ConvertActionView
from dynpy.ui.models.convert import ConvertionView
from dynpy.ui.models.source import SourceListView
from dynpy.ui.models.uiargs import UiArgs


def ask_config_folder() -> Path:
    dir_path = dialog.askdirectory(
        title="Select directory for configuration file",
        initialdir=Path.home(),
    )
    return Path(dir_path)


def ask_config_file(service: IConvertService) -> Path:
    file_path = dialog.askopenfilename(
        defaultextension=f".{service.config_extension}",
        filetypes=[("DynPy config", f"*.{service.config_extension}")],
        title="Select a configuration file",
        initialdir=Path.home(),
    )
    return Path(file_path)


class ConvertLoadFrame(tk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        args = UiArgs(sticky=tk.NSEW)
        self.grid_columnconfigure(**args.column_args(weight=1))
        self.grid_rowconfigure(**args.row_args(weight=1))
        args.add_row()
        self._add_button_row(args)
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=1))

    def _add_button_row(self, args: UiArgs, minsize: int = 200):
        self.grid_rowconfigure(**args.row_args(weight=0), minsize=minsize)
        args.add_column()
        self.grid_columnconfigure(**args.column_args(weight=0), minsize=minsize)
        self._add_create_button(args)
        args.add_column()
        self.grid_columnconfigure(**args.column_args(weight=0), minsize=minsize)
        self._add_load_button(args)
        args.add_column()
        self.grid_columnconfigure(**args.column_args(weight=1))

    def _button_image(self, icon: res.DynPyResource) -> Optional[tk.PhotoImage]:
        path = res.icon_path(icon).absolute()
        if not path.exists():
            return None
        return tk.PhotoImage(file=path)

    def _add_button(self, image: Optional[tk.PhotoImage], args: UiArgs) -> tk.Button:
        if image is None:
            button = tk.Button(self, compound=tk.TOP)
        else:
            button = tk.Button(self, image=image, compound=tk.TOP)
        button.grid(cnf=args.grid_args(sticky=tk.NSEW))
        return button

    def _add_create_button(self, args: UiArgs) -> None:
        self.create_image = self._button_image(res.DynPyResource.ICON_CREATE)
        self.create_config = self._add_button(self.create_image, args)

    def _add_load_button(self, args: UiArgs) -> None:
        self.load_image = self._button_image(res.DynPyResource.ICON_LOAD)
        self.load_config = self._add_button(self.load_image, args)

    def add_create_command(self, command: Callable[[], None], name: str = "Create config"):
        self.create_config.config(command=command, text=name)

    def add_load_command(self, command: Callable[[], None], name: str = "Load config"):
        self.load_config.config(command=command, text=name)


class ConvertAppFrame(tk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        args = UiArgs(sticky=tk.NSEW)
        self.grid_columnconfigure(**args.column_args())
        self.grid_rowconfigure(**args.row_args())
        args = args.create()
        self.tab_frame = Notebook(self)
        self.tab_frame.grid_columnconfigure(**args.column_args())
        self.tab_frame.grid_rowconfigure(**args.row_args())
        self.tab_frame.grid(cnf=args.grid_args())
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

    def update_views(self, service: IConvertService):
        self.actions.update_view(service.actions)
        self.source.update_view(service.source_configs)
        # self.convert.update_view(service.handler)


class ConvertApp(tk.Tk):
    def __init__(self, service: IConvertService) -> None:
        super().__init__()
        self.service = service
        args = UiArgs(sticky=tk.NSEW)
        self.grid_columnconfigure(**args.column_args())
        self.grid_rowconfigure(**args.row_args())
        self.frm_app = ConvertAppFrame(self)
        self.frm_load = ConvertLoadFrame(self)
        self.frm_load.add_create_command(self.config_create_command)
        self.frm_load.add_load_command(self.config_load_command)
        self.frm_load.grid(cnf=args.grid_args())
        self.setup_ui()

    def config_create_command(self):
        dir_path = ask_config_folder()
        file_path = self.service.create_config(dir_path)
        self._load_config(file_path)

    def config_load_command(self):
        file_path = ask_config_file(self.service)
        self._load_config(file_path)

    def _load_config(self, file_path: Path):
        try:
            self.service.load_config(file_path)
            self._switch_frame()
        except FileNotFoundError:
            msg.showerror("Error", "Configuration file does not exist.")
        except Exception:
            trace = traceback.format_exc()
            msg.showerror("Error", f"An error occurred while loading config file:\n{trace}")

    def _switch_frame(self):
        self.frm_load.grid_forget()
        args = UiArgs(sticky=tk.NSEW)
        self.frm_app.update_views(self.service)
        self.frm_app.grid(cnf=args.grid_args())

    def setup_ui(self):
        icon_path = res.icon_path(res.DynPyResource.ICON_APP)
        self.iconphoto(True, tk.PhotoImage(file=icon_path))
        self.title("Dynamo <-> Python Convert")
