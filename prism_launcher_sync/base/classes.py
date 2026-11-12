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
    def from_src(cls, src: str | os.PathLike[str]) -> Self:
        path = Path(src)
        if not path.exists():
            raise FileNotFoundError("Failed to find file using provided URI")

        return cls(
            path=path,
            name=path.name,
            dt_modified=datetime.fromtimestamp(path.stat().st_mtime)
        )

    def remove(self) -> None:
        if not self.path:
            raise TypeError("No path in object")

        if not self.path.exists():
            return None

        try:
            if self.path.is_dir():
                self.path.rmdir()
            else:
                self.path.unlink()

        except OSError as e:
            e.add_note(f"{self.name} could not be removed")
            raise

    def clean_dir(self) -> None:
        if not self.path:
            raise TypeError("No path in object")
        if not self.path.exists():
            raise FileNotFoundError("Directory not found")
        if not self.path.is_dir():
            raise OSError("Not a directory")

        dir_contents = self.path.iterdir()
        try:
            for item in dir_contents:
                _file = self.__class__.from_src(item)
                _file.remove()
        except OSError as e:
            e.add_note("Failed to clean directory")
            raise
