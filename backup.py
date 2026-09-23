import os
import asyncio
import subprocess
from datetime import datetime,timezone,timedelta
from dotenv import load_dotenv
from simple_logging import log_backup

# Load environment variables
load_dotenv()

# Config
MYSQLDUMP_PATH = os.getenv("MYSQLDUMP_PATH", r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DATABASE = os.getenv("MYSQL_DB", "baabu")
MYSQL_TABLE = os.getenv("MYSQL_TABLE", "Order")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", 3600))  # seconds

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

IST_OFFSET = timedelta(hours=5, minutes=30)

def get_ist_timestamp():
    utc_now = datetime.now(timezone.utc)
    ist_now = utc_now + IST_OFFSET
    return ist_now.strftime("%Y%m%d_%H%M%S")

def run_mysqldump(filename: str):
    """Run mysqldump command and save output to filename."""
    cmd = [MYSQLDUMP_PATH, f"-u{MYSQL_USER}", f"-p{MYSQL_PASSWORD}", MYSQL_DATABASE, MYSQL_TABLE]
    try:
        with open(filename, "w", encoding="utf-8") as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=True)
        log_backup(f"✅ Backup successful → {filename}")
    except subprocess.CalledProcessError as e:
        log_backup(f"❌ Backup failed: {e.stderr}", level="ERROR")
        raise
    except Exception as e:
        log_backup(f"❌ Unexpected error: {e}", level="ERROR")
        raise

def backup_table_once() -> str:
    """Perform a single backup and return filename."""
    timestamp = get_ist_timestamp()
    backup_file = os.path.join(BACKUP_DIR, f"{MYSQL_TABLE}_backup_{timestamp}.sql")
    run_mysqldump(backup_file)
    return backup_file

async def backup_table_task():
    """Continuously backup table at BACKUP_INTERVAL."""
    while True:
        try:
            # Run blocking backup in a separate thread so FastAPI doesn't freeze
            await asyncio.to_thread(backup_table_once)
        except Exception:
            # Errors are already logged in run_mysqldump
            pass
        await asyncio.sleep(BACKUP_INTERVAL)
