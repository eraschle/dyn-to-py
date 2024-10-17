import argparse
from pathlib import Path
from typing import Optional

from dynpy.cli import dynamo, python
from dynpy.core import factory
from dynpy.core.convert import ConvertHandler, Direction
from dynpy.core.models import ConvertConfig


def _parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="ath to the configuration file",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Source name in the configuration file",
    )
    parser.add_argument(
        "--do-import",
        required=False,
        action="store_true",
        default=False,
        help="Replace the Python code in the Dynamo files",
    )
    parser.add_argument(
        "--do-export",
        required=False,
        action="store_true",
        default=False,
        help="Create Python code from the Dynamo files",
    )
    parser.add_argument(
        "--create-config",
        required=False,
        action="store_true",
        default=False,
        help="Create a new configuration file in given path",
    )
    return parser.parse_args()


def _get_config_path(file_path: Optional[str] = None) -> Path:
    path = Path.cwd() if file_path is None else Path(file_path)
    if file_path is None:
        path = path / "config.json"
    path = path.with_suffix(".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read_config(path: Optional[str]) -> ConvertConfig:
    if path is None:
        config_path = _get_config_path(path)
    else:
        config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    return factory.convert_config(config_path.resolve())


def _convert_direction(args: argparse.Namespace) -> Direction:
    if not args.do_export and not args.do_import:
        raise Exception("Please provide either --do-export or --do-import")
    if args.do_export and not args.do_import:
        return Direction.TO_PYTHON
    elif args.do_import and not args.do_export:
        return Direction.TO_DYNAMO
    raise Exception("Can not export and import at the same time")


def _create_config(path: Optional[str] = None):
    config_path = _get_config_path(path)
    config = factory.default_convert_config()
    config.save(config_path)


def main():
    args = _parse_argument()
    if args.create_config is not None:
        return _create_config(args.create_config)
    handler = ConvertHandler(
        convert=_read_config(args.config),
        source_name=args.source,
        direction=_convert_direction(args),
    )
    if handler.direction == Direction.TO_PYTHON:
        dynamo.to_python(handler)
    else:
        python.to_dynamo(handler)


if __name__ == "__main__":
    main()
