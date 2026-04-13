"""
ui/screen_history.py
Màn hình lịch sử: xem tất cả lần thi, xem chi tiết, làm lại
- Fix: nút Quay lại + Làm lại luôn hiển thị dù đang xem chi tiết
- Fix: truy cập được bất kỳ lúc nào từ nav bar
- Lịch sử đọc trực tiếp từ file history.json — không cần quiz_manager
"""

import tkinter as tk
import tkinter.font as tkfont
import json
import os
from tkinter import messagebox

from ui.app import COLORS

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

    # ── BUILD UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        c = self.controller

        # Header
        tk.Label(self, text="QuizGen", font=c.fonts["title"],
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(20, 2))
        tk.Label(self, text="Lịch sử bài thi",
                 font=c.fonts["small"], bg=COLORS["bg"],
                 fg=COLORS["muted"]).pack()

        self._build_nav()

        # ── PHẦN CHÍNH: chia trái/phải, chiều cao cố định ──
        # Dùng place để kiểm soát chính xác — tránh bị đẩy bởi nội dung
        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=16, pady=8)

        # Cột trái — danh sách (cố định 280px)
        left = tk.Frame(content, bg=COLORS["surface"], width=280)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)

        tk.Label(left, text="📋 Danh sách lần thi",
                 font=c.fonts["small"], bg=COLORS["surface"],
                 fg=COLORS["muted"], pady=6).pack(fill="x", padx=8)

        # Listbox + scrollbar
        lb_frame = tk.Frame(left, bg=COLORS["surface"])
        lb_frame.pack(fill="both", expand=True, padx=6)

        sb = tk.Scrollbar(lb_frame)
        sb.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            lb_frame,
            font=c.fonts["small"],
            bg=COLORS["card"], fg=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground="white",
            relief="flat", bd=0,
            yscrollcommand=sb.set,
            activestyle="none",
            cursor="hand2"
        )
        self.listbox.pack(fill="both", expand=True)
        sb.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        tk.Button(left, text="🗑 Xóa tất cả lịch sử",
                  font=c.fonts["small"], bg=COLORS["surface"],
                  fg=COLORS["accent"], relief="flat", cursor="hand2",
                  command=self._clear_history).pack(pady=6)

        # Cột phải — chi tiết
        right = tk.Frame(content, bg=COLORS["surface"])
        right.pack(side="left", fill="both", expand=True)

        # Phần trên: nội dung chi tiết (có thể scroll)
        self.detail_frame = tk.Frame(right, bg=COLORS["surface"])
        self.detail_frame.pack(fill="both", expand=True, padx=10, pady=(8, 4))

        self._show_empty_detail()

        # ── PHẦN DƯỚI: nút bấm — LUÔN CỐ ĐỊNH Ở ĐÁY ──
        # pack trực tiếp vào self (không vào content) để không bị đẩy
        btn_bar = tk.Frame(self, bg=COLORS["bg"], pady=8)
        btn_bar.pack(fill="x", side="bottom")

        tk.Button(btn_bar, text="◀ Quay lại",
                  font=c.fonts["btn"], bg=COLORS["surface"],
                  fg=COLORS["muted"], relief="flat", cursor="hand2",
                  padx=14, pady=7,
                  command=self._go_back).pack(side="left", padx=(20, 6))

        self.btn_retry = tk.Button(
            btn_bar, text="🔁 Làm lại đề này",
            font=c.fonts["btn"], bg=COLORS["accent"],
            fg="white", relief="flat", cursor="hand2",
            padx=16, pady=7,
            state="disabled",
            command=self._retry_quiz
        )
        self.btn_retry.pack(side="left", padx=6)

        tk.Button(btn_bar, text="🔄 Tạo đề mới",
                  font=c.fonts["btn"], bg=COLORS["green"],
                  fg=COLORS["bg"], relief="flat", cursor="hand2",
                  padx=16, pady=7,
                  command=lambda: self.controller.show_screen("upload")
                  ).pack(side="right", padx=(6, 20))

    def _build_nav(self):
        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(pady=(8, 0))
        for label, name in [
            ("📂 Tải lên",  "upload"),
            ("⚙️ Cài đặt", "settings"),
            ("📝 Thi thử",  "quiz"),
            ("📊 Kết quả",  "result"),
            ("📜 Lịch sử",  "history"),
        ]:
            bg = COLORS["accent"] if name == "history" else COLORS["surface"]
            fg = "white" if name == "history" else COLORS["muted"]
            tk.Label(nav, text=label,
                     font=self.controller.fonts["small"],
                     bg=bg, fg=fg, padx=10, pady=5,
                     cursor="hand2"
                     ).pack(side="left", padx=2)

    # ── LOAD & HIỂN THỊ DANH SÁCH ────────────────────────────────────────────

    def _load_history(self):
        """Đọc thẳng từ file history.json — không cần quiz_manager."""
        self.history = self._read_history_file()
        self.listbox.delete(0, tk.END)
        self.selected_index = None
        self.btn_retry.config(state="disabled")

        if not self.history:
            self.listbox.insert(tk.END, "  Chưa có lịch sử thi")
            self._show_empty_detail()
            return

        # Mới nhất lên đầu
        self.history = list(reversed(self.history))
        for item in self.history:
            score = item.get("score", 0)
            total = item.get("total", 0)
            grade = item.get("grade", "")
            date  = item.get("date", "")
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

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel or not self.history:
            return
        idx = sel[0]
        if idx >= len(self.history):
            return
        self.selected_index = idx
        self._show_detail(self.history[idx])
        self.btn_retry.config(state="normal")

    # ── CHI TIẾT ─────────────────────────────────────────────────────────────

    def _show_empty_detail(self):
        for w in self.detail_frame.winfo_children():
            w.destroy()
        tk.Label(self.detail_frame,
                 text="← Chọn một lần thi để xem chi tiết",
                 font=self.controller.fonts["body"],
                 bg=COLORS["surface"], fg=COLORS["muted"]
                 ).pack(expand=True)

    def _show_detail(self, result: dict):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        c = self.controller

        # Điểm số
        score_box = tk.Frame(self.detail_frame, bg=COLORS["card"], pady=10)
        score_box.pack(fill="x", pady=(0, 8))

        score = result.get("score", 0)
        total = result.get("total", 0)

        tk.Label(score_box,
                 text=f"{score}/{total}",
                 font=tkfont.Font(family="Consolas", size=30, weight="bold"),
                 bg=COLORS["card"],
                 fg=COLORS["green"] if score / max(total, 1) >= 0.5 else COLORS["accent"]
                 ).pack()

        tk.Label(score_box,
                 text=(f"{result.get('grade','')}  ·  "
                       f"{result.get('percentage',0)}%  ·  "
                       f"{result.get('time_taken','')}"),
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack()

        tk.Label(score_box,
                 text=result.get("quiz_title", ""),
                 font=c.fonts["body"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack()

        # Label "Chi tiết"
        tk.Label(self.detail_frame, text="Chi tiết từng câu:",
                 font=c.fonts["small"], bg=COLORS["surface"],
                 fg=COLORS["muted"]).pack(anchor="w", pady=(4, 2))

        # Canvas scroll cho danh sách câu — chiều cao cố định
        wrap = tk.Frame(self.detail_frame, bg=COLORS["surface"])
        wrap.pack(fill="both", expand=True)

        canvas = tk.Canvas(wrap, bg=COLORS["surface"], highlightthickness=0)
        vsb = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLORS["surface"])

        inner.bind("<Configure>",
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)

        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Bind scroll chuột
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * e.delta / 120), "units"))

        detail_list = result.get("detail", [])
        if not detail_list:
            tk.Label(inner, text="Không có dữ liệu chi tiết.",
                     font=c.fonts["small"], bg=COLORS["surface"],
                     fg=COLORS["muted"]).pack(pady=10)
            return

        for item in detail_list:
            is_correct = item.get("is_correct", False)
            color = COLORS["green"] if is_correct else COLORS["accent"]
            icon  = "✓" if is_correct else "✗"

            row = tk.Frame(inner, bg=COLORS["card"], pady=5, padx=8)
            row.pack(fill="x", pady=2, padx=2)

            # Icon + số câu
            tk.Label(row, text=f"[{icon}] Câu {item['index']+1}",
                     font=c.fonts["small"], bg=COLORS["card"],
                     fg=color, width=9, anchor="w").pack(side="left")

            # Nội dung câu hỏi rút gọn
            q = item.get("question", "")
            q_short = q[:48] + "…" if len(q) > 48 else q
            tk.Label(row, text=q_short,
                     font=c.fonts["small"], bg=COLORS["card"],
                     fg=COLORS["text"], anchor="w"
                     ).pack(side="left", fill="x", expand=True)

            # Đáp án
            user_ans    = item.get("user_answer") or "—"
            correct_ans = item.get("correct_answer", "?")
            tk.Label(row,
                     text=f"Bạn: {user_ans}  Đúng: {correct_ans}",
                     font=c.fonts["small"], bg=COLORS["card"],
                     fg=COLORS["muted"], anchor="e"
                     ).pack(side="right")

    # ── HÀNH ĐỘNG ────────────────────────────────────────────────────────────

    def _go_back(self):
        """Quay lại màn hình phù hợp."""
        result = self.controller.get_shared("result")
        if result:
            self.controller.show_screen("result")
        else:
            self.controller.show_screen("upload")

    def _retry_quiz(self):
        """Làm lại đề thi đã chọn.
        Load câu hỏi từ history.json — không cần app đang chạy dở."""
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

        # Khôi phục quiz_manager từ dữ liệu lịch sử
        from Core.quiz_manager import QuizManager
        quiz_manager = QuizManager()
        settings = result.get("settings", {
            "num_questions": len(questions),
            "difficulty": "medium",
            "time_limit": 15
        })
        quiz_manager.create_quiz(questions, settings, result.get("quiz_title", "Làm lại"))
        quiz_manager.user_answers = {}

        # Lưu vào shared để màn hình quiz dùng
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
                self.btn_retry.config(state="disabled")
                messagebox.showinfo("Xong", "Đã xóa toàn bộ lịch sử.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {e}")