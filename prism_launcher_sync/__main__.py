import subprocess
import sys
import time

import colorlog
import argparse

from prism_launcher_sync import config
from prism_launcher_sync import utils
from prism_launcher_sync import base

from prism_launcher_sync import gdrive
from prism_launcher_sync import prismlauncher

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
    arg_parser.add_argument(
        "--ask",
        action=argparse.BooleanOptionalAction,
        required=False
    )
    arg_parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        required=False
    )
    arg_parser.add_argument(
        "--cmd",
        action=argparse.BooleanOptionalAction,
        required=False
    )
    args = arg_parser.parse_args()

    if args.debug is True:
        config.DEBUG_MODE = True

    if args.cmd is True:
        # Execute in a new cmd window
        sys.argv.remove("--cmd")
        logger.info("Opening in new window...")
        subprocess_args = ["cmd.exe", "/c", "start", "/wait"]
        if config.PYTHON_SCRIPT:
            subprocess_args.append(sys.executable)
        subprocess_args.extend(sys.argv)
        _new_window = subprocess.call(subprocess_args)
        sys.exit()

    gd_manager = gdrive.DriveFileManager(
        _root=gdrive.DriveFile(config.DRIVE_FOLDER),
        _api=gdrive.DriveApi.build()
    )
    gd_manager.map_from_drive()

    prism_instance = prismlauncher.Instance.from_src(args.instance)

    # Ask the user if they want to sync their instance
    last_backup = gd_manager.last_backup_for_instance(prism_instance)
    last_backup_date_str = last_backup.dt_modified.strftime("%Y-%m-%d %H:%M:%S") if last_backup else "No backups"
    instance_date_str = prism_instance.dt_modified.strftime("%Y-%m-%d %H:%M:%S")
    menu = (
        "\n"
        f"-- {prism_instance.name} --\n"
        f"Most recent backup: {last_backup_date_str}\n"
        f"Most recent savefile: {instance_date_str}\n"
        "Would you like to sync this instance to drive? (y/N):"
    )
    logger.info(menu)
    menu_choice = input()
    if menu_choice.lower().strip() != "y":
        sys.exit()

    logger.info("Sync process starting...")
    gd_manager.sync_instance(prism_instance)

    logger.info("Cleaning up temp files...")
    zip_dir = base.BaseFile.from_src(config.ZIPFILES_DIR)
    zip_dir.clean_dir()

    logger.info("Sync complete!")


except (argparse.ArgumentError, gdrive.DriveFileManagerError, gdrive.DriveApiError, base.BaseFileError) as e:
    logger.error(e, exc_info=config.DEBUG_MODE)
