import os
from datetime import datetime
from pathlib import Path
from typing import Self


class BaseFile:

    def __init__(
            self,
            name: str,
            dt_modified: datetime,
            path: str | os.PathLike[str] | None = None,
    ):
        self.name = name
        self.path = Path(path) if path else None
        self.dt_modified = dt_modified

    @classmethod
    def from_uri(cls, uri: str) -> Self:
        path = Path(uri)
        if not path.exists():
            raise FileNotFoundError("Could not find file using provided URI")

        return cls(
            path=path,
            name=path.name,
            dt_modified=datetime.fromtimestamp(path.stat().st_mtime)
        )