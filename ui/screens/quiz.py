"""Quiz screen."""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from ui.components import Card, AppButton, GlowProgressBar
from ui.screens.base import BaseScreen


class AnswerCard(ctk.CTkFrame):
    def __init__(self, parent, theme, key, text, command):
        super().__init__(
            parent,
            fg_color=theme.colors["surface"],
            border_color=theme.colors["border"],
            border_width=1,
            corner_radius=theme.radius["md"],
        )
        self.theme = theme
        self.key = key
        self.command = command

        self.key_label = ctk.CTkLabel(self, text=key, font=theme.fonts["header"],
                                      text_color=theme.colors["muted"], width=28)
        self.key_label.pack(side="left", padx=(12, 6), pady=10)

        self.text_label = ctk.CTkLabel(self, text=text, font=theme.fonts["body"],
                                       text_color=theme.colors["text"], justify="left")
        self.text_label.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)

        self.icon_label = ctk.CTkLabel(self, text="", font=theme.fonts["header"],
                                       text_color=theme.colors["success"], width=24)
        self.icon_label.pack(side="right", padx=(0, 12))

        for widget in (self, self.key_label, self.text_label, self.icon_label):
            widget.bind("<Button-1>", self._on_click)

    def set_text(self, text):
        self.text_label.configure(text=text)

    def set_state(self, selected, correct, wrong):
        if correct:
            border = self.theme.colors["success"]
            icon = "✓"
        elif wrong:
            border = self.theme.colors["danger"]
            icon = "✕"
        elif selected:
            border = self.theme.colors["primary"]
            icon = ""
        else:
            border = self.theme.colors["border"]
            icon = ""

        self.configure(border_color=border)
        self.icon_label.configure(text=icon)

    def _on_click(self, _event=None):
        if self.command:
            self.command(self.key)


