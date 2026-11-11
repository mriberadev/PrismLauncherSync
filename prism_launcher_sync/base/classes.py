from datetime import datetime
from pathlib import Path


class BaseFile:

    def __init__(
            self,
            name: str,
            last_modified: datetime,
            path: Path | None = None
    ):
        self.name = name
        self.last_modified = last_modified
        self.path = path