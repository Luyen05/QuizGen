"""Settings screen."""

import customtkinter as ctk
import tkinter as tk

from ui.components import Card, AppButton
from ui.screens.base import BaseScreen


class ScreenSettings(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "settings", "Cài đặt đề thi",
                         "Tùy chỉnh thông số và AI model")

        self.num_questions = tk.IntVar(value=10)
        self.num_options = tk.IntVar(value=4)
        self.time_limit = tk.IntVar(value=15)
        self.difficulty = tk.StringVar(value="medium")
        self.language = tk.StringVar(value="Tiếng Việt")
        self.model = tk.StringVar(value="Gemini")

        self._build_ui()

    def _build_ui(self):
        theme = self.theme

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        left = Card(self.content, theme, fg_color=theme.colors["card_alt"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = Card(self.content, theme, fg_color=theme.colors["card_blue"])
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(left, text="Thông số đề thi", font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        def section(label):
            ctk.CTkLabel(left, text=label, font=theme.fonts["small"],
                         text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(10, 4))

        section("Số câu hỏi")
        q_slider = ctk.CTkSlider(left, from_=5, to=30, number_of_steps=25,
                                 variable=self.num_questions,
                                 progress_color=theme.colors["primary"],
                                 button_color=theme.colors["accent"])
        q_slider.pack(fill="x", padx=12)

        section("Số đáp án")
        options = ctk.CTkSegmentedButton(left, values=["2", "3", "4", "5"],
                                         variable=self.num_options)
        options.pack(fill="x", padx=12)

        section("Độ khó")
        diff = ctk.CTkSegmentedButton(left, values=["easy", "medium", "hard"],
                                      variable=self.difficulty)
        diff.pack(fill="x", padx=12)

        section("Thời gian (phút)")
        time_slider = ctk.CTkSlider(left, from_=5, to=60, number_of_steps=55,
                                    variable=self.time_limit,
                                    progress_color=theme.colors["primary"],
                                    button_color=theme.colors["accent"])
        time_slider.pack(fill="x", padx=12)

        section("Ngôn ngữ")
        lang = ctk.CTkOptionMenu(left, values=["Tiếng Việt", "English"],
                                 variable=self.language)
        lang.pack(fill="x", padx=12)

        section("AI model")
        model = ctk.CTkOptionMenu(left, values=["Gemini", "Groq", "OpenAI"],
                                  variable=self.model)
        model.pack(fill="x", padx=12)

        ctk.CTkLabel(right, text="Tóm tắt", font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.summary_label = ctk.CTkLabel(right, text="", font=theme.fonts["body"],
                                          text_color=theme.colors["text"],
                                          justify="left")
        self.summary_label.pack(anchor="w", padx=12, pady=(6, 10))

        AppButton(right, theme, text="Sinh đề AI", command=self._go_generate,
                  variant="primary", height=40).pack(fill="x", padx=12, pady=(20, 12))

        self._update_summary()
        for var in [self.num_questions, self.num_options, self.time_limit,
                    self.difficulty, self.language, self.model]:
            var.trace_add("write", lambda *_: self._update_summary())

    def _update_summary(self):
        diff_map = {"easy": "Dễ", "medium": "Trung bình", "hard": "Khó"}
        summary = (
            f"Số câu: {self.num_questions.get()}\n"
            f"Số đáp án: {self.num_options.get()}\n"
            f"Độ khó: {diff_map.get(self.difficulty.get(), '—')}\n"
            f"Thời gian: {self.time_limit.get()} phút\n"
            f"Ngôn ngữ: {self.language.get()}\n"
            f"AI model: {self.model.get()}"
        )
        self.summary_label.configure(text=summary)

    def _go_generate(self):
        settings = {
            "num_questions": self.num_questions.get(),
            "num_options": self.num_options.get(),
            "difficulty": self.difficulty.get(),
            "language": self.language.get(),
            "time_limit": self.time_limit.get(),
            "model": self.model.get(),
        }
        self.controller.set_shared("settings", settings)
        self.controller.show_screen("generate")
