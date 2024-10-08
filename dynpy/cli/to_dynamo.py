from pathlib import Path
from typing import Dict, Iterable, List, Mapping

from dynpy.core import factory
from dynpy.core.context import DynamoFileContext
from dynpy.core.models import ConvertHandler, PythonFile


def _python_files(handler: ConvertHandler) -> List[PythonFile]:
    source = handler.source
    return [factory.python_file(path, handler) for path in source.export_files()]


def _dynamo_file_group(handler: ConvertHandler) -> Mapping[Path, Iterable[PythonFile]]:
    dyn_map: Dict[Path, List[PythonFile]] = {}
    for python in _python_files(handler):
        dyn_path = python.dynamo_path
        if not dyn_path.exists():
            continue
        if dyn_path not in dyn_map:
            dyn_map[dyn_path] = []
        dyn_map[dyn_path].append(python)
    return dyn_map


def replace_code_in(files: Iterable[PythonFile], context: DynamoFileContext) -> None:
    for file in files:
        node_id = file.info.uuid
        context.replace_code(node_id, file.code)


def python_to_dynamo(handler: ConvertHandler):
    for path, files in _dynamo_file_group(handler).items():
        with DynamoFileContext(path=path) as ctx:
            replace_code_in(files, ctx)
