import logging
import os
import tkinter as tk
from abc import ABC, abstractmethod
from pathlib import Path
from tkinter import ttk
from typing import Callable, Iterable, List, Optional, Tuple

from dynpy import ressources as res
from dynpy.core import factory
from dynpy.core.context import DynamoFileContext
from dynpy.core.convert import ConvertHandler, Direction
from dynpy.core.models import ContentNode, PythonFile, SourceConfig
from dynpy.service import IConvertService, dynamo, python
from dynpy.ui.models.uiargs import UiArgs
from dynpy.ui.models.views import AAppView

log = logging.getLogger(__name__)


def _sub_path_of(file_path: Path, root: Path) -> str:
    path_str = str(file_path.resolve()).removeprefix(str(root.resolve()))
    if path_str.startswith(os.path.sep):
        path_str = path_str.removeprefix(os.path.sep)
    return path_str


class ANodeViewModel[TOther: ANodeViewModel](ABC):
    def __init__(self):
        self.tree_id: str = ""
        self.other_model: Optional[TOther] = None

    @property
    @abstractmethod
    def uuid(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def node_name(self) -> str:
        pass

    @property
    def name(self) -> str:
        return f"{self.node_name} ({self.uuid})"

    @property
    @abstractmethod
    def code(self) -> List[str]:
        pass

    @abstractmethod
    def update_code(self, callback_func: Callable) -> None:
        pass

    def code_hash(self) -> int:
        return hash(tuple(self.code))

    @property
    def tags(self) -> Tuple[str, ...]:
        if self.other_model is None or self.code_hash() == self.other_model.code_hash():
            return ()
        return ("changed",)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ANodeViewModel):
            return False
        return self.name == other.name

    def __lt__(self, other: "ANodeViewModel") -> bool:
        return self.name < other.name


class AFileViewModel[TOther: AFileViewModel, TNode: ANodeViewModel](ABC):
    def __init__(self, path: Path, root: Path):
        self.root = root
        self.path = path
        self.tree_id: str = ""
        self.other_model: Optional[TOther] = None
        self._children: List[TNode] = []

    @property
    def name(self) -> str:
        return _sub_path_of(self.path, self.root)

    @property
    def sub_path(self) -> str:
        path = self.path.with_suffix("")
        return _sub_path_of(path, self.root).lower()

    @property
    def has_children(self) -> bool:
        return len(self.children) > 0

    @property
    def children(self) -> List[TNode]:
        if len(self._children) == 0:
            self._children = sorted(self._create_children())
        return self._children

    def child_by(self, uuid: Optional[str]) -> Optional[TNode]:
        if uuid is None:
            return None
        for child in self.children:
            if child.uuid is None or child.uuid != uuid:
                continue
            return child
        return None

    @abstractmethod
    def _create_children(self) -> List[TNode]:
        pass

    def update_code(self, callback_func: Callable) -> None:
        for child in self.children:
            child.update_code(callback_func)

    def set_other_model(self, other_model: TOther) -> None:
        if self.other_model is not None or other_model.other_model is not None:
            return
        self.other_model = other_model
        other_model.other_model = self
        self.set_other_children()

    def set_other_children(self) -> None:
        if self.other_model is None:
            return
        for child in self.children:
            if child.other_model is not None:
                continue
            other_child = self.other_model.child_by(child.uuid)
            if other_child is None:
                continue
            child.other_model = other_child
            other_child.other_model = child

    @property
    def tags(self) -> Tuple[str, ...]:
        if self.other_model is None:
            return ()
        model_tags = set()
        for child in self.children:
            model_tags.update(child.tags)
        if not self.path.exists():
            model_tags.add("not_exist")
        return tuple(model_tags)

    def __eq__(self, other) -> bool:
        if not isinstance(other, AFileViewModel):
            return False
        return self.sub_path == other.sub_path

    def __lt__(self, other: "AFileViewModel") -> bool:
        return self.sub_path < other.sub_path


