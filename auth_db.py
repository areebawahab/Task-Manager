import hashlib
import oracledb

class AuthDB:
    def __init__(self):
        self.conn = oracledb.connect(
            user="system",
            password="system",
            dsn="localhost:1522/XE"
        )

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, email, password):
        password_hash = self.hash_password(password)
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users1122 (email, password_hash)
                VALUES (:1, :2)
                """,
                (email, password_hash)
            )
            self.conn.commit()
            return True
        except oracledb.IntegrityError:
            return False
        finally:
            cursor.close()

    def login(self, email, password):
        password_hash = self.hash_password(password)
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT id FROM users1122
            WHERE email = :1 AND password_hash = :2
            """,
            (email, password_hash)
        )

        user = cursor.fetchone()
        cursor.close()
        return user is not None
