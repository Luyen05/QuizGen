"""Statistics screen."""

import customtkinter as ctk
import tkinter as tk
import json
import os

from ui.components import Card, GlowProgressBar
from ui.screens.base import BaseScreen

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "Data", "history.json")


class ScreenStats(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "stats", "Thống kê",
                         "Biểu đồ và phân tích hiệu suất")
        self.trend_scores = []
        self._build_ui()

    def on_enter(self):
        self._load_stats()

    def _build_ui(self):
        theme = self.theme
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        kpi_row = ctk.CTkFrame(self.content, fg_color="transparent")
        kpi_row.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1)

        self.kpi_values = {}
        kpis = [
            ("Tổng lần thi", "attempts", theme.colors["primary"]),
            ("Điểm trung bình", "avg", theme.colors["accent"]),
            ("Accuracy", "accuracy", theme.colors["accent_blue"]),
            ("Điểm cao nhất", "best", theme.colors["success"]),
        ]

        card_colors = [
            theme.colors["card_purple"],
            theme.colors["card_blue"],
            theme.colors["card_cyan"],
            theme.colors["card_green"],
        ]

        for idx, (label, key, color) in enumerate(kpis):
            card = Card(kpi_row, theme, fg_color=card_colors[idx])
            card.grid(row=0, column=idx, padx=8, sticky="nsew")
            ctk.CTkLabel(card, text=label, font=theme.fonts["small"],
                         text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(10, 0))
            value = ctk.CTkLabel(card, text="—", font=theme.fonts["title"],
                                 text_color=color)
            value.pack(anchor="w", padx=12, pady=(2, 10))
            self.kpi_values[key] = value

        charts = ctk.CTkFrame(self.content, fg_color="transparent")
        charts.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        charts.grid_columnconfigure(0, weight=2)
        charts.grid_columnconfigure(1, weight=1)
        charts.grid_rowconfigure(0, weight=1)

        self.trend_card = Card(charts, theme, fg_color=theme.colors["card_alt"])
        self.trend_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(self.trend_card, text="Xu hướng điểm gần đây",
                     font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.trend_canvas = tk.Canvas(
            self.trend_card,
            bg=theme.colors["card"],
            highlightthickness=0,
            height=180,
        )
        self.trend_canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.trend_canvas.bind("<Configure>", lambda _e: self._draw_trend(self.trend_scores))

        summary_card = Card(charts, theme, fg_color=theme.colors["card_blue"])
        summary_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(summary_card, text="Tổng quan câu hỏi",
                     font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.summary_labels = {
            "total_questions": ctk.CTkLabel(summary_card, text="— câu",
                                             font=theme.fonts["body"],
                                             text_color=theme.colors["text"]),
            "correct": ctk.CTkLabel(summary_card, text="— đúng",
                                     font=theme.fonts["body"],
                                     text_color=theme.colors["success"]),
            "wrong": ctk.CTkLabel(summary_card, text="— sai",
                                   font=theme.fonts["body"],
                                   text_color=theme.colors["danger"]),
        }

        for label in self.summary_labels.values():
            label.pack(anchor="w", padx=12, pady=4)

        ctk.CTkLabel(summary_card, text="Tỷ lệ đúng",
                     font=theme.fonts["small"],
                     text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(12, 2))
        self.correct_bar = GlowProgressBar(summary_card, theme)
        self.correct_bar.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(summary_card, text="Tỷ lệ sai",
                     font=theme.fonts["small"],
                     text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(6, 2))
        self.wrong_bar = ctk.CTkProgressBar(
            summary_card,
            fg_color=theme.colors["surface"],
            progress_color=theme.colors["danger"],
            border_width=0,
            corner_radius=theme.radius["sm"],
        )
        self.wrong_bar.pack(fill="x", padx=12, pady=(0, 12))

    def _load_stats(self):
        history = self._read_history_file()
        attempts = len(history)
        if attempts == 0:
            self._set_empty()
            return

        total_questions = sum(item.get("total", 0) for item in history)
        total_correct = sum(item.get("score", 0) for item in history)

        percents = []
        for item in history:
            total = item.get("total", 0)
            score = item.get("score", 0)
            pct = round(score / total * 100, 1) if total else 0
            percents.append(pct)

        avg_pct = round(sum(percents) / attempts, 1)
        best_pct = max(percents) if percents else 0
        accuracy = round(total_correct / total_questions * 100, 1) if total_questions else 0

        self.kpi_values["attempts"].configure(text=str(attempts))
        self.kpi_values["avg"].configure(text=f"{avg_pct}%")
        self.kpi_values["accuracy"].configure(text=f"{accuracy}%")
        self.kpi_values["best"].configure(text=f"{best_pct}%")

        self.summary_labels["total_questions"].configure(text=f"{total_questions} câu")
        self.summary_labels["correct"].configure(text=f"{total_correct} đúng")
        self.summary_labels["wrong"].configure(text=f"{max(total_questions - total_correct, 0)} sai")

        correct_ratio = total_correct / total_questions if total_questions else 0
        self.correct_bar.set(correct_ratio)
        self.wrong_bar.set(1 - correct_ratio)

        self.trend_scores = percents[-8:]
        self._draw_trend(self.trend_scores)

    def _set_empty(self):
        self.kpi_values["attempts"].configure(text="0")
        self.kpi_values["avg"].configure(text="—")
        self.kpi_values["accuracy"].configure(text="—")
        self.kpi_values["best"].configure(text="—")
        self.summary_labels["total_questions"].configure(text="0 câu")
        self.summary_labels["correct"].configure(text="0 đúng")
        self.summary_labels["wrong"].configure(text="0 sai")
        self.correct_bar.set(0)
        self.wrong_bar.set(0)
        self.trend_scores = []
        self._draw_trend([])

    def _draw_trend(self, scores):
        canvas = self.trend_canvas
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w <= 10 or h <= 10:
            return

        if not scores:
            canvas.create_text(
                w // 2,
                h // 2,
                text="Chưa có dữ liệu",
                fill=self.theme.colors["muted"],
                font=("Segoe UI", 10),
            )
            return

        pad_x = 12
        pad_y = 16
        bar_count = len(scores)
        gap = 10
        available = w - pad_x * 2 - gap * (bar_count - 1)
        bar_w = max(8, int(available / bar_count))
        max_h = h - pad_y * 2

        for i, pct in enumerate(scores):
            bar_h = int(max_h * (pct / 100))
            x0 = pad_x + i * (bar_w + gap)
            y0 = h - pad_y - bar_h
            x1 = x0 + bar_w
            y1 = h - pad_y

            if pct >= 80:
                color = self.theme.colors["success"]
            elif pct >= 60:
                color = self.theme.colors["accent_blue"]
            elif pct >= 40:
                color = self.theme.colors["warning"]
            else:
                color = self.theme.colors["danger"]

            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def _read_history_file(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
