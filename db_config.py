"""PostgreSQL settings for Lab 11.

Values are read from environment variables (or a local .env file).  The password
is deliberately not stored in this source file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

DB_SETTINGS = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "Team_28_DBMS"),
    "user": os.getenv("DB_USER", "hetpethani"),
    "password": os.getenv("DB_PASSWORD", ""),
}
