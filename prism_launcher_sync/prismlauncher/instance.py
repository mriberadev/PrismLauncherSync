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

    def to_zip(self) -> Self:
        if not self.path:
            raise TypeError("No file to zip")
        if not self.path.exists():
            raise FileNotFoundError("File to zip not found")

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
        self.name = zip_name
        self.path = Path(zip_file)
        return self
