import tkinter as tk
import traceback
from abc import ABC, abstractmethod
from pathlib import Path
from tkinter import filedialog as dialog
from tkinter import messagebox as msg
from typing import TYPE_CHECKING, Optional, Protocol, Tuple, TypeVar

from dynpy import resources as res
from dynpy.service import IConvertService
from dynpy.ui.models.uiargs import UiArgs

if TYPE_CHECKING:
    from dynpy.ui.app import DynPyAppView

TModel = TypeVar("TModel")


class IView(Protocol[TModel]):
    def get_model(self) -> TModel:
        """Return model with values from view component

        Returns
        -------
        TModel
            The updated model
        """
        ...

    def update_model(self, model: TModel) -> None:
        """Update view with model values

        Update the view components with the values from model.

        Parameters
        ----------
        model : TModel
            the model
        """
        ...


class AAppView(ABC, tk.Frame):
    def __init__(self, master: "DynPyAppView"):
        super().__init__(master)
        self.app = master
        self._init_view()

    @abstractmethod
    def _init_view(self):
        pass

    def _load_icon(self, frame: tk.Frame, icon: res.DynPyResource) -> tk.PhotoImage:
        path = res.icon_path(icon).absolute()
        if not path.exists():
            raise FileNotFoundError(f"Icon file not found: {path}")
        return tk.PhotoImage(master=frame, file=path)

    def _load_config(self, file_path: Path):
        try:
            self.app.service.load_config(file_path)
        except FileNotFoundError:
            msg.showerror("Error", "Configuration file does not exist.")
        except Exception:
            trace = traceback.format_exc()
            msg.showerror("Error", f"An error occurred while loading config file:\n{trace}")

    def ask_for_path(self) -> Optional[Path]:
        service = self.app.service
        file_path = dialog.askopenfilename(
            defaultextension=f".{service.config_extension}",
            filetypes=[("DynPy config", f"*.{service.config_extension}")],
            title="Select a configuration file",
            initialdir=Path.home(),
        )
        if file_path is None or file_path == "":
            return None
        return Path(file_path)

    def _on_button_click(self, event):
        if self.btn_view is None or event.widget != self.btn_view:
            return
        self._button_command()

    @abstractmethod
    def _button_command(self):
        pass

    @abstractmethod
    def _button_text_and_icon(self) -> Tuple[str, res.DynPyResource]:
        pass

    def button(self, frame: tk.Frame) -> tk.Button:
        text, icon = self._button_text_and_icon()
        self.image = self._load_icon(frame, icon)
        self.btn_view = tk.Button(
            frame, text=text, command=self._button_command, image=self.image, compound=tk.TOP
        )
        self.btn_view.bind("<Button-1>", self._on_button_click)
        return self.btn_view

    @abstractmethod
    def update_service(self, service: IConvertService) -> bool:
        """Update the service

        Update the service with the view values.

        Parameters
        ----------
        service : IConvertService
            The service

        Returns
        -------
        bool
            True if the service was updated successfully
        """
        pass

    @abstractmethod
    def update_view(self) -> None:
        pass

    def show(self, args: UiArgs) -> None:
        """Show the view

        Show the view and update the view with the model values if provided.

        Parameters
        ----------
        args : UiArgs
            The ui arguments for the view
        """
        self.grid(cnf=args.grid_args())

    def hide(self) -> None:
        """Hide the view"""
        self.grid_forget()
