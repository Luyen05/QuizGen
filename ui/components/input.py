"""Input components."""

import customtkinter as ctk


class TextInput(ctk.CTkEntry):
    def __init__(self, parent, theme, placeholder="", **kwargs):
        super().__init__(
            parent,
            placeholder_text=placeholder,
            fg_color=theme.colors["surface"],
            text_color=theme.colors["text"],
            placeholder_text_color=theme.colors["muted"],
            border_color=theme.colors["border"],
            border_width=1,
            corner_radius=theme.radius["md"],
            font=theme.fonts["body"],
            **kwargs,
        )


class TextArea(ctk.CTkTextbox):
    def __init__(self, parent, theme, **kwargs):
        super().__init__(
            parent,
            fg_color=theme.colors["surface"],
            text_color=theme.colors["text"],
            border_color=theme.colors["border"],
            border_width=1,
            corner_radius=theme.radius["md"],
            font=theme.fonts["body"],
            **kwargs,
        )
