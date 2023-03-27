from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Settings:
    BACKUP_FILENAME = "backup.pkl"
    ATTEMPTS_INTERVAL = timedelta(seconds=4)
    TIMEOUT_SECONDS = 0
