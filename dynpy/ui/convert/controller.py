import logging
import tkinter as tk
from tkinter import font as tkf
from enum import Enum
from typing import TYPE_CHECKING, Iterable, List, Optional, OrderedDict, Tuple

from dynpy.core import factory
from dynpy.core.handler import ConvertHandler, Direction
from dynpy.core.models import SourceConfig
from dynpy.service import python
from dynpy.ui.convert.models import (
    AFileViewModel,
    ANodeViewModel,
    ExportDirModel,
    SourceFileModel,
)

if TYPE_CHECKING:
    from dynpy.ui.convert.view import ConvertAppView

log = logging.getLogger(__name__)


class Tag(str, Enum):
    EQUAL = "equal"
    CHANGED = "changed"
    NOT_EXIST = "not_exist"
    ORPHAN = "orphan"
    MULTIPLE = "multiple"
    ADDED = "added"
    REMOVED = "removed"


class TagController:
    def __init__(self, font: Optional[tkf.Font] = None):
        font = tkf.nametofont("TkDefaultFont") if font is None else font
        self.font = font
        self._tags_map = {}

    def add_tag(self, tag: Tag, **kwargs):
        self._tags_map[tag] = kwargs

    def tags(self, *tags: Tag) -> List[Tuple[str, dict]]:
        return [(t.value, self._tags_map[t]) for t in tags]


def _create_tag_controller(default: tkf.Font) -> TagController:
    controller = TagController()
    controller.add_tag(
        Tag.CHANGED,
        foreground="orange red",
    )
    controller.add_tag(
        Tag.NOT_EXIST,
        foreground="yellow",
        background="red",
    )
    controller.add_tag(
        Tag.ORPHAN,
        foreground="red",
    )
    controller.add_tag(
        Tag.MULTIPLE,
        foreground="red",
        font=(default["family"], default["size"], tkf.ITALIC),
    )
    controller.add_tag(
        Tag.ADDED,
        foreground="green",
        font=("monospace", 10),
    )
    controller.add_tag(
        Tag.REMOVED,
        foreground="red",
        font=("monospace", 10),
    )
    return controller


