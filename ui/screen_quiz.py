"""
ui/screen_quiz.py
Màn hình 3: Thi thử — giao diện dashboard hiện đại
"""

import tkinter as tk
from tkinter import messagebox

from ui.app import COLORS
from ui.components import (
    RoundedCard,
    GlowProgress,
    GradientButton,
    PillButton,
    SidebarItem,
    QuestionListItem,
    AnswerCard,
    blend,
)


class ScreenQuiz(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.current_index = 0
        self.selected_var = tk.StringVar(value="")
        self.flagged = set()
        self._suppress_choice_trace = False
        self.time_remaining = 0
        self.total_time = 0
        self._timer_id = None
        self.quiz_manager = None

        self.answer_cards = []
        self.question_items = []

        self.selected_var.trace_add("write", self._on_choice_changed)
        self._build_ui()

    def on_enter(self):
        """Reset và bắt đầu bài thi mới."""
        self.current_index = 0
        self.selected_var.set("")
        self.flagged = set()

        settings = self.controller.get_shared("settings") or {}
        self.total_time = settings.get("time_limit", 15) * 60
        self.time_remaining = self.total_time
        self.quiz_manager = self.controller.get_shared("quiz_manager")

        self._build_question_list()
        self._refresh_question()
        self._start_timer()

    # ── BUILD UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=240)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self._build_sidebar()

        self.main = tk.Frame(self, bg=COLORS["bg"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(2, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self._build_top_section()
        self._build_info_cards()
        self._build_content_area()
        self._build_footer()

    def _build_sidebar(self):
        c = self.controller

        logo_row = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        logo_row.pack(padx=16, pady=(24, 12), anchor="w")

        logo = tk.Canvas(logo_row, width=44, height=44,
                         bg=COLORS["sidebar"], highlightthickness=0)
        logo.create_oval(2, 2, 42, 42, fill=COLORS["accent"], outline="")
        logo.create_text(22, 22, text="QG", fill="white",
                         font=c.fonts["header"])
        logo.pack(side="left")

        title_box = tk.Frame(logo_row, bg=COLORS["sidebar"])
        title_box.pack(side="left", padx=10)
        tk.Label(title_box, text="QuizGen",
                 font=c.fonts["header"], bg=COLORS["sidebar"],
                 fg=COLORS["text"]).pack(anchor="w")
        tk.Label(title_box, text="Hệ thống tạo đề thi tự động",
                 font=c.fonts["small"], bg=COLORS["sidebar"],
                 fg=COLORS["muted"], wraplength=160,
                 justify="left").pack(anchor="w")

        menu = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        menu.pack(fill="x", padx=12, pady=(8, 6))

        items = [
            ("Tải lên", "upload", "↥"),
            ("Cài đặt", "settings", "⚙"),
            ("Thi thử", "quiz", "▶"),
            ("Kết quả", "result", "✓"),
            ("Lịch sử", "history", "⏳"),
        ]

        for label, name, icon in items:
            item = SidebarItem(
                menu,
                text=f"{icon}  {label}",
                command=lambda n=name: self.controller.show_screen(n),
                colors=COLORS,
                font=c.fonts["small"],
                active=(name == "quiz"),
            )
            item.pack(fill="x", pady=4)

        spacer = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        spacer.pack(expand=True, fill="both")

        footer = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        footer.pack(side="bottom", fill="x", padx=16, pady=16)

        avatar = tk.Canvas(footer, width=40, height=40,
                           bg=COLORS["sidebar"], highlightthickness=0)
        avatar.create_oval(2, 2, 38, 38, fill=COLORS["card"],
                           outline=COLORS["border"])
        avatar.create_text(20, 20, text="SV",
                           fill=COLORS["text"], font=c.fonts["small"])
        avatar.pack(side="left")

        user_box = tk.Frame(footer, bg=COLORS["sidebar"])
        user_box.pack(side="left", padx=10)
        tk.Label(user_box, text="Sinh viên",
                 font=c.fonts["small"], bg=COLORS["sidebar"],
                 fg=COLORS["text"]).pack(anchor="w")
        tk.Label(user_box, text="MSSV: 2312682 · Lớp: KTPM",
                 font=c.fonts["small"], bg=COLORS["sidebar"],
                 fg=COLORS["muted"]).pack(anchor="w")

    def _build_top_section(self):
        c = self.controller

        top = tk.Frame(self.main, bg=COLORS["bg"])
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))
        top.grid_columnconfigure(0, weight=1)

        left = tk.Frame(top, bg=COLORS["bg"])
        left.grid(row=0, column=0, sticky="w")

        tk.Label(left, text="Thi thử", font=c.fonts["display"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(left, text="Luyện tập và theo dõi tiến độ theo thời gian thực",
                 font=c.fonts["small"], bg=COLORS["bg"],
                 fg=COLORS["muted"]).pack(anchor="w")

        right = tk.Frame(top, bg=COLORS["bg"])
        right.grid(row=0, column=1, sticky="e")

        time_card = RoundedCard(
            right,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=16,
            padding=12,
            height=86,
            width=220,
        )
        time_card.pack(side="left", padx=(0, 12))

        time_header = tk.Frame(time_card.inner, bg=COLORS["card"])
        time_header.pack(fill="x")
        tk.Label(time_header, text="⏱", font=c.fonts["header"],
                 bg=COLORS["card"], fg=COLORS["accent"]).pack(side="left")

        self.timer_var = tk.StringVar(value="00:00")
        self.timer_label = tk.Label(time_header, textvariable=self.timer_var,
                                    font=c.fonts["header"],
                                    bg=COLORS["card"], fg=COLORS["accent"])
        self.timer_label.pack(side="left", padx=8)

        self.countdown_progress = GlowProgress(
            time_card.inner,
            height=6,
            bg=COLORS["card_alt"],
            fill=COLORS["accent"],
            glow=COLORS["glow"],
        )
        self.countdown_progress.pack(fill="x", pady=(8, 2))

        tk.Label(time_card.inner, text="Thời gian còn lại",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

        self.btn_submit = GradientButton(
            right,
            text="Nộp bài",
            command=self._submit,
            left_color=COLORS["danger"],
            right_color=COLORS["accent"],
            hover_left=blend(COLORS["danger"], "#FFFFFF", 0.08),
            hover_right=blend(COLORS["accent"], "#FFFFFF", 0.08),
            fg="white",
            font=c.fonts["btn"],
            height=44,
            width=140,
        )
        self.btn_submit.pack(side="left")

    def _build_info_cards(self):
        c = self.controller

        row = tk.Frame(self.main, bg=COLORS["bg"])
        row.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)
        row.grid_columnconfigure(2, weight=1)

        self.card_quiz = RoundedCard(
            row, bg=COLORS["card"], border=COLORS["border"], shadow=COLORS["shadow"],
            radius=16, padding=14, height=130
        )
        self.card_quiz.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(self.card_quiz.inner, text="Đề thi hiện tại",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

        self.quiz_title_var = tk.StringVar(value="—")
        tk.Label(self.card_quiz.inner, textvariable=self.quiz_title_var,
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(4, 6))

        self.diff_var = tk.StringVar(value="Độ khó: —")
        self.accuracy_var = tk.StringVar(value="Tỷ lệ đúng: —")
        self.avg_time_var = tk.StringVar(value="TB/câu: —")

        for var in (self.diff_var, self.accuracy_var, self.avg_time_var):
            tk.Label(self.card_quiz.inner, textvariable=var,
                     font=c.fonts["small"], bg=COLORS["card"],
                     fg=COLORS["muted"]).pack(anchor="w")

        self.card_progress = RoundedCard(
            row, bg=COLORS["card"], border=COLORS["border"], shadow=COLORS["shadow"],
            radius=16, padding=14, height=130
        )
        self.card_progress.grid(row=0, column=1, sticky="nsew", padx=10)

        tk.Label(self.card_progress.inner, text="Tiến độ",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

        self.progress_count_var = tk.StringVar(value="0/0 câu")
        tk.Label(self.card_progress.inner, textvariable=self.progress_count_var,
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(4, 4))

        self.progress_bar = GlowProgress(
            self.card_progress.inner,
            height=8,
            bg=COLORS["card_alt"],
            fill=COLORS["accent"],
            glow=COLORS["glow"],
        )
        self.progress_bar.pack(fill="x", pady=(2, 4))

        self.progress_hint_var = tk.StringVar(value="Đã làm: 0 · Còn lại: 0")
        tk.Label(self.card_progress.inner, textvariable=self.progress_hint_var,
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

        self.card_score = RoundedCard(
            row, bg=COLORS["card"], border=COLORS["border"], shadow=COLORS["shadow"],
            radius=16, padding=14, height=130
        )
        self.card_score.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        tk.Label(self.card_score.inner, text="Điểm hiện tại",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

        self.score_pct_var = tk.StringVar(value="0%")
        tk.Label(self.card_score.inner, textvariable=self.score_pct_var,
                 font=c.fonts["display"], bg=COLORS["card"],
                 fg=COLORS["green"]).pack(anchor="w", pady=(2, 0))

        self.score_count_var = tk.StringVar(value="0/0 câu đúng")
        tk.Label(self.card_score.inner, textvariable=self.score_count_var,
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

    def _build_content_area(self):
        c = self.controller

        content = tk.Frame(self.main, bg=COLORS["bg"])
        content.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 12))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        self.left_panel = RoundedCard(
            content, bg=COLORS["card"], border=COLORS["border"],
            shadow=COLORS["shadow"], radius=18, padding=12, width=360
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(self.left_panel.inner, text="Danh sách câu hỏi",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(0, 6))

        list_wrap = tk.Frame(self.left_panel.inner, bg=COLORS["card"])
        list_wrap.pack(fill="both", expand=True)

        self.question_canvas = tk.Canvas(list_wrap, bg=COLORS["card"],
                                         highlightthickness=0)
        self.question_scroll = tk.Scrollbar(
            list_wrap, orient="vertical", command=self.question_canvas.yview,
            bg=COLORS["border"], troughcolor=COLORS["surface"],
            activebackground=COLORS["accent"], bd=0, highlightthickness=0
        )

        self.question_inner = tk.Frame(self.question_canvas, bg=COLORS["card"])
        self.question_inner.bind(
            "<Configure>",
            lambda e: self.question_canvas.configure(
                scrollregion=self.question_canvas.bbox("all")
            ),
        )

        self._question_window = self.question_canvas.create_window(
            (0, 0), window=self.question_inner, anchor="nw"
        )
        self.question_canvas.configure(yscrollcommand=self.question_scroll.set)
        self.question_canvas.bind("<Configure>", self._on_question_canvas_resize)
        self.question_canvas.bind("<Enter>", self._bind_question_scroll)
        self.question_canvas.bind("<Leave>", self._unbind_question_scroll)

        self.question_canvas.pack(side="left", fill="both", expand=True)
        self.question_scroll.pack(side="right", fill="y")

        legend = tk.Frame(self.left_panel.inner, bg=COLORS["card"])
        legend.pack(fill="x", pady=(8, 0))

        self._legend_item(legend, COLORS["green"], "Đúng")
        self._legend_item(legend, COLORS["danger"], "Sai")
        self._legend_item(legend, COLORS["accent"], "Đang làm")
        self._legend_item(legend, COLORS["muted"], "Chưa làm")

        self.right_panel = tk.Frame(content, bg=COLORS["bg"])
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=1)

        self.question_card = RoundedCard(
            self.right_panel, bg=COLORS["card"], border=COLORS["border"],
            shadow=COLORS["shadow"], radius=18, padding=16, height=180
        )
        self.question_card.grid(row=0, column=0, sticky="ew")

        header_row = tk.Frame(self.question_card.inner, bg=COLORS["card"])
        header_row.pack(fill="x")

        self.q_num_label = tk.Label(header_row, text="Câu 1",
                                    font=c.fonts["header"],
                                    bg=COLORS["card"], fg=COLORS["accent"])
        self.q_num_label.pack(side="left")

        self.flag_btn = PillButton(
            header_row,
            text="Đánh dấu",
            command=self._toggle_flag,
            bg=COLORS["surface_alt"],
            hover_bg=COLORS["surface"],
            fg=COLORS["text"],
            hover_fg=COLORS["text"],
            font=c.fonts["small"],
            height=28,
            width=110,
        )
        self.flag_btn.pack(side="right")

        self.q_text_label = tk.Label(
            self.question_card.inner,
            text="",
            font=c.fonts["body"],
            bg=COLORS["card"],
            fg=COLORS["text"],
            wraplength=620,
            justify="left",
        )
        self.q_text_label.pack(anchor="w", pady=(10, 0))

        self.options_frame = tk.Frame(self.right_panel, bg=COLORS["bg"])
        self.options_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 6))

        self.explain_card = RoundedCard(
            self.right_panel, bg=COLORS["card_alt"], border=COLORS["yellow"],
            shadow=COLORS["shadow"], radius=16, padding=12, height=110
        )
        self.explain_card.grid(row=2, column=0, sticky="ew")

        explain_row = tk.Frame(self.explain_card.inner, bg=COLORS["card_alt"])
        explain_row.pack(fill="x")
        tk.Label(explain_row, text="💡", font=c.fonts["header"],
                 bg=COLORS["card_alt"], fg=COLORS["yellow"]).pack(side="left")
        tk.Label(explain_row, text="Giải thích",
                 font=c.fonts["small"], bg=COLORS["card_alt"],
                 fg=COLORS["yellow"]).pack(side="left", padx=6)

        self.explain_label = tk.Label(
            self.explain_card.inner,
            text="",
            font=c.fonts["small"],
            bg=COLORS["card_alt"],
            fg=COLORS["muted"],
            wraplength=620,
            justify="left",
        )
        self.explain_label.pack(anchor="w", pady=(6, 0))

    def _build_footer(self):
        c = self.controller

        footer = tk.Frame(self.main, bg=COLORS["bg"])
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 16))
        footer.grid_columnconfigure(1, weight=1)

        self.btn_prev = PillButton(
            footer,
            text="Câu trước",
            command=self._prev_question,
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["btn"],
            height=40,
            width=140,
        )
        self.btn_prev.grid(row=0, column=0, sticky="w")

        self.footer_indicator_var = tk.StringVar(value="Câu 1/1")
        tk.Label(footer, textvariable=self.footer_indicator_var,
                 font=c.fonts["small"], bg=COLORS["bg"],
                 fg=COLORS["muted"]).grid(row=0, column=1)

        self.btn_next = PillButton(
            footer,
            text="Câu tiếp theo",
            command=self._next_question,
            bg=COLORS["accent"],
            hover_bg=blend(COLORS["accent"], "#FFFFFF", 0.1),
            fg="white",
            hover_fg="white",
            font=c.fonts["btn"],
            height=40,
            width=160,
        )
        self.btn_next.grid(row=0, column=2, sticky="e")

    # ── BUILD HELPERS ───────────────────────────────────────────────────────

    def _legend_item(self, parent, color: str, text: str):
        item = tk.Frame(parent, bg=COLORS["card"])
        dot = tk.Canvas(item, width=8, height=8, bg=COLORS["card"], highlightthickness=0)
        dot.create_oval(1, 1, 7, 7, fill=color, outline="")
        dot.pack(side="left")
        tk.Label(item, text=text, font=self.controller.fonts["small"],
                 bg=COLORS["card"], fg=COLORS["muted"]).pack(side="left", padx=4)
        item.pack(side="left", padx=6)

    def _on_question_canvas_resize(self, event):
        self.question_canvas.itemconfigure(self._question_window, width=event.width)

    def _bind_question_scroll(self, _event):
        self.question_canvas.bind_all("<MouseWheel>", self._on_question_scroll)

    def _unbind_question_scroll(self, _event):
        self.question_canvas.unbind_all("<MouseWheel>")

    def _on_question_scroll(self, event):
        self.question_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── LOGIC/UI UPDATE ─────────────────────────────────────────────────────

    def _build_question_list(self):
        for w in self.question_inner.winfo_children():
            w.destroy()
        self.question_items = []

        if not self.quiz_manager:
            return

        questions = self.quiz_manager.get_questions()
        for i in range(len(questions)):
            item = QuestionListItem(
                self.question_inner,
                text=f"Câu {i + 1}",
                command=lambda idx=i: self._jump_to_question(idx),
                colors=COLORS,
                font=self.controller.fonts["small"],
            )
            item.pack(fill="x", pady=4, padx=2)
            self.question_items.append(item)

        self._update_question_list()

    def _refresh_question(self):
        """Cập nhật UI theo câu hỏi hiện tại."""
        if not self.quiz_manager:
            return

        questions = self.quiz_manager.get_questions()
        total = len(questions)
        if total == 0:
            return

        idx = self.current_index
        q = questions[idx]

        self.q_num_label.config(text=f"Câu {idx + 1:02d}")
        self.q_text_label.config(text=q.get("question", ""))
        self.explain_label.config(text=q.get("explanation", "Chưa có giải thích."))

        saved = self.quiz_manager.get_answer(idx)
        self._suppress_choice_trace = True
        self.selected_var.set(saved if saved else "")
        self._suppress_choice_trace = False

        self._build_answer_cards(q)
        self._update_answer_cards()
        self._update_progress_info()
        self._update_question_list()
        self._update_footer()

    def _build_answer_cards(self, question: dict):
        for w in self.options_frame.winfo_children():
            w.destroy()
        self.answer_cards = []

        options = question.get("options", [])
        for i, option in enumerate(options[:4]):
            key = chr(65 + i)
            card = AnswerCard(
                self.options_frame,
                key=key,
                text=option,
                command=self._select_answer,
                colors=COLORS,
                font=self.controller.fonts["body"],
            )
            card.pack(fill="x", pady=6)
            self.answer_cards.append(card)

    def _update_answer_cards(self):
        if not self.quiz_manager:
            return
        question = self.quiz_manager.get_question(self.current_index)
        correct_key = question.get("answer")
        selected = self.selected_var.get()
        reveal = bool(selected)

        for card in self.answer_cards:
            is_selected = card.key == selected
            is_correct = reveal and card.key == correct_key
            is_wrong = reveal and is_selected and selected != correct_key
            card.set_state(selected=is_selected, correct=is_correct, incorrect=is_wrong)

        is_flagged = self.current_index in self.flagged
        self.flag_btn.set_text("Bỏ đánh dấu" if is_flagged else "Đánh dấu")

    def _update_question_list(self):
        if not self.quiz_manager:
            return
        questions = self.quiz_manager.get_questions()
        for i, item in enumerate(self.question_items):
            answer = self.quiz_manager.get_answer(i)
            status_color = COLORS["muted"]

            if i == self.current_index:
                status_color = COLORS["accent"]
            elif answer is not None:
                correct = questions[i].get("answer")
                if answer == correct:
                    status_color = COLORS["green"]
                else:
                    status_color = COLORS["danger"]

            item.set_state(status_color=status_color, active=(i == self.current_index))

    def _update_progress_info(self):
        if not self.quiz_manager:
            return

        questions = self.quiz_manager.get_questions()
        total = len(questions)
        answered = len(self.quiz_manager.user_answers)
        remaining = max(total - answered, 0)
        flagged = len(self.flagged)

        correct = 0
        for i, q in enumerate(questions):
            if self.quiz_manager.get_answer(i) == q.get("answer"):
                correct += 1

        pct = round(correct / total * 100) if total else 0
        accuracy = round(correct / answered * 100) if answered else 0

        self.progress_count_var.set(f"{answered}/{total} câu")
        self.progress_bar.set(answered / max(total, 1), animate=True)
        self.progress_hint_var.set(
            f"Đã làm: {answered} · Còn lại: {remaining} · Đánh dấu: {flagged}"
        )

        self.score_pct_var.set(f"{pct}%")
        self.score_count_var.set(f"{correct}/{total} câu đúng")

        self.accuracy_var.set(f"Tỷ lệ đúng: {accuracy}%" if answered else "Tỷ lệ đúng: —")

        elapsed = max(self.total_time - self.time_remaining, 0)
        if answered and elapsed:
            avg = int(elapsed / answered)
            self.avg_time_var.set(f"TB/câu: {self._format_short_time(avg)}")
        else:
            self.avg_time_var.set("TB/câu: —")

        title = "Đề thi tự động"
        settings = self.controller.get_shared("settings") or {}
        if self.quiz_manager and self.quiz_manager.current_quiz:
            title = self.quiz_manager.current_quiz.get("title", title)
        self.quiz_title_var.set(title)

        diff_map = {"easy": "Dễ", "medium": "Trung bình", "hard": "Khó"}
        diff_value = diff_map.get(settings.get("difficulty"), "—")
        self.diff_var.set(f"Độ khó: {diff_value}")

        self.footer_indicator_var.set(f"Câu {self.current_index + 1}/{max(total, 1)}")

    def _update_footer(self):
        if not self.quiz_manager:
            return
        total = len(self.quiz_manager.get_questions())
        self.btn_prev.set_enabled(self.current_index > 0)
        last_q = self.current_index == total - 1
        self.btn_next.set_text("Nộp bài" if last_q else "Câu tiếp theo")

    def _select_answer(self, key: str):
        if not self.quiz_manager:
            return
        self._suppress_choice_trace = True
        self.selected_var.set(key)
        self._suppress_choice_trace = False
        self._on_choice_changed()

    def _prev_question(self):
        self._save_current_answer()
        if self.current_index > 0:
            self.current_index -= 1
            self._refresh_question()

    def _next_question(self):
        self._save_current_answer()
        questions = self.quiz_manager.get_questions()
        if self.current_index < len(questions) - 1:
            self.current_index += 1
            self._refresh_question()
        else:
            self._submit()

    def _save_current_answer(self):
        """Lưu đáp án câu hiện tại vào quiz_manager."""
        ans = self.selected_var.get()
        if ans and self.quiz_manager:
            self.quiz_manager.submit_answer(self.current_index, ans)

    def _toggle_flag(self):
        if self.current_index in self.flagged:
            self.flagged.remove(self.current_index)
        else:
            self.flagged.add(self.current_index)
        self._update_progress_info()
        self._update_question_list()
        self._update_answer_cards()

    def _jump_to_question(self, index: int):
        self._save_current_answer()
        self.current_index = index
        self._refresh_question()

    def _submit(self, force: bool = False):
        """Nộp bài, tính điểm, chuyển màn hình kết quả."""
        if not self.quiz_manager:
            return
        total = len(self.quiz_manager.get_questions())
        unanswered = max(total - len(self.quiz_manager.user_answers), 0)
        flagged = len(self.flagged)

        if not force:
            msg = "Bạn có chắc muốn nộp bài không?"
            if unanswered > 0 or flagged > 0:
                msg = f"Bạn còn {unanswered} câu chưa trả lời"
                if flagged > 0:
                    msg += f" và {flagged} câu đánh dấu"
                msg += ". Bạn vẫn muốn nộp bài chứ?"
            if not messagebox.askyesno("Nộp bài", msg):
                return

        self._stop_timer()
        elapsed = (self.controller.get_shared("settings").get("time_limit", 15) * 60
                   - self.time_remaining)
        result = self.quiz_manager.calculate_result(elapsed)
        self.quiz_manager.save_history(result)
        self.controller.set_shared("result", result)
        self.controller.show_screen("result")

    # ── Timer ───────────────────────────────────────────────────────────────

    def _start_timer(self):
        self._stop_timer()
        self._tick()

    def _stop_timer(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None

    def _tick(self):
        """Đếm ngược mỗi giây."""
        if self.time_remaining <= 0:
            self.timer_var.set("00:00")
            self.countdown_progress.set(0.0)
            messagebox.showwarning("Hết giờ!", "Thời gian đã hết. Bài thi sẽ được nộp tự động.")
            self._submit(force=True)
            return

        m, s = divmod(self.time_remaining, 60)
        self.timer_var.set(f"{m:02d}:{s:02d}")
        self.timer_label.config(
            fg=COLORS["danger"] if self.time_remaining < 60 else COLORS["accent"]
        )

        if self.total_time:
            self.countdown_progress.set(self.time_remaining / self.total_time)

        self.time_remaining -= 1
        self._timer_id = self.after(1000, self._tick)

    def _on_choice_changed(self, *_):
        if self._suppress_choice_trace or not self.quiz_manager:
            return
        ans = self.selected_var.get()
        if ans:
            self.quiz_manager.submit_answer(self.current_index, ans)
        else:
            self.quiz_manager.user_answers.pop(self.current_index, None)
        self._update_progress_info()
        self._update_question_list()
        self._update_answer_cards()

    # ── Utils ───────────────────────────────────────────────────────────────

    def _format_short_time(self, seconds: int) -> str:
        if seconds < 60:
            return f"{seconds}s"
        m, s = divmod(seconds, 60)
        return f"{m}m {s:02d}s"
