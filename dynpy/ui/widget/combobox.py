import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk
from typing import List, Optional

from dynpy.ui.convert.controller import ConvertController


class ConvertBox(ABC, ttk.Combobox):
    def __init__(self, master: tk.Misc, controller: ConvertController) -> None:
        super().__init__(master)
        self.controller = controller
        self.config(state="readonly")
        self.bind("<<ComboboxSelected>>", self._selected_event)

    @abstractmethod
    def _get_values(self) -> List[str]:
        pass

    @abstractmethod
    def _selected_event(self, event: tk.Event) -> Optional[str]:
        pass

    def reset(self):
        self.config(values=self._get_values())


class SourceBox(ConvertBox):
    def _get_values(self) -> List[str]:
        return self.controller.source_configs()

    def _selected_event(self, event: tk.Event) -> Optional[str]:
        if self != event.widget:
            return
        selected = self.selection_get()
        self.controller.select_source_config(selected)
        return "break"


class DirectionBox(ConvertBox):
    def reset(self):
        super().reset()
        self.set(self._get_values()[0])

    def _get_values(self) -> List[str]:
        return self.controller.direction_values()

    def _selected_event(self, event: tk.Event) -> Optional[str]:
        if self != event.widget:
            return
        selected = self.selection_get()
        self.controller.select_direction(selected)
        return "break"
