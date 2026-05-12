"""Progress components."""

import customtkinter as ctk


class GlowProgressBar(ctk.CTkProgressBar):
    def __init__(self, parent, theme, **kwargs):
        super().__init__(
            parent,
            fg_color=theme.colors["surface"],
            progress_color=theme.colors["accent"],
            border_color=theme.colors["border"],
            border_width=0,
            corner_radius=theme.radius["sm"],
            **kwargs,
        )
