"""
ui/screen_result.py
Màn hình 4: Hiển thị kết quả, thống kê chi tiết, xuất file
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, filedialog
import json

from ui.app import COLORS


class ScreenResult(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.current_result = {}
        self.filter_mode = "all"
        self._build_ui()

    def on_enter(self):
        """Cập nhật kết quả mỗi khi vào màn hình."""
        result = self.controller.get_shared("result") or {}
        self.current_result = result
        self._update_result(result)

    def _build_ui(self):
        c = self.controller

        tk.Label(self, text="QuizGen", font=c.fonts["title"],
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(30, 4))
        tk.Label(self, text="Kết quả bài thi",
                 font=c.fonts["small"], bg=COLORS["bg"],
                 fg=COLORS["muted"]).pack()

        self._build_nav(active="result")

        # ── Thanh hành động dưới cùng (luon hien thi) ──
        bottom_bar = tk.Frame(self, bg=COLORS["bg"])
        bottom_bar.pack(side="bottom", fill="x", pady=(4, 10))

        export_frame = tk.Frame(bottom_bar, bg=COLORS["bg"])
        export_frame.pack(pady=(2, 6))

        for label, cmd in [("📄 Xuất JSON", self._export_json),
                   ("📝 Xuất TXT", self._export_txt)]:
            tk.Button(export_frame, text=label,
                  font=c.fonts["btn"], bg=COLORS["surface"],
                  fg=COLORS["text"], relief="flat", cursor="hand2",
                  padx=12, pady=7, command=cmd
                  ).pack(side="left", padx=5)

        action_row = tk.Frame(bottom_bar, bg=COLORS["bg"])
        action_row.pack(pady=(0, 6))

        tk.Button(action_row, text="🔁 Làm lại đề này",
              font=c.fonts["btn"], bg=COLORS["yellow"],
              fg=COLORS["bg"], relief="flat", cursor="hand2",
              padx=16, pady=8,
              command=self._retry_quiz
              ).pack(side="left", padx=6)

        tk.Button(action_row, text="📜 Xem lịch sử",
              font=c.fonts["btn"], bg=COLORS["surface"],
              fg=COLORS["text"], relief="flat", cursor="hand2",
              padx=16, pady=8,
              command=lambda: self.controller.show_screen("history")
              ).pack(side="left", padx=6)

        tk.Button(action_row, text="🔄 Tạo đề mới",
              font=c.fonts["btn"], bg=COLORS["green"],
              fg=COLORS["bg"], relief="flat", cursor="hand2",
              padx=16, pady=8,
              command=lambda: self.controller.show_screen("upload")
              ).pack(side="left", padx=6)

        # ── Noi dung chinh ──
        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True)

        # ── Điểm số lớn ──
        score_frame = tk.Frame(content, bg=COLORS["card"], padx=14, pady=8)
        score_frame.pack(fill="x", padx=24, pady=(8, 6))

        self.score_label = tk.Label(score_frame, text="—/—",
                                     font=tkfont.Font(family="Consolas", size=40, weight="bold"),
                                     bg=COLORS["card"], fg=COLORS["green"])
        self.score_label.pack()

        self.grade_label = tk.Label(score_frame, text="",
                                     font=c.fonts["header"],
                                     bg=COLORS["card"], fg=COLORS["yellow"])
        self.grade_label.pack()

        self.time_label = tk.Label(score_frame, text="",
                                   font=c.fonts["small"],
                                   bg=COLORS["card"], fg=COLORS["muted"])
        self.time_label.pack()

        # ── Thống kê chi tiết ──
        stats_frame = tk.LabelFrame(content, text=" Thống kê ",
                        bg=COLORS["surface"], fg=COLORS["text"],
                        font=c.fonts["small"], padx=10, pady=6,
                        bd=1, relief="solid")
        stats_frame.pack(fill="x", padx=24, pady=6)

        self.stat_vars = {}
        for key, label in [("correct", "✅ Câu đúng"),
                           ("wrong", "❌ Câu sai"),
                           ("percentage", "📊 Tỷ lệ đúng"),
                           ("time_taken", "⏱ Thời gian")]:
            row = tk.Frame(stats_frame, bg=COLORS["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=c.fonts["body"],
                     bg=COLORS["surface"], fg=COLORS["text"],
                     width=20, anchor="w").pack(side="left")
            var = tk.StringVar(value="—")
            tk.Label(row, textvariable=var, font=c.fonts["body"],
                     bg=COLORS["surface"], fg=COLORS["yellow"],
                     anchor="w").pack(side="left")
            self.stat_vars[key] = var

        # ── Xem lại từng câu ──
        review_frame = tk.LabelFrame(content, text=" Xem lại từng câu ",
                         bg=COLORS["surface"], fg=COLORS["text"],
                         font=c.fonts["small"], padx=10, pady=8,
                         bd=1, relief="solid")
        review_frame.pack(fill="both", expand=True, padx=16, pady=(4, 6))

        filter_row = tk.Frame(review_frame, bg=COLORS["surface"])
        filter_row.pack(fill="x", pady=(2, 6))

        tk.Label(filter_row, text="Bộ lọc:", font=c.fonts["small"],
                 bg=COLORS["surface"], fg=COLORS["muted"]).pack(side="left")

        self.btn_filter_all = tk.Button(
            filter_row, text="Tất cả",
            font=c.fonts["small"], bg=COLORS["surface"],
            fg=COLORS["text"], relief="flat", cursor="hand2",
            command=lambda: self._set_filter("all")
        )
        self.btn_filter_all.pack(side="left", padx=6)

        self.btn_filter_wrong = tk.Button(
            filter_row, text="Chỉ câu sai",
            font=c.fonts["small"], bg=COLORS["surface"],
            fg=COLORS["text"], relief="flat", cursor="hand2",
            command=lambda: self._set_filter("wrong")
        )
        self.btn_filter_wrong.pack(side="left", padx=6)

        self.btn_filter_skipped = tk.Button(
            filter_row, text="Chưa trả lời",
            font=c.fonts["small"], bg=COLORS["surface"],
            fg=COLORS["text"], relief="flat", cursor="hand2",
            command=lambda: self._set_filter("skipped")
        )
        self.btn_filter_skipped.pack(side="left", padx=6)

        self.detail_canvas = tk.Canvas(review_frame, bg=COLORS["surface"],
                           highlightthickness=0)
        self.detail_scroll = tk.Scrollbar(review_frame, orient="vertical",
                                          command=self.detail_canvas.yview)
        self.detail_inner = tk.Frame(self.detail_canvas, bg=COLORS["surface"])

        self.detail_inner.bind(
            "<Configure>",
            lambda e: self.detail_canvas.configure(
                scrollregion=self.detail_canvas.bbox("all")
            )
        )

        self._detail_window = self.detail_canvas.create_window(
            (0, 0), window=self.detail_inner, anchor="nw"
        )
        self.detail_canvas.configure(yscrollcommand=self.detail_scroll.set)
        self.detail_canvas.bind("<Configure>", self._on_canvas_configure)
        self.detail_canvas.bind("<Enter>", self._bind_mousewheel)
        self.detail_canvas.bind("<Leave>", self._unbind_mousewheel)
        self.detail_inner.bind("<Enter>", self._bind_mousewheel)
        self.detail_inner.bind("<Leave>", self._unbind_mousewheel)

        self.detail_canvas.pack(side="left", fill="both", expand=True)
        self.detail_scroll.pack(side="right", fill="y")

        self._update_filter_buttons()

    def _retry_quiz(self):
        """Làm lại chính xác đề thi vừa thi — reset đáp án, giữ nguyên câu hỏi."""
        quiz_manager = self.controller.get_shared("quiz_manager")
        if not quiz_manager or not quiz_manager.get_questions():
            messagebox.showwarning("Không thể làm lại",
                                   "Không còn dữ liệu đề thi.\nVui lòng tạo đề mới.")
            return
        quiz_manager.user_answers = {}
        self.controller.show_screen("quiz")

    def _build_nav(self, active: str):
        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(pady=(12, 0))
        tabs = [
            ("📂 Tải lên", "upload"),
            ("⚙️ Cài đặt", "settings"),
            ("📝 Thi thử", "quiz"),
            ("📊 Kết quả", "result"),
            ("📜 Lịch sử", "history"),
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

    def _update_result(self, result: dict):
        """Điền dữ liệu kết quả vào UI."""
        if not result:
            self._render_detail({})
            return

        score = result.get("score", 0)
        total = result.get("total", 0)
        self.score_label.config(text=f"{score}/{total}")
        self.grade_label.config(text=result.get("grade", ""))
        self.time_label.config(text=f"Hoàn thành trong {result.get('time_taken', '—')}")

        self.stat_vars["correct"].set(f"{score} câu")
        self.stat_vars["wrong"].set(f"{total - score} câu")
        self.stat_vars["percentage"].set(f"{result.get('percentage', 0)}%")
        self.stat_vars["time_taken"].set(result.get("time_taken", "—"))

        self._render_detail(result)

    def _set_filter(self, mode: str):
        self.filter_mode = mode
        self._update_filter_buttons()
        self._render_detail(self.current_result)

    def _update_filter_buttons(self):
        def apply_style(btn, active):
            bg = COLORS["accent"] if active else COLORS["surface"]
            fg = "white" if active else COLORS["text"]
            btn.config(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)

        apply_style(self.btn_filter_all, self.filter_mode == "all")
        apply_style(self.btn_filter_wrong, self.filter_mode == "wrong")
        apply_style(self.btn_filter_skipped, self.filter_mode == "skipped")

    def _render_detail(self, result: dict):
        for w in self.detail_inner.winfo_children():
            w.destroy()

        detail_list = result.get("detail", []) if result else []
        if self.filter_mode == "wrong":
            detail_list = [d for d in detail_list if not d.get("is_correct", False)]
        elif self.filter_mode == "skipped":
            detail_list = [d for d in detail_list if not d.get("user_answer")]

        if not detail_list:
            tk.Label(self.detail_inner, text="Không có dữ liệu phù hợp.",
                     font=self.controller.fonts["small"],
                     bg=COLORS["surface"], fg=COLORS["muted"]).pack(pady=12)
            return

        for item in detail_list:
            user_ans = item.get("user_answer")
            correct_ans = item.get("correct_answer", "?")
            is_correct = item.get("is_correct", False)

            if not user_ans:
                status_text = "⏭ Bỏ qua"
                color = COLORS["yellow"]
            elif is_correct:
                status_text = "✓ Đúng"
                color = COLORS["green"]
            else:
                status_text = "✗ Sai"
                color = COLORS["accent"]

            row = tk.Frame(self.detail_inner, bg=COLORS["card"], padx=10, pady=8)
            row.pack(fill="x", pady=4)

            header = tk.Frame(row, bg=COLORS["card"])
            header.pack(fill="x")
            tk.Label(header, text=f"Câu {item['index'] + 1}",
                     font=self.controller.fonts["small"],
                     bg=COLORS["card"], fg=COLORS["text"]).pack(side="left")
            tk.Label(header, text=status_text,
                     font=self.controller.fonts["small"],
                     bg=COLORS["card"], fg=color).pack(side="right")

            tk.Label(row, text=item.get("question", ""),
                     font=self.controller.fonts["body"],
                     bg=COLORS["card"], fg=COLORS["text"],
                     wraplength=760, justify="left").pack(anchor="w", pady=(4, 2))

            tk.Label(row, text=f"Bạn chọn: {user_ans or '—'}",
                     font=self.controller.fonts["small"],
                     bg=COLORS["card"], fg=COLORS["muted"]).pack(anchor="w")

            tk.Label(row, text=f"Đáp án đúng: {correct_ans}",
                     font=self.controller.fonts["small"],
                     bg=COLORS["card"], fg=COLORS["muted"]).pack(anchor="w")

            explanation = item.get("explanation", "")
            if explanation:
                tk.Label(row, text=f"Giải thích: {explanation}",
                         font=self.controller.fonts["small"],
                         bg=COLORS["card"], fg=COLORS["muted"],
                         wraplength=760, justify="left").pack(anchor="w", pady=(2, 0))

        self.detail_inner.update_idletasks()
        self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.detail_canvas.itemconfig(self._detail_window, width=event.width)

    def _bind_mousewheel(self, event=None):
        self.detail_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.detail_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.detail_canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        self.detail_canvas.unbind_all("<MouseWheel>")
        self.detail_canvas.unbind_all("<Button-4>")
        self.detail_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 * int(event.delta / 120)
        self.detail_canvas.yview_scroll(delta, "units")

    def _export_json(self):
        """Xuất kết quả ra file JSON."""
        result = self.controller.get_shared("result")
        if not result:
            messagebox.showwarning("Chưa có kết quả", "Hãy làm bài thi trước.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="ket_qua_thi.json"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công", f"Đã lưu kết quả vào:\n{path}")

    def _export_txt(self):
        """Xuất kết quả dạng text dễ đọc."""
        result = self.controller.get_shared("result")
        if not result:
            messagebox.showwarning("Chưa có kết quả", "Hãy làm bài thi trước.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt")],
            initialfile="ket_qua_thi.txt"
        )
        if not path:
            return

        lines = [
            f"KẾT QUẢ BÀI THI — {result.get('quiz_title', '')}",
            f"Ngày thi: {result.get('date', '')}",
            f"Điểm số: {result.get('score')}/{result.get('total')} "
            f"({result.get('percentage')}%) — {result.get('grade')}",
            f"Thời gian: {result.get('time_taken')}",
            "=" * 50,
            ""
        ]
        for item in result.get("detail", []):
            status = "✓" if item.get("is_correct") else "✗"
            user_ans = item.get("user_answer") or "—"
            lines.append(f"[{status}] Câu {item['index'] + 1}: {item.get('question', '')}")
            lines.append(f"    Bạn chọn: {user_ans}  |  Đáp án: {item.get('correct_answer', '?')}")
            explanation = item.get("explanation", "")
            if explanation:
                lines.append(f"    Giải thích: {explanation}")
            lines.append("")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Thành công", f"Đã xuất kết quả vào:\n{path}")
