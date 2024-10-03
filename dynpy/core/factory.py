from pathlib import Path
from typing import Any, Iterable, List, Mapping, Type

from dynpy import code, context
from dynpy.core.actions import ActionType, ConvertAction, RemoveLineAction, TypeIgnoreAction
from dynpy.core.models import (
    CodeNode,
    ContentNode,
    ConvertConfig,
    ConvertHandler,
    NodeInfo,
    NodeView,
    PythonFile,
    SourceConfig,
)
from dynpy.core import utils


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


def _get_actions(action_type: ActionType, content: Iterable[Mapping[str, Any]]) -> List[ConvertAction]:
    return [_get_action(action_type)(**act) for act in content]


def _create_actions(action_content: Mapping[str, Any]) -> Mapping[ActionType, List[ConvertAction]]:
    actions = {}
    for action, content in action_content.items():
        action_type = ActionType(action)
        actions[action_type] = _get_actions(action_type, content)
    return actions


def convert_config(path: Path) -> ConvertConfig:
    content = utils.read_json(path.resolve())
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
        node_id=context.node_uuid(node),
        code=context.node_code(node),
        engine=context.node_engine(node),
    )


def node_view(view: Mapping[str, Any]) -> NodeView:
    return NodeView(
        node_id=context.node_uuid(view),
        name=context.node_name(view),
    )


def content_node(node: CodeNode, view: Mapping[str, Any], path: Path) -> ContentNode:
    return ContentNode(
        node=node,
        view=node_view(view),
        path=path,
    )


def node_info(node_info: str) -> NodeInfo:
    node_info = node_info.replace(NodeInfo.file_prefix, "")
    infos = node_info.split(NodeInfo.separator)
    infos = [value.split(":") for value in infos]
    info_dict = {key.strip(): value.strip() for key, value in infos}
    return NodeInfo(**info_dict)


def python_file(path: Path, handler: ConvertHandler) -> PythonFile:
    code_lines = utils.read_python(path)
    return PythonFile(
        path=path,
        info=node_info(code_lines[0]),
        code=code.to_dynamo(code_lines[1:], handler),
    )
