import colorlog
import argparse

from . import config
from . import utils
from . import base

from . import gdrive
from . import prismlauncher

utils.logs.config_logger()
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

    gd_manager = gdrive.DriveFileManager(
        _root=gdrive.DriveFile(config.DRIVE_FOLDER),
        _api=gdrive.DriveApi.build()
    )
    gd_manager.map_from_drive()

    prism_instance = prismlauncher.Instance.from_src(args.instance)

    logger.info("Sync process starting...")
    gd_manager.sync_instance(prism_instance)

    logger.info("Cleaning up temp files...")
    zip_dir = base.BaseFile.from_src(config.ZIPFILES_DIR)
    zip_dir.clean_dir()

    logger.info("Sync complete!")


except (argparse.ArgumentError, gdrive.DriveFileManagerError, base.BaseFileException) as e:
    logger.error(e, exc_info=config.DEBUG_MODE)
