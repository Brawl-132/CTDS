import os
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

load_dotenv()

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)


# Simple Database Logger
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)

# Simple database file handler
file_handler = RotatingFileHandler(
    "logs/database.log",
    maxBytes=20*1024*1024,  
    backupCount=2,
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)


# Database URLs
MYSQL_URL = os.getenv("DATABASE_URL")
SQLITE_URL = "sqlite:///orders.db"


# Engine creation with fallback
def create_db_engine():
    """Try MySQL first, fallback to SQLite if unavailable."""
    if MYSQL_URL:
        try:
            engine = create_engine(MYSQL_URL, echo=False)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).scalar()  # test connection
            logger.info("✅ Connected to MySQL!")
            return engine
        except OperationalError as e:
            logger.warning(f"⚠️ MySQL not available ({e}), falling back to SQLite...")
    else:
        logger.info("No MySQL URL provided, using SQLite fallback.")
    engine = create_engine(SQLITE_URL, echo=False)
    logger.info("✅ Using SQLite database.")
    return engine

# Engine
engine = create_db_engine()
# Initialize DB
def init_db():
    SQLModel.metadata.create_all(engine)
    logger.info("🗄️ Database tables created/verified.")

# Session generator

def get_session():
    """Yields a SQLModel session for FastAPI routes."""
    with Session(engine) as session:
        yield session
