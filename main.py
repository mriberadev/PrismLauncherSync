import logging
import argparse

from core import gdrive, prismlauncher

logger = logging.getLogger(__name__)

try:
    arg_parser = argparse.ArgumentParser(
        prog="main",
        description="Sync Prism Launcher instances to Google Drive",
        exit_on_error=False
    )
    arg_parser.add_argument("-i", "--instance", type=str, required=True)
    args = arg_parser.parse_args()

    prism_instance = prismlauncher.Instance.from_file_uri(args.instance)


except argparse.ArgumentError as e:
    logger.error(e.__str__())
