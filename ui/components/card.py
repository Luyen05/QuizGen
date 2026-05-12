"""Reusable card components."""

import customtkinter as ctk


class Card(ctk.CTkFrame):
    def __init__(self, parent, theme, radius=None, fg_color=None, border_color=None, **kwargs):
        corner = radius if radius is not None else theme.radius["lg"]
        bg_color = fg_color if fg_color is not None else theme.colors["card"]
        border = border_color if border_color is not None else theme.colors["border"]
        super().__init__(
            parent,
            fg_color=bg_color,
            border_color=border,
            border_width=1,
            corner_radius=corner,
            **kwargs,
        )


class GlassCard(ctk.CTkFrame):
    def __init__(self, parent, theme, radius=None, fg_color=None, border_color=None, **kwargs):
        corner = radius if radius is not None else theme.radius["lg"]
        bg_color = fg_color if fg_color is not None else theme.colors["surface"]
        border = border_color if border_color is not None else theme.colors["border"]
        super().__init__(
            parent,
            fg_color=bg_color,
            border_color=border,
            border_width=1,
            corner_radius=corner,
            **kwargs,
        )
