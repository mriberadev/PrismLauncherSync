import os
from datetime import datetime
from pathlib import Path
from typing import Self


class BaseFileException(Exception):
    pass


class BaseFile:

    def __init__(
            self,
            name: str,
            dt_modified: datetime | None = None,
            path: str | os.PathLike[str] | None = None,
    ):
        self.name = name
        self.path = path
        self.dt_modified = dt_modified

    @classmethod
    def from_src(cls, src: str | os.PathLike[str]) -> Self:
        path = Path(src)
        if not path.exists():
            raise FileNotFoundError

        return cls(
            path=path,
            name=path.name,
            dt_modified=datetime.fromtimestamp(path.stat().st_mtime).astimezone()
        )

    def remove(self) -> None:
        try:
            if not self.path:
                raise AttributeError("No path in object")

            self.path = Path(self.path)
            if not self.path.exists():
                return None

            if self.path.is_dir():
                self.path.rmdir()
            else:
                self.path.unlink()

        except (AttributeError, OSError) as e:
            raise BaseFileException("Failed to remove file") from e

    def clean_dir(self) -> None:
        try:
            if not self.path:
                raise AttributeError("No path in object")

            self.path = Path(self.path)
            if not self.path.exists():
                raise FileNotFoundError("Directory not found")

            if not self.path.is_dir():
                raise ValueError("Not a directory")

            dir_contents = self.path.iterdir()
            for item in dir_contents:
                self.__class__.from_src(item).remove()

        except (AttributeError, FileNotFoundError, ValueError, BaseFileException) as e:
            raise BaseFileException("Failed to clean directory") from e
