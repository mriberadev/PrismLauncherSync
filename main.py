import logging
from gdrive_management.auth import gdrive_auth
from gdrive_management.exception import InitAuthError

logger = logging.getLogger(__name__)

try:
    gdrive = gdrive_auth()

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

except InitAuthError as e:
    logger.error(e.__str__())