class SourceCodeModel(ANodeViewModel["ExportFileModel"]):
    def __init__(self, node: ContentNode):
        super().__init__()
        self.node = node
        self._code_lines: List[str] = []

    @property
    def uuid(self) -> Optional[str]:
        return self.node.node_id

    @property
    def node_name(self) -> str:
        return self.node.view.name

    @property
    def code(self) -> List[str]:
        return self._code_lines

    def update_code(self, callback_func: Callable[[str], List[str]]) -> None:
        self._code_lines = callback_func(self.node.code)


class SourceFileModel(AFileViewModel["ExportDirModel", SourceCodeModel]):
    def __init__(self, path: Path, root: Path):
        super().__init__(path, root)

    def _create_children(self) -> List[SourceCodeModel]:
        with DynamoFileContext(self.path, save=False) as ctx:
            return [SourceCodeModel(node) for node in dynamo.content_nodes(ctx)]

    def update_code(self, callback_func: Callable[[str], List[str]]) -> None:
        super().update_code(callback_func)


class ExportFileModel(ANodeViewModel[SourceCodeModel]):
    def __init__(self, py_file: PythonFile):
        super().__init__()
        self.python = py_file
        self._code_lines: List[str] = []

    @property
    def uuid(self) -> Optional[str]:
        if self.python.info is None:
            return None
        return self.python.info.uuid

    @property
    def node_name(self) -> str:
        return self.python.path.name

    @property
    def code(self) -> List[str]:
        return self._code_lines

    def update_code(self, callback_func: Callable[[List[str]], List[str]]) -> None:
        self._code_lines = callback_func(self.python.code_lines)


class ExportDirModel(AFileViewModel[SourceFileModel, ExportFileModel]):
    def __init__(self, path: Path, root: Path, py_files: Iterable[PythonFile]):
        super().__init__(path, root)
        self.py_files = py_files

    def _create_children(self) -> List[ExportFileModel]:
        return [ExportFileModel(py_file) for py_file in self.py_files]

    def update_code(self, callback_func: Callable[[List[str]], List[str]]) -> None:
        super().update_code(callback_func)


TreeviewEvent = Callable[[Optional[str], Tuple[float, float]], None]


