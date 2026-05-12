"""Reusable button components."""

import customtkinter as ctk


class AppButton(ctk.CTkButton):
    def __init__(self, parent, theme, text, command=None, variant="primary", **kwargs):
        colors = theme.colors
        if variant == "primary":
            fg = colors["primary"]
            hover = colors["accent"]
            text_color = colors["text"]
        elif variant == "secondary":
            fg = colors["surface"]
            hover = colors["card"]
            text_color = colors["text"]
        elif variant == "ghost":
            fg = "transparent"
            hover = colors["surface"]
            text_color = colors["muted"]
        elif variant == "danger":
            fg = colors["danger"]
            hover = colors["accent"]
            text_color = colors["text"]
        else:
            fg = colors["primary"]
            hover = colors["accent"]
            text_color = colors["text"]

        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            corner_radius=theme.radius["md"],
            font=theme.fonts["body"],
            **kwargs,
        )

    def set_loading(self, loading: bool, loading_text="Đang xử lý..."):
        if loading:
            self.configure(state="disabled", text=loading_text)
        else:
            self.configure(state="normal")
