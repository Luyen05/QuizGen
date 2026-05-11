"""
ui/screen_quiz.py
Màn hình 3: Thi thử — hiển thị câu hỏi, đếm giờ, ghi nhận đáp án
"""

import tkinter as tk
from tkinter import messagebox
from ui.app import COLORS


class ScreenQuiz(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.current_index = 0
        self.selected_var = tk.StringVar(value="")
        self.flagged = set()
        self._suppress_choice_trace = False
        self.time_remaining = 0
        self._timer_id = None
        self.quiz_manager = None  # fix AttributeError
        self.selected_var.trace_add("write", self._on_choice_changed)
        self._build_ui()

    def on_enter(self):
        """Reset và bắt đầu bài thi mới."""
        self.current_index = 0
        self.selected_var.set("")
        self.flagged = set()

        settings = self.controller.get_shared("settings") or {}
        self.time_remaining = settings.get("time_limit", 15) * 60
        self.quiz_manager = self.controller.get_shared("quiz_manager")

        self._build_question_grid()
        self._refresh_question()
        self._start_timer()

    def _build_ui(self):
        c = self.controller

        tk.Label(self, text="QuizGen", font=c.fonts["title"],
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(30, 4))

        self._build_nav(active="quiz")

        # ── Header: câu số / đồng hồ ──
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=40, pady=(12, 4))

        self.q_counter_var = tk.StringVar(value="Câu 1 / 10")
        tk.Label(header, textvariable=self.q_counter_var,
                 font=c.fonts["body"], bg=COLORS["bg"],
                 fg=COLORS["muted"]).pack(side="left")

        self.timer_var = tk.StringVar(value="⏱ 15:00")
        tk.Label(header, textvariable=self.timer_var,
                 font=c.fonts["header"], bg=COLORS["bg"],
                 fg=COLORS["yellow"]).pack(side="right")

        # Progress bar câu hỏi
        self.prog_canvas = tk.Canvas(self, height=6, bg=COLORS["surface"],
                                     highlightthickness=0)
        self.prog_canvas.pack(fill="x", padx=40, pady=2)
        self.prog_canvas.bind("<Configure>", self._draw_progress)

        info_row = tk.Frame(self, bg=COLORS["bg"])
        info_row.pack(fill="x", padx=40, pady=(2, 6))

        self.progress_var = tk.StringVar(value="Đã làm: 0/0 · Còn lại: 0 · Đánh dấu: 0")
        tk.Label(info_row, textvariable=self.progress_var,
             font=c.fonts["small"], bg=COLORS["bg"],
             fg=COLORS["muted"]).pack(side="left")

        self.flag_state_var = tk.StringVar(value="")
        tk.Label(info_row, textvariable=self.flag_state_var,
             font=c.fonts["small"], bg=COLORS["bg"],
             fg=COLORS["yellow"]).pack(side="right")

        # ── Câu hỏi ──
        frame_q = tk.Frame(self, bg=COLORS["card"], padx=16, pady=12)
        frame_q.pack(fill="x", padx=40, pady=(10, 6))

        self.q_num_label = tk.Label(frame_q, text="CÂU HỎI 01",
                                     font=c.fonts["small"], bg=COLORS["card"],
                                     fg=COLORS["accent"])
        self.q_num_label.pack(anchor="w")

        self.q_text_label = tk.Label(frame_q, text="",
                                      font=c.fonts["body"], bg=COLORS["card"],
                                      fg=COLORS["text"], wraplength=680,
                                      justify="left")
        self.q_text_label.pack(anchor="w", pady=(4, 0))

        # ── Đáp án (4 radio button) ──
        self.option_frame = tk.Frame(self, bg=COLORS["bg"])
        self.option_frame.pack(fill="x", padx=40, pady=4)
        self.option_buttons = []

        for key in ["A", "B", "C", "D"]:
            btn = tk.Radiobutton(
                self.option_frame,
                text="", variable=self.selected_var, value=key,
                font=c.fonts["body"], bg=COLORS["surface"],
                fg=COLORS["text"], selectcolor=COLORS["card"],
                activebackground=COLORS["surface"],
                indicatoron=True, padx=12, pady=8,
                anchor="w", relief="flat"
            )
            btn.pack(fill="x", pady=3)
            self.option_buttons.append(btn)

        # ── Danh sách câu (nhảy nhanh) ──
        grid_box = tk.LabelFrame(self, text=" Danh sách câu ",
                                 bg=COLORS["surface"], fg=COLORS["text"],
                                 font=c.fonts["small"], padx=8, pady=8,
                                 bd=1, relief="solid")
        grid_box.pack(fill="x", padx=40, pady=(6, 4))

        self.grid_container = tk.Frame(grid_box, bg=COLORS["surface"])
        self.grid_container.pack(fill="x")
        self.grid_buttons = []

        # ── Nút điều hướng ──
        nav_row = tk.Frame(self, bg=COLORS["bg"])
        nav_row.pack(pady=12)

        self.btn_prev = tk.Button(nav_row, text="◀ Câu trước",
                   font=c.fonts["btn"], bg=COLORS["surface"],
                   fg=COLORS["muted"], relief="flat", cursor="hand2",
                   padx=14, pady=8, command=self._prev_question)
        self.btn_prev.pack(side="left", padx=6)

        self.btn_skip = tk.Button(nav_row, text="Bỏ qua",
               font=c.fonts["btn"], bg=COLORS["surface"],
               fg=COLORS["text"], relief="flat", cursor="hand2",
               padx=14, pady=8, command=self._skip_question)
        self.btn_skip.pack(side="left", padx=6)

        self.btn_mark = tk.Button(nav_row, text="🔖 Đánh dấu",
               font=c.fonts["btn"], bg=COLORS["surface"],
               fg=COLORS["text"], relief="flat", cursor="hand2",
               padx=14, pady=8, command=self._toggle_flag)
        self.btn_mark.pack(side="left", padx=6)

        self.btn_next = tk.Button(nav_row, text="Câu tiếp theo ▶",
                   font=c.fonts["btn"], bg=COLORS["accent"],
                   fg="white", relief="flat", cursor="hand2",
                   padx=20, pady=8, command=self._next_question)
        self.btn_next.pack(side="left", padx=6)

    def _build_nav(self, active: str):
        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(pady=(12, 0))
        tabs = [
            ("📂 Tải lên",  "upload"),
            ("⚙️ Cài đặt", "settings"),
            ("📝 Thi thử",  "quiz"),
            ("📊 Kết quả",  "result"),
            ("📜 Lịch sử",  "history"),
        ]
        for label, name in tabs:
            bg = COLORS["accent"] if name == active else COLORS["surface"]
            fg = "white" if name == active else COLORS["muted"]
            lbl = tk.Label(nav, text=label,
                           font=self.controller.fonts["small"],
                           bg=bg, fg=fg, padx=10, pady=5,
                           cursor="hand2")
            lbl.pack(side="left", padx=2)
            if name != active:
                lbl.bind("<Button-1>",
                         lambda e, n=name: self.controller.show_screen(n))

    def _refresh_question(self):
        """Cập nhật UI theo câu hỏi hiện tại."""
        if not self.quiz_manager:
            return

        questions = self.quiz_manager.get_questions()
        total = len(questions)
        idx = self.current_index
        q = questions[idx]

        # Cập nhật counter và câu hỏi
        self.q_counter_var.set(f"Câu {idx + 1} / {total}")
        self.q_num_label.config(text=f"CÂU HỎI {idx + 1:02d}")
        self.q_text_label.config(text=q["question"])

        # Cập nhật đáp án
        for i, btn in enumerate(self.option_buttons):
            if i < len(q["options"]):
                btn.config(text=q["options"][i], state="normal")
            else:
                btn.config(text="", state="disabled")

        # Khôi phục đáp án đã chọn (nếu có)
        saved = self.quiz_manager.get_answer(idx)
        self._suppress_choice_trace = True
        self.selected_var.set(saved if saved else "")
        self._suppress_choice_trace = False

        # Cập nhật nút điều hướng
        self.btn_prev.config(state="normal" if idx > 0 else "disabled")
        last_q = (idx == total - 1)
        self.btn_next.config(text="🏁 Nộp bài" if last_q else "Câu tiếp theo ▶")

        is_flagged = idx in self.flagged
        self.btn_mark.config(
            text="🔖 Bỏ đánh dấu" if is_flagged else "🔖 Đánh dấu",
            bg=COLORS["yellow"] if is_flagged else COLORS["surface"],
            fg=COLORS["bg"] if is_flagged else COLORS["text"]
        )

        self._update_progress_info()
        self._update_grid_buttons()

        self._draw_progress()

    def _draw_progress(self, event=None):
        self.prog_canvas.delete("all")
        if not self.quiz_manager:
            return
        total = len(self.quiz_manager.get_questions())
        if total == 0:
            return
        w = self.prog_canvas.winfo_width()
        fill_w = int(w * (self.current_index + 1) / total)
        self.prog_canvas.create_rectangle(0, 0, w, 6,
                                          fill=COLORS["surface"], outline="")
        self.prog_canvas.create_rectangle(0, 0, fill_w, 6,
                                          fill=COLORS["accent"], outline="")

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
            # Câu cuối → nộp bài
            self._submit()

    def _save_current_answer(self):
        """Lưu đáp án câu hiện tại vào quiz_manager."""
        ans = self.selected_var.get()
        if ans and self.quiz_manager:
            self.quiz_manager.submit_answer(self.current_index, ans)

    def _clear_current_answer(self):
        if not self.quiz_manager:
            return
        self.quiz_manager.user_answers.pop(self.current_index, None)
        self._suppress_choice_trace = True
        self.selected_var.set("")
        self._suppress_choice_trace = False
        self._update_progress_info()
        self._update_grid_buttons()

    def _skip_question(self):
        """Bỏ qua câu hiện tại và chuyển sang câu kế tiếp."""
        if not self.quiz_manager:
            return
        self._clear_current_answer()
        questions = self.quiz_manager.get_questions()
        total = len(questions)
        if total == 0:
            return

        if self.current_index < total - 1:
            self.current_index += 1
            self._refresh_question()
            return

        self._jump_to_first_unanswered()

    def _jump_to_first_unanswered(self):
        if not self.quiz_manager:
            return
        questions = self.quiz_manager.get_questions()
        total = len(questions)
        if total == 0:
            return
        for idx in range(total):
            if self.quiz_manager.get_answer(idx) is None:
                self.current_index = idx
                self._refresh_question()
                return

    def _toggle_flag(self):
        if self.current_index in self.flagged:
            self.flagged.remove(self.current_index)
        else:
            self.flagged.add(self.current_index)
        self._update_progress_info()
        self._update_grid_buttons()
        self._refresh_question()

    def _jump_to_question(self, index: int):
        self._save_current_answer()
        self.current_index = index
        self._refresh_question()

    def _build_question_grid(self):
        if not self.quiz_manager:
            return
        for w in self.grid_container.winfo_children():
            w.destroy()
        self.grid_buttons = []

        questions = self.quiz_manager.get_questions()
        cols = 10
        for i in range(len(questions)):
            btn = tk.Button(
                self.grid_container,
                text=str(i + 1),
                width=4,
                font=self.controller.fonts["small"],
                bg=COLORS["surface"], fg=COLORS["text"],
                relief="flat", cursor="hand2",
                command=lambda idx=i: self._jump_to_question(idx)
            )
            btn.grid(row=i // cols, column=i % cols, padx=3, pady=3)
            self.grid_buttons.append(btn)

        self._update_progress_info()
        self._update_grid_buttons()

    def _update_grid_buttons(self):
        if not self.quiz_manager:
            return
        for i, btn in enumerate(self.grid_buttons):
            answered = self.quiz_manager.get_answer(i) is not None
            flagged = i in self.flagged
            is_current = i == self.current_index

            if is_current:
                bg = COLORS["accent"]
                fg = "white"
            elif flagged:
                bg = COLORS["yellow"]
                fg = COLORS["bg"]
            elif answered:
                bg = COLORS["green"]
                fg = COLORS["bg"]
            else:
                bg = COLORS["surface"]
                fg = COLORS["text"]

            btn.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)

    def _update_progress_info(self):
        if not self.quiz_manager:
            return
        total = len(self.quiz_manager.get_questions())
        answered = len(self.quiz_manager.user_answers)
        remaining = max(total - answered, 0)
        flagged = len(self.flagged)
        self.progress_var.set(
            f"Đã làm: {answered}/{total} · Còn lại: {remaining} · Đánh dấu: {flagged}"
        )
        self.flag_state_var.set("🔖 Đã đánh dấu" if self.current_index in self.flagged else "")

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

    # ── Timer ────────────────────────────────────────────────────────────────

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
            self.timer_var.set("⏱ 00:00")
            messagebox.showwarning("Hết giờ!", "Thời gian đã hết. Bài thi sẽ được nộp tự động.")
            self._submit(force=True)
            return

        m, s = divmod(self.time_remaining, 60)
        self.timer_var.set(f"⏱ {m:02d}:{s:02d}")

        # Chuyển màu đỏ khi còn < 1 phút
        color = COLORS["accent"] if self.time_remaining < 60 else COLORS["yellow"]
        # Tìm label timer và đổi màu
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and "⏱" in str(child.cget("textvariable")):
                        child.config(fg=color)

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
        self._update_grid_buttons()