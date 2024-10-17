import argparse
from pathlib import Path

from dynpy.core import convert as cvt
from dynpy.core.convert import Direction
from dynpy.service import dynamo, python


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
        type=Path,
        help="Create a new configuration file in given path",
    )
    return parser.parse_args()


def main():
    args = _parse_argument()
    if args.create_config is not None:
        return cvt.create_config(args.create_config)
    handler = cvt.create_handler(args.config, args.source, args.do_import, args.do_export)
    if handler.direction == Direction.TO_PYTHON:
        dynamo.to_python(handler)
    else:
        python.to_dynamo(handler)


if __name__ == "__main__":
    main()
