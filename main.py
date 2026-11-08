import logging
from gdrive_management.auth import gdrive_auth
from gdrive_management.exception import InitAuthError

logger = logging.getLogger(__name__)

try:
    gdrive = gdrive_auth()

    #TODO: file and directory handling in google drive using files.py module

except InitAuthError as e:
    logger.error(e.__str__())


