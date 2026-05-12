"""
ui/theme/theme_manager.py
ThemeManager quản lý màu sắc, font, spacing và radius.
"""

from __future__ import annotations

import customtkinter as ctk


class ThemeManager:
    def __init__(self):
        self.colors = {
            "bg": "#111111",
            "surface": "#1A1A1A",
            "card": "#202020",
            "card_alt": "#1D1D1D",
            "card_purple": "#241F32",
            "card_violet": "#221A2E",
            "card_blue": "#1F2436",
            "card_cyan": "#1C2A2E",
            "card_green": "#1F2B24",
            "card_orange": "#2B241F",
            "card_red": "#2B2024",
            "sidebar": "#151515",
            "primary": "#8B5CF6",
            "accent": "#A855F7",
            "accent_blue": "#6366F1",
            "success": "#22C55E",
            "danger": "#EF4444",
            "warning": "#FACC15",
            "border": "#2A2A2A",
            "text": "#FFFFFF",
            "muted": "#B3B3B3",
            "shadow": "#0B0B0B",
        }

        self.radius = {
            "sm": 10,
            "md": 14,
            "lg": 18,
            "xl": 22,
        }

        self.spacing = {
            "xs": 6,
            "sm": 10,
            "md": 16,
            "lg": 24,
            "xl": 32,
        }

        self.fonts = {
            "display": ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            "title": ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            "header": ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            "body": ctk.CTkFont(family="Segoe UI", size=12),
            "small": ctk.CTkFont(family="Segoe UI", size=10),
            "mono": ctk.CTkFont(family="Consolas", size=11),
        }

    @staticmethod
    def init_global():
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
