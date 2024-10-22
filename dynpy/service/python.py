import logging
from pathlib import Path
from typing import Dict, Iterable, List, Mapping

from dynpy.core import factory
from dynpy.core.context import DynamoFileContext
from dynpy.core.handler import ConvertHandler
from dynpy.core.models import PythonFile

log = logging.getLogger(__name__)


def _create_python_files(handler: ConvertHandler) -> List[PythonFile]:
    source = handler.source
    return [factory.python_file(path, handler.apply_action) for path in source.export_files()]


def python_file_group(handler: ConvertHandler) -> Mapping[Path, List[PythonFile]]:
    py_map = {}
    for python in _create_python_files(handler):
        py_path = python.path.parent
        if py_path not in py_map:
            py_map[py_path] = []
        py_map[py_path].append(python)
    return py_map


def _dynamo_file_group(handler: ConvertHandler) -> Mapping[Path, Iterable[PythonFile]]:
    dyn_map: Dict[Path, List[PythonFile]] = {}
    for python in _create_python_files(handler):
        if python.info is None:
            log.warning(f"Python file {python.path} has no info")
            continue
        dyn_path = python.dynamo_path
        if not dyn_path.exists():
            log.warning(f"Dynamo file {dyn_path} does not exist")
            continue
        if dyn_path not in dyn_map:
            dyn_map[dyn_path] = []
        dyn_map[dyn_path].append(python)
    return dyn_map


def replace_code_in(py_files: Iterable[PythonFile], context: DynamoFileContext) -> None:
    for py_file in py_files:
        if py_file.info is None:
            continue
        node_id = py_file.info.uuid
        context.replace_code(node_id, py_file.code)


def to_dynamo(handler: ConvertHandler):
    for path, files in _dynamo_file_group(handler).items():
        with DynamoFileContext(path=path) as ctx:
            replace_code_in(files, ctx)
