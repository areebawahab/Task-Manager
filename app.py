from auth_gui import AuthWindow
from gui import TaskManagerGUI

auth = AuthWindow()
auth.mainloop()

if auth.username:
    app = TaskManagerGUI(auth.username)
    app.mainloop()
