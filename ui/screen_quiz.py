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
        self.time_remaining = 0
        self._timer_id = None
        self.quiz_manager = None
        self._build_ui()

    def on_enter(self):
        """Reset và bắt đầu bài thi mới."""
        self.current_index = 0
        self.selected_var.set("")

        settings = self.controller.get_shared("settings") or {}
        self.time_remaining = settings.get("time_limit", 15) * 60
        self.quiz_manager = self.controller.get_shared("quiz_manager")

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

        # ── Nút điều hướng ──
        nav_row = tk.Frame(self, bg=COLORS["bg"])
        nav_row.pack(pady=12)

        self.btn_prev = tk.Button(nav_row, text="◀ Câu trước",
                   font=c.fonts["btn"], bg=COLORS["surface"],
                   fg=COLORS["muted"], relief="flat", cursor="hand2",
                   padx=14, pady=8, command=self._prev_question)
        self.btn_prev.pack(side="left", padx=6)

        self.btn_next = tk.Button(nav_row, text="Câu tiếp theo ▶",
                   font=c.fonts["btn"], bg=COLORS["accent"],
                   fg="white", relief="flat", cursor="hand2",
                   padx=20, pady=8, command=self._next_question)
        self.btn_next.pack(side="left", padx=6)

    def _build_nav(self, active: str):
        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(pady=(12, 0))
        for label, name in [("📂 Tải lên","upload"),("⚙️ Cài đặt","settings"),
                             ("📝 Thi thử","quiz"),("📊 Kết quả","result")]:
            bg = COLORS["accent"] if name == active else COLORS["surface"]
            fg = "white" if name == active else COLORS["muted"]
            tk.Label(nav, text=label, font=self.controller.fonts["small"],
                     bg=bg, fg=fg, padx=12, pady=5).pack(side="left", padx=2)

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
        self.selected_var.set(saved if saved else "")

        # Cập nhật nút điều hướng
        self.btn_prev.config(state="normal" if idx > 0 else "disabled")
        last_q = (idx == total - 1)
        self.btn_next.config(text="🏁 Nộp bài" if last_q else "Câu tiếp theo ▶")

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

    def _submit(self):
        """Nộp bài, tính điểm, chuyển màn hình kết quả."""
        if messagebox.askyesno("Nộp bài", "Bạn có chắc muốn nộp bài không?"):
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
            self._submit()
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