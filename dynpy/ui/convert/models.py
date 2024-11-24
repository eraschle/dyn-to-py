import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

from dynpy.core.context import DynamoFileContext
from dynpy.core.models import ContentNode, PythonEngine, PythonFile
from dynpy.service import dynamo

log = logging.getLogger(__name__)


def _sub_path_of(file_path: Path, root: Path) -> str:
    path_str = str(file_path.resolve()).removeprefix(str(root.resolve()))
    if path_str.startswith(os.path.sep):
        path_str = path_str.removeprefix(os.path.sep)
    return path_str


def _number(number: int) -> str:
    return f"{number:>4}"


class ATreeViewModel(ABC):
    def __init__(self):
        self.tree_id: str = ""
        self._tooltip: Optional[str] = None

    @property
    def tooltip(self) -> str:
        if self._tooltip is None:
            lines = self._create_tooltip()
            self._tooltip = "---" if len(lines) == 0 else "\n".join(lines)
        return self._tooltip

    @abstractmethod
    def _create_tooltip(self) -> List[str]:
        pass


class ANodeViewModel(ATreeViewModel):
    def __init__(self, source_name: str):
        super().__init__()
        self.source_name = source_name
        self.other_node: Optional[ANodeViewModel] = None
        self._code_hash: Optional[int] = None

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

    @property
    def file_and_code(self) -> Tuple[str, List[str]]:
        return self.source_name, self.code

    @abstractmethod
    def update_code(self, func: Callable) -> None:
        pass

    def same_code(self) -> bool:
        if self.other_node is None:
            return False
        return self.code_hash() == self.other_node.code_hash()

    def code_hash(self) -> int:
        if self._code_hash is None:
            self._code_hash = hash(tuple(self.code))
        return self._code_hash

    def __eq__(self, other) -> bool:
        if not isinstance(other, ANodeViewModel):
            return False
        return self.uuid == other.uuid

    def __lt__(self, other: "ANodeViewModel") -> bool:
        return self.name < other.name

    def __str__(self) -> str:
        return f"{self.source_name}: {self.name} ({self.uuid}))"


class AFileViewModel(ATreeViewModel):
    def __init__(self, path: Path, root: Path):
        super().__init__()
        self.root = root
        self.path = path
        self.other_model: Optional[AFileViewModel] = None
        self._children: List[ANodeViewModel] = []

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
    def children(self) -> List[ANodeViewModel]:
        if len(self._children) == 0:
            self._children = sorted(self._create_children())
        return self._children

    def child_by(self, uuid: Optional[str]) -> Optional[ANodeViewModel]:
        if uuid is None:
            return None
        for child in self.children:
            if child.uuid is None or child.uuid != uuid:
                continue
            return child
        return None

    @abstractmethod
    def _create_children(self) -> List[ANodeViewModel]:
        pass

    def update_code(self, func: Callable) -> None:
        for child in self.children:
            child.update_code(func)

    def connect_with(self, other_model: "AFileViewModel") -> None:
        if self.other_model is not None or other_model.other_model is not None:
            return
        self.other_model = other_model
        other_model.other_model = self
        self._set_other_children()

    def _set_other_children(self) -> None:
        if self.other_model is None:
            return
        for child in self.children:
            if child.other_node is not None:
                continue
            other = self.other_model.child_by(child.uuid)
            if other is None:
                continue
            child.other_node = other
            other.other_node = child

    def __eq__(self, other) -> bool:
        if not isinstance(other, AFileViewModel):
            return False
        return self.sub_path == other.sub_path

    def __lt__(self, other: "AFileViewModel") -> bool:
        return self.sub_path < other.sub_path

    def __str__(self) -> str:
        return f"{self.name} ({self.sub_path})"


class SourceCodeModel(ANodeViewModel):
    def __init__(self, node: ContentNode, source_name: str = "Dynamo Node"):
        super().__init__(source_name)
        self.node = node
        self._code_lines = []

    def _create_tooltip(self) -> List[str]:
        lines = ["Dynamo Python Node:"]
        lines.append(f"- UUID: {self.uuid}")
        lines.append(f"- Node Name: {self.node_name}")
        lines.append(f"- Lines: {len(self.code)}")
        return lines

    @property
    def uuid(self) -> Optional[str]:
        return self.node.node_id

    @property
    def node_name(self) -> str:
        return self.node.view.name

    @property
    def code(self) -> List[str]:
        return self._code_lines

    def update_code(self, func: Callable[[str], List[str]]) -> None:
        lines = func(self.node.code)
        self._code_lines = [f"{line}\n" for line in lines]


