import colorlog
from datetime import datetime
from pathlib import Path
from typing import Self
import shutil

from prism_launcher_sync.base import BaseFile
from prism_launcher_sync import config


class Instance(BaseFile):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        logger.info(f"Zipping instance {self.name}...")
        zip_file = shutil.make_archive(
            zip_name,
            format="zip",
            root_dir=config.ZIPFILES_DIR,
            base_dir=self.path,
            dry_run=True,
            logger=logger
        )
        logger.info(f"Zipped to {zip_file}")
        return Path(zip_file)
