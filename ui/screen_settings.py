"""
ui/screen_settings.py
Màn hình 2: Cài đặt thông số đề thi → tạo đề
"""

import tkinter as tk
from tkinter import messagebox
import threading

from Core.ai_generator import generate_questions
from Core.quiz_manager import QuizManager
from ui.app import COLORS
from ui.components import RoundedCard, GlowProgress, GradientButton, PillButton, blend
from ui.layout import build_sidebar, build_title_block


class ScreenSettings(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.quiz_manager = QuizManager()

        self.num_questions = tk.IntVar(value=10)
        self.num_options = tk.IntVar(value=4)
        self.difficulty = tk.StringVar(value="medium")
        self.language = tk.StringVar(value="Tiếng Việt")
        self.time_limit = tk.IntVar(value=15)

        self._build_ui()
        self._bind_summary()

    def on_enter(self):
        """Reset progress bar khi vào màn hình."""
        self.progress_var.set(0)
        self.status_var.set("Sẵn sàng tạo đề...")
        self.progress_bar.set(0.0)
        self.btn_generate.set_enabled(True)

    def _build_ui(self):
        c = self.controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = build_sidebar(self, c, active="settings")
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.main = tk.Frame(self, bg=COLORS["bg"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(2, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        top = tk.Frame(self.main, bg=COLORS["bg"])
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        top.grid_columnconfigure(0, weight=1)

        title_block = build_title_block(
            top,
            c,
            "Cài đặt",
            "Tùy chỉnh đề thi, ngôn ngữ và độ khó trước khi tạo",
        )
        title_block.grid(row=0, column=0, sticky="w")

        quick_card = RoundedCard(
            top,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=14,
            padding=10,
            height=72,
            width=220,
        )
        quick_card.grid(row=0, column=1, sticky="e")
        tk.Label(quick_card.inner, text="AI Generator",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")
        tk.Label(quick_card.inner, text="Sẵn sàng xử lý",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["green"]).pack(anchor="w", pady=(4, 0))

        info_row = tk.Frame(self.main, bg=COLORS["bg"])
        info_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        info_row.grid_columnconfigure(0, weight=1)
        info_row.grid_columnconfigure(1, weight=1)
        info_row.grid_columnconfigure(2, weight=1)

        self.summary_q_var = tk.StringVar(value="10 câu")
        self.summary_diff_var = tk.StringVar(value="Độ khó: Trung bình")
        self.summary_time_var = tk.StringVar(value="15 phút")

        summaries = [
            ("Số câu hỏi", self.summary_q_var),
            ("Độ khó", self.summary_diff_var),
            ("Thời gian", self.summary_time_var),
        ]

        for i, (title, var) in enumerate(summaries):
            card = RoundedCard(
                info_row,
                bg=COLORS["card"],
                border=COLORS["border"],
                shadow=COLORS["shadow"],
                radius=14,
                padding=12,
                height=92,
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0, 10) if i < 2 else 0)
            tk.Label(card.inner, text=title, font=c.fonts["small"],
                     bg=COLORS["card"], fg=COLORS["muted"]).pack(anchor="w")
            tk.Label(card.inner, textvariable=var, font=c.fonts["header"],
                     bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self.main, bg=COLORS["bg"])
        content.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 12))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        form_card = RoundedCard(
            content,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=14,
        )
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(form_card.inner, text="Thông số đề thi",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(0, 8))

        def setting_row(label, widget_fn):
            row = tk.Frame(form_card.inner, bg=COLORS["card"])
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, font=c.fonts["body"],
                     bg=COLORS["card"], fg=COLORS["text"],
                     width=18, anchor="w").pack(side="left")
            widget_fn(row)

        setting_row("Số câu hỏi", lambda r: tk.Spinbox(
            r, from_=5, to=30, textvariable=self.num_questions,
            width=6, font=c.fonts["body"], bg=COLORS["card_alt"],
            fg=COLORS["text"], relief="flat", insertbackground=COLORS["text"]
        ).pack(side="left"))

        setting_row("Số đáp án", lambda r: tk.Spinbox(
            r, from_=2, to=5, textvariable=self.num_options,
            width=6, font=c.fonts["body"], bg=COLORS["card_alt"],
            fg=COLORS["text"], relief="flat", insertbackground=COLORS["text"]
        ).pack(side="left"))

        def build_difficulty(r):
            for val, label in [("easy", "Dễ"), ("medium", "Trung bình"), ("hard", "Khó")]:
                tk.Radiobutton(
                    r,
                    text=label,
                    variable=self.difficulty,
                    value=val,
                    font=c.fonts["small"],
                    bg=COLORS["surface"],
                    fg=COLORS["text"],
                    selectcolor=COLORS["accent"],
                    activebackground=COLORS["surface_alt"],
                    activeforeground="white",
                    indicatoron=False,
                    padx=12,
                    pady=4,
                ).pack(side="left", padx=4)
        setting_row("Độ khó", build_difficulty)

        def build_language(r):
            opt = tk.OptionMenu(r, self.language, "Tiếng Việt", "English")
            opt.config(
                bg=COLORS["card_alt"],
                fg=COLORS["text"],
                activebackground=COLORS["surface_alt"],
                activeforeground="white",
                highlightthickness=0,
                relief="flat",
                font=c.fonts["body"],
            )
            opt["menu"].config(
                bg=COLORS["card_alt"],
                fg=COLORS["text"],
                activebackground=COLORS["accent"],
                activeforeground="white",
            )
            opt.pack(side="left")
        setting_row("Ngôn ngữ", build_language)

        setting_row("Thời gian (phút)", lambda r: tk.Spinbox(
            r, from_=5, to=60, textvariable=self.time_limit,
            width=6, font=c.fonts["body"], bg=COLORS["card_alt"],
            fg=COLORS["text"], relief="flat", insertbackground=COLORS["text"]
        ).pack(side="left"))

        status_card = RoundedCard(
            content,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=14,
        )
        status_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(status_card.inner, text="Tiến trình tạo đề",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(0, 8))

        self.status_var = tk.StringVar(value="Sẵn sàng tạo đề...")
        tk.Label(status_card.inner, textvariable=self.status_var,
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = GlowProgress(
            status_card.inner,
            height=8,
            bg=COLORS["card_alt"],
            fill=COLORS["accent"],
            glow=COLORS["glow"],
        )
        self.progress_bar.pack(fill="x", pady=10)

        tips = tk.Frame(status_card.inner, bg=COLORS["card"])
        tips.pack(fill="x", pady=(6, 0))
        tk.Label(tips, text="• Quá trình tạo đề có thể mất 30-60 giây",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")
        tk.Label(tips, text="• Hãy giữ kết nối mạng ổn định",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

        footer = tk.Frame(self.main, bg=COLORS["bg"])
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 18))
        footer.grid_columnconfigure(1, weight=1)

        self.btn_back = PillButton(
            footer,
            text="Quay lại",
            command=lambda: self.controller.show_screen("upload"),
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["btn"],
            height=40,
            width=140,
        )
        self.btn_back.grid(row=0, column=0, sticky="w")

        self.btn_generate = GradientButton(
            footer,
            text="Tạo đề thi",
            command=self._start_generate,
            left_color=COLORS["accent"],
            right_color=COLORS["accent2"],
            hover_left=blend(COLORS["accent"], "#FFFFFF", 0.08),
            hover_right=blend(COLORS["accent2"], "#FFFFFF", 0.08),
            fg="white",
            font=c.fonts["btn"],
            height=44,
            width=200,
        )
        self.btn_generate.grid(row=0, column=2, sticky="e")

    def _bind_summary(self):
        def update_summary(*_):
            self.summary_q_var.set(f"{self.num_questions.get()} câu")
            diff_map = {"easy": "Dễ", "medium": "Trung bình", "hard": "Khó"}
            diff_text = diff_map.get(self.difficulty.get(), "—")
            self.summary_diff_var.set(f"Độ khó: {diff_text}")
            self.summary_time_var.set(f"{self.time_limit.get()} phút")

        self.num_questions.trace_add("write", update_summary)
        self.difficulty.trace_add("write", update_summary)
        self.time_limit.trace_add("write", update_summary)
        update_summary()

    def _update_progress(self, value: float, status: str):
        """Cập nhật UI từ thread phụ — dùng after() để an toàn."""
        def _update():
            self.progress_var.set(value)
            self.status_var.set(status)
            self.progress_bar.set(value / 100.0, animate=True)
        self.after(0, _update)

    def _start_generate(self):
        """Chạy generate trong thread riêng để UI không bị đơ."""
        self.btn_generate.set_enabled(False)
        thread = threading.Thread(target=self._generate_worker, daemon=True)
        thread.start()

    def _generate_worker(self):
        """Worker chạy trong thread phụ — gọi AI và xử lý kết quả."""
        try:
            self._update_progress(20, "Đang chuẩn bị văn bản...")
            text = self.controller.get_shared("raw_text")

            if not text:
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi", "Không có văn bản. Quay lại bước 1."))
                return

            self._update_progress(40, "Đang gửi lên AI tạo câu hỏi...")

            settings = {
                "num_questions": self.num_questions.get(),
                "num_options": self.num_options.get(),
                "difficulty": self.difficulty.get(),
                "language": self.language.get(),
                "time_limit": self.time_limit.get(),
            }

            questions = generate_questions(
                text=text,
                num_questions=settings["num_questions"],
                num_options=settings["num_options"],
                difficulty=settings["difficulty"],
                language=settings["language"],
            )

            self._update_progress(80, "Đang xử lý kết quả...")

            self.quiz_manager.create_quiz(questions, settings)

            self.controller.set_shared("questions", questions)
            self.controller.set_shared("settings", settings)
            self.controller.set_shared("quiz_manager", self.quiz_manager)

            self._update_progress(100, f"✅ Tạo xong {len(questions)} câu hỏi!")

            self.after(500, lambda: self.controller.show_screen("quiz"))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi tạo đề", str(e)))
            self._update_progress(0, "Lỗi — thử lại")
            self.after(0, lambda: self.btn_generate.set_enabled(True))
