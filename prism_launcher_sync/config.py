import sys
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    PYTHON_SCRIPT = False
    ROOT_DIR = Path(sys._MEIPASS).resolve()
    json_path = ROOT_DIR
else:
    PYTHON_SCRIPT = True
    ROOT_DIR = Path(__file__).parent
    json_path = (ROOT_DIR / "gdrive").resolve()

ZIPFILES_DIR = (ROOT_DIR / "temp").resolve()
CLIENT_FILE = (json_path / "resource" / "client_secret.json").resolve()
USER_CREDS_FILE = (json_path / "resource" / "user_credentials.json").resolve()

DEBUG_MODE = False

G_API_SERVICE = "drive"
G_API_VERSION = "v3"
DRIVE_FOLDER = "Prism Launcher Sync"

UPLOAD_CHUNK_SIZE = 10 * 1024 * 1024  # Bytes
UPLOAD_MAX_ATTEMPTS = 10
DOWNLOAD_CHUNK_SIZE = 20 * 1024 * 1024  # Bytes
DOWNLOAD_MAX_ATTEMPTS = 10
MAX_BACKUPS = 5
