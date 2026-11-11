import colorlog
from datetime import datetime
from pathlib import Path
from typing import Self
import shutil

from prism_launcher_sync.base import BaseFile
from prism_launcher_sync import config


class Instance(BaseFile):

    def __init__(self, path: Path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    @classmethod
    def from_file_uri(cls, uri) -> Self:
        path = Path(uri)
        if not path.exists():
            raise FileNotFoundError("Could not find instance using provided URI")

        last_modified = datetime.fromtimestamp(path.stat().st_mtime)

        return cls(
            path=path,
            name=path.name,
            last_modified=last_modified
        )

    def to_zip(self) -> Path:
        logger = colorlog.getLogger(__name__)
        dt_suffix = datetime.now().strftime("_%Y%m%d_%H%M%S")
        zip_name = f"{self.name}{dt_suffix}"
        zip_dst = (config.ZIPFILES_DIR / zip_name).resolve().__str__()
        logger.info(f"Zipping instance {self.name}...")
        zip_file = shutil.make_archive(
            zip_dst,
            format="zip",
            root_dir=self.path.parent,
            base_dir=self.name,
            dry_run=False,
            # logger=logger
        )
        logger.info(f"Zipped to {zip_file}")
        return Path(zip_file)
