import tkinter as tk
from tkinter import ttk
from typing import Optional

from dynpy.ui.models.uiargs import UiArgs


class ProgressBar(tk.Toplevel):
    def __init__(self, app: tk.Misc):
        args = UiArgs()
        self.app = app.winfo_toplevel()
        self.title("Convert code...")
        self.grid_columnconfigure(**args.grid_args())
        self.grid_rowconfigure(**args.row_args())
        content = tk.Frame(self)
        content.grid(cnf=args.grid_args(padx=10, pady=10))
        content.grid_columnconfigure(**args.column_args())
        content.grid_rowconfigure(**args.row_args())
        self.progress_bar = ttk.Progressbar(
            content,
            orient="horizontal",
            length=300,
            mode="indeterminate",
            maximum=100,
        )
        self.progress_bar.grid(cnf=args.grid_args())
        self.lbl_desc = tk.Label(content, text="Please wait...")
        self.lbl_desc.grid(cnf=args.grid_args())
        self.protocol("WM_DELETE_WINDOW", self.cancel_command)
        self.wm_resizable(False, False)
        self._started = False

    def center_on_app(self):
        self.update_idletasks()
        points = self._app_center_point()
        top_x = int(points[0] - (self.winfo_width() / 2))
        top_y = int(points[1] - (self.winfo_height() / 2))
        self.geometry(f"+{int(top_x)}+{int(top_y)}")

    def _app_center_point(self) -> tuple:
        middle_x = int(self.app.winfo_x() + (self.app.winfo_width() / 2))
        middle_y = int(self.app.winfo_y() + (self.app.winfo_height() / 2))
        return middle_x, middle_y

    def start(self, description: Optional[str] = None):
        """Starts the process bar and placed it in the middle of the parent

        :param master: The parent TK
        :type master: Tk
        """
        if description is not None:
            self.lbl_desc.config(text=description)
        self.center_on_app()
        self.progress_bar.start()
        self.app.config(cursor="exchange")
        self.update()
        self.grab_set()
        self.transient(self.app)

    def cancel_command(self):
        return "break"

    def stop(self):
        """Stops and destroy the process bar"""
        self.progress_bar.stop()
        self.app.config(cursor="arrow")
        self.destroy()
