import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as dialog
from tkinter import ttk
from typing import Optional, Tuple

from dynpy import ressources as res
from dynpy.service import IConvertService
from dynpy.ui.models.action import ConvertActionView
from dynpy.ui.models.source import SourceListView
from dynpy.ui.models.uiargs import UiArgs
from dynpy.ui.models.views import AAppView

log = logging.getLogger(__name__)


class ConvertConfigAppView(AAppView):
    def _init_view(self):
        args = UiArgs(sticky=tk.NSEW)
        self.grid_columnconfigure(**args.column_args())
        self.grid_rowconfigure(**args.row_args())
        args = args.create()
        self.tab_frame = ttk.Notebook(self)
        self.tab_frame.grid_columnconfigure(**args.column_args())
        self.tab_frame.grid_rowconfigure(**args.row_args())
        self.tab_frame.grid(cnf=args.grid_args())
        self.add_sources()
        self.add_actions()

    def add_sources(self):
        self.source = SourceListView(self.tab_frame)
        self.tab_frame.add(self.source, text="Source")

    def add_actions(self):
        self.actions = ConvertActionView(self.tab_frame)
        self.tab_frame.add(self.actions, text="Actions")

    def _button_command(self):
        file_path = self.ask_for_path()
        if file_path is None:
            log.debug("No file selected")
            return
        self._load_config(file_path)
        self.app.switch_frame(self)

    def _button_text_and_icon(self) -> Tuple[str, res.DynPyResource]:
        return "Load Config", res.DynPyResource.ICON_LOAD

    def update_view(self, service: IConvertService):
        self.source.update_model(service.sources())
        self.actions.update_model(service.actions())

    def update_service(self, service: IConvertService) -> bool:
        sources = service.update_sources(self.source.get_model())
        actions = service.update_actions(self.actions.get_model())
        return sources or actions


class CreateConvertConfigAppView(ConvertConfigAppView):
    def ask_for_path(self) -> Optional[Path]:
        dir_path = dialog.askdirectory(
            title="Select directory for configuration file",
            initialdir=Path.home(),
        )
        if dir_path is None or dir_path == "":
            return None
        return Path(dir_path)

    def _button_text_and_icon(self) -> Tuple[str, res.DynPyResource]:
        return "Create Config", res.DynPyResource.ICON_CREATE

    def _button_command(self):
        dir_path = self.ask_for_path()
        if dir_path is None:
            log.debug("No dir path selected")
            return
        file_path = self.app.service.create_config(dir_path)
        self._load_config(file_path)
        self.app.switch_frame(self)
