from pathlib import Path
from typing import Callable, List

NAME_LOOKUP = [" ", "<", ">", "?", "|", "*", "/", "\\", "\"", ":", ";", ",", "-"]
NAME_SEPARATOR = "_"


def clean_name(name: str) -> str:
    for replace in NAME_LOOKUP:
        name = name.replace(replace, NAME_SEPARATOR)
    names = name.split(NAME_SEPARATOR)
    names = [name.strip() for name in names if name is not None]
    names = [name for name in names if len(name) > 0]
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
