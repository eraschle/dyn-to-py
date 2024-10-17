from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Dict, Iterable, List, Mapping, OrderedDict

from dynpy.core import paths as pth
from dynpy.core import reader
from dynpy.core.actions import ActionType, ConvertAction


@dataclass(frozen=True)
class DynamoNode:
    node_id: str


@dataclass(frozen=True)
class NodeView(DynamoNode):
    name: str


class PythonEngine(str, Enum):
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
            self.node_id,
            self.code_engine,
            pth.path_as_str(self.path),
        )

    @property
    def file_name(self) -> str:
        version = self.code_engine.value[-1]
        return f"{self.node_name}_py{version}_{self.node_id}"

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
    code: str
    info: NodeInfo

    @property
    def dynamo_path(self) -> Path:
        return Path(self.info.path)


@dataclass(frozen=True)
class SourceConfig:
    source_ext: ClassVar[Iterable[str]] = (".dyn", ".dyf")
    export_ext: ClassVar[str] = ".py"
    name: str
    source: str
    export: str

    @property
    def source_path(self) -> Path:
        return Path(self.source)

    @property
    def export_path(self) -> Path:
        return Path(self.export)

    def is_source(self, path: Path) -> bool:
        return path.suffix in self.source_ext

    def source_files(self) -> List[Path]:
        return pth.get_files(self.source_path, self.is_source)

    def is_export(self, path: Path) -> bool:
        return path.suffix == self.export_ext

    def export_files(self) -> List[Path]:
        return pth.get_files(self.export_path, self.is_export)

    def _check_is_source(self, file_path: Path) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} not found")
        if pth.path_as_str(file_path).startswith(self.source):
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

    sources: List[SourceConfig]
    actions: Mapping[ActionType, List[ConvertAction]] = field(default_factory=dict)

    def add_source(self, source: SourceConfig) -> None:
        if source in self.sources:
            return
        self.sources.append(source)

    def update(self, source: SourceConfig) -> None:
        if source not in self.sources:
            return
        index = self.sources.index(source)
        self.sources[index] = source

    def actions_by(self, action: ActionType) -> List[ConvertAction]:
        return self.actions.get(action, [])

    def _action_dict(self, action: ActionType) -> List[Dict[str, Any]]:
        return [act.to_dict() for act in self.actions_by(action)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "configs": [config.to_dict() for config in self.sources],
            "actions": {action: self._action_dict(action) for action in ActionType},
        }

    def source_by(self, name: str) -> SourceConfig:
        for source in self.sources:
            if source.name != name:
                continue
            return source
        raise Exception(f"Source {name} not found in the configuration")

    def save(self, path: Path) -> None:
        reader.write_json(path, OrderedDict(self.to_dict()))
