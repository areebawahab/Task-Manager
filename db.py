import oracledb
from datetime import datetime


class TaskDB:
    def __init__(self):
        self.conn = oracledb.connect(
            user="system",
            password="system",
            dsn="localhost:1522/XE"
        )
        self._create_tables()
        self._ensure_user_email_column()

    def _create_tables(self):
        """
        Oracle does not support CREATE TABLE IF NOT EXISTS.
        We safely ignore ORA-00955 (name already exists).
        """
        cur = self.conn.cursor()
        try:
            cur.execute("""
            CREATE TABLE tasks (
                id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_email VARCHAR2(200) NOT NULL,
                title VARCHAR2(200) NOT NULL,
                description CLOB,
                due_date DATE,
                priority VARCHAR2(20),
                category VARCHAR2(50),
                status VARCHAR2(20)
            )
            """)
            self.conn.commit()
        except oracledb.DatabaseError as e:
            error, = e.args
            if error.code != 955:  # ORA-00955: name already used
                raise

    def _ensure_user_email_column(self):
        """
        If the table already existed without user_email or other columns,
        try adding them. Ignore errors if they already exist.
        """
        cur = self.conn.cursor()

        def safe_add(column_sql):
            try:
                cur.execute(f"ALTER TABLE tasks ADD ({column_sql})")
                self.conn.commit()
            except oracledb.DatabaseError:
                # Ignore if column already exists or other non-critical issues
                pass

        safe_add("user_email VARCHAR2(200) NOT NULL")
        safe_add("title VARCHAR2(200) NOT NULL")
        safe_add("description CLOB")
        safe_add("due_date DATE")
        safe_add("priority VARCHAR2(20)")
        safe_add("category VARCHAR2(50)")
        safe_add("status VARCHAR2(20)")

    # ================= CRUD =================

    def add_task(self, task, user_email):
        """
        task keys expected (lowercase): title, description, due_date, priority, category, status
        """
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO tasks
        (user_email, title, description, due_date, priority, category, status)
        VALUES (:user_email, :title, :description, :due_date, :priority, :category, :status)
        """, {
            "user_email": user_email,
            "title": task.get("title", ""),
            "description": task.get("description", ""),
            "due_date": self._parse_date(task.get("due_date")),
            "priority": task.get("priority", "Medium"),
            "category": task.get("category", "General"),
            "status": task.get("status", "Pending"),
        })
        self.conn.commit()

    def update_task(self, task_id, task, user_email):
        cur = self.conn.cursor()
        cur.execute("""
        UPDATE tasks
        SET title = :title,
            description = :description,
            due_date = :due_date,
            priority = :priority,
            category = :category,
            status = :status
        WHERE id = :id AND user_email = :user_email
        """, {
            "title": task.get("title", ""),
            "description": task.get("description", ""),
            "due_date": self._parse_date(task.get("due_date")),
            "priority": task.get("priority", "Medium"),
            "category": task.get("category", "General"),
            "status": task.get("status", "Pending"),
            "id": task_id,
            "user_email": user_email
        })
        self.conn.commit()

    def delete_task(self, task_id, user_email):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = :id AND user_email = :user_email",
                    {"id": task_id, "user_email": user_email})
        self.conn.commit()

    def get_tasks(self, user_email):
        """
        Returns tasks for a specific user, sorted by priority (High > Medium > Low) then newest first.
        """
        cur = self.conn.cursor()
        cur.execute("""
        SELECT id, title, description, due_date, priority, category, status
        FROM tasks
        WHERE user_email = :user_email
        ORDER BY
            CASE priority
                WHEN 'High' THEN 3
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 1
                ELSE 0
            END DESC,
            id DESC
        """, {"user_email": user_email})

        rows = cur.fetchall()
        return [
            {
                "ID": r[0],
                "TITLE": r[1],
                "DESCRIPTION": r[2],
                "DUE_DATE": r[3].strftime("%Y-%m-%d") if r[3] else "",
                "PRIORITY": r[4],
                "CATEGORY": r[5],
                "STATUS": r[6]
            }
            for r in rows
        ]

    # ================= HELPERS =================

    def _parse_date(self, date_str):
        """
        Converts 'YYYY-MM-DD' string to datetime for Oracle DATE type
        """
        if not date_str:
            return None
        return datetime.strptime(date_str, "%Y-%m-%d")
   