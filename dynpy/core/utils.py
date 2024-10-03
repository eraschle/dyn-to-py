import json
import re
from pathlib import Path
from typing import Callable, List, OrderedDict

NAME_LOOKUP = [" ", "<", ">", "?", "|", "*", "/", "\\", "\"", ":", ";", ",", "-"]
NAME_SEPARATOR = "_"
NAME_REGEX = re.compile(r"\(\[_\]*\)")


def clean_name(name: str) -> str:
    for replace in NAME_LOOKUP:
        name = name.replace(replace, NAME_SEPARATOR)
    names = NAME_REGEX.split(name)
    return NAME_SEPARATOR.join(names)


def path_as_str(file_path: Path) -> str:
    return str(file_path.resolve())


def replace_path(path: Path, from_path: str, to_path: str) -> Path:
    path_str = path_as_str(path)
    path_str = path_str.replace(from_path, to_path)
    return Path(path_str)


def get_files(current: Path, callback: Callable[[Path], bool]) -> List[Path]:
    if current.is_file():
        return [current] if callback(current) else []
    dyn_files = []
    for path in current.iterdir():
        if path.is_dir():
            dyn_files.extend(get_files(path, callback))
        if not callback(path):
            continue
        dyn_files.append(path)
    return dyn_files


def read_json(path: Path) -> OrderedDict:
    with open(path, mode="r", encoding="utf8") as file:
        return json.load(file, object_pairs_hook=OrderedDict)


def write_json(path: Path, content: OrderedDict) -> None:
    with open(path, mode="w", encoding="utf8") as file:
        json.dump(content, file, indent=2, ensure_ascii=False)


def read_python(path: Path) -> List[str]:
    with open(path, mode="r", encoding="utf8") as file:
        code = file.read()
        return code.splitlines(keepends=False)


def write_python(path: Path, content: List[str]) -> None:
    code = "\n".join(content)
    with open(path, mode="w", encoding="utf8") as file:
        file.write(code)
