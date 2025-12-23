import tkinter as tk
from tkinter import ttk, messagebox
from dialogs import TaskDialog
from db import TaskDB

# ================= COLORS =================
BG = "#0f172a"
SIDEBAR = "#020617"
CARD = "#1e293b"
TEXT = "#e5e7eb"
ACCENT = "#6366f1"
ENTRY = "#020617"


class TaskManagerGUI(tk.Tk):
    def __init__(self, user_email):
        super().__init__()

        self.title("Task Manager")
        self.geometry("1200x700")
        self.configure(bg=BG)

        self.user_email = user_email
        self.db = TaskDB()
        self.tasks = []
        self.current_category = None

        self._layout()
        self.load_tasks()

    # ========== LAYOUT ==========
    def _layout(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._sidebar_profile()
        self._sidebar_menu()
        self._main_header()
        self._dashboard()
        self._search_bar()
        self._task_table()

    # ========== SIDEBAR ==========
    def _sidebar_profile(self):
        f = tk.Frame(self.sidebar, bg=SIDEBAR)
        f.pack(fill=tk.X, pady=20)

        tk.Label(
            f,
            text=self.user_email,
            fg=TEXT,
            bg=SIDEBAR,
            font=("Segoe UI", 11, "bold"),
            wraplength=180,
            justify="left"
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            f,
            text="⎋ Logout",
            fg=TEXT,
            bg=SIDEBAR,
            activebackground=CARD,
            activeforeground=TEXT,
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            command=self.logout
        ).pack(side=tk.RIGHT, padx=15)

    def _sidebar_menu(self):
        tk.Button(
            self.sidebar,
            text="📋 Tasks",
            bg=SIDEBAR,
            fg=TEXT,
            relief=tk.FLAT,
            command=self.show_categories
        ).pack(fill=tk.X, padx=20, pady=10)

        self.cat_frame = tk.Frame(self.sidebar, bg=SIDEBAR)
        self.cat_frame.pack(fill=tk.X, padx=10)

    # ========== MAIN ==========
    def _main_header(self):
        h = tk.Frame(self.main, bg=BG)
        h.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            h,
            text="Dashboard",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 18, "bold")
        ).pack(side=tk.LEFT)

        tk.Button(
            h,
            text="+ Add Task",
            bg=ACCENT,
            fg="white",
            relief=tk.FLAT,
            command=self.add_task
        ).pack(side=tk.RIGHT)

    def _dashboard(self):
        d = tk.Frame(self.main, bg=BG)
        d.pack(fill=tk.X, padx=20)

        self.total_lbl = self._stat_card(d, "Total", 0)
        self.done_lbl = self._stat_card(d, "Completed", 1)
        self.pending_lbl = self._stat_card(d, "Pending", 2)

    def _stat_card(self, parent, text, col):
        c = tk.Frame(parent, bg=CARD, padx=20, pady=10)
        c.grid(row=0, column=col, padx=10)

        tk.Label(c, text=text, fg=TEXT, bg=CARD).pack()

        lbl = tk.Label(
            c,
            text="0",
            fg=ACCENT,
            bg=CARD,
            font=("Segoe UI", 16, "bold")
        )
        lbl.pack()
        return lbl

    def _search_bar(self):
        f = tk.Frame(self.main, bg=BG)
        f.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(f, text="Search:", fg=TEXT, bg=BG).pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.filter_search())

        tk.Entry(
            f,
            textvariable=self.search_var,
            bg=ENTRY,
            fg=TEXT,
            insertbackground=TEXT
        ).pack(side=tk.LEFT, padx=10)

    # ========== TASK TABLE ==========
    def _task_table(self):
        f = tk.Frame(self.main, bg=BG)
        f.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        cols = ("ID", "Title", "Description", "Due", "Priority", "Category", "Status")
        self.tree = ttk.Treeview(f, columns=cols, show="headings")

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=CARD,
            foreground=TEXT,
            fieldbackground=CARD,
            rowheight=25
        )
        style.map("Treeview", background=[("selected", ACCENT)])

        for c in cols:
            self.tree.heading(c, text=c)
            # Give sensible widths; allow overflow horizontally
            width = 100
            if c == "Title":
                width = 220
            elif c == "Description":
                width = 300
            elif c == "Due":
                width = 120
            elif c == "Category":
                width = 140
            elif c == "Priority":
                width = 120
            elif c == "Status":
                width = 120
            self.tree.column(c, anchor="center", width=width, stretch=False)

        # Add horizontal scrollbar
        scroll_x = tk.Scrollbar(f, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=scroll_x.set)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        btns = tk.Frame(self.main, bg=BG)
        btns.pack(pady=10)

        tk.Button(btns, text="Edit", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Delete", command=self.delete_task).pack(side=tk.LEFT, padx=5)

    # ========== CORE LOGIC ==========
    def load_tasks(self):
        self.tasks = self.db.get_tasks(self.user_email)
        self.refresh_table(self.tasks)

        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["STATUS"] == "Completed")

        self.total_lbl.config(text=total)
        self.done_lbl.config(text=done)
        self.pending_lbl.config(text=total - done)

        self.show_categories()

    def refresh_table(self, data):
        self.tree.delete(*self.tree.get_children())
        for t in data:
            self.tree.insert("", "end", values=(
                t["ID"],
                t["TITLE"],
                t.get("DESCRIPTION", ""),
                t["DUE_DATE"],
                t["PRIORITY"],
                t["CATEGORY"],
                t["STATUS"]
            ))

    # ========== TASK CRUD ==========
    def add_task(self):
        d = TaskDialog(self, "Add Task")
        # Wait for dialog to close
        self.wait_window(d)
        if d.result:
            self.db.add_task(d.result, self.user_email)
            messagebox.showinfo(
                "Task Added",
                f"Task '{d.result['title']}' added to category '{d.result['category']}'"
            )
            self.load_tasks()
            # If a category is selected, keep the filter applied
            if self.current_category:
                self.filter_category(self.current_category)

    def edit_task(self):
        sel = self.tree.focus()
        if not sel:
            return

        tid = self.tree.item(sel)["values"][0]
        task = next(t for t in self.tasks if t["ID"] == tid)

        d = TaskDialog(self, "Edit Task", task)
        self.wait_window(d)
        if d.result:
            self.db.update_task(tid, d.result, self.user_email)
            self.load_tasks()
            if self.current_category:
                self.filter_category(self.current_category)

    def delete_task(self):
        sel = self.tree.focus()
        if not sel:
            return

        tid = self.tree.item(sel)["values"][0]
        if messagebox.askyesno("Delete", "Delete this task?"):
            self.db.delete_task(tid, self.user_email)
            self.load_tasks()
            if self.current_category:
                self.filter_category(self.current_category)

    # ========== CATEGORY ==========
    def show_categories(self):
        for w in self.cat_frame.winfo_children():
            w.destroy()

        categories = sorted(
            set(t["CATEGORY"] for t in self.tasks if t["CATEGORY"])
        )

        for c in categories:
            count = sum(1 for t in self.tasks if t["CATEGORY"] == c)
            tk.Button(
                self.cat_frame,
                text=f"{c} ({count})",
                bg=CARD,
                fg=TEXT,
                relief=tk.FLAT,
                command=lambda x=c: self.filter_category(x)
            ).pack(fill=tk.X, pady=3)

    def filter_category(self, cat):
        self.current_category = cat
        filtered = [t for t in self.tasks if t["CATEGORY"] == cat]
        self.refresh_table(filtered)

    # ========== SEARCH ==========
    def filter_search(self):
        q = self.search_var.get().lower()
        base = self.tasks
        if self.current_category:
            base = [t for t in self.tasks if t["CATEGORY"] == self.current_category]
        self.refresh_table([t for t in base if q in t["TITLE"].lower()])

    # ========== LOGOUT ==========
    def logout(self):
        self.destroy()
        from auth_gui import AuthWindow
        AuthWindow().mainloop()


# ========== RUN ==========
if __name__ == "__main__":
    TaskManagerGUI("test@example.com").mainloop()
