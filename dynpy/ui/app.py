import tkinter as tk
from typing import List, Optional

from dynpy import ressources as res
from dynpy.service import IConvertService
from dynpy.ui.models.config import ConvertConfigAppView, CreateConvertConfigAppView
from dynpy.ui.models.convert import ConvertionAppView
from dynpy.ui.models.uiargs import UiArgs
from dynpy.ui.models.views import AAppView


class ConverMenuFrame(tk.Frame):
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


class ConvertAppView(tk.Tk):
    def __init__(self, service: IConvertService) -> None:
        super().__init__()
        self.service = service
        self.current_view: Optional[AAppView] = None
        args = UiArgs(sticky=tk.NSEW)
        self.grid_columnconfigure(**args.column_args())
        self.grid_rowconfigure(**args.row_args())
        app_views = [
            ConvertionAppView(self),
            ConvertConfigAppView(self),
            CreateConvertConfigAppView(self),
        ]
        self.frm_load = ConverMenuFrame(self, app_views)
        self.frm_load.grid(cnf=args.grid_args())
        self.setup_ui()

    def switch_frame(self, view: AAppView):
        if self.current_view is None:
            self.frm_load.grid_forget()
        else:
            self.current_view.update_service(self.service)
            self.current_view.hide()
        self.current_view = view
        self.current_view.update_view(self.service)
        self.current_view.show(UiArgs(sticky=tk.NSEW))

    def setup_ui(self):
        icon_path = res.icon_path(res.DynPyResource.ICON_APP)
        self.iconphoto(True, tk.PhotoImage(file=icon_path))
        self.title("Dynamo <-> Python Convert")
