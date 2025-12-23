import tkinter as tk
from tkinter import ttk, messagebox

# ===== COLORS (MATCH DASHBOARD CARDS) =====
BG = "#1e293b"
ENTRY_BG = "#020617"
TEXT = "#e5e7eb"
ACCENT = "#6366f1"

PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Pending", "Completed"]
CATEGORIES = ["General", "Work", "Personal", "Others"]


class TaskDialog(tk.Toplevel):
    def __init__(self, parent, title="Add Task", initial=None):
        super().__init__(parent)
        self.result = None
        self.initial = initial or {}

        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.geometry("420x520")

        self._build()
        self.grab_set()

    def _build(self):
        container = tk.Frame(self, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        def label(text):
            tk.Label(container, text=text, fg=TEXT, bg=BG,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 3))

        def entry(var):
            e = tk.Entry(container, textvariable=var,
                         bg=ENTRY_BG, fg=TEXT,
                         insertbackground=TEXT,
                         relief=tk.FLAT)
            e.pack(fill=tk.X, ipady=6)
            return e

        # ===== FIELDS =====
        self.title_var = tk.StringVar(value=self.initial.get("TITLE", ""))
        label("Title")
        entry(self.title_var)

        self.desc_var = tk.StringVar(value=self.initial.get("DESCRIPTION", ""))
        label("Description")
        entry(self.desc_var)

        self.due_var = tk.StringVar(value=self.initial.get("DUE_DATE", ""))
        label("Due Date (YYYY-MM-DD)")
        entry(self.due_var)

        self.cat_var = tk.StringVar(value=self.initial.get("CATEGORY", "General"))
        label("Category")
        ttk.Combobox(
            container, values=CATEGORIES,
            textvariable=self.cat_var,
            state="readonly"
        ).pack(fill=tk.X, ipady=3)

        self.priority_var = tk.StringVar(value=self.initial.get("PRIORITY", "Medium"))
        label("Priority")
        ttk.Combobox(
            container, values=PRIORITIES,
            textvariable=self.priority_var,
            state="readonly"
        ).pack(fill=tk.X, ipady=3)

        self.status_var = tk.StringVar(value=self.initial.get("STATUS", "Pending"))
        label("Status")
        ttk.Combobox(
            container, values=STATUSES,
            textvariable=self.status_var,
            state="readonly"
        ).pack(fill=tk.X, ipady=3)

        # ===== SAVE BUTTON =====
        tk.Button(
            container, text="Save",
            bg=ACCENT, fg="white",
            relief=tk.FLAT,
            font=("Segoe UI", 11, "bold"),
            command=self._save
        ).pack(pady=25, fill=tk.X)

    def _save(self):
        if not self.title_var.get().strip():
            messagebox.showwarning("Validation", "Title is required")
            return
        # Lowercase keys for DB adapter expectation
        self.result = {
            "title": self.title_var.get().strip(),
            "description": self.desc_var.get().strip(),
            "due_date": self.due_var.get().strip() or None,
            "priority": self.priority_var.get(),
            "category": self.cat_var.get().strip(),
            "status": self.status_var.get(),
        }
        self.destroy()
