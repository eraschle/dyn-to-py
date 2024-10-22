from enum import Enum
from pathlib import Path


class DynPyResource(str, Enum):
    """Resource enumeration for all resources of the application."""

    LOGS = "dynpy.log"
    ICON_APP = "favicon.png"
    ICON_LOAD = "load_config.png"
    ICON_CREATE = "create_config.png"
    ICON_CONVERT = "convert.png"


def icon_path(resource: DynPyResource) -> Path:
    """Return file path to icon resource."""
    if not resource.name.startswith("ICON_"):
        raise ValueError(f"Resource {resource} is not an icon")
    return Path.cwd() / "dynpy" / f"resources/{resource.value}"
