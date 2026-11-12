import os
from datetime import datetime
from pathlib import Path


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