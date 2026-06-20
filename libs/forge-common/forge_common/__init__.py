"""Forge shared library for Python services.

Re-exports the common building blocks every service uses so imports stay short:

    from forge_common import Settings, get_logger, NatsBus, Event
"""

from forge_common.config import Settings
from forge_common.logging import get_logger
from forge_common.bus import NatsBus
from forge_common.events import Event
from forge_common.metrics import metrics_app, request_counter

__all__ = [
    "Settings",
    "get_logger",
    "NatsBus",
    "Event",
    "metrics_app",
    "request_counter",
]
