"""Home dashboard screen."""

import customtkinter as ctk

from ui.components import Card, AppButton, GlowProgressBar
from ui.screens.base import BaseScreen


class ScreenHome(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "home", "Trang chủ",
                         "Tổng quan tiến độ học tập và thống kê nhanh")
        self._build_ui()

    def _build_ui(self):
        theme = self.theme

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        kpi_row = ctk.CTkFrame(self.content, fg_color="transparent")
        kpi_row.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)

        kpis = [
            ("Tổng đề thi", "12"),
            ("Lượt làm bài", "58"),
            ("Điểm trung bình", "78%"),
            ("Accuracy", "82%"),
        ]

        card_colors = [
            theme.colors["card_purple"],
            theme.colors["card_blue"],
            theme.colors["card_green"],
            theme.colors["card_orange"],
        ]

        for idx, (label, value) in enumerate(kpis):
            card = Card(kpi_row, theme, fg_color=card_colors[idx])
            card.grid(row=0, column=idx, padx=8, sticky="nsew")
            ctk.CTkLabel(card, text=label,
                         font=theme.fonts["small"],
                         text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(10, 0))
            ctk.CTkLabel(card, text=value,
                         font=theme.fonts["title"],
                         text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(2, 10))

        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        activity_card = Card(main, theme, fg_color=theme.colors["card_alt"])
        activity_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(activity_card, text="Hoạt động gần đây",
                     font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        list_frame = ctk.CTkScrollableFrame(activity_card, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for item in [
            "Đã hoàn thành đề "
            "Python OOP - 85%",
            "Tạo đề AI từ bài giảng "
            "Chương 4",
            "Làm lại đề "
            "Data Structures",
        ]:
            row = ctk.CTkFrame(list_frame, fg_color=theme.colors["surface"], corner_radius=theme.radius["md"])
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=item, font=theme.fonts["body"],
                         text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=8)

        quick_card = Card(main, theme, fg_color=theme.colors["card_blue"])
        quick_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(quick_card, text="Quick actions",
                     font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        AppButton(quick_card, theme, text="Tải tài liệu mới",
                  command=lambda: self.controller.show_screen("upload")).pack(fill="x", padx=12, pady=6)
        AppButton(quick_card, theme, text="Cài đặt đề thi",
                  variant="secondary",
                  command=lambda: self.controller.show_screen("settings")).pack(fill="x", padx=12, pady=6)
        AppButton(quick_card, theme, text="Bắt đầu thi thử",
                  variant="primary",
                  command=lambda: self.controller.show_screen("quiz")).pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(quick_card, text="Tiến độ tuần này",
                     font=theme.fonts["small"],
                     text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(16, 4))
        progress = GlowProgressBar(quick_card, theme)
        progress.pack(fill="x", padx=12, pady=(0, 12))
        progress.set(0.62)