class SourceFileListBox[TFile: AFileViewModel](tk.LabelFrame):
    select_event = "<<TreeviewSelect>>"
    open_event = "<<TreeviewOpen>>"
    close_event = "<<TreeviewClose>>"

    def __init__(self, master: tk.Misc, text: str):
        super().__init__(master=master, text=text)
        args = UiArgs()
        self._select_callback: Optional[TreeviewEvent] = None
        self._open_callback: Optional[TreeviewEvent] = None
        self._close_callback: Optional[TreeviewEvent] = None
        self.view_models: List[TFile] = []
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args())
        self.var_root_path = self.add_root_path_frame(args)
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=1))
        self.tree_files = ttk.Treeview(self)
        self.tree_files.tag_configure('changed', background='orange')
        self.tree_files.tag_configure('not_exist', background='red')
        self.tree_files.grid(cnf=args.grid_args(sticky=tk.NSEW))

    def add_root_path_frame(self, args_frame: UiArgs) -> tk.StringVar:
        frm_root = tk.Frame(self)
        frm_root.grid(cnf=args_frame.grid_args())
        args = args_frame.create(row=0, column=0, sticky=tk.NSEW)
        frm_root.grid_rowconfigure(**args.row_args(weight=0))
        frm_root.grid_columnconfigure(**args.column_args(weight=0, minsize=args.east_min))
        lbl_root = tk.Label(frm_root, text="Root-Path", anchor=tk.W)
        lbl_root.grid(cnf=args.grid_args(sticky=tk.W))
        args.add_column()
        frm_root.grid_columnconfigure(**args.column_args(weight=1))
        var_root_path = tk.StringVar(master=frm_root, value="")
        lbl_path = tk.Label(frm_root, textvariable=var_root_path, anchor=tk.W)
        lbl_path.grid(cnf=args.grid_args(sticky=tk.EW))
        return var_root_path

    def _pause_event(
        self, event: str, callback: Callable[[tk.Event], None], ms_befor_rebind: int = 100
    ):
        self.tree_files.unbind(event)
        self.tree_files.after(ms_befor_rebind, lambda: self.tree_files.bind(event, callback))

    def _other_tree_id(self, event: tk.Event) -> Optional[str]:
        if self.tree_files != event.widget:
            return
        selected = self.tree_files.selection()
        if len(selected) != 1:
            return
        return self.find_other_tree_id_of(selected[0])

    def _select_event(self) -> Callable[[tk.Event], None]:
        def select_event(event: tk.Event):
            if self._select_callback is None:
                return
            tree_id = self._other_tree_id(event)
            scroll = self.tree_files.yview()
            self._select_callback(tree_id, scroll)

        return select_event

    def _close_event(self) -> Callable[[tk.Event], None]:
        def close_event(event: tk.Event):
            if self._close_callback is None:
                return
            view_model = self._other_tree_id(event)
            scroll = self.tree_files.yview()
            self._close_callback(view_model, scroll)

        return close_event

    def _open_event(self) -> Callable[[tk.Event], None]:
        def open_event(event: tk.Event):
            if self._open_callback is None:
                return
            view_model = self._other_tree_id(event)
            scroll = self.tree_files.yview()
            self._open_callback(view_model, scroll)

        return open_event

    def add_select_event(self, callback: TreeviewEvent):
        self._select_callback = callback
        self.tree_files.bind(self.select_event, self._select_event())

    def add_open_event(self, callback: TreeviewEvent):
        self._open_callback = callback
        self.tree_files.bind(self.open_event, self._open_event())

    def add_close_event(self, callback: TreeviewEvent):
        self._close_callback = callback
        self.tree_files.bind(self.close_event, self._close_event())

    def find_other_tree_id_of(self, tree_id: str) -> Optional[str]:
        for view_model in self.view_models:
            if view_model.tree_id == tree_id:
                if view_model.other_model is not None:
                    return view_model.other_model.tree_id
                return None
            for child in view_model.children:
                if child.tree_id == tree_id:
                    if child.other_model is not None:
                        return child.other_model.tree_id
                    return None
        return None

    def select_view_model_by(self, tree_id: str, yscrol: Tuple[float, float]) -> None:
        self._pause_event(self.select_event, self._select_event())
        self.tree_files.selection_set(tree_id)
        self.tree_files.yview_moveto(yscrol[0])

    def open_by_view_model(self, tree_id: str, yscrol: Tuple[float, float]) -> None:
        self._pause_event(self.open_event, self._open_event())
        self.tree_files.item(tree_id, open=True)
        self.tree_files.yview_moveto(yscrol[0])

    def close_by_view_model(self, tree_id: str, yscrol: Tuple[float, float]) -> None:
        self._pause_event(self.close_event, self._close_event())
        self.tree_files.item(tree_id, open=False)
        self.tree_files.yview_moveto(yscrol[0])

    def clean_values(self):
        self.tree_files.delete(*self.tree_files.get_children())

    def add_children(self, view_model: TFile):
        for child in view_model.children:
            tree_id = self.tree_files.insert(
                view_model.tree_id, tk.END, text=child.name, tags=child.tags
            )
            child.tree_id = tree_id

    def add_models(self):
        if len(self.view_models) == 0:
            return
        for idx, view_model in enumerate(self.view_models):
            if idx == 0:
                self.var_root_path.set(str(view_model.root))
            tree_id = self.tree_files.insert("", tk.END, text=view_model.name, tags=view_model.tags)
            view_model.tree_id = tree_id
            self.add_children(view_model)

    def update_children_tags(self, view_model: TFile):
        for child in view_model.children:
            self.tree_files.item(child.tree_id, tags=child.tags)

    def update_tags(self):
        if len(self.view_models) == 0:
            return
        for view_model in self.view_models:
            self.tree_files.item(view_model.tree_id, tags=view_model.tags)
            self.update_children_tags(view_model)

    def update_files(self, models: List[TFile]):
        self.view_models = sorted(models)
        self.clean_values()
        self.add_models()

    def show_files(self):
        self.tree_files.grid()

    def hide_files(self):
        self.tree_files.grid_remove()


