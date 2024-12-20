import logging
from functools import cache
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Type

from dynpy.core import context as ctx
from dynpy.core import reader
from dynpy.core.actions import (
    ActionType,
    AConvertAction,
    RemoveConvertAction,
    ReplaceConvertAction,
)
from dynpy.core.models import (
    CodeNode,
    ContentNode,
    ConvertConfig,
    NodeInfo,
    NodeView,
    PythonEngine,
    PythonFile,
    SourceConfig,
)

log = logging.getLogger(__name__)


def source_config(content: Mapping[str, Any]) -> SourceConfig:
    return SourceConfig(
        name=content["name"],
        source=content["source"],
        export=content["export"],
    )


def _create_sources(content: Iterable[Mapping[str, Any]]) -> List[SourceConfig]:
    return [source_config(source) for source in content]


def _get_action(action_type: ActionType) -> Type[AConvertAction]:
    return (
        ReplaceConvertAction
        if action_type == ActionType.REPLACE
        else RemoveConvertAction
    )


def _get_actions(
    action_type: ActionType, content: Iterable[Mapping[str, Any]]
) -> List[AConvertAction]:
    return [_get_action(action_type)(**act) for act in content]


def _create_actions(
    action_content: Mapping[str, Any],
) -> Dict[ActionType, List[AConvertAction]]:
    actions = {}
    for action, content in action_content.items():
        action_type = ActionType(action)
        actions[action_type] = _get_actions(action_type, content)
    return actions


def convert_config(path: Path) -> ConvertConfig:
    content = reader.read_json(path.resolve())
    return ConvertConfig(
        file_path=path,
        sources=_create_sources(content["configs"]),
        actions=_create_actions(content["actions"]),
    )


def default_remove_action() -> RemoveConvertAction:
    return RemoveConvertAction(
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


def default_type_ignore_action() -> ReplaceConvertAction:
    return ReplaceConvertAction(
        value="# type: ignore",
        contains=[
            "clr.ImportExtensions(Revit.Elements)",
            "clr.ImportExtensions(Revit.GeometryConversion)",
            "Application.DocumentManager.MdiActiveDocument",
            "TransactionManager.Instance.",
            "InvalidOperationException:" "LabelUtils.GetLabelFor",
            "basestring",
        ],
        regex=[
            "^from System import [a-zA-Z]+",
            "[^a-zA-Z0-9]+IN\\[\\d*\\]",
            "[^a-zA-Z0-9]+UnwrapElement\\([a-zA-Z]+.*\\)",
        ],
    )


def default_convert_config() -> ConvertConfig:
    config = ConvertConfig(
        file_path=None,
        sources=[
            SourceConfig(
                name="<SOURCE_NAME>",
                source="<SOURCE_PATH>",
                export="<EXPORT_PATH>",
            )
        ],
        actions={
            ActionType.REMOVE: [
                default_remove_action(),
            ],
            ActionType.REPLACE: [
                default_type_ignore_action(),
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


def content_node(
    node: CodeNode, view: Mapping[str, Any], path: Path
) -> ContentNode:
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


def _info_key(key: str) -> str:
    return key.strip().removeprefix("node-")


def _repair_path(info: List[str]) -> List[str]:
    if len(info) != 3:
        return info
    return [info[0], f"{info[1]}:{info[2]}"]


def _trim_values(info: List[str]) -> List[str]:
    return [value.strip() for value in info]


_INFO_PREFIX: str = "# -*-"
_INFO_SUFFIX: str = "-*-"
_INFO_SEPARATOR: str = ";"


def node_info(node_info: str) -> Optional[NodeInfo]:
    if not node_info.startswith(_INFO_PREFIX):
        log.error(
            f"Invalid NodeInfo > does not start with {_INFO_PREFIX}: {node_info}"
        )
        return None
    node_info = node_info.removeprefix(_INFO_PREFIX).strip()
    node_info = node_info.replace("\"", "")
    if _INFO_SUFFIX in node_info:
        node_info = node_info.removesuffix(_INFO_SUFFIX).strip()
    infos = node_info.split(_INFO_SEPARATOR)
    infos = [value.split(":") for value in infos]
    infos = [_trim_values(info) for info in infos]
    infos = [_repair_path(info) for info in infos]
    infos = [info for info in infos if len(info) == 2]
    info_dict: Mapping[str, Any] = {
        _info_key(key): value.strip() for key, value in infos
    }
    info_dict = {
        key: _info_value(key, value) for key, value in info_dict.items()
    }
    try:
        return NodeInfo(**info_dict)
    except TypeError:
        log.error(f"Invalid NodeInfo: {node_info}", exc_info=True)
        return None


def node_info_to_dict(info: NodeInfo) -> Dict[str, str]:
    return {
        "node-uuid": info.uuid,
        "node-engine": info.engine.value,
        "node-path": info.path,
    }


def _info_as_str(info: NodeInfo) -> str:
    infos = [
        f"{key}: {value}" for key, value in node_info_to_dict(info).items()
    ]
    info_str = f"{_INFO_SEPARATOR} ".join(infos)
    return f"{_INFO_PREFIX} {info_str} {_INFO_SUFFIX}"


def dynamo_to_python_code(code: str) -> List[str]:
    code_lines = code.splitlines(keepends=False)
    code_lines = clean_empty_lines(code_lines)
    return code_lines


ActionFunc = Callable[[List[str]], List[str]]


def code_to_python(node: ContentNode, action_func: ActionFunc) -> List[str]:
    code_lines = dynamo_to_python_code(node.code)
    code_lines = action_func(code_lines)
    lines = [_info_as_str(node.node_info), ""]
    lines.extend(code_lines)
    return lines


def clean_beginning_empty_lines(lines: List[str]) -> List[str]:
    while len(lines[0].strip()) == 0:
        lines.pop(0)
    return lines


def clean_ending_empty_lines(lines: List[str]) -> List[str]:
    while len(lines[-1].strip()) == 0:
        lines.pop()
    return lines


def clean_empty_lines(lines: List[str]) -> List[str]:
    return clean_ending_empty_lines(clean_beginning_empty_lines(lines))


def python_to_dynamo_code(
    code_lines: List[str], action_func: ActionFunc
) -> List[str]:
    code_lines = action_func(code_lines)
    code_lines = clean_empty_lines(code_lines)
    return code_lines


def python_file(path: Path, action_func: ActionFunc) -> PythonFile:
    code_lines = reader.read_python(path)
    code_lines = clean_beginning_empty_lines(code_lines)
    if len(code_lines) < 2:
        message = f"Python file {path} has no info line or code"
        raise Exception(message)
    info = node_info(code_lines[0])
    if info is not None:
        code_lines = code_lines[1:]
    code_lines = python_to_dynamo_code(code_lines, action_func)
    return PythonFile(path=path, info=info, code_lines=code_lines)