class ScreenQuiz(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "quiz", "Thi thử",
                         "Luyện tập và theo dõi tiến độ theo thời gian thực")
        self.current_index = 0
        self.selected_var = tk.StringVar(value="")
        self.flagged = set()
        self.time_remaining = 0
        self.total_time = 0
        self._timer_id = None
        self.quiz_manager = None

        self.answer_cards = []
        self.question_buttons = []

        self._build_ui()

    def on_enter(self):
        settings = self.controller.get_shared("settings") or {}
        self.total_time = settings.get("time_limit", 15) * 60
        self.time_remaining = self.total_time
        self.quiz_manager = self.controller.get_shared("quiz_manager")
        self.current_index = 0
        self.flagged = set()
        self.selected_var.set("")

        self._build_question_list()
        self._refresh_question()
        self._start_timer()

    def _build_ui(self):
        theme = self.theme

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        timer_card = Card(header, theme, fg_color=theme.colors["card_violet"])
        timer_card.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(timer_card, text="Thời gian còn lại",
                     font=theme.fonts["small"],
                     text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(10, 0))

        self.timer_label = ctk.CTkLabel(timer_card, text="00:00",
                                        font=theme.fonts["header"],
                                        text_color=theme.colors["primary"])
        self.timer_label.pack(anchor="w", padx=12)

        self.countdown_bar = GlowProgressBar(timer_card, theme)
        self.countdown_bar.pack(fill="x", padx=12, pady=(6, 12))

        AppButton(header, theme, text="Nộp bài", variant="danger",
                  command=self._submit, height=36).grid(row=0, column=2, padx=(8, 0))

        kpi = ctk.CTkFrame(self.content, fg_color="transparent")
        kpi.grid(row=1, column=0, sticky="ew", pady=(12, 12))
        for i in range(3):
            kpi.grid_columnconfigure(i, weight=1)

        self.card_info = Card(kpi, theme, fg_color=theme.colors["card_purple"])
        self.card_info.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        self.card_progress = Card(kpi, theme, fg_color=theme.colors["card_blue"])
        self.card_progress.grid(row=0, column=1, padx=8, sticky="nsew")
        self.card_score = Card(kpi, theme, fg_color=theme.colors["card_green"])
        self.card_score.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        self.quiz_title = ctk.CTkLabel(self.card_info, text="Đề thi hiện tại",
                                       font=theme.fonts["small"],
                                       text_color=theme.colors["muted"])
        self.quiz_title.pack(anchor="w", padx=12, pady=(10, 0))
        self.quiz_meta = ctk.CTkLabel(self.card_info, text="—",
                                      font=theme.fonts["body"],
                                      text_color=theme.colors["text"])
        self.quiz_meta.pack(anchor="w", padx=12, pady=(4, 10))

        ctk.CTkLabel(self.card_progress, text="Tiến độ",
                     font=theme.fonts["small"],
                     text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(10, 0))
        self.progress_text = ctk.CTkLabel(self.card_progress, text="0/0 câu",
                                          font=theme.fonts["header"],
                                          text_color=theme.colors["text"])
        self.progress_text.pack(anchor="w", padx=12)
        self.progress_bar = GlowProgressBar(self.card_progress, theme)
        self.progress_bar.pack(fill="x", padx=12, pady=(6, 12))

        ctk.CTkLabel(self.card_score, text="Điểm hiện tại",
                     font=theme.fonts["small"],
                     text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(10, 0))
        self.score_text = ctk.CTkLabel(self.card_score, text="0%",
                                       font=theme.fonts["title"],
                                       text_color=theme.colors["success"])
        self.score_text.pack(anchor="w", padx=12, pady=(4, 10))

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        left = Card(body, theme, fg_color=theme.colors["card_alt"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(left, text="Danh sách câu hỏi",
                     font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.question_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.question_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.grid_rowconfigure(1, weight=1)

        self.question_card = Card(right, theme, fg_color=theme.colors["card_blue"])
        self.question_card.grid(row=0, column=0, sticky="ew")
        self.question_title = ctk.CTkLabel(self.question_card, text="Câu 1",
                                           font=theme.fonts["header"],
                                           text_color=theme.colors["primary"])
        self.question_title.pack(anchor="w", padx=12, pady=(10, 4))
        self.question_text = ctk.CTkLabel(self.question_card, text="",
                                          font=theme.fonts["body"],
                                          text_color=theme.colors["text"],
                                          justify="left", wraplength=560)
        self.question_text.pack(anchor="w", padx=12, pady=(0, 12))

        self.answer_area = ctk.CTkFrame(right, fg_color="transparent")
        self.answer_area.grid(row=1, column=0, sticky="nsew", pady=(12, 12))

        self.explain_card = Card(right, theme, fg_color=theme.colors["card_violet"])
        self.explain_card.grid(row=2, column=0, sticky="ew")
        ctk.CTkLabel(self.explain_card, text="Giải thích",
                     font=theme.fonts["small"],
                     text_color=theme.colors["warning"]).pack(anchor="w", padx=12, pady=(10, 0))
        self.explain_text = ctk.CTkLabel(self.explain_card, text="",
                                         font=theme.fonts["small"],
                                         text_color=theme.colors["muted"],
                                         wraplength=560, justify="left")
        self.explain_text.pack(anchor="w", padx=12, pady=(4, 12))

        footer = ctk.CTkFrame(self.content, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        footer.grid_columnconfigure(1, weight=1)

        AppButton(footer, theme, text="Câu trước", variant="secondary",
                  command=self._prev_question, height=36).grid(row=0, column=0)
        self.footer_label = ctk.CTkLabel(footer, text="Câu 1/1",
                                         font=theme.fonts["small"],
                                         text_color=theme.colors["muted"])
        self.footer_label.grid(row=0, column=1)
        self.next_btn = AppButton(footer, theme, text="Câu tiếp theo",
                                  variant="primary", command=self._next_question,
                                  height=36)
        self.next_btn.grid(row=0, column=2)

    def _build_question_list(self):
        for w in self.question_list.winfo_children():
            w.destroy()
        self.question_buttons = []
        if not self.quiz_manager:
            return

        for idx in range(len(self.quiz_manager.get_questions())):
            btn = ctk.CTkButton(
                self.question_list,
                text=f"Câu {idx + 1}",
                fg_color="transparent",
                hover_color=self.theme.colors["surface"],
                text_color=self.theme.colors["muted"],
                anchor="w",
                command=lambda i=idx: self._jump_to_question(i),
            )
            btn.pack(fill="x", pady=4)
            self.question_buttons.append(btn)

    def _refresh_question(self):
        if not self.quiz_manager:
            return
        questions = self.quiz_manager.get_questions()
        if not questions:
            return

        idx = self.current_index
        q = questions[idx]
        self.question_title.configure(text=f"Câu {idx + 1}")
        self.question_text.configure(text=q.get("question", ""))

        saved = self.quiz_manager.get_answer(idx)
        self.selected_var.set(saved or "")
        self._update_explanation(q)
        self._build_answer_cards(q)
        self._update_answer_cards()
        self._update_progress()
        self._update_question_list()
        self.footer_label.configure(text=f"Câu {idx + 1}/{len(questions)}")

    def _build_answer_cards(self, question):
        for w in self.answer_area.winfo_children():
            w.destroy()
        self.answer_cards = []
        options = question.get("options", [])
        for i, option in enumerate(options[:4]):
            key = chr(65 + i)
            card = AnswerCard(self.answer_area, self.theme, key, option, self._select_answer)
            card.pack(fill="x", pady=6)
            self.answer_cards.append(card)

    def _select_answer(self, key):
        self.selected_var.set(key)
        self._on_choice_changed()

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
            card.set_state(is_selected, is_correct, is_wrong)

    def _update_question_list(self):
        if not self.quiz_manager:
            return
        questions = self.quiz_manager.get_questions()
        for idx, btn in enumerate(self.question_buttons):
            answer = self.quiz_manager.get_answer(idx)
            if idx == self.current_index:
                btn.configure(fg_color=self.theme.colors["primary"], text_color=self.theme.colors["text"])
            elif answer is None:
                btn.configure(fg_color="transparent", text_color=self.theme.colors["muted"])
            else:
                correct = questions[idx].get("answer")
                color = self.theme.colors["success"] if answer == correct else self.theme.colors["danger"]
                btn.configure(fg_color=color, text_color=self.theme.colors["text"])

    def _update_progress(self):
        if not self.quiz_manager:
            return
        questions = self.quiz_manager.get_questions()
        total = len(questions)
        answered = len(self.quiz_manager.user_answers)
        correct = 0
        for i, q in enumerate(questions):
            if self.quiz_manager.get_answer(i) == q.get("answer"):
                correct += 1
        pct = round(correct / total * 100) if total else 0

        self.progress_text.configure(text=f"{answered}/{total} câu")
        self.progress_bar.set(answered / max(total, 1))
        self.score_text.configure(text=f"{pct}%")

        title = self.quiz_manager.current_quiz.get("title", "Đề thi hiện tại")
        self.quiz_meta.configure(text=title)

    def _on_choice_changed(self, *_):
        if not self.quiz_manager:
            return
        ans = self.selected_var.get()
        if ans:
            self.quiz_manager.submit_answer(self.current_index, ans)
        else:
            self.quiz_manager.user_answers.pop(self.current_index, None)
        self._update_progress()
        self._update_question_list()
        self._update_answer_cards()
        self._update_explanation(self.quiz_manager.get_question(self.current_index))

    def _prev_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self._refresh_question()

    def _next_question(self):
        questions = self.quiz_manager.get_questions()
        if self.current_index < len(questions) - 1:
            self.current_index += 1
            self._refresh_question()
        else:
            self._submit()

    def _jump_to_question(self, index):
        self.current_index = index
        self._refresh_question()

    def _submit(self, force: bool = False):
        if not self.quiz_manager:
            return
        total = len(self.quiz_manager.get_questions())
        unanswered = max(total - len(self.quiz_manager.user_answers), 0)

        if not force:
            msg = "Bạn có chắc muốn nộp bài không?"
            if unanswered > 0:
                msg = f"Bạn còn {unanswered} câu chưa trả lời. Bạn vẫn muốn nộp bài chứ?"
            if not messagebox.askyesno("Nộp bài", msg):
                return

        self._stop_timer()
        elapsed = self.total_time - self.time_remaining
        result = self.quiz_manager.calculate_result(elapsed)
        self.quiz_manager.save_history(result)
        self.controller.set_shared("result", result)
        self.controller.show_screen("result")

    def _start_timer(self):
        self._stop_timer()
        self._tick()

    def _stop_timer(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None

    def _tick(self):
        if self.time_remaining <= 0:
            self.timer_label.configure(text="00:00")
            messagebox.showwarning("Hết giờ", "Thời gian đã hết. Bài thi sẽ nộp tự động.")
            self._submit(force=True)
            return

        m, s = divmod(self.time_remaining, 60)
        self.timer_label.configure(text=f"{m:02d}:{s:02d}")
        if self.total_time:
            self.countdown_bar.set(self.time_remaining / self.total_time)

        self.time_remaining -= 1
        self._timer_id = self.after(1000, self._tick)

    def _update_explanation(self, question):
        selected = self.selected_var.get()
        if selected:
            text = question.get("explanation", "Chưa có giải thích.")
        else:
            text = ""
        self.explain_text.configure(text=text)