ComboBoxEvent = Callable[[tk.Event], Optional[str]]
Command = Callable[[], None]


class ConvertionAppView(AAppView):
    def _init_view(self):
        args = UiArgs()
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args(weight=1))

        frm_convert = tk.Frame(self)
        frm_convert.grid(cnf=args.grid_args(columnspan=2))
        args_src = args.create(row=0, column=0, sticky=tk.NSEW)
        self.cbx_source = self._get_combobox(
            frm_convert, "Source", self._select_source_event, args_src
        )
        args_src.add_column()
        self.cbx_direction = self._get_combobox(
            frm_convert, "Direction", self._direction_select_event, args_src
        )
        self.btn_convert = self._convert_button(frm_convert, self._convert_command, args_src)
        args.add_row()
        self.files_row = args.row
        self.grid_rowconfigure(**args.row_args(weight=1))
        self.lst_source = SourceFileListBox[SourceFileModel](self, "Source Files")
        self.lst_source.add_select_event(self.select_export_by_source)
        self.lst_source.add_open_event(self.open_export_by_source)
        self.lst_source.add_close_event(self.close_export_by_source)
        args.add_column()
        self.grid_columnconfigure(**args.column_args(weight=1))
        self.lst_export = SourceFileListBox[ExportDirModel](self, "Export Files")
        self.lst_export.add_select_event(self.select_source_by_export)
        self.lst_export.add_open_event(self.open_source_by_export)
        self.lst_export.add_close_event(self.close_source_by_export)

    def select_source_by_export(self, export_id: Optional[str], yscrol: Tuple[float, float]):
        if export_id is None:
            return
        self.lst_source.select_view_model_by(export_id, yscrol)

    def select_export_by_source(self, source_id: Optional[str], yscrol: Tuple[float, float]):
        if source_id is None:
            return
        self.lst_export.select_view_model_by(source_id, yscrol)

    def open_source_by_export(self, export_id: Optional[str], yscrol: Tuple[float, float]):
        if export_id is None:
            return
        self.lst_source.open_by_view_model(export_id, yscrol)

    def open_export_by_source(self, source_id: Optional[str], yscrol: Tuple[float, float]):
        if source_id is None:
            return
        self.lst_export.open_by_view_model(source_id, yscrol)

    def close_source_by_export(self, export_id: Optional[str], yscrol: Tuple[float, float]):
        if export_id is None:
            return
        self.lst_source.close_by_view_model(export_id, yscrol)

    def close_export_by_source(self, source_id: Optional[str], yscrol: Tuple[float, float]):
        if source_id is None:
            return
        self.lst_export.close_by_view_model(source_id, yscrol)

    def _get_combobox(
        self, frame: tk.Frame, name: str, callback: ComboBoxEvent, args: UiArgs
    ) -> ttk.Combobox:
        frame.grid_columnconfigure(**args.column_args(weight=0, minsize=args.east_min))
        label = tk.Label(frame, text=name)
        label.grid(cnf=args.grid_args(sticky=tk.W))
        args.add_column()
        frame.grid_columnconfigure(**args.column_args())
        combo_box = ttk.Combobox(frame, state="readonly")
        combo_box.bind("<<ComboboxSelected>>", callback)
        combo_box.grid(cnf=args.grid_args())
        return combo_box

    def _update_source_and_export_files(self):
        name = self.cbx_source.selection_get()
        handler = self.service.convert_handle_by(name)
        self.update_source_files(handler)

    def _select_source_event(self, event: tk.Event) -> Optional[str]:
        if self.cbx_source != event.widget:
            return
        self._update_source_and_export_files()
        self._update_convert_button()
        return "break"

    def _create_source_models(
        self, source: SourceConfig, callback_func: Callable[[str], List[str]]
    ) -> List[SourceFileModel]:
        view_models = []
        for path in source.source_files():
            view_model = SourceFileModel(path, source.source_path)
            if not view_model.has_children:
                continue
            view_model.update_code(callback_func=callback_func)
            view_models.append(view_model)
        return sorted(view_models)

    def _create_export_models(
        self, handler: ConvertHandler, callback_func: Optional[Callable[[List[str]], List[str]]]
    ) -> List[ExportDirModel]:
        view_models = []
        source = handler.source
        group_dyn_files = python.python_file_group(handler)
        for path, children in group_dyn_files.items():
            view_model = ExportDirModel(path, source.export_path, children)
            if not view_model.has_children:
                continue
            if callback_func is not None:
                view_model.update_code(callback_func=callback_func)
            view_models.append(view_model)
        return sorted(view_models)

    def _get_export_model(
        self, source: SourceFileModel, exports: List[ExportDirModel]
    ) -> Optional[ExportDirModel]:
        src_name = source.sub_path
        for export in exports:
            if export.sub_path != src_name:
                continue
            return export
        return None

    def connect_view_models(self, sources: List[SourceFileModel], exports: List[ExportDirModel]):
        for source in sources:
            export = self._get_export_model(source, exports)
            if export is None:
                continue
            source.set_other_model(export)
            exports.remove(export)

    def update_source_files(self, handler: ConvertHandler):
        source_callback = factory.dynamo_to_python_code
        source_models = self._create_source_models(handler.source, source_callback)
        export_models = self._create_export_models(handler, None)
        self.connect_view_models(source_models, export_models)
        self.lst_source.update_files(source_models)
        self.lst_export.update_files(export_models)

    def _update_source_frame(self, direction: Direction):
        if direction == Direction.UNKNOWN:
            self.lst_source.hide_files()
            return
        self.lst_source.show_files()
        column = 0 if direction == Direction.TO_PYTHON else 1
        args = UiArgs(row=self.files_row, column=column, sticky=tk.NSEW)
        self.lst_source.grid(cnf=args.grid_args(sticky=tk.NSEW))
        self.lst_source.update_tags()

    def _update_export_frame(self, direction: Direction):
        if direction == Direction.UNKNOWN:
            self.lst_export.hide_files()
            return
        self.lst_export.show_files()
        column = 1 if direction == Direction.TO_PYTHON else 0
        args = UiArgs(row=self.files_row, column=column, sticky=tk.NSEW)
        self.lst_export.grid(cnf=args.grid_args(sticky=tk.NSEW))
        self.lst_export.update_tags()

    def _update_files_frame(self, direction: Direction):
        self._update_source_frame(direction)
        self._update_export_frame(direction)

    def _direction_select_event(self, event: tk.Event) -> Optional[str]:
        if self.cbx_direction != event.widget:
            return
        selected = self.cbx_direction.selection_get()
        direction = self.service.set_convert_direction(selected)
        self._update_files_frame(direction)
        self._update_convert_button()
        return "break"

    def update_source_and_direction(self, sources: List[SourceConfig]):
        src_names = [src.name for src in sources]
        self.cbx_source.config(values=src_names)
        directions = [dire.value for dire in Direction]
        self.cbx_direction.config(values=directions)
        self.cbx_direction.set(directions[0])

    def _convert_button(self, frame: tk.Frame, command: Command, args: UiArgs) -> tk.Button:
        frame.grid_columnconfigure(**args.column_args(weight=1))
        args.add_column()
        frame.grid_columnconfigure(**args.column_args(weight=0, minsize=args.west_min))
        button = tk.Button(frame, text="Convert", command=command, state=tk.DISABLED)
        button.grid(cnf=args.grid_args())
        return button

    def _update_convert_button(self):
        state = tk.NORMAL if self.service.can_convert else tk.DISABLED
        self.btn_convert.config(state=state)

    def _convert_command(self):
        self.service.convert()
        self._update_source_and_export_files()

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

    def update_view(self, service: IConvertService):
        if not service.config_loaded:
            log.error("No convert handler found")
            return
        self.service = service
        self.update_source_and_direction(service.sources())

    def update_service(self, service: IConvertService) -> None:
        log.info(f"Dont updating service {service}")
