from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    OrderedDict,
)

from dynpy.core import paths as pth
from dynpy.core import reader
from dynpy.core.actions import ActionType, AConvertAction


@dataclass(frozen=True)
class DynamoNode:
    node_id: str


@dataclass(frozen=True)
class NodeView(DynamoNode):
    name: str


class PythonEngine(str, Enum):
    @classmethod
    def short(cls, engine: "PythonEngine") -> str:
        return f"py{engine.value[-1]}"

    IRON_PYTHON_2 = "IronPython2"
    IRON_PYTHON_3 = "IronPython3"
    C_PYTHON_3 = "CPython3"


@dataclass(frozen=True)
class CodeNode(DynamoNode):
    code: str
    engine: PythonEngine


@dataclass(frozen=True)
class NodeInfo:
    uuid: str
    engine: PythonEngine
    path: str


@dataclass(frozen=True)
class ContentNode:
    node: CodeNode
    view: NodeView
    path: Path

    @property
    def node_id(self) -> str:
        return self.node.node_id

    @property
    def node_name(self) -> str:
        return pth.clean_name(self.view.name)

    @property
    def code_engine(self) -> PythonEngine:
        return self.node.engine

    @property
    def code(self) -> str:
        return self.node.code

    @property
    def node_info(self) -> NodeInfo:
        return NodeInfo(
            uuid=self.node_id,
            engine=self.code_engine,
            path=pth.path_as_str(self.path),
        )

    @property
    def file_name(self) -> str:
        version = PythonEngine.short(self.code_engine)
        return f"{self.node_name}_{version}_{self.node_id}"

    @property
    def as_dir(self) -> str:
        path = self.path.with_suffix("")
        return pth.clean_name(path.name)

    @property
    def export_path(self) -> Path:
        return self.path.parent / self.as_dir / self.file_name


@dataclass(frozen=True)
class PythonFile:
    path: Path
    code_lines: List[str]
    info: Optional[NodeInfo]

    @property
    def code(self) -> str:
        return "\n".join(self.code_lines)

    @property
    def dynamo_path(self) -> Path:
        if self.info is None:
            raise ValueError("No node info provided")
        return Path(self.info.path)


def _default_exclude_dirs() -> List[str]:
    return [
        "__pycache__",
        ".git",
        ".vscode",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        "dist",
        "build",
        "venv",
        ".venv",
    ]


@dataclass(frozen=True)
class SourceConfig:
    source_ext: ClassVar[Iterable[str]] = (".dyn", ".dyf")
    export_ext: ClassVar[str] = ".py"
    name: str = field(compare=True, hash=True, repr=True)
    source: str = field(compare=True, hash=False, repr=True)
    export: str = field(compare=True, hash=False, repr=True)
    exclude_dirs: List[str] = field(default_factory=_default_exclude_dirs)

    def _is_exclude_dir(self, dir_name: str) -> bool:
        return dir_name in self.exclude_dirs

    def is_exclude(self, path: Path) -> bool:
        return any(self._is_exclude_dir(parent.name) for parent in path.parents)

    @property
    def source_path(self) -> Path:
        return Path(self.source)

    @property
    def export_path(self) -> Path:
        return Path(self.export)

    def is_source(self, path: Path) -> bool:
        if self.is_exclude(path):
            return False
        return path.suffix in self.source_ext

    def source_files(self) -> List[Path]:
        if not self.source_path.exists():
            return []
        return pth.get_files(self.source_path, self.is_source, self.is_exclude)

    def is_export(self, path: Path) -> bool:
        if self.is_exclude(path):
            return False
        return path.suffix == self.export_ext

    def export_files(self) -> List[Path]:
        if not self.export_path.exists():
            return []
        return pth.get_files(self.export_path, self.is_export, self.is_exclude)

    def _is_parent(self, path: Path, parent_path: Path) -> bool:
        if path == parent_path:
            return True
        for parent in path.parents:
            if parent != parent_path:
                continue
            return True
        return False

    def _check_is_source(self, file_path: Path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} not found")
        if self._is_parent(file_path, self.source_path):
            return
        raise Exception(f"{file_path} is not sub path of {self.source}")

    def export_file_path(self, node: ContentNode) -> Path:
        self._check_is_source(node.path)
        path = node.export_path.with_suffix(self.export_ext)
        return pth.replace_path(path, self.source, self.export)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "export": self.export,
        }


@dataclass(frozen=True)
class ConvertConfig:
    extension: ClassVar[str] = "dynpy"

    file_path: Optional[Path]
    sources: List[SourceConfig]
    actions: Dict[ActionType, List[AConvertAction]] = field(
        default_factory=dict
    )

    def add_source(self, source: SourceConfig) -> None:
        if source in self.sources:
            return
        self.sources.append(source)

    def update(self, source: SourceConfig) -> None:
        if source not in self.sources:
            return
        index = self.sources.index(source)
        self.sources[index] = source

    def set_sources(self, sources: List[SourceConfig]) -> None:
        self.sources.clear()
        self.sources.extend(sources)

    def set_actions(
        self, actions: Mapping[ActionType, List[AConvertAction]]
    ) -> None:
        self.actions.clear()
        self.actions.update(actions)

    def actions_by(self, action: ActionType) -> List[AConvertAction]:
        return self.actions.get(action, [])

    def _action_dict(self, action: ActionType) -> List[Dict[str, Any]]:
        return [act.to_dict() for act in self.actions_by(action)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "configs": [config.to_dict() for config in self.sources],
            "actions": {
                action: self._action_dict(action) for action in ActionType
            },
        }

    def source_by(self, name: str) -> SourceConfig:
        for source in self.sources:
            if source.name != name:
                continue
            return source
        raise Exception(f"Source {name} not found in the configuration")

    def can_save(self) -> bool:
        return self.file_path is not None

    def save(self) -> None:
        if self.file_path is None:
            raise ValueError("No file path provided")
        self.save_as(self.file_path)

    def save_as(self, path: Path) -> None:
        reader.write_json(path, OrderedDict(self.to_dict()))
