from dataclasses import asdict
from functools import cache
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Type

from dynpy.core import context as ctx
from dynpy.core import reader
from dynpy.core.actions import (
    ActionType,
    ConvertAction,
    RemoveLineAction,
    TypeIgnoreAction,
)
from dynpy.core.models import (
    CodeNode,
    ContentNode,
    ConvertConfig,
    ConvertHandler,
    NodeInfo,
    NodeView,
    PythonEngine,
    PythonFile,
    SourceConfig,
)


def source_config(content: Mapping[str, Any]) -> SourceConfig:
    return SourceConfig(
        name=content["name"],
        source=content["source"],
        export=content["export"],
    )


def _create_sources(content: Iterable[Mapping[str, Any]]) -> List[SourceConfig]:
    return [source_config(source) for source in content]


def _get_action(action_type: ActionType) -> Type[ConvertAction]:
    return TypeIgnoreAction if action_type == ActionType.REPLACE else RemoveLineAction


def _get_actions(
    action_type: ActionType, content: Iterable[Mapping[str, Any]]
) -> List[ConvertAction]:
    return [_get_action(action_type)(**act) for act in content]


def _create_actions(action_content: Mapping[str, Any]) -> Mapping[ActionType, List[ConvertAction]]:
    actions = {}
    for action, content in action_content.items():
        action_type = ActionType(action)
        actions[action_type] = _get_actions(action_type, content)
    return actions


def convert_config(path: Path) -> ConvertConfig:
    content = reader.read_json(path.resolve())
    return ConvertConfig(
        configs=_create_sources(content["configs"]),
        actions=_create_actions(content["actions"]),
    )


def _default_remove_action() -> RemoveLineAction:
    return RemoveLineAction(
        contains=[
            "# Load the Python Standard",
            "Phython-Standard- und DesignScript-Bibliotheken laden",
            "# The inputs to this node will be stored",
            "Die Eingaben für diesen Block werden in Form einer Liste in den IN-Variablen gespeichert.",
            "dataEnteringNode = IN",
            "Assign your output to the OUT variable.",
            "Weisen Sie Ihre Ausgabe der OUT-Variablen zu.",
        ]
    )


def _default_type_ignore_action() -> TypeIgnoreAction:
    return TypeIgnoreAction(
        value="# type: ignore",
        contains=[
            "clr.ImportExtensions(Revit.Elements)",
            "clr.ImportExtensions(Revit.GeometryConversion)",
            "Application.DocumentManager.MdiActiveDocument",
            "TransactionManager.Instance.",
            "InvalidOperationException:" "LabelUtils.GetLabelFor",
            "basestring",
        ],
        regex=[],
    )


def default_convert_config() -> ConvertConfig:
    config = ConvertConfig(
        configs=[
            SourceConfig(
                name="<SOURCE_NAME>",
                source="<SOURCE_PATH>",
                export="<EXPORT_PATH>",
            )
        ],
        actions={
            ActionType.DELETE_: [
                _default_remove_action(),
            ],
            ActionType.REPLACE: [
                _default_type_ignore_action(),
            ],
        },
    )
    return config


def code_node(node: Mapping[str, Any]) -> CodeNode:
    return CodeNode(
        node_id=ctx.node_uuid(node),
        code=ctx.node_code(node),
        engine=ctx.node_engine(node),
    )


def node_view(view: Mapping[str, Any]) -> NodeView:
    return NodeView(
        node_id=ctx.node_uuid(view),
        name=ctx.node_name(view),
    )


def content_node(node: CodeNode, view: Mapping[str, Any], path: Path) -> ContentNode:
    return ContentNode(
        node=node,
        view=node_view(view),
        path=path,
    )


@cache
def _py_engine() -> List[str]:
    return [eng.value for eng in PythonEngine]


def _is_engine(key: str, value: Any) -> bool:
    if key != "engine" or value not in _py_engine():
        return False
    return True


def _info_value(key: str, value: Any) -> Any:
    if not _is_engine(key, value):
        return value
    return PythonEngine(value)


_INFO_PREFIX: str = "# -*-"
_INFO_SEPARATOR: str = ";"


def node_info(node_info: str) -> NodeInfo:
    node_info = node_info.replace(_INFO_PREFIX, "")
    infos = node_info.split(_INFO_SEPARATOR)
    infos = [value.split(":") for value in infos]
    info_dict: Mapping[str, Any] = {key.strip(): value.strip() for key, value in infos}
    info_dict = {key: _info_value(key, value) for key, value in info_dict.items()}
    return NodeInfo(**info_dict)


def _info_as_str(info: NodeInfo) -> str:
    infos = [f"{key}: {value}" for key, value in asdict(info).items()]
    info_str = f"{_INFO_SEPARATOR} ".join(infos)
    return f"{_INFO_PREFIX} {info_str}"


def code_to_python(node: ContentNode, handler: ConvertHandler) -> List[str]:
    code_lines = node.code.splitlines(keepends=False)
    code_lines = handler.apply_action(code_lines)
    lines = [_info_as_str(node.node_info), "", ""]
    lines.extend(code_lines)
    return lines


def code_to_dynamo(lines: List[str], handler: ConvertHandler) -> str:
    lines = handler.apply_action(lines)
    return "\n".join(lines)


def python_file(path: Path, handler: ConvertHandler) -> PythonFile:
    code_lines = reader.read_python(path)
    return PythonFile(
        path=path,
        info=node_info(code_lines[0]),
        code=code_to_dynamo(code_lines[1:], handler),
    )
