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

    prism_instance = prismlauncher.Instance.from_uri(args.instance)

    gd_manager = gdrive.DriveFileManager.load_files()

    if gd_manager.needs_sync(prism_instance.last_modified):
        logger.info("Sync needed, starting...")
        zipped_instance = prism_instance.to_zip()
        gd_manager.sync(zipped_instance, prism_instance.last_modified)
        logger.info("Sync complete!")

except (argparse.ArgumentError, FileNotFoundError) as e:
    logger.error(e)