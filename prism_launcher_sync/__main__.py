import colorlog
import argparse

import gdrive
import prismlauncher
from utils import logs

logs.config_logger()
logger = colorlog.getLogger(__name__)

try:
    arg_parser = argparse.ArgumentParser(
        prog="main",
        description="Sync Prism Launcher instances to Google Drive",
        exit_on_error=False
    )
    arg_parser.add_argument("-i", "--instance", type=str, required=True)
    args = arg_parser.parse_args()

    gd_manager = gdrive.DriveFileManager.load_files()

    prism_instance = prismlauncher.Instance.from_file_uri(args.instance)

    if gd_manager.needs_sync(prism_instance.last_modified):
        zipped_instance = prism_instance.to_zip()
        gd_manager.sync(zipped_instance, prism_instance.last_modified)


except argparse.ArgumentError as e:
    logger.error(e)
except prismlauncher.InstanceError as e:
    logger.error(e)