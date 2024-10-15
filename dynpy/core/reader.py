import json
from pathlib import Path
from typing import Any, List, Mapping, OrderedDict


def read_json(path: Path) -> OrderedDict:
    with open(path, mode="r", encoding="utf8") as js:
        return json.load(js, object_pairs_hook=OrderedDict)


def write_json(path: Path, content: OrderedDict) -> None:
    with open(path, mode="w", encoding="utf8") as js:
        json.dump(content, js, indent=2, ensure_ascii=False)


def read_python(path: Path) -> List[str]:
    with open(path, mode="r", encoding="utf8") as py:
        code = py.read()
        return code.splitlines(keepends=False)


def write_python(path: Path, content: List[str]) -> None:
    code = "\n".join(content)
    with open(path, mode="w", encoding="utf8") as py:
        py.write(code)


def read_config(path: Path) -> Mapping[str, Any]:
    with open(path, mode="r", encoding="utf8") as js:
        return json.load(js)


def write_config(path: Path, content: Mapping[str, Any]) -> None:
    with open(path, mode="w", encoding="utf8") as js:
        json.dump(content, js, indent=2, ensure_ascii=False)
