"""
ui/screen_history.py
Màn hình lịch sử: xem tất cả lần thi, xem chi tiết, làm lại
"""

import tkinter as tk
import tkinter.font as tkfont
import json
import os
from tkinter import messagebox

from ui.app import COLORS
from ui.components import RoundedCard, PillButton, GradientButton, blend
from ui.layout import build_sidebar, build_title_block

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "Data", "history.json")


class ScreenHistory(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.history = []
        self.selected_index = None
        self._build_ui()

    def on_enter(self):
        """Tải lại lịch sử mỗi khi vào màn hình — không cần quiz_manager."""
        self._load_history()

    # ── BUILD UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        c = self.controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = build_sidebar(self, c, active="history")
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
            "Lịch sử",
            "Theo dõi các lần thi và luyện tập lại bất kỳ lúc nào",
        )
        title_block.grid(row=0, column=0, sticky="w")

        content = tk.Frame(self.main, bg=COLORS["bg"])
        content.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 12))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        list_card = RoundedCard(
            content,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=12,
        )
        list_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(list_card.inner, text="Danh sách lần thi",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(0, 6))

        lb_frame = tk.Frame(list_card.inner, bg=COLORS["card"])
        lb_frame.pack(fill="both", expand=True)

        sb = tk.Scrollbar(lb_frame)
        sb.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            lb_frame,
            font=c.fonts["small"],
            bg=COLORS["card_alt"],
            fg=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground="white",
            relief="flat",
            bd=0,
            yscrollcommand=sb.set,
            activestyle="none",
            cursor="hand2",
        )
        self.listbox.pack(fill="both", expand=True)
        sb.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        self.btn_clear = PillButton(
            list_card.inner,
            text="Xóa tất cả lịch sử",
            command=self._clear_history,
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=32,
            width=170,
        )
        self.btn_clear.pack(anchor="w", pady=(10, 0))

        detail_card = RoundedCard(
            content,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=12,
        )
        detail_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(detail_card.inner, text="Chi tiết lần thi",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(0, 6))

        self.detail_frame = tk.Frame(detail_card.inner, bg=COLORS["card"])
        self.detail_frame.pack(fill="both", expand=True)

        self._show_empty_detail()

        footer = tk.Frame(self.main, bg=COLORS["bg"])
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 18))
        footer.grid_columnconfigure(1, weight=1)

        self.btn_back = PillButton(
            footer,
            text="Quay lại",
            command=self._go_back,
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["btn"],
            height=40,
            width=140,
        )
        self.btn_back.grid(row=0, column=0, sticky="w")

        self.btn_retry = PillButton(
            footer,
            text="Làm lại đề này",
            command=self._retry_quiz,
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["btn"],
            height=40,
            width=160,
        )
        self.btn_retry.grid(row=0, column=1)
        self.btn_retry.set_enabled(False)

        self.btn_new = GradientButton(
            footer,
            text="Tạo đề mới",
            command=lambda: self.controller.show_screen("upload"),
            left_color=COLORS["accent"],
            right_color=COLORS["accent2"],
            hover_left=blend(COLORS["accent"], "#FFFFFF", 0.08),
            hover_right=blend(COLORS["accent2"], "#FFFFFF", 0.08),
            fg="white",
            font=c.fonts["btn"],
            height=42,
            width=160,
        )
        self.btn_new.grid(row=0, column=2, sticky="e")

    # ── LOAD & HIỂN THỊ DANH SÁCH ───────────────────────────────────────────

    def _load_history(self):
        """Đọc thẳng từ file history.json — không cần quiz_manager."""
        self.history = self._read_history_file()
        self.listbox.delete(0, tk.END)
        self.selected_index = None
        self.btn_retry.set_enabled(False)

        if not self.history:
            self.listbox.insert(tk.END, "  Chưa có lịch sử thi")
            self._show_empty_detail()
            return

        self.history = list(reversed(self.history))
        for item in self.history:
            score = item.get("score", 0)
            total = item.get("total", 0)
            grade = item.get("grade", "")
            date = item.get("date", "")
            self.listbox.insert(
                tk.END,
                f"  {date}   {score}/{total}  ({grade})"
            )

    def _read_history_file(self) -> list:
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    # ── CHỌN LẦN THI ─────────────────────────────────────────────────────────

    def _on_select(self, _event):
        sel = self.listbox.curselection()
        if not sel or not self.history:
            return
        idx = sel[0]
        if idx >= len(self.history):
            return
        self.selected_index = idx
        self._show_detail(self.history[idx])
        self.btn_retry.set_enabled(True)

    # ── CHI TIẾT ─────────────────────────────────────────────────────────────

    def _show_empty_detail(self):
        for w in self.detail_frame.winfo_children():
            w.destroy()
        tk.Label(self.detail_frame,
                 text="← Chọn một lần thi để xem chi tiết",
                 font=self.controller.fonts["body"],
                 bg=COLORS["card"], fg=COLORS["muted"]
                 ).pack(expand=True)

    def _show_detail(self, result: dict):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        c = self.controller

        score_box = tk.Frame(self.detail_frame, bg=COLORS["card_alt"], pady=10)
        score_box.pack(fill="x", pady=(0, 8))

        score = result.get("score", 0)
        total = result.get("total", 0)

        tk.Label(score_box,
                 text=f"{score}/{total}",
                 font=tkfont.Font(family="Consolas", size=30, weight="bold"),
                 bg=COLORS["card_alt"],
                 fg=COLORS["green"] if score / max(total, 1) >= 0.5 else COLORS["accent"]
                 ).pack()

        tk.Label(score_box,
                 text=(f"{result.get('grade','')}  ·  "
                       f"{result.get('percentage',0)}%  ·  "
                       f"{result.get('time_taken','')}")
                 , font=c.fonts["small"], bg=COLORS["card_alt"],
                 fg=COLORS["muted"]).pack()

        tk.Label(score_box,
                 text=result.get("quiz_title", ""),
                 font=c.fonts["body"], bg=COLORS["card_alt"],
                 fg=COLORS["text"]).pack()

        tk.Label(self.detail_frame, text="Chi tiết từng câu:",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w", pady=(4, 2))

        wrap = tk.Frame(self.detail_frame, bg=COLORS["card"])
        wrap.pack(fill="both", expand=True)

        canvas = tk.Canvas(wrap, bg=COLORS["card"], highlightthickness=0)
        vsb = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLORS["card"])

        inner.bind("<Configure>",
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)

        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        detail_list = result.get("detail", [])
        if not detail_list:
            tk.Label(inner, text="Không có dữ liệu chi tiết.",
                     font=c.fonts["small"], bg=COLORS["card"],
                     fg=COLORS["muted"]).pack(pady=10)
            return

        for item in detail_list:
            is_correct = item.get("is_correct", False)
            color = COLORS["green"] if is_correct else COLORS["danger"]
            icon = "✓" if is_correct else "✗"

            row = tk.Frame(inner, bg=COLORS["card_alt"], pady=5, padx=8)
            row.pack(fill="x", pady=2, padx=2)

            tk.Label(row, text=f"[{icon}] Câu {item['index']+1}",
                     font=c.fonts["small"], bg=COLORS["card_alt"],
                     fg=color, width=9, anchor="w").pack(side="left")

            q = item.get("question", "")
            q_short = q[:48] + "…" if len(q) > 48 else q
            tk.Label(row, text=q_short,
                     font=c.fonts["small"], bg=COLORS["card_alt"],
                     fg=COLORS["text"], anchor="w"
                     ).pack(side="left", fill="x", expand=True)

            user_ans = item.get("user_answer") or "—"
            correct_ans = item.get("correct_answer", "?")
            tk.Label(row,
                     text=f"Bạn: {user_ans}  Đúng: {correct_ans}",
                     font=c.fonts["small"], bg=COLORS["card_alt"],
                     fg=COLORS["muted"], anchor="e"
                     ).pack(side="right")

        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * e.delta / 120), "units"))

    # ── HÀNH ĐỘNG ───────────────────────────────────────────────────────────

    def _go_back(self):
        """Quay lại màn hình phù hợp."""
        result = self.controller.get_shared("result")
        if result:
            self.controller.show_screen("result")
        else:
            self.controller.show_screen("upload")

    def _retry_quiz(self):
        """Làm lại đề thi đã chọn."""
        if self.selected_index is None:
            return

        result = self.history[self.selected_index]
        questions = result.get("questions", [])

        if not questions:
            messagebox.showwarning(
                "Không có câu hỏi",
                "Lần thi này không lưu câu hỏi gốc.\n"
                "Chỉ áp dụng cho các lần thi sau khi cập nhật."
            )
            return

        from Core.quiz_manager import QuizManager
        quiz_manager = QuizManager()
        settings = result.get("settings", {
            "num_questions": len(questions),
            "difficulty": "medium",
            "time_limit": 15
        })
        quiz_manager.create_quiz(questions, settings, result.get("quiz_title", "Làm lại"))
        quiz_manager.user_answers = {}

        self.controller.set_shared("quiz_manager", quiz_manager)
        self.controller.set_shared("settings", settings)
        self.controller.set_shared("questions", questions)

        self.controller.show_screen("quiz")

    def _clear_history(self):
        if not self.history:
            messagebox.showinfo("Thông báo", "Chưa có lịch sử để xóa.")
            return
        if messagebox.askyesno("Xác nhận", "Xóa toàn bộ lịch sử thi?"):
            try:
                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f)
                self.history = []
                self.listbox.delete(0, tk.END)
                self.listbox.insert(tk.END, "  Chưa có lịch sử thi")
                self._show_empty_detail()
                self.btn_retry.set_enabled(False)
                messagebox.showinfo("Xong", "Đã xóa toàn bộ lịch sử.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {e}")
