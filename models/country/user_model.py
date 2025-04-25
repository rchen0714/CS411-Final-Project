from dataclasses import dataclass
import logging
import os
import sqlite3
import bcrypt

from utils.logger import configure_logger
from utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class User:
    id: int
    username: str
    salt: str
    hashed_password: str

def create_user(username: str, password: str) -> None:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Users (username, salt, hashed_password)
                VALUES (?, ?, ?)
            """, (username, salt, hashed_password))
            conn.commit()
            logger.info("User created successfully: %s", username)
    except sqlite3.IntegrityError:
        logger.error("User with username '%s' already exists.", username)
        raise ValueError(f"User '{username}' already exists.")
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def login(username: str, password: str) -> bool:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT salt, hashed_password FROM Users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                salt, hashed = row
                if hashed == bcrypt.hashpw(password.encode('utf-8'), salt):
                    logger.info("Login successful for user %s", username)
                    return True
                else:
                    logger.info("Incorrect password for user %s", username)
                    return False
            else:
                raise ValueError(f"User '{username}' not found.")
    except sqlite3.Error as e:
        logger.error("Database error during login for '%s': %s", username, str(e))
        raise e

def update_password(username: str, new_password: str) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT salt FROM Users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                salt = row[0]
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
                cursor.execute("UPDATE Users SET hashed_password = ? WHERE username = ?", (new_hash, username))
                conn.commit()
                logger.info("Password updated for user %s", username)
            else:
                raise ValueError(f"User '{username}' not found.")
    except sqlite3.Error as e:
        logger.error("Database error while updating password for '%s': %s", username, str(e))
        raise e

def clear_users() -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS Users;")
            cursor.execute("""
                CREATE TABLE Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    salt BLOB NOT NULL,
                    hashed_password BLOB NOT NULL
                );
            """)
            conn.commit()
            logger.info("Users table reset.")
    except sqlite3.Error as e:
        logger.error("Error clearing users: %s", str(e))
        raise e