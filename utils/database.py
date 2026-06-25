import psycopg2
from psycopg2 import pool
import bcrypt
from dotenv import load_dotenv
import os
from contextlib import contextmanager


load_dotenv()

# Database configuration from environment variables 

DATABASE_URL = os.getenv("DATABASE_URL")

# Create connection pool (min 1, max 10 connections)
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        dsn=DATABASE_URL
    )
    
    print("PostgreSQL connection pool created successfully")
except Exception as e:
    print(f"Failed to create connection pool: {e}")
    connection_pool = None


CLERK_MANAGED_PASSWORD = "clerk_managed"


def create_tables():
    """Create database tables if they don't exist."""
    
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        clerk_id VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    resumes_table = """
    CREATE TABLE IF NOT EXISTS resumes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        public_id TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        with get_db_cursor() as cursor:
            cursor.execute(users_table)
            cursor.execute(resumes_table)
            cursor.execute(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS clerk_id VARCHAR(255) UNIQUE"
            )

        print("Tables created successfully")

    except Exception as e:
        print(f"Error creating tables: {e}")

        
@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically handles connection checkout/checkin and commit/rollback.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    if connection_pool is None:
        raise Exception("Database connection pool not initialized")
    
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        connection_pool.putconn(conn)


@contextmanager
def get_db_cursor(commit=True):
    """
    Context manager that provides a cursor directly.
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


# PASSWORD HASHING

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


# USER AUTHENTICATION QUERIES

def create_user(name: str, email: str, password: str) -> dict:
    """
    Create a new user account.
    
    Returns:
        dict with user info if successful, or None if email already exists
    """
    password_hash = hash_password(password)
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, name, email, created_at
                """,
                (name, email, password_hash)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'id':         result[0],
                    'name':       result[1],
                    'email':      result[2],
                    'created_at': result[3]
                }
            return None
    
    except psycopg2.errors.UniqueViolation:
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def authenticate_user(email: str, password: str) -> dict:
    """
    Authenticate a user by email and password.
    
    Returns:
        dict with user info if credentials are valid, None otherwise
    """
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT id, name, email, password_hash FROM users WHERE email = %s",
                (email,)
            )
            result = cursor.fetchone()
            
            if result is None:
                return None
            
            user_id, name, email, password_hash = result
            
            # Verify password
            if verify_password(password, password_hash):
                return {
                    'id':    user_id,
                    'name':  name,
                    'email': email
                }
            
            return None
    
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None


def get_user_by_id(user_id: int) -> dict:
    """Get user information by ID."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT id, name, email, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'id':         result[0],
                    'name':       result[1],
                    'email':      result[2],
                    'created_at': result[3]
                }
            return None
    
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_user_by_email(email: str) -> dict:
    """Get user information by email."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT id, name, email, created_at FROM users WHERE email = %s",
                (email,)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'id':         result[0],
                    'name':       result[1],
                    'email':      result[2],
                    'created_at': result[3]
                }
            return None
    
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_user_by_clerk_id(clerk_id: str) -> dict | None:
    """Get user information by Clerk user ID."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT id, name, email, created_at FROM users WHERE clerk_id = %s",
                (clerk_id,),
            )
            result = cursor.fetchone()

            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "email": result[2],
                    "created_at": result[3],
                }
            return None

    except Exception as e:
        print(f"Error getting user by clerk_id: {e}")
        return None


def get_or_create_user_from_clerk(clerk_id: str, name: str, email: str) -> dict | None:
    """Find or create a local user linked to a Clerk account."""
    user = get_user_by_clerk_id(clerk_id)
    if user:
        return user

    normalized_email = email.strip().lower()
    if not normalized_email:
        return None

    existing = get_user_by_email(normalized_email)
    if existing:
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE users
                    SET clerk_id = %s, name = %s
                    WHERE id = %s
                    RETURNING id, name, email, created_at
                    """,
                    (clerk_id, name, existing["id"]),
                )
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "name": result[1],
                        "email": result[2],
                        "created_at": result[3],
                    }
        except Exception as e:
            print(f"Error linking Clerk user: {e}")
            return None

    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash, clerk_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, email, created_at
                """,
                (name, normalized_email, CLERK_MANAGED_PASSWORD, clerk_id),
            )
            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "email": result[2],
                    "created_at": result[3],
                }
    except psycopg2.errors.UniqueViolation:
        return get_user_by_clerk_id(clerk_id) or get_user_by_email(normalized_email)
    except Exception as e:
        print(f"Error creating Clerk user: {e}")

    return None


# RESUME MANAGEMENT QUERIES

def save_resume(user_id: int, filename: str, file_path: str, public_id: str) -> dict:
    """
    Save a resume for a user.
    If user already has a resume, it will be replaced (UPSERT).
    """

    try:
        with get_db_cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO resumes (user_id, filename, file_path, public_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    filename = EXCLUDED.filename,
                    file_path = EXCLUDED.file_path,
                    public_id = EXCLUDED.public_id,
                    uploaded_at = CURRENT_TIMESTAMP
                RETURNING id, user_id, filename, file_path, public_id, uploaded_at
                """,
                (user_id, filename, file_path, public_id)
            )

            result = cursor.fetchone()

            if result:
                return {
                    'id': result[0],
                    'user_id': result[1],
                    'filename': result[2],
                    'file_path': result[3],
                    'public_id': result[4],
                    'uploaded_at': result[5]
                }

            return None

    except Exception as e:
        print(f"Error saving resume: {e}")
        return None
    
    
def get_user_resume(user_id: int) -> dict:
    """
    Get the resume for a user.
    
    Returns:
        dict with resume info, or None if no resume exists
    """
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                """
                SELECT id, user_id, filename, file_path, public_id, uploaded_at
                FROM resumes
                WHERE user_id = %s
                """,
                (user_id,)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'user_id': result[1],
                    'filename': result[2],
                    'file_path': result[3],
                    'public_id': result[4],
                    'uploaded_at': result[5]
                }
            return None
    
    except Exception as e:
        print(f"Error getting resume: {e}")
        return None


def delete_user_resume(user_id: int) -> bool:
    """
    Delete a user's resume from the database.
    
    Returns:
        True if deleted, False otherwise
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM resumes WHERE user_id = %s RETURNING id",
                (user_id,)
            )
            result = cursor.fetchone()
            return result is not None
    
    except Exception as e:
        print(f"Error deleting resume: {e}")
        return False


# UTILITY QUERIES

def get_all_users():
    """Get all users (for admin/debugging)."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY id")
            results = cursor.fetchall()
            
            return [
                {
                    'id':         row[0],
                    'name':       row[1],
                    'email':      row[2],
                    'created_at': row[3]
                }
                for row in results
            ]
    
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []


def close_all_connections():
    """Close all database connections (call on app shutdown)."""
    if connection_pool:
        connection_pool.closeall()
        print("All database connections closed")
