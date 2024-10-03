import os
from pathlib import Path
import shutil


DYNAMO_FILE = Path(__file__).parent / "data" / "dynamo.dyn"
PYTHON_FILE = Path(__file__).parent / "data" / "python.py"


def ensure_not_exists(path: Path) -> Path:
    if path.exists():
        os.remove(path)
    return path


def test_file_path(path: Path) -> Path:
    name = path.with_suffix("").name
    return path.with_name(f"{name}_test{path.suffix}")


def create_test_file(path: Path) -> Path:
    test_path = test_file_path(path)
    test_path = ensure_not_exists(test_path)
    shutil.copy(path, test_path)
    return test_path
