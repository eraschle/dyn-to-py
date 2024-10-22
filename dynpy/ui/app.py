import logging
import tkinter as tk
from typing import List, Optional

from dynpy import resources as res
from dynpy.service import IConvertService
from dynpy.ui.convert.view import ConvertAppView
from dynpy.ui.models.config import (
    ConvertConfigAppView,
    CreateConvertConfigAppView,
)
from dynpy.ui.models.uiargs import UiArgs
from dynpy.ui.models.views import AAppView

log = logging.getLogger(__name__)


class ConvertMenuFrame(tk.Frame):
    def __init__(self, master: tk.Misc, views: List[AAppView]):
        super().__init__(master)
        args = UiArgs(sticky=tk.NSEW)
        minsize = 200
        self.grid_columnconfigure(**args.column_args(weight=1))
        self.grid_rowconfigure(**args.row_args(weight=1))
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=0, minsize=minsize))
        self._add_button_row(views, args, minsize)
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=1))

    def _add_button_row(self, views: List[AAppView], args: UiArgs, minsize: int = 200):
        for view in views:
            args.add_column()
            self.grid_columnconfigure(**args.column_args(weight=0, minsize=minsize))
            button = view.button(self)
            button.grid(cnf=args.grid_args(sticky=tk.NSEW))
        args.add_column()
        self.grid_columnconfigure(**args.column_args(weight=1))


class DynPyAppView(tk.Tk):
    def __init__(self, service: IConvertService) -> None:
        super().__init__()
        args = UiArgs(sticky=tk.NSEW)
        self.service = service
        self.current_view: Optional[AAppView] = None
        self.grid_columnconfigure(**args.column_args())
        self.grid_rowconfigure(**args.row_args())
        app_views = [
            ConvertAppView(self),
            ConvertConfigAppView(self),
            CreateConvertConfigAppView(self),
        ]
        self.frm_load = ConvertMenuFrame(self, app_views)
        self.frm_load.grid(cnf=args.grid_args())
        self.setup_ui()

    def _screen_center_x(self, width: float) -> int:
        screen_width = self.winfo_screenwidth()
        return int((screen_width / 2) - (width / 2))

    def _screen_center_y(self, height: float) -> int:
        screen_height = self.winfo_screenheight()
        return int((screen_height / 2) - (height / 2))

    def center_on_screen(self, width: float = 900, height: float = 800):
        x_center = self._screen_center_x(width)
        y_center = self._screen_center_y(height)
        geometry = f"{width}x{height}+{x_center}+{y_center}"
        self.geometry(geometry)

    def update_service(self, view: AAppView) -> bool:
        if not view.update_service(self.service):
            return False
        return self.service.can_save_config

    def switch_frame(self, view: AAppView):
        if self.current_view is None:
            self.frm_load.grid_forget()
        else:
            if self.update_service(self.current_view):
                self.service.config_save()
            self.current_view.hide()
        self.current_view = view
        self.current_view.update_view()
        self.current_view.show(UiArgs(sticky=tk.NSEW))

    def setup_ui(self):
        icon_path = res.icon_path(res.DynPyResource.ICON_APP)
        self.iconphoto(True, tk.PhotoImage(file=icon_path))
        self.title("Dynamo <-> Python Convert")
