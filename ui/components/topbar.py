"""Topbar component."""

import customtkinter as ctk


class Topbar(ctk.CTkFrame):
    def __init__(self, parent, theme, title, subtitle):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=theme.fonts["display"],
            text_color=theme.colors["text"],
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=theme.fonts["small"],
            text_color=theme.colors["muted"],
        )
        self.subtitle_label.pack(anchor="w")

    def set_text(self, title, subtitle=""):
        self.title_label.configure(text=title)
        self.subtitle_label.configure(text=subtitle)
