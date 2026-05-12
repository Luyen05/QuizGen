"""Result screen."""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json

from ui.components import Card, AppButton
from ui.screens.base import BaseScreen


class ScreenResult(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "result", "Kết quả",
                         "Tổng quan hiệu suất và chi tiết đáp án")
        self.current_result = {}
        self.filter_mode = "all"
        self._build_ui()

    def on_enter(self):
        result = self.controller.get_shared("result") or {}
        self.current_result = result
        self._update_result(result)

    def _build_ui(self):
        theme = self.theme

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=2)
        self.content.grid_rowconfigure(0, weight=1)

        left = Card(self.content, theme, fg_color=theme.colors["card_purple"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = Card(self.content, theme, fg_color=theme.colors["card_blue"])
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(left, text="Tổng quan", font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.score_label = ctk.CTkLabel(left, text="—/—", font=theme.fonts["title"],
                                        text_color=theme.colors["success"])
        self.score_label.pack(anchor="w", padx=12)

        self.grade_label = ctk.CTkLabel(left, text="", font=theme.fonts["body"],
                                        text_color=theme.colors["warning"])
        self.grade_label.pack(anchor="w", padx=12)

        self.time_label = ctk.CTkLabel(left, text="", font=theme.fonts["small"],
                                       text_color=theme.colors["muted"])
        self.time_label.pack(anchor="w", padx=12, pady=(0, 10))

        self.stat_vars = {}
        for key, label in [("correct", "Câu đúng"), ("wrong", "Câu sai"),
                           ("percentage", "Accuracy"), ("time_taken", "Thời gian")]:
            row = ctk.CTkFrame(left, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=4)
            ctk.CTkLabel(row, text=label, font=theme.fonts["small"],
                         text_color=theme.colors["muted"], width=12, anchor="w").pack(side="left")
            var = tk.StringVar(value="—")
            ctk.CTkLabel(row, textvariable=var, font=theme.fonts["body"],
                         text_color=theme.colors["text"]).pack(side="left")
            self.stat_vars[key] = var

        action_row = ctk.CTkFrame(left, fg_color="transparent")
        action_row.pack(fill="x", padx=12, pady=(12, 6))

        AppButton(action_row, theme, text="Làm lại", command=self._retry_quiz,
                  variant="secondary", height=36).pack(side="left", padx=(0, 8))
        AppButton(action_row, theme, text="Lịch sử",
                  command=lambda: self.controller.show_screen("history"),
                  variant="secondary", height=36).pack(side="left", padx=(0, 8))
        AppButton(action_row, theme, text="Tạo đề mới",
                  command=lambda: self.controller.show_screen("upload"),
                  variant="primary", height=36).pack(side="left")

        export_row = ctk.CTkFrame(left, fg_color="transparent")
        export_row.pack(fill="x", padx=12, pady=(0, 12))
        AppButton(export_row, theme, text="Xuất JSON", command=self._export_json,
                  variant="ghost", height=32).pack(side="left", padx=(0, 8))
        AppButton(export_row, theme, text="Xuất TXT", command=self._export_txt,
                  variant="ghost", height=32).pack(side="left")

        ctk.CTkLabel(right, text="Chi tiết đáp án", font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))

        self.detail_frame = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.detail_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _retry_quiz(self):
        quiz_manager = self.controller.get_shared("quiz_manager")
        if not quiz_manager or not quiz_manager.get_questions():
            messagebox.showwarning("Không thể làm lại",
                                   "Không còn dữ liệu đề thi.\nVui lòng tạo đề mới.")
            return
        quiz_manager.user_answers = {}
        self.controller.show_screen("quiz")

    def _update_result(self, result: dict):
        if not result:
            self._render_detail({})
            return

        score = result.get("score", 0)
        total = result.get("total", 0)
        self.score_label.configure(text=f"{score}/{total}")
        self.grade_label.configure(text=result.get("grade", ""))
        self.time_label.configure(text=f"Hoàn thành trong {result.get('time_taken', '—')}")

        self.stat_vars["correct"].set(f"{score} câu")
        self.stat_vars["wrong"].set(f"{total - score} câu")
        self.stat_vars["percentage"].set(f"{result.get('percentage', 0)}%")
        self.stat_vars["time_taken"].set(result.get("time_taken", "—"))

        self._render_detail(result)

    def _render_detail(self, result: dict):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        detail_list = result.get("detail", []) if result else []
        if not detail_list:
            ctk.CTkLabel(self.detail_frame, text="Không có dữ liệu.",
                         font=self.theme.fonts["small"],
                         text_color=self.theme.colors["muted"]).pack(pady=12)
            return

        for item in detail_list:
            row = ctk.CTkFrame(self.detail_frame, fg_color=self.theme.colors["surface"],
                               corner_radius=self.theme.radius["md"])
            row.pack(fill="x", pady=6)

            title = f"Câu {item['index'] + 1}"
            status = "✓" if item.get("is_correct") else "✗"
            ctk.CTkLabel(row, text=f"{status} {title}",
                         font=self.theme.fonts["small"],
                         text_color=self.theme.colors["text"]).pack(anchor="w", padx=12, pady=(8, 0))

            ctk.CTkLabel(row, text=item.get("question", ""),
                         font=self.theme.fonts["body"],
                         text_color=self.theme.colors["text"],
                         wraplength=520, justify="left").pack(anchor="w", padx=12, pady=(4, 0))

            user_ans = item.get("user_answer") or "—"
            correct = item.get("correct_answer", "?")
            ctk.CTkLabel(row, text=f"Bạn chọn: {user_ans}  |  Đáp án: {correct}",
                         font=self.theme.fonts["small"],
                         text_color=self.theme.colors["muted"]).pack(anchor="w", padx=12, pady=(2, 8))

    def _export_json(self):
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
