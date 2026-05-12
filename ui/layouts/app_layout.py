"""Shared application layout."""

import customtkinter as ctk

from ui.components import Sidebar, Topbar


class AppLayout(ctk.CTkFrame):
    def __init__(self, parent, controller, active_key, title, subtitle):
        theme = controller.theme
        super().__init__(parent, fg_color=theme.colors["bg"])
        self.controller = controller
        self.theme = theme

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        items = [
            ("Trang chủ", "home", "⌂"),
            ("Tải lên", "upload", "↥"),
            ("Cài đặt", "settings", "⚙"),
            ("Sinh đề AI", "generate", "✦"),
            ("Thi thử", "quiz", "▶"),
            ("Kết quả", "result", "✓"),
            ("Lịch sử", "history", "⏳"),
            ("Thống kê", "stats", "∑"),
        ]

        self.sidebar = Sidebar(self, controller, items, active_key)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.configure(width=240)

        self.main = ctk.CTkFrame(self, fg_color=theme.colors["bg"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.topbar = Topbar(self.main, theme, title, subtitle)
        self.topbar.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        self.content = ctk.CTkFrame(self.main, fg_color=theme.colors["bg"])
        self.content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))

    def set_active(self, key):
        self.sidebar.set_active(key)

    def set_title(self, title, subtitle=""):
        self.topbar.set_text(title, subtitle)
