from typing import List

from dynpy.core.models import ContentNode, ConvertHandler


def to_python(node: ContentNode, handler: ConvertHandler) -> List[str]:
    code_lines = node.code.splitlines(keepends=False)
    code_lines = handler.apply_action(code_lines)
    lines = [node.node_info.as_str(), "", ""]
    lines.extend(code_lines)
    return lines


def to_dynamo(lines: List[str], handler: ConvertHandler) -> str:
    lines = handler.apply_action(lines)
    return "\n".join(lines)
