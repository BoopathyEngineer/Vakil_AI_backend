import os
import logging
from dotenv import load_dotenv
load_dotenv(override=True)

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import URL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

logger.info(f"Connecting to database...")

# Create engine with SSL requirements for Neon PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Add event listeners for connection debugging
@event.listens_for(engine, 'connect')
def receive_connect(dbapi_connection, connection_record):
    logger.info('Database connection established')

@event.listens_for(engine, 'checkout')
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    logger.info('Database connection retrieved from pool')

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Test the database connection
try:
    with engine.connect() as connection:
        logger.info("Successfully connected to the database!")
except Exception as e:
    logger.error(f"Error connecting to the database: {str(e)}")
    raise

def get_db():
    session = SessionLocal(bind=engine)
    try:
        yield session
    finally:
        session.close()