class ConvertController:
    exclude_diff_line = ["@"]
    show_diff = "Show Diff?"
    hide_diff = "Hide Diff?"

    direction_map = OrderedDict(
        {
            "-": Direction.UNKNOWN,
            "Dynamo to Python": Direction.TO_PYTHON,
            "Python to Dynamo": Direction.TO_DYNAMO,
        }
    )

    def __init__(self, view: "ConvertAppView"):
        self.view = view
        self.tags_ctrl = _create_tag_controller(tkf.nametofont("TkDefaultFont"))
        self.service = view.app.service
        self.current_handler: Optional[ConvertHandler] = None
        self.dyn_models: List[AFileViewModel] = []
        self.py_models: List[AFileViewModel] = []
        self.view_models: List[AFileViewModel] = []

        self.var_source_text = tk.StringVar(
            master=view.frm_menu, value="Source-Config:"
        )
        self.var_direction_text = tk.StringVar(
            master=view.frm_menu, value="Convert Direction:"
        )
        self.var_diff_text = tk.StringVar(
            master=view.frm_menu, value=self.show_diff
        )
        self.var_show_diff = tk.BooleanVar(master=view.frm_menu, value=False)

    def clean_code_diff(self):
        self.view.txt_diff.delete("0.0", tk.END)

    def _exclude_diff_line(self, line: str) -> bool:
        for exclude in self.exclude_diff_line:
            if line.startswith(exclude):
                return True
        return False

    def _show_code_diff(self, code_diff_lines: Iterable[str]):
        self.clean_code_diff()
        for line in code_diff_lines:
            if self._exclude_diff_line(line):
                continue
            line = line.replace("\t", "    ")
            if line.startswith("+"):
                self.view.txt_diff.insert(tk.END, line, (Tag.ADDED))
            elif line.startswith("-"):
                self.view.txt_diff.insert(tk.END, line, (Tag.REMOVED))
            else:
                self.view.txt_diff.insert(tk.END, line)

    def setup_diff_tags(self):
        for tag, config in self.tags_ctrl.tags(Tag.ADDED, Tag.REMOVED):
            self.view.txt_diff.tag_config(tag, **config)

    def show_code_diff(self, source: Optional[ANodeViewModel]) -> None:
        if source is None or source.other_node is None:
            return
        code_diff = self.service.code_diff(
            source=source.file_and_code,
            other=source.other_node.file_and_code,
        )
        self._show_code_diff(code_diff)

    def show_diff_command(self):
        if self.var_show_diff.get():
            selected = self.view.lst_files.selected_code_node()
            self.show_code_diff(selected)
            self.var_diff_text.set(self.hide_diff)
            self.view.win_paned.add(self.view.txt_diff)
        else:
            self.var_diff_text.set(self.show_diff)
            self.view.win_paned.remove(self.view.txt_diff)

    def setup_show_code_button(self):
        self.view.ckb_show_code.config(
            textvariable=self.var_diff_text,
            command=self.show_diff_command,
            variable=self.var_show_diff,
        )

    def setup_tree_tags(self):
        tags = (Tag.CHANGED, Tag.NOT_EXIST, Tag.ORPHAN, Tag.MULTIPLE)
        for tag, config in self.tags_ctrl.tags(*tags):
            self.view.lst_files.tree_files.tag_configure(tag, **config)

    def _node_tags_for(self, view_model: ANodeViewModel) -> Tuple[Tag, ...]:
        if view_model.other_node is None:
            return (Tag.ORPHAN,)
        if view_model.same_code():
            return (Tag.EQUAL,)
        return (Tag.CHANGED,)

    def node_tags_for(self, view_model: ANodeViewModel) -> Tuple[str, ...]:
        return tuple([t.value for t in self._node_tags_for(view_model)])

    def model_tags_for(self, view_model: AFileViewModel) -> Tuple[str, ...]:
        tags = set()
        if view_model.other_model is None:
            tags.add(Tag.ORPHAN)
        if not view_model.path.exists():
            tags.add(Tag.NOT_EXIST)
        for child in view_model.children:
            tags.update(self._node_tags_for(child))
        if len(tags) > 1:
            tags = (Tag.MULTIPLE,)
        return tuple([t.value for t in tags])

    def on_tree_select(self, event: tk.Event):
        if event.widget != self.view.lst_files.tree_files:
            return
        selected = self.view.lst_files.selected_code_node()
        self.show_code_diff(selected)

    def get_source_models(self, source: SourceConfig) -> List[AFileViewModel]:
        source_callback = factory.dynamo_to_python_code
        view_models = []
        for path in source.source_files():
            view_model = SourceFileModel(path, source.source_path)
            if not view_model.has_children:
                continue
            view_model.update_code(func=source_callback)
            view_models.append(view_model)
        return sorted(view_models)

    def get_export_models(
        self, handler: ConvertHandler
    ) -> List[AFileViewModel]:
        view_models = []
        source = handler.source
        group_dyn_files = python.python_file_group(handler)
        for path, children in group_dyn_files.items():
            view_model = ExportDirModel(path, source.export_path, children)
            if not view_model.has_children:
                continue
            view_models.append(view_model)
        return sorted(view_models)

    def _connected_model(
        self, source: AFileViewModel, exports: List[AFileViewModel]
    ) -> Optional[AFileViewModel]:
        src_name = source.sub_path
        for export in exports:
            if export.sub_path != src_name:
                continue
            return export
        return None

    def _connect_models(self):
        not_connected = list(self.py_models)
        for source in self.dyn_models:
            export = self._connected_model(source, not_connected)
            if export is None:
                continue
            source.connect_with(export)
            not_connected.remove(export)
        log.debug(f"not connected files: {not_connected}")

    def create_source_and_export(self) -> None:
        if self.current_handler is None:
            return
        self.dyn_models = self.get_source_models(self.current_handler.source)
        self.py_models = self.get_export_models(self.current_handler)
        self._connect_models()

    def source_configs(self) -> List[str]:
        return [src.name for src in self.service.sources()]

    def select_source_config(self, selected: str):
        self.current_handler = self.service.convert_handle_by(selected)
        self.create_source_and_export()
        self._update_view()

    def _update_view(self):
        state = tk.DISABLED
        title = "Select source config and direction"
        view_models = []
        if self.service.can_convert:
            state = tk.NORMAL
            if self.service.direction == Direction.TO_PYTHON:
                title = "Dynamo Files"
                view_models = self.dyn_models
            else:
                title = "Python Files"
                view_models = self.py_models
        self.view_models = view_models
        self.view.lst_files.text = title
        self.view.lst_files.update_files()
        self.view.btn_convert.config(state=state)

    def convert_command(self):
        self.service.convert()
        if self.service.source_name is None:
            return
        self.select_source_config(self.service.source_name)

    def direction_values(self) -> List[str]:
        return list(self.direction_map.keys())

    def select_direction(self, selected: str):
        direction = self.direction_map.get(selected, Direction.UNKNOWN)
        if direction == Direction.UNKNOWN:
            self.view.lst_files.clean_values()
            return
        if self.service.direction == direction:
            return
        other_model = self.view.lst_files.selected_other_view_models()
        self.service.direction = direction
        self._update_view()
        self.view.lst_files.select_model(other_model)
