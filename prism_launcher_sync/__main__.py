import colorlog
import argparse

from . import config
from .utils import logs
from .base import BaseFile

from . import gdrive
from . import prismlauncher

logs.config_logger()
logger = colorlog.getLogger(__name__)

try:
    arg_parser = argparse.ArgumentParser(
        prog="main",
        description="Sync Prism Launcher instances to Google Drive",
        exit_on_error=False
    )
    arg_parser.add_argument(
        "-i", "--instance",
        type=str,
        required=True
    )
    args = arg_parser.parse_args()

    if not config.ZIPFILES_DIR.exists():
        config.ZIPFILES_DIR.mkdir()

    prism_instance = prismlauncher.Instance.from_src(args.instance)

    gd_manager = gdrive.DriveFileManager.load_files()

    logger.info("Sync process starting...")
    gd_manager.sync_instance(prism_instance)

    logger.info("Cleaning up temp files...")
    zip_dir = BaseFile.from_src(config.ZIPFILES_DIR)
    zip_dir.clean_dir()

    logger.info("Sync complete!")


except (argparse.ArgumentError, OSError, TypeError, FileNotFoundError, gdrive.DriveFileManagerError) as e:
    logger.error(e, exc_info=config.DEBUG_MODE)
