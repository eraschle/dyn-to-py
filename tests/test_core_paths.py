from pathlib import Path
from dynpy.core import paths


def test_clean_name():
    file_name = " name!with.a/lot#}symbols$-().extension"
    clean_name = paths.clean_name(file_name)
    assert clean_name == "name_with_a_lot_symbols.extension"


def _test_replace_path(replaced_path, from_path, to_path):
    replaced_str = str(replaced_path)
    assert from_path not in replaced_str
    assert replaced_str.startswith(to_path)
    assert "//" not in replaced_str


def test_replace_path_with_ending_slash():
    to_path = "/some/root/path/"
    from_path = paths.path_as_str(Path.cwd())
    file_path = Path(from_path) / "other/path/to/a/file.extension"
    replaced_path = paths.replace_path(file_path, from_path, to_path)
    _test_replace_path(replaced_path, from_path, to_path)
    assert str(replaced_path)[len(to_path) - 1] == "/"


def test_replace_path_without_ending_slash():
    to_path = "some/root/path"
    from_path = paths.path_as_str(Path.cwd())
    file_path = Path(from_path) / "other/path/to/a/file.extension"
    replaced_path = paths.replace_path(file_path, from_path, to_path)
    _test_replace_path(replaced_path, from_path, to_path)
    assert str(replaced_path)[len(to_path)] == "/"
