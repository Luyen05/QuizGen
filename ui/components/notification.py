"""Notification banner."""

import customtkinter as ctk


class NotificationBanner(ctk.CTkFrame):
    def __init__(self, parent, theme, text, variant="info"):
        colors = {
            "info": theme.colors["accent"],
            "success": theme.colors["success"],
            "warning": theme.colors["warning"],
            "danger": theme.colors["danger"],
        }
        super().__init__(parent, fg_color=colors.get(variant, theme.colors["accent"]))
        ctk.CTkLabel(
            self,
            text=text,
            font=theme.fonts["small"],
            text_color=theme.colors["text"],
        ).pack(padx=12, pady=6)
