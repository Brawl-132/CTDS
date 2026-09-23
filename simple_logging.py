import os
import logging
from logging.handlers import RotatingFileHandler

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

def setup_simple_logging():
    """Setup simple three-file logging system"""
    
    # =====================
    # App Logger
    # =====================
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    app_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=3,
        encoding="utf-8"
    )
    app_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    if not app_logger.handlers:
        app_logger.addHandler(app_handler)
    
    # =====================
    # Database Logger
    # =====================
    db_logger = logging.getLogger("sqlalchemy.engine")
    db_logger.setLevel(logging.INFO)
    
    db_handler = RotatingFileHandler(
        "logs/database.log",
        maxBytes=20*1024*1024,  # 20 MB
        backupCount=2,
        encoding="utf-8"
    )
    db_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    if not db_logger.handlers:
        db_logger.addHandler(db_handler)

    # =====================
    # Backup Logger
    # =====================
    backup_logger = logging.getLogger("backup")
    backup_logger.setLevel(logging.INFO)
    
    backup_handler = RotatingFileHandler(
        "logs/backup.log",
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    backup_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    if not backup_logger.handlers:
        backup_logger.addHandler(backup_handler)
    
    return app_logger, db_logger, backup_logger


# Initialize logging
app_logger, db_logger, backup_logger = setup_simple_logging()


# =====================
# Helper functions
# =====================
def log_app(message: str, level: str = "INFO"):
    """Log application messages"""
    level = level.upper()
    if level == "ERROR":
        app_logger.error(message)
    elif level == "WARNING":
        app_logger.warning(message)
    else:
        app_logger.info(message)

def log_db(message: str):
    """Log database messages"""
    db_logger.info(message)

def log_backup(message: str, level: str = "INFO"):
    """Log backup task messages"""
    level = level.upper()
    if level == "ERROR":
        backup_logger.error(message)
    elif level == "WARNING":
        backup_logger.warning(message)
    else:
        backup_logger.info(message)