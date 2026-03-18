from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ActionType(str, Enum):
    QUARANTINE = "quarantine"
    KEEP_REPRESENTATIVE = "keep_representative"
    MOVE = "move"
    COPY = "copy"
    DELETE = "delete"


@dataclass
class ActionPlan:
    """Describes what should happen to a set of files after a scan."""

    action: ActionType
    targets: list[Path]
    destination: Path | None = None   # for move/copy/quarantine
    dry_run: bool = True
    notes: str = ""
    executed_paths: list[Path] = field(default_factory=list)

    def is_destructive(self) -> bool:
        return self.action in {ActionType.DELETE, ActionType.MOVE}
