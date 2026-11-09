import datetime
from pathlib import Path

from .exception import InstanceNotFound


class Instance:

    def __init__(
            self,
            path: Path | None = None,
            name: str | None = None,
            last_modified: datetime.datetime | None = None
    ):
        self.path = path
        self.name = name
        self.last_modified = last_modified

    @classmethod
    def from_file_uri(cls, uri):
        path = Path(uri)
        if not path.exists():
            raise InstanceNotFound("Could not find instance using provided URI")

        last_modified = datetime.datetime.fromtimestamp(path.stat().st_mtime)

        return cls(
            path=path,
            name=path.name,
            last_modified=last_modified
        )
