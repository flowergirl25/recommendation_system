from datetime import datetime
from app.config.db_connection import connecting_db
from app.utils.logging_decorator import log_call
import pymysql.cursors

class User:
    def __init__(self, email: str, first_name: str, last_name: str, password: str, role: str = "user"):
        self.email = email
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.name = f"{self.first_name} {self.last_name}".strip()
        self.password = password
        self.role = role
        self.is_active = True
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    # Table setup
    @staticmethod
    def create_table():
        """Create users table if not exists."""
        conn = connecting_db()
        cursor = conn.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(100) PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            name VARCHAR(100),
            password VARCHAR(255) NOT NULL,
            role ENUM('admin', 'user') DEFAULT 'user',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        cursor.execute(sql)
        conn.commit()
        conn.close()
        print("Users table ready in database")

    # CRUD Operations
    def save(self):
        """Insert new user into DB."""
        conn = connecting_db()
        cursor = conn.cursor()
        sql = """
        INSERT INTO users (
            email, first_name, last_name, name, 
            password, role, is_active
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            self.email,
            self.first_name,
            self.last_name,
            self.name,
            self.password,
            self.role,
            self.is_active
        ))
        conn.commit()
        conn.close()
        print(f"User {self.email} created successfully")

    @staticmethod
    @log_call(log_args=True, log_result=False)
    def fetch_by_email(email):
        """Fetch user by email."""
        conn = connecting_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    @log_call(log_args=True, log_result=False)
    def fetch_all(active_only=True):
        """Fetch all (optionally active) users."""
        conn = connecting_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if active_only:
            cursor.execute("SELECT * FROM users WHERE is_active=TRUE")
        else:
            cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        return users

    @staticmethod
    def update_profile(email, first_name=None, last_name=None,password=None):
        """Update user name and/or password."""
        conn = connecting_db()
        cursor = conn.cursor()
        updates = []
        values = []

        if first_name:
            updates.append("name=%s")
            values.append(first_name)
        if last_name:
            updates.append("name=%s")
            values.append(last_name)
        if password:
            updates.append("password=%s")
            values.append(password)
        if not updates:
            print("No updates provided.")
            return

        updates.append("updated_at=%s")
        values.append(datetime.now())
        values.append(email)

        sql = f"UPDATE users SET {', '.join(updates)} WHERE email=%s"
        cursor.execute(sql, tuple(values))
        conn.commit()
        conn.close()
        print(f"Profile updated for {email}")

    @staticmethod
    def update_role(email, new_role):
        """Update user role."""
        conn = connecting_db()
        cursor = conn.cursor()
        sql = "UPDATE users SET role=%s, updated_at=%s WHERE email=%s"
        cursor.execute(sql, (new_role, datetime.now(), email))
        conn.commit()
        conn.close()
        print(f"Role updated for {email} -> {new_role}")

    @staticmethod
    def deactivate(email):
        """Deactivate user (soft delete)."""
        conn = connecting_db()
        cursor = conn.cursor()
        sql = "UPDATE users SET is_active=FALSE, updated_at=%s WHERE email=%s"
        cursor.execute(sql, (datetime.now(), email))
        conn.commit()
        conn.close()
        print(f"User {email} deactivated")

    @staticmethod
    def activate(email):
        """Reactivate user."""
        conn = connecting_db()
        cursor = conn.cursor()
        sql = "UPDATE users SET is_active=TRUE, updated_at=%s WHERE email=%s"
        cursor.execute(sql, (datetime.now(), email))
        conn.commit()
        conn.close()
        print(f"User {email} reactivated")

 