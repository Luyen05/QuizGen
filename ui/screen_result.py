"""
ui/screen_result.py
Màn hình 4: Hiển thị kết quả, thống kê chi tiết, xuất file
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, filedialog
import json

from ui.app import COLORS
from ui.components import RoundedCard, PillButton, GradientButton, blend
from ui.layout import build_sidebar, build_title_block


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

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = build_sidebar(self, c, active="result")
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
            "Kết quả",
            "Tổng quan hiệu suất và chi tiết từng câu hỏi",
        )
        title_block.grid(row=0, column=0, sticky="w")

        actions = tk.Frame(top, bg=COLORS["bg"])
        actions.grid(row=0, column=1, sticky="e")

        self.btn_export_json = PillButton(
            actions,
            text="Xuất JSON",
            command=self._export_json,
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=32,
            width=110,
        )
        self.btn_export_json.pack(side="left", padx=6)

        self.btn_export_txt = PillButton(
            actions,
            text="Xuất TXT",
            command=self._export_txt,
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=32,
            width=110,
        )
        self.btn_export_txt.pack(side="left")

        summary = tk.Frame(self.main, bg=COLORS["bg"])
        summary.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        summary.grid_columnconfigure(0, weight=1)
        summary.grid_columnconfigure(1, weight=1)
        summary.grid_columnconfigure(2, weight=1)

        self.summary_score_var = tk.StringVar(value="—/—")
        self.summary_accuracy_var = tk.StringVar(value="—%")
        self.summary_time_var = tk.StringVar(value="—")

        summary_specs = [
            ("Điểm số", self.summary_score_var, COLORS["green"]),
            ("Tỷ lệ đúng", self.summary_accuracy_var, COLORS["accent"]),
            ("Thời gian", self.summary_time_var, COLORS["yellow"]),
        ]

        for i, (title, var, color) in enumerate(summary_specs):
            card = RoundedCard(
                summary,
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
                     bg=COLORS["card"], fg=color).pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self.main, bg=COLORS["bg"])
        content.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 12))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        left_stack = tk.Frame(content, bg=COLORS["bg"])
        left_stack.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        score_card = RoundedCard(
            left_stack,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=14,
            height=180,
        )
        score_card.pack(fill="x", pady=(0, 12))

        self.score_label = tk.Label(score_card.inner, text="—/—",
                                    font=tkfont.Font(family="Consolas", size=36, weight="bold"),
                                    bg=COLORS["card"], fg=COLORS["green"])
        self.score_label.pack(anchor="w")

        self.grade_label = tk.Label(score_card.inner, text="",
                                    font=c.fonts["header"],
                                    bg=COLORS["card"], fg=COLORS["yellow"])
        self.grade_label.pack(anchor="w")

        self.time_label = tk.Label(score_card.inner, text="",
                                   font=c.fonts["small"],
                                   bg=COLORS["card"], fg=COLORS["muted"])
        self.time_label.pack(anchor="w")

        stats_card = RoundedCard(
            left_stack,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=14,
        )
        stats_card.pack(fill="x", pady=(0, 12))

        tk.Label(stats_card.inner, text="Thống kê",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(0, 8))

        self.stat_vars = {}
        for key, label in [
            ("correct", "Câu đúng"),
            ("wrong", "Câu sai"),
            ("percentage", "Tỷ lệ đúng"),
            ("time_taken", "Thời gian"),
        ]:
            row = tk.Frame(stats_card.inner, bg=COLORS["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=c.fonts["small"],
                     bg=COLORS["card"], fg=COLORS["muted"],
                     width=14, anchor="w").pack(side="left")
            var = tk.StringVar(value="—")
            tk.Label(row, textvariable=var, font=c.fonts["small"],
                     bg=COLORS["card"], fg=COLORS["text"],
                     anchor="w").pack(side="left")
            self.stat_vars[key] = var

        action_row = tk.Frame(left_stack, bg=COLORS["bg"])
        action_row.pack(fill="x")

        self.btn_retry = PillButton(
            action_row,
            text="Làm lại đề này",
            command=self._retry_quiz,
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=36,
            width=150,
        )
        self.btn_retry.pack(side="left", padx=(0, 8))

        self.btn_history = PillButton(
            action_row,
            text="Xem lịch sử",
            command=lambda: self.controller.show_screen("history"),
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=36,
            width=130,
        )
        self.btn_history.pack(side="left", padx=(0, 8))

        self.btn_new = GradientButton(
            action_row,
            text="Tạo đề mới",
            command=lambda: self.controller.show_screen("upload"),
            left_color=COLORS["accent"],
            right_color=COLORS["accent2"],
            hover_left=blend(COLORS["accent"], "#FFFFFF", 0.08),
            hover_right=blend(COLORS["accent2"], "#FFFFFF", 0.08),
            fg="white",
            font=c.fonts["small"],
            height=36,
            width=140,
        )
        self.btn_new.pack(side="left")

        review_card = RoundedCard(
            content,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=14,
        )
        review_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(review_card.inner, text="Xem lại từng câu",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w")

        filter_row = tk.Frame(review_card.inner, bg=COLORS["card"])
        filter_row.pack(fill="x", pady=(8, 6))

        self.btn_filter_all = PillButton(
            filter_row,
            text="Tất cả",
            command=lambda: self._set_filter("all"),
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=30,
            width=90,
        )
        self.btn_filter_all.pack(side="left", padx=(0, 6))

        self.btn_filter_wrong = PillButton(
            filter_row,
            text="Câu sai",
            command=lambda: self._set_filter("wrong"),
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=30,
            width=90,
        )
        self.btn_filter_wrong.pack(side="left", padx=(0, 6))

        self.btn_filter_skipped = PillButton(
            filter_row,
            text="Bỏ qua",
            command=lambda: self._set_filter("skipped"),
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=30,
            width=90,
        )
        self.btn_filter_skipped.pack(side="left")

        self.detail_canvas = tk.Canvas(review_card.inner, bg=COLORS["card"],
                                       highlightthickness=0)
        self.detail_scroll = tk.Scrollbar(
            review_card.inner,
            orient="vertical",
            command=self.detail_canvas.yview,
            bg=COLORS["border"],
            troughcolor=COLORS["surface"],
            activebackground=COLORS["accent"],
            bd=0,
            highlightthickness=0,
        )
        self.detail_inner = tk.Frame(self.detail_canvas, bg=COLORS["card"])

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

    def _update_result(self, result: dict):
        """Điền dữ liệu kết quả vào UI."""
        if not result:
            self.score_label.config(text="—/—")
            self.grade_label.config(text="")
            self.time_label.config(text="")
            self.summary_score_var.set("—/—")
            self.summary_accuracy_var.set("—%")
            self.summary_time_var.set("—")
            for var in self.stat_vars.values():
                var.set("—")
            self._render_detail({})
            return

        score = result.get("score", 0)
        total = result.get("total", 0)
        percentage = result.get("percentage", 0)

        self.score_label.config(text=f"{score}/{total}")
        self.grade_label.config(text=result.get("grade", ""))
        self.time_label.config(text=f"Hoàn thành trong {result.get('time_taken', '—')}")

        self.summary_score_var.set(f"{score}/{total}")
        self.summary_accuracy_var.set(f"{percentage}%")
        self.summary_time_var.set(result.get("time_taken", "—"))

        self.stat_vars["correct"].set(f"{score} câu")
        self.stat_vars["wrong"].set(f"{total - score} câu")
        self.stat_vars["percentage"].set(f"{percentage}%")
        self.stat_vars["time_taken"].set(result.get("time_taken", "—"))

        self._render_detail(result)

    def _set_filter(self, mode: str):
        self.filter_mode = mode
        self._update_filter_buttons()
        self._render_detail(self.current_result)

    def _update_filter_buttons(self):
        def apply(btn, active):
            if active:
                btn.set_colors(
                    bg=COLORS["accent"],
                    hover_bg=blend(COLORS["accent"], "#FFFFFF", 0.08),
                    fg="white",
                    hover_fg="white",
                )
            else:
                btn.set_colors(
                    bg=COLORS["surface"],
                    hover_bg=COLORS["surface_alt"],
                    fg=COLORS["text"],
                    hover_fg="white",
                )

        apply(self.btn_filter_all, self.filter_mode == "all")
        apply(self.btn_filter_wrong, self.filter_mode == "wrong")
        apply(self.btn_filter_skipped, self.filter_mode == "skipped")

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
                     bg=COLORS["card"], fg=COLORS["muted"]).pack(pady=12)
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
                color = COLORS["danger"]

            row = tk.Frame(self.detail_inner, bg=COLORS["card_alt"], padx=10, pady=8)
            row.pack(fill="x", pady=4)

            header = tk.Frame(row, bg=COLORS["card_alt"])
            header.pack(fill="x")
            tk.Label(header, text=f"Câu {item['index'] + 1}",
                     font=self.controller.fonts["small"],
                     bg=COLORS["card_alt"], fg=COLORS["text"]).pack(side="left")
            tk.Label(header, text=status_text,
                     font=self.controller.fonts["small"],
                     bg=COLORS["card_alt"], fg=color).pack(side="right")

            tk.Label(row, text=item.get("question", ""),
                     font=self.controller.fonts["body"],
                     bg=COLORS["card_alt"], fg=COLORS["text"],
                     wraplength=680, justify="left").pack(anchor="w", pady=(4, 2))

            tk.Label(row, text=f"Bạn chọn: {user_ans or '—'}",
                     font=self.controller.fonts["small"],
                     bg=COLORS["card_alt"], fg=COLORS["muted"]).pack(anchor="w")

            tk.Label(row, text=f"Đáp án đúng: {correct_ans}",
                     font=self.controller.fonts["small"],
                     bg=COLORS["card_alt"], fg=COLORS["muted"]).pack(anchor="w")

            explanation = item.get("explanation", "")
            if explanation:
                tk.Label(row, text=f"Giải thích: {explanation}",
                         font=self.controller.fonts["small"],
                         bg=COLORS["card_alt"], fg=COLORS["muted"],
                         wraplength=680, justify="left").pack(anchor="w", pady=(2, 0))

        self.detail_inner.update_idletasks()
        self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.detail_canvas.itemconfig(self._detail_window, width=event.width)

    def _bind_mousewheel(self, _event=None):
        self.detail_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.detail_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.detail_canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event=None):
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
