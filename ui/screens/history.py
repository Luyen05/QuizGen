"""History screen."""

import customtkinter as ctk
import json
import os
from tkinter import messagebox

from Core.quiz_manager import QuizManager
from ui.components import Card, AppButton, TextInput
from ui.screens.base import BaseScreen

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "Data", "history.json")


class ScreenHistory(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "history", "Lịch sử",
                         "Theo dõi các lần thi và tra cứu nhanh")
        self.history = []
        self.filtered = []
        self.selected_index = None
        self._build_ui()

    def on_enter(self):
        self._load_history()

    def _build_ui(self):
        theme = self.theme

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=2)
        self.content.grid_rowconfigure(1, weight=1)

        search_row = ctk.CTkFrame(self.content, fg_color="transparent")
        search_row.grid(row=0, column=0, columnspan=2, sticky="ew")
        search_row.grid_columnconfigure(0, weight=1)

        self.search_input = TextInput(search_row, theme, placeholder="Tìm kiếm theo tiêu đề...")
        self.search_input.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        AppButton(search_row, theme, text="Lọc", variant="secondary",
                  command=self._apply_filter).grid(row=0, column=1)

        left = Card(self.content, theme, fg_color=theme.colors["card_alt"])
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(16, 0))
        right = Card(self.content, theme, fg_color=theme.colors["card_blue"])
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(16, 0))

        ctk.CTkLabel(left, text="Danh sách bài thi",
                     font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.list_frame = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        AppButton(left, theme, text="Xóa toàn bộ lịch sử", variant="danger",
                  command=self._clear_history, height=36).pack(anchor="w", padx=12, pady=(0, 12))

        ctk.CTkLabel(right, text="Chi tiết lần thi",
                     font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.detail_frame = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.detail_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        action_row = ctk.CTkFrame(right, fg_color="transparent")
        action_row.pack(fill="x", padx=12, pady=(0, 12))

        self.btn_retry = AppButton(action_row, theme, text="Làm lại đề này",
                       variant="primary", height=36,
                       command=self._retry_selected)
        self.btn_retry.pack(side="left")
        self.btn_retry.configure(state="disabled")

        self._show_empty_detail()

    def _apply_filter(self):
        keyword = self.search_input.get().strip().lower()
        if not keyword:
            self.filtered = self.history
        else:
            self.filtered = [h for h in self.history if keyword in h.get("quiz_title", "").lower()]
        self._render_list()

    def _load_history(self):
        self.history = self._read_history_file()
        self.filtered = list(reversed(self.history))
        self.btn_retry.configure(state="disabled")
        self._render_list()

    def _render_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        if not self.filtered:
            ctk.CTkLabel(self.list_frame, text="Chưa có lịch sử thi",
                         font=self.theme.fonts["small"],
                         text_color=self.theme.colors["muted"]).pack(pady=10)
            self._show_empty_detail()
            return

        for idx, item in enumerate(self.filtered):
            row = ctk.CTkFrame(self.list_frame, fg_color=self.theme.colors["card"],
                               corner_radius=self.theme.radius["md"])
            row.pack(fill="x", pady=6)
            header = ctk.CTkFrame(row, fg_color="transparent")
            header.pack(fill="x", padx=12, pady=(8, 0))

            score = item.get("score", 0)
            total = item.get("total", 0)
            pct = round(score / total * 100) if total else 0
            if pct >= 80:
                pct_color = self.theme.colors["success"]
            elif pct >= 50:
                pct_color = self.theme.colors["warning"]
            else:
                pct_color = self.theme.colors["danger"]

            label = f"{item.get('date','')}  {score}/{total}"
            title = ctk.CTkLabel(header, text=label, font=self.theme.fonts["body"],
                                 text_color=self.theme.colors["text"])
            title.pack(side="left")

            pct_label = ctk.CTkLabel(header, text=f"{pct}%",
                                     font=self.theme.fonts["small"],
                                     text_color=pct_color)
            pct_label.pack(side="right")

            subtitle = ctk.CTkLabel(row, text=item.get("quiz_title", ""),
                                    font=self.theme.fonts["small"],
                                    text_color=self.theme.colors["muted"])
            subtitle.pack(anchor="w", padx=12, pady=(0, 8))

            for widget in (row, header, title, pct_label, subtitle):
                widget.bind("<Button-1>", lambda _e, i=idx: self._select(i))

    def _select(self, index):
        if index >= len(self.filtered):
            return
        self.selected_index = index
        self.btn_retry.configure(state="normal")
        self._show_detail(self.filtered[index])

    def _show_empty_detail(self):
        for w in self.detail_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.detail_frame, text="Chọn một lần thi để xem chi tiết",
                     font=self.theme.fonts["small"],
                     text_color=self.theme.colors["muted"]).pack(pady=12)

    def _show_detail(self, result: dict):
        for w in self.detail_frame.winfo_children():
            w.destroy()
        if not result:
            self._show_empty_detail()
            return

        ctk.CTkLabel(self.detail_frame, text=f"{result.get('score',0)}/{result.get('total',0)}",
                     font=self.theme.fonts["title"],
                     text_color=self.theme.colors["success"]).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(self.detail_frame, text=result.get("quiz_title", ""),
                     font=self.theme.fonts["body"],
                     text_color=self.theme.colors["text"]).pack(anchor="w", pady=(0, 8))

        for item in result.get("detail", []):
            row = ctk.CTkFrame(self.detail_frame, fg_color=self.theme.colors["card_alt"],
                               corner_radius=self.theme.radius["md"])
            row.pack(fill="x", pady=6)
            status = "✓" if item.get("is_correct") else "✗"
            ctk.CTkLabel(row, text=f"{status} Câu {item['index'] + 1}",
                         font=self.theme.fonts["small"],
                         text_color=self.theme.colors["text"]).pack(anchor="w", padx=12, pady=(6, 0))
            ctk.CTkLabel(row, text=item.get("question", ""),
                         font=self.theme.fonts["small"],
                         text_color=self.theme.colors["muted"],
                         wraplength=520, justify="left").pack(anchor="w", padx=12, pady=(0, 8))

    def _retry_selected(self):
        if self.selected_index is None or self.selected_index >= len(self.filtered):
            return

        result = self.filtered[self.selected_index]
        questions = result.get("questions", [])
        if not questions:
            messagebox.showwarning(
                "Không có câu hỏi",
                "Lần thi này không lưu câu hỏi gốc.\nVui lòng tạo đề mới."
            )
            return

        settings = result.get("settings", {
            "num_questions": len(questions),
            "difficulty": "medium",
            "time_limit": 15,
            "language": "Tiếng Việt",
        })

        quiz_manager = QuizManager()
        quiz_manager.create_quiz(questions, settings, result.get("quiz_title", "Làm lại"))
        quiz_manager.user_answers = {}

        self.controller.set_shared("quiz_manager", quiz_manager)
        self.controller.set_shared("settings", settings)
        self.controller.set_shared("questions", questions)
        self.controller.show_screen("quiz")

    def _read_history_file(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _clear_history(self):
        if not self.history:
            messagebox.showinfo("Thông báo", "Chưa có lịch sử để xóa.")
            return
        if messagebox.askyesno("Xác nhận", "Xóa toàn bộ lịch sử thi?"):
            try:
                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f)
                self.history = []
                self.filtered = []
                self._render_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {e}")