class SourceFileModel(AFileViewModel):
    def __init__(self, path: Path, root: Path):
        super().__init__(path, root)

    def _create_children(self) -> List[ANodeViewModel]:
        with DynamoFileContext(self.path, save=False) as ctx:
            return [SourceCodeModel(node) for node in dynamo.content_nodes(ctx)]

    def update_code(self, func: Callable[[str], List[str]]) -> None:
        super().update_code(func)

    def _create_tooltip(self) -> List[str]:
        with DynamoFileContext(self.path, save=False) as ctx:
            code_nodes = len(ctx.code_nodes)
            not_code_nodes = len(ctx.nodes) - code_nodes
            lines = ["Dynamo File Overview:"]
            lines.append("Nodes / Annotations:")
            lines.append(f"- {_number(code_nodes)} Python Nodes")
            lines.append(f"- {_number(not_code_nodes)} Other Nodes")
            lines.append(f"- {_number(len(ctx.annotations))} Annotations")
            lines.append(f"- {_number(len(ctx.connectors))} Connectors")
            if len(ctx.library_dependencies) > 0:
                lines.append("Dependencies:")
                if len(ctx.package_dependencies) > 0:
                    lines.append(
                        f"- {_number(len(ctx.package_dependencies))} Package Dependencies"
                    )
                if len(ctx.external_dependencies) > 0:
                    lines.append(
                        f"- {_number(len(ctx.external_dependencies))} External Dependencies"
                    )
            return lines


class ExportFileModel(ANodeViewModel):
    def __init__(self, py_file: PythonFile, source_name: str = "Python File"):
        super().__init__(source_name)
        self.python = py_file
        self._code_lines = [f"{line}\n" for line in self.python.code_lines]

    @property
    def uuid(self) -> Optional[str]:
        if self.python.info is None:
            return None
        return self.python.info.uuid

    @property
    def node_name(self) -> str:
        if self.python.info is None:
            return self.python.path.name
        info = self.python.info
        py_version = PythonEngine.short(info.engine)
        idx = self.python.path.name.find(py_version)
        name = self.python.path.name[:idx]
        return name.removesuffix("_")

    @property
    def code(self) -> List[str]:
        return self._code_lines

    def _create_tooltip(self) -> List[str]:
        lines = ["Python Code File:"]
        info = self.python.info
        if info is not None:
            lines.append(f"- UUID: {info.uuid}")
            lines.append(f"- Node Name: {self.node_name}")
            lines.append(f"- Engine: {info.engine}")
        lines.append(f"- Code Lines: {len(self.code)}")
        lines.append(f"- Python Path: {self.python.path}")
        lines.append(f"- Dynamo Path: {self.python.dynamo_path}")
        return lines

    def update_code(self, func: Callable[[List[str]], List[str]]) -> None:
        raise NotImplementedError(
            f"ExportFileModel does not support update_code with {func}"
        )


class ExportDirModel(AFileViewModel):
    def __init__(self, path: Path, root: Path, py_files: Sequence[PythonFile]):
        super().__init__(path, root)
        self.py_files = py_files

    def _create_children(self) -> List[ANodeViewModel]:
        return [ExportFileModel(py_file) for py_file in self.py_files]

    def _create_tooltip(self) -> List[str]:
        lines = ["Dynamo Python Code Directory:"]
        lines.append(f"- Directory Path: {self.path}")
        if len(self.py_files) > 0 and self.py_files[0].info is not None:
            dyn_path = self.py_files[0].info.path
            lines.append(f"- Dynamo Path: {dyn_path}")
        lines.append(f"- Code Files: {len(self.children)} ")
        code_lines = sum([len(child.code) for child in self.children])
        lines.append(f"- Code Lines: {code_lines}")
        return lines

    def update_code(self, func: Callable[[List[str]], List[str]]) -> None:
        raise NotImplementedError(
            f"ExportDirModel does not support update_code with {func}"
        )
