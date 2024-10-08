import os
from pathlib import Path
from typing import List, Sequence

from dynpy.core import factory, reader
from dynpy.core.context import DynamoFileContext
from dynpy.core.models import (
    CodeNode,
    ContentNode,
    ConvertHandler,
    SourceConfig,
)


def _get_code_nodes(context: DynamoFileContext) -> List[CodeNode]:
    return [factory.code_node(node=node) for node in context.code_nodes]


def _content_nodes(context: DynamoFileContext) -> List[ContentNode]:
    nodes = []
    view_maps = context.views_mapping
    for node in _get_code_nodes(context):
        view = view_maps.get(node.node_id)
        if view is None:
            raise Exception(f"No view found for node {node.node_id}")
        nodes.append(factory.content_node(node=node, view=view, path=context.path))
    return nodes


def _get_python_path(node: ContentNode, source: SourceConfig) -> Path:
    path = source.export_file_path(node)
    if not path.parent.exists():
        os.makedirs(path.parent, exist_ok=True)
    return path


def _create_py_file(node: ContentNode, handler: ConvertHandler):
    code_lines = factory.code_to_python(node=node, handler=handler)
    path = _get_python_path(node, handler.source)
    reader.write_python(path=path, content=code_lines)


def _create_python_files(nodes: Sequence[ContentNode], handler: ConvertHandler):
    for node in nodes:
        _create_py_file(node, handler=handler)


def dynamo_to_python(handler: ConvertHandler):
    for dyn_file in handler.source.source_files():
        with DynamoFileContext(dyn_file, save=False) as ctx:
            nodes = _content_nodes(ctx)
        _create_python_files(nodes, handler)
