import os
from pathlib import Path
from datetime import datetime

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
            **kwargs,
    ):
        super().__init__(**kwargs)
        if self.path:
            self.path = Path(self.path)
            savefile_dir = list(Path(self.path / "minecraft" / "saves").iterdir())[0]
            self.dt_modified = datetime.fromtimestamp(savefile_dir.stat().st_mtime).astimezone()


    def export_zip(self) -> str:
        logger = colorlog.getLogger(__name__)

        dt_suffix = datetime.now().strftime("_%Y%m%d_%H%M%S")
        _zip = config.ZIPFILES_DIR.joinpath(f"{self.name}{dt_suffix}").resolve()

        logger.info(f"Zipping instance {self.name}...")
        return shutil.make_archive(
            str(_zip),
            format="zip",
            root_dir=self.path,
            dry_run=False,
            logger=None
        )

    def import_zip(self, src: str | os.PathLike[str]) -> None:
        try:
            src = Path(src)
            if not src.exists():
                raise FileNotFoundError("Zip to import not found")

            logger = colorlog.getLogger(__name__)

            logger.info(f"Importing instance {self.name}...")
            shutil.unpack_archive(
                filename=src,
                extract_dir=self.path,
                format="zip"
            )

        except (AttributeError, FileNotFoundError) as e:
            raise InstanceError("Failed to zip instance") from e
