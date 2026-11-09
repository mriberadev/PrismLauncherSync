import logging
import core.gdrive as gdrive

logger = logging.getLogger(__name__)

try:

    gdrive_creds = gdrive.get_user_credentials()


except gdrive.InitAuthError as e:
    logger.error(e.__str__())


