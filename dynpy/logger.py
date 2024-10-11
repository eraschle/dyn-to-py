import logging
import logging.config
from typing import Iterable, Optional


def _format_message(ends_with: Optional[str] = None) -> str:
    return "%(message)s" + (ends_with or "")


def _format_func(ends_with: Optional[str] = None) -> str:
    return "%(funcName)s" + (ends_with or "")


def _format_level(ends_with: Optional[str] = None) -> str:
    return "'%(levelname)-8s" + (ends_with or "")


# def _format_time(ends_with: Optional[str] = None) -> str:
#     return "%(asctime)-12s" + (ends_with or "")


def _format_name(ends_with: Optional[str] = None) -> str:
    return "%(name)-12s" + (ends_with or "")


def _log_format(format_strings: Iterable[str]) -> logging.Formatter:
    format_str = " ".join(format_strings)
    return logging.Formatter(format_str)


def console(level) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = _log_format(
        [
            _format_level(ends_with=":"),
            _format_name(),
            _format_func(ends_with=">"),
            _format_message(),
        ]
    )
    handler.setFormatter(formatter)
    return handler


# def log_file(level) -> logging.Handler:
#     log_file = PctResources.app_data(PctResource.PCT_LOG)
#     ten_mega_bytes = 10 * 1024 * 1024
#     handler = RotatingFileHandler(
#         filename=log_file,
#         mode='a',
#         maxBytes=ten_mega_bytes,
#         backupCount=3,
#         encoding='utf-8',
#     )
#     handler.setLevel(level)
#     formatter = logging.Formatter(
#         '%(asctime)s - %(levelname)s - %(name)s - %(message)s', '%d-%b-%y %H:%M:%S'
#     )
#     handler.setFormatter(formatter)
#     return handler


def config_logger():
    handlers = [
        console(logging.DEBUG),
        # log_file(logging.INFO),
    ]
    logging.basicConfig(handlers=handlers, level=logging.DEBUG)
