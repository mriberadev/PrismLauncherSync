from pathlib import Path

ROOT_DIR = Path(__file__).parent
ZIPFILES_DIR = (ROOT_DIR / "prismlauncher" / "temp").resolve()
CLIENT_FILE = (ROOT_DIR / "gdrive" / "resource" / "client_secret.json").resolve()
USER_CREDS_FILE = (ROOT_DIR / "gdrive" / "resource" / "user_credentials.json").resolve()

DRIVE_FOLDER = "Prism Launcher Sync"