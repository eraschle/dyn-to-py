import re
from abc import abstractmethod
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple


class ConvertAction:
    @abstractmethod
    def apply_to(self, line: str) -> Optional[str]:
        pass

    def apply(self, lines: Iterable[str]) -> List[str]:
        applied = [self.apply_to(line) for line in lines]
        return [line for line in applied if line is not None]

    @abstractmethod
    def restore_in(self, line: str) -> str:
        pass

    def restore(self, lines: Iterable[str]) -> List[str]:
        return [self.restore_in(line) for line in lines]

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


class RemoveLineAction(ConvertAction):
    def __init__(self, contains: List[str]) -> None:
        self.contains = contains

    def apply_to(self, line: str) -> Optional[str]:
        if any(val in line for val in self.contains):
            return None
        return line

    def restore_in(self, line: str) -> str:
        return line

    def to_dict(self) -> Dict[str, Any]:
        return {"contains": self.contains}


class TypeIgnoreAction(ConvertAction):
    def __init__(self, value: str, contains: List[str], regex: List[str]) -> None:
        super().__init__()
        self.value = value
        self.contains = contains
        self.regex = regex
        self._pattern = [re.compile(reg) for reg in self.regex]

    def _append_value(self, line: str) -> str:
        return f"{line}  {self.value}"

    def apply_to_line(self, line: str) -> Tuple[bool, str]:
        if not any(value in line for value in self.contains):
            return False, line
        return True, self._append_value(line)

    def _any_match(self, line: str) -> bool:
        return any(pat.match(line) is not None for pat in self._pattern)

    def apply_regex(self, line: str) -> Tuple[bool, str]:
        if not self._any_match(line):
            return False, line
        return True, self._append_value(line)

    def apply_to(self, line: str) -> Optional[str]:
        applied, line = self.apply_to_line(line)
        if applied:
            return line
        _, line = self.apply_regex(line)
        return line

    def restore_in(self, line: str) -> str:
        if self.value not in line:
            return line
        return line.replace(self.value, "").rstrip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "contains": self.contains,
            "regex": self.regex,
        }


class ActionType(str, Enum):
    REMOVE = "DELETE"
    REPLACE = "REPLACE"
