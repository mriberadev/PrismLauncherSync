import colorlog
import argparse

from core import gdrive, prismlauncher
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

    prism_instance = prismlauncher.Instance.from_file_uri(args.instance)
    gdrive_manager = gdrive.FileManager.load_files()


except argparse.ArgumentError as e:
    logger.error(e.__str__())
