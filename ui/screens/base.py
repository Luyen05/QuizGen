"""Base screen for shared layout."""

import customtkinter as ctk

from ui.layouts.app_layout import AppLayout


class BaseScreen(ctk.CTkFrame):
    def __init__(self, parent, controller, name, title, subtitle):
        theme = controller.theme
        super().__init__(parent, fg_color=theme.colors["bg"])
        self.controller = controller
        self.theme = theme
        self.name = name

        self.layout = AppLayout(self, controller, name, title, subtitle)
        self.layout.pack(fill="both", expand=True)
        self.content = self.layout.content

    def on_enter(self):
        """Hook when screen is shown."""
        return None
