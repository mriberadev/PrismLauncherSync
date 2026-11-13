from pathlib import Path

ROOT_DIR = Path(__file__).parent
ZIPFILES_DIR = (ROOT_DIR / "temp").resolve()
CLIENT_FILE = (ROOT_DIR / "gdrive" / "resource" / "client_secret.json").resolve()
USER_CREDS_FILE = (ROOT_DIR / "gdrive" / "resource" / "user_credentials.json").resolve()

DEBUG_MODE = False

G_API_SERVICE = "drive"
G_API_VERSION = "v3"
DRIVE_FOLDER = "Prism Launcher Sync"

UPLOAD_CHUNK_SIZE = 20 * 1024 * 1024
UPLOAD_MAX_ATTEMPTS = 10
DOWNLOAD_CHUNK_SIZE = 20 * 1024 * 1024
DOWNLOAD_MAX_ATTEMPTS = 10
MAX_BACKUPS = 5