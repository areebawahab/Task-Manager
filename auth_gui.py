import tkinter as tk
from tkinter import messagebox
from auth_db import AuthDB
from gui import TaskManagerGUI

# ---------- THEME ----------
BG = "#0f172a"
CARD = "#1e293b"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
ACCENT = "#6366f1"
ENTRY_BG = "#020617"


class AuthWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager – Authentication")
        self.geometry("420x480")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.db = AuthDB()
        self.container = None

        self.show_register()

    # ---------- HELPERS ----------
    def clear(self):
        if self.container:
            self.container.destroy()

    def card(self, title):
        self.container = tk.Frame(self, bg=CARD)
        self.container.place(relx=0.5, rely=0.5, anchor="center",
                             width=360, height=400)

        tk.Label(
            self.container, text=title,
            bg=CARD, fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(pady=20)

        return self.container

    def entry(self, parent, label, var, show=None):
        tk.Label(parent, text=label, bg=CARD, fg=MUTED).pack(anchor="w", padx=30)
        e = tk.Entry(
            parent, textvariable=var,
            bg=ENTRY_BG, fg=TEXT,
            insertbackground=TEXT,
            relief=tk.FLAT, show=show
        )
        e.pack(fill=tk.X, padx=30, pady=6, ipady=6)
        return e

    # ================= REGISTER =================
    def show_register(self):
        self.clear()
        card = self.card("Register")

        self.reg_email = tk.StringVar()
        self.reg_pass = tk.StringVar()
        self.show_pass = tk.BooleanVar()

        self.entry(card, "Email", self.reg_email)
        self.pass_entry = self.entry(card, "Password", self.reg_pass, show="*")

        tk.Checkbutton(
            card, text="Show password",
            variable=self.show_pass,
            command=self.toggle_password,
            bg=CARD, fg=MUTED, selectcolor=CARD,
            activebackground=CARD
        ).pack(anchor="w", padx=30)

        tk.Button(
            card, text="Register",
            bg=ACCENT, fg="white",
            relief=tk.FLAT, command=self.register
        ).pack(pady=18, ipadx=20, ipady=6)

        tk.Button(
            card, text="Already have an account? Login",
            bg=CARD, fg=ACCENT,
            relief=tk.FLAT, command=self.show_login
        ).pack()

    def register(self):
        email = self.reg_email.get().strip()
        password = self.reg_pass.get().strip()

        if not email or not password:
            messagebox.showwarning("Validation", "Email and password required")
            return

        try:
            ok = self.db.register(email, password)
            if ok:
                messagebox.showinfo("Success", "Registration successful")
                self.show_login()
            else:
                messagebox.showerror("Error", "Email already registered")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= LOGIN =================
    def show_login(self):
        self.clear()
        card = self.card("Login")

        self.login_email = tk.StringVar()
        self.login_pass = tk.StringVar()
        self.show_pass = tk.BooleanVar()

        self.entry(card, "Email", self.login_email)
        self.pass_entry = self.entry(card, "Password", self.login_pass, show="*")

        tk.Checkbutton(
            card, text="Show password",
            variable=self.show_pass,
            command=self.toggle_password,
            bg=CARD, fg=MUTED, selectcolor=CARD,
            activebackground=CARD
        ).pack(anchor="w", padx=30)

        tk.Button(
            card, text="Login",
            bg=ACCENT, fg="white",
            relief=tk.FLAT, command=self.login
        ).pack(pady=18, ipadx=20, ipady=6)

        tk.Button(
            card, text="Don’t have an account? Register",
            bg=CARD, fg=ACCENT,
            relief=tk.FLAT, command=self.show_register
        ).pack()

    def login(self):
        email = self.login_email.get().strip()
        password = self.login_pass.get().strip()
        if self.db.login(email, password):
            self.destroy()
            TaskManagerGUI(user_email=email).mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password")

    def toggle_password(self):
        self.pass_entry.config(show="" if self.show_pass.get() else "*")


# ---------- RUN ----------
if __name__ == "__main__":
    AuthWindow().mainloop()
