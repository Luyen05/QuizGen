"""AI generation screen."""

import threading
import customtkinter as ctk
from tkinter import messagebox

from Core.ai_generator import generate_questions
from Core.quiz_manager import QuizManager
from ui.components import Card, GlowProgressBar, TextArea
from ui.screens.base import BaseScreen


class ScreenGenerate(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "generate", "Sinh đề AI",
                         "Theo dõi quá trình tạo câu hỏi")
        self.quiz_manager = QuizManager()
        self._build_ui()

    def on_enter(self):
        self.progress.set(0)
        self.log_box.delete("1.0", "end")
        self._start_generate()

    def _build_ui(self):
        theme = self.theme

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        left = Card(self.content, theme, fg_color=theme.colors["card_blue"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = Card(self.content, theme, fg_color=theme.colors["card_purple"])
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(left, text="Trạng thái AI", font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.status_label = ctk.CTkLabel(left, text="Đang chuẩn bị...",
                                         font=theme.fonts["body"],
                                         text_color=theme.colors["muted"])
        self.status_label.pack(anchor="w", padx=12, pady=(0, 10))

        self.progress = GlowProgressBar(left, theme)
        self.progress.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkLabel(left, text="Token usage", font=theme.fonts["small"],
                     text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(10, 0))
        self.token_label = ctk.CTkLabel(left, text="0 tokens", font=theme.fonts["body"],
                                        text_color=theme.colors["text"])
        self.token_label.pack(anchor="w", padx=12, pady=(2, 0))

        ctk.CTkLabel(right, text="Log phản hồi", font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.log_box = TextArea(right, theme, height=260)
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _start_generate(self):
        thread = threading.Thread(target=self._generate_worker, daemon=True)
        thread.start()

    def _log(self, text: str):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def _update(self, value: float, status: str):
        self.progress.set(value)
        self.status_label.configure(text=status)

    def _generate_worker(self):
        try:
            self._log("Khởi tạo AI generator...")
            self._update(0.1, "Chuẩn bị dữ liệu")

            text = self.controller.get_shared("raw_text")
            settings = self.controller.get_shared("settings") or {}
            if not text:
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi", "Không có văn bản. Quay lại bước 1."))
                return

            self._update(0.3, "Đang gửi lên AI")
            self._log("Đang gửi nội dung lên AI...")

            questions = generate_questions(
                text=text,
                num_questions=settings.get("num_questions", 10),
                num_options=settings.get("num_options", 4),
                difficulty=settings.get("difficulty", "medium"),
                language=settings.get("language", "Tiếng Việt"),
            )

            self._update(0.7, "Đang xử lý kết quả")
            self._log(f"Nhận {len(questions)} câu hỏi từ AI")

            self.quiz_manager.create_quiz(questions, settings)
            self.controller.set_shared("questions", questions)
            self.controller.set_shared("quiz_manager", self.quiz_manager)

            self._update(1.0, "Hoàn tất")
            self._log("Hoàn tất tạo đề. Đang chuyển sang thi thử...")
            self.after(600, lambda: self.controller.show_screen("quiz"))
        except Exception as e:
            self._log(f"Lỗi: {e}")
            self.after(0, lambda: messagebox.showerror("Lỗi tạo đề", str(e)))
