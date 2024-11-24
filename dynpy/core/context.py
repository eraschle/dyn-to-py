from pathlib import Path
from typing import Any, List, Mapping, MutableMapping, OrderedDict

from dynpy.core import reader
from dynpy.core.models import PythonEngine

KEY_ID = "Id"
KEY_NAME = "Name"
KEY_CODE = "Code"
KEY_ENGINE = "Engine"
KEY_PATH = "Path"
KEY_NODES = "Nodes"
KEY_VIEW = "View"
KEY_NODE_VIEWS = "NodeViews"
KEY_NODE_TYPE = "NodeType"
KEY_ANNOTATIONS = "Annotations"
KEY_CONNECTORS = "Connectors"
KEY_LIBRARY_DEPENDENCIES = "NodeLibraryDependencies"
KEY_DEPENDENCIES_TYPE = "ReferenceType"
PYTHON_NODE_TYPE = "PythonScriptNode"


def is_code_node(content: Mapping[str, Any]) -> bool:
    if KEY_NODE_TYPE not in content:
        return False
    return content[KEY_NODE_TYPE] == PYTHON_NODE_TYPE


def node_uuid(content: Mapping[str, Any]) -> str:
    return content.get(KEY_ID, "NO NODE-ID")


def node_name(content: Mapping[str, Any]) -> str:
    return content.get(KEY_NAME, "NO NODE-NAME")


def node_code(content: Mapping[str, Any]) -> str:
    return content.get(KEY_CODE, "NO CODE")


def node_engine(content: Mapping[str, Any]) -> PythonEngine:
    engine = content.get(KEY_ENGINE, "IronPython2")
    return PythonEngine(engine)


def _dependency_type(content: Mapping[str, Any]) -> str:
    return content.get(KEY_DEPENDENCIES_TYPE, "")


def is_package_dependency(content: Mapping[str, Any]) -> bool:
    return _dependency_type(content) == "Package"


def is_external_dependency(content: Mapping[str, Any]) -> bool:
    return _dependency_type(content) == "External"


class DynamoFileContext:
    def __init__(self, path: Path, save: bool = True):
        self.path = path
        self.save = save
        self.content: OrderedDict = OrderedDict()

    @property
    def nodes(self) -> List[MutableMapping[str, Any]]:
        return self.content.get(KEY_NODES, [])

    @property
    def node_views(self) -> List[Mapping[str, Any]]:
        views = self.content.get(KEY_VIEW, {})
        return views.get(KEY_NODE_VIEWS, [])

    @property
    def views_mapping(self) -> Mapping[str, Mapping[str, Any]]:
        return {node_uuid(view): view for view in self.node_views}

    @property
    def code_nodes(self) -> List[Mapping[str, Any]]:
        return [node for node in self.nodes if is_code_node(node)]

    @property
    def library_dependencies(self) -> List[Mapping[str, Any]]:
        return self.content.get(KEY_LIBRARY_DEPENDENCIES, [])

    @property
    def package_dependencies(self) -> List[Mapping[str, Any]]:
        return [
            dep
            for dep in self.library_dependencies
            if is_package_dependency(dep)
        ]

    @property
    def external_dependencies(self) -> List[Mapping[str, Any]]:
        return [
            dep
            for dep in self.library_dependencies
            if is_external_dependency(dep)
        ]

    @property
    def annotations(self) -> List[Mapping[str, Any]]:
        views = self.content.get(KEY_VIEW, {})
        return views.get(KEY_ANNOTATIONS, [])

    @property
    def connectors(self) -> List[Mapping[str, Any]]:
        return self.content.get(KEY_CONNECTORS, [])

    def index_of(self, node_id: str) -> int:
        for idx, node in enumerate(self.nodes):
            if node_uuid(node) != node_id:
                continue
            return idx
        raise ValueError(f"Node with id {node_id} not found")

    def replace_code(self, node_id: str, code: str) -> None:
        idx = self.index_of(node_id)
        self.nodes[idx][KEY_CODE] = code

    def __enter__(self) -> "DynamoFileContext":
        self.content = reader.read_json(self.path)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if any(exc is not None for exc in (exc_type, exc_value, traceback)):
            raise exc_value
        if not self.save:
            return
        reader.write_json(self.path, self.content)
