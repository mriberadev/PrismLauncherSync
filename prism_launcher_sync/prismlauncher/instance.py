import os
from pathlib import Path
from datetime import datetime
from typing import Self

import colorlog
import shutil

from prism_launcher_sync import config
from prism_launcher_sync.base import BaseFile

if not config.ZIPFILES_DIR.exists():
    config.ZIPFILES_DIR.mkdir()


class InstanceError(Exception):
    pass


class Instance(BaseFile):

    def __init__(
            self,
            name: str,
            dt_modified: datetime | None = None,
            path: str | os.PathLike[str] | None = None,
    ):
        super().__init__(
            name=name,
            path=path,
            dt_modified=dt_modified
        )

    def export_zip(self) -> str:
        try:

            if not self.path:
                raise AttributeError("No file to zip")

            self.path = Path(self.path)
            if not self.path.exists():
                raise FileNotFoundError("File to zip not found")

            logger = colorlog.getLogger(__name__)

            dt_suffix = datetime.now().strftime("_%Y%m%d_%H%M%S")
            _zip = config.ZIPFILES_DIR.joinpath(f"{self.name}{dt_suffix}").resolve()

            logger.info(f"Zipping instance {self.name}...")
            return shutil.make_archive(
                str(_zip),
                format="zip",
                root_dir=self.path.parent,
                base_dir=self.name,
                dry_run=False,
                logger=None
            )
        except (AttributeError, FileNotFoundError) as e:
            raise InstanceError("Failed to zip instance")
