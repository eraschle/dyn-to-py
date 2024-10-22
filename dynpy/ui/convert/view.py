import logging
import tkinter as tk
from tkinter import messagebox as msg
from typing import Callable, Optional, Tuple, Type

from dynpy import resources as res
from dynpy.service import IConvertService
from dynpy.ui.convert.controller import ConvertController
from dynpy.ui.models.uiargs import UiArgs
from dynpy.ui.models.views import AAppView
from dynpy.ui.widget.combobox import ConvertBox, DirectionBox, SourceBox
from dynpy.ui.widget.tree import ModelListBox

log = logging.getLogger(__name__)


ComboBoxEvent = Callable[[tk.Event], Optional[str]]
Command = Callable[[], None]


def _create_box[T: ConvertBox](
    view: "ConvertAppView",
    var_name: tk.StringVar,
    box_type: Type[T],
    args: UiArgs,
) -> T:
    view.frm_menu.grid_columnconfigure(
        **args.column_args(weight=0, minsize=args.east_min),
    )
    label = tk.Label(view.frm_menu, textvariable=var_name)
    label.grid(cnf=args.grid_args(sticky=tk.W))
    args.add_column()
    view.frm_menu.grid_columnconfigure(**args.column_args())
    box = box_type(view.frm_menu, view.controller)
    box.grid(cnf=args.grid_args())
    return box


class ConvertAppView(AAppView):
    def _init_view(self):
        args = UiArgs()
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args(weight=1))
        self.frm_menu = tk.Frame(self)
        self.frm_menu.grid(cnf=args.grid_args(columnspan=2))
        self.controller = ConvertController(self)
        args_src = args.create(row=0, column=0, sticky=tk.NSEW)
        self.cbx_source = self.create_source(args_src)
        args_src.add_column()
        self.cbx_direction = self.create_direction(args_src)
        args_src.add_column()
        self.frm_menu.grid_columnconfigure(
            **args_src.column_args(weight=1, minsize=args_src.east_min)
        )
        self.ckb_show_code = tk.Checkbutton(self.frm_menu)
        self.controller.setup_show_code_button()
        self.ckb_show_code.grid(cnf=args_src.grid_args(sticky=tk.EW))
        self._create_convert_button(args_src)
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=1))
        self.win_paned = self.get_paned_window()
        self.win_paned.grid(cnf=args.grid_args(sticky=tk.NSEW))
        self.controller.setup_diff_tags()
        self.controller.setup_tree_tags()

    def create_source(self, args: UiArgs) -> SourceBox:
        var_name = self.controller.var_source_text
        return _create_box(self, var_name, SourceBox, args)

    def create_direction(self, args: UiArgs) -> DirectionBox:
        var_name = self.controller.var_direction_text
        return _create_box(self, var_name, DirectionBox, args)

    def get_paned_window(self) -> tk.PanedWindow:
        args = UiArgs()
        paned = tk.PanedWindow(self, orient=tk.VERTICAL, showhandle=True)
        paned.grid_rowconfigure(**args.row_args(weight=1))
        paned.grid_columnconfigure(**args.column_args(weight=1))
        self.lst_files = ModelListBox(controller=self.controller, text="Files")
        paned.add(self.lst_files)
        self.txt_diff = tk.Text(wrap=tk.WORD)
        return paned

    def _create_convert_button(self, args: UiArgs):
        args.add_column()
        self.frm_menu.grid_columnconfigure(
            **args.column_args(weight=1),
        )
        args.add_column()
        col_config = args.column_args(weight=0, minsize=args.east_min)
        self.frm_menu.grid_columnconfigure(**col_config)
        self.btn_convert = tk.Button(
            self.frm_menu,
            state=tk.DISABLED,
            text="Convert",
            command=self.controller.convert_command,
        )
        self.btn_convert.grid(cnf=args.grid_args())

    def _button_command(self):
        if not self.app.service.config_loaded:
            file_path = self.ask_for_path()
            if file_path is None:
                log.info("No file path selected")
                return
            self._load_config(file_path)
        self.app.switch_frame(self)

    def _button_text_and_icon(self) -> Tuple[str, res.DynPyResource]:
        return "Convert", res.DynPyResource.ICON_CONVERT

    def update_view(self):
        if not self.app.service.config_loaded:
            log.error("No convert configuration loaded")
            msg.showerror("Error", "No convert configuration loaded")
            return
        self.cbx_source.reset()
        self.cbx_direction.reset()

    def update_service(self, service: IConvertService) -> bool:
        log.info(f"Don't updating service {service}")
        return False
