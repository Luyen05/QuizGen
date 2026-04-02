"""
ui/screen_settings.py
Màn hình 2: Người dùng cài đặt thông số → bấm tạo đề → AI xử lý
"""

import tkinter as tk
from tkinter import messagebox
import threading

from Core.ai_generator import generate_questions
from Core.quiz_manager import QuizManager
from ui.app import COLORS


class ScreenSettings(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.quiz_manager = QuizManager()

        # Biến cài đặt
        self.num_questions = tk.IntVar(value=10)
        self.num_options   = tk.IntVar(value=4)
        self.difficulty    = tk.StringVar(value="medium")
        self.language      = tk.StringVar(value="Tiếng Việt")
        self.time_limit    = tk.IntVar(value=15)

        self._build_ui()

    def on_enter(self):
        """Reset progress bar khi vào màn hình."""
        self.progress_var.set(0)
        self.status_var.set("Sẵn sàng tạo đề...")
        self.btn_generate.config(state="normal")

    def _build_ui(self):
        c = self.controller

        tk.Label(self, text="QuizGen", font=c.fonts["title"],
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(30, 4))
        tk.Label(self, text="Cài đặt thông số đề thi",
                 font=c.fonts["small"], bg=COLORS["bg"],
                 fg=COLORS["muted"]).pack()

        self._build_nav(active="settings")

        # ── Form cài đặt ──
        frame = tk.LabelFrame(self, text=" Thông số đề thi ",
                              bg=COLORS["surface"], fg=COLORS["text"],
                              font=c.fonts["small"], padx=20, pady=12,
                              bd=1, relief="solid")
        frame.pack(fill="x", padx=40, pady=(16, 8))

        # Hàm tạo 1 dòng cài đặt
        def setting_row(label, widget_fn):
            row = tk.Frame(frame, bg=COLORS["surface"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=c.fonts["body"],
                     bg=COLORS["surface"], fg=COLORS["text"],
                     width=20, anchor="w").pack(side="left")
            widget_fn(row)

        # Số câu hỏi
        setting_row("Số câu hỏi:", lambda r: tk.Spinbox(
            r, from_=5, to=30, textvariable=self.num_questions,
            width=6, font=c.fonts["body"], bg=COLORS["card"],
            fg=COLORS["text"], relief="flat"
        ).pack(side="left"))

        # Số đáp án
        setting_row("Số đáp án mỗi câu:", lambda r: tk.Spinbox(
            r, from_=2, to=5, textvariable=self.num_options,
            width=6, font=c.fonts["body"], bg=COLORS["card"],
            fg=COLORS["text"], relief="flat"
        ).pack(side="left"))

        # Độ khó
        def build_difficulty(r):
            for val, label in [("easy","Dễ"),("medium","Trung bình"),("hard","Khó")]:
                tk.Radiobutton(r, text=label, variable=self.difficulty, value=val,
                               font=c.fonts["body"], bg=COLORS["surface"],
                               fg=COLORS["text"], selectcolor=COLORS["card"],
                               activebackground=COLORS["surface"]).pack(side="left", padx=6)
        setting_row("Độ khó:", build_difficulty)

        # Ngôn ngữ
        setting_row("Ngôn ngữ:", lambda r: tk.OptionMenu(
            r, self.language, "Tiếng Việt", "English"
        ).pack(side="left"))

        # Thời gian
        setting_row("Thời gian (phút):", lambda r: tk.Spinbox(
            r, from_=5, to=60, textvariable=self.time_limit,
            width=6, font=c.fonts["body"], bg=COLORS["card"],
            fg=COLORS["text"], relief="flat"
        ).pack(side="left"))

        # ── Progress bar ──
        frame_prog = tk.Frame(self, bg=COLORS["bg"])
        frame_prog.pack(fill="x", padx=40, pady=8)

        self.status_var = tk.StringVar(value="Sẵn sàng tạo đề...")
        tk.Label(frame_prog, textvariable=self.status_var,
                 font=c.fonts["small"], bg=COLORS["bg"],
                 fg=COLORS["muted"]).pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_canvas = tk.Canvas(frame_prog, height=8,
                                         bg=COLORS["surface"],
                                         highlightthickness=0)
        self.progress_canvas.pack(fill="x", pady=4)
        self.progress_canvas.bind("<Configure>", self._draw_progress)

        # ── Nút ──
        btn_row = tk.Frame(self, bg=COLORS["bg"])
        btn_row.pack(pady=12)

        tk.Button(btn_row, text="◀ Quay lại",
                  font=c.fonts["btn"], bg=COLORS["surface"],
                  fg=COLORS["muted"], relief="flat", cursor="hand2",
                  padx=14, pady=8,
                  command=lambda: self.controller.show_screen("upload")
                  ).pack(side="left", padx=6)

        self.btn_generate = tk.Button(btn_row, text="🤖 Tạo đề thi",
                  font=c.fonts["btn"], bg=COLORS["accent"],
                  fg="white", relief="flat", cursor="hand2",
                  padx=20, pady=8,
                  command=self._start_generate)
        self.btn_generate.pack(side="left", padx=6)

    def _build_nav(self, active: str):
        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(pady=(12, 0))
        for label, name in [("📂 Tải lên","upload"),("⚙️ Cài đặt","settings"),
                             ("📝 Thi thử","quiz"),("📊 Kết quả","result")]:
            bg = COLORS["accent"] if name == active else COLORS["surface"]
            fg = "white" if name == active else COLORS["muted"]
            tk.Label(nav, text=label, font=self.controller.fonts["small"],
                     bg=bg, fg=fg, padx=12, pady=5).pack(side="left", padx=2)

    def _draw_progress(self, event=None):
        """Vẽ thanh progress thủ công bằng Canvas."""
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width()
        pct = self.progress_var.get() / 100
        fill_w = int(w * pct)
        self.progress_canvas.create_rectangle(0, 0, w, 8,
                                              fill=COLORS["surface"], outline="")
        if fill_w > 0:
            self.progress_canvas.create_rectangle(0, 0, fill_w, 8,
                                                   fill=COLORS["accent"], outline="")

    def _update_progress(self, value: float, status: str):
        """Cập nhật UI từ thread phụ — dùng after() để an toàn."""
        def _update():
            self.progress_var.set(value)
            self.status_var.set(status)
            self._draw_progress()
        self.after(0, _update)

    def _start_generate(self):
        """
        Chạy generate trong thread riêng để UI không bị đơ.
        Đây là kỹ thuật quan trọng khi gọi API tốn thời gian.
        """
        self.btn_generate.config(state="disabled")
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
                "num_options":   self.num_options.get(),
                "difficulty":    self.difficulty.get(),
                "language":      self.language.get(),
                "time_limit":    self.time_limit.get(),
            }

            questions = generate_questions(
                text=text,
                num_questions=settings["num_questions"],
                num_options=settings["num_options"],
                difficulty=settings["difficulty"],
                language=settings["language"],
            )

            self._update_progress(80, "Đang xử lý kết quả...")

            quiz = self.quiz_manager.create_quiz(questions, settings)

            # Lưu vào shared data
            self.controller.set_shared("questions", questions)
            self.controller.set_shared("settings", settings)
            self.controller.set_shared("quiz_manager", self.quiz_manager)

            self._update_progress(100, f"✅ Tạo xong {len(questions)} câu hỏi!")

            # Chuyển màn hình sau 500ms
            self.after(500, lambda: self.controller.show_screen("quiz"))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi tạo đề", str(e)))
            self._update_progress(0, "Lỗi — thử lại")
            self.after(0, lambda: self.btn_generate.config(state="normal"))