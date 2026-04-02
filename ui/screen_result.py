"""
ui/screen_result.py
Màn hình 4: Hiển thị kết quả, thống kê chi tiết, xuất file
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

from ui.app import COLORS


class ScreenResult(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self._build_ui()

    def on_enter(self):
        """Cập nhật kết quả mỗi khi vào màn hình."""
        result = self.controller.get_shared("result") or {}
        self._update_result(result)

    def _build_ui(self):
        c = self.controller

        tk.Label(self, text="QuizGen", font=c.fonts["title"],
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(30, 4))
        tk.Label(self, text="Kết quả bài thi",
                 font=c.fonts["small"], bg=COLORS["bg"],
                 fg=COLORS["muted"]).pack()

        self._build_nav(active="result")

        # ── Điểm số lớn ──
        score_frame = tk.Frame(self, bg=COLORS["card"], padx=20, pady=16)
        score_frame.pack(fill="x", padx=40, pady=(16, 8))

        self.score_label = tk.Label(score_frame, text="—/—",
                                     font=tk.font.Font(family="Consolas", size=40, weight="bold"),
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
        stats_frame = tk.LabelFrame(self, text=" Thống kê ",
                                    bg=COLORS["surface"], fg=COLORS["text"],
                                    font=c.fonts["small"], padx=16, pady=10,
                                    bd=1, relief="solid")
        stats_frame.pack(fill="x", padx=40, pady=8)

        self.stat_vars = {}
        for key, label in [("correct",    "✅ Câu đúng"),
                            ("wrong",      "❌ Câu sai"),
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

        # ── Nút xuất file & làm lại ──
        export_frame = tk.Frame(self, bg=COLORS["bg"])
        export_frame.pack(pady=8)

        for label, cmd in [("📄 Xuất JSON", self._export_json),
                            ("📝 Xuất TXT",  self._export_txt)]:
            tk.Button(export_frame, text=label,
                      font=c.fonts["btn"], bg=COLORS["surface"],
                      fg=COLORS["text"], relief="flat", cursor="hand2",
                      padx=12, pady=7, command=cmd
                      ).pack(side="left", padx=5)

        tk.Button(self, text="🔄 Tạo đề mới",
                  font=c.fonts["btn"], bg=COLORS["green"],
                  fg=COLORS["bg"], relief="flat", cursor="hand2",
                  padx=20, pady=10,
                  command=lambda: self.controller.show_screen("upload")
                  ).pack(pady=10)

    def _build_nav(self, active: str):
        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(pady=(12, 0))
        for label, name in [("📂 Tải lên","upload"),("⚙️ Cài đặt","settings"),
                             ("📝 Thi thử","quiz"),("📊 Kết quả","result")]:
            bg = COLORS["accent"] if name == active else COLORS["surface"]
            fg = "white" if name == active else COLORS["muted"]
            tk.Label(nav, text=label, font=self.controller.fonts["small"],
                     bg=bg, fg=fg, padx=12, pady=5).pack(side="left", padx=2)

    def _update_result(self, result: dict):
        """Điền dữ liệu kết quả vào UI."""
        if not result:
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
            status = "✓" if item["is_correct"] else "✗"
            lines.append(f"[{status}] Câu {item['index'] + 1}: {item['question']}")
            lines.append(f"    Bạn chọn: {item['user_answer']}  |  Đáp án: {item['correct_answer']}")
            if not item["is_correct"]:
                lines.append(f"    Giải thích: {item['explanation']}")
            lines.append("")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Thành công", f"Đã xuất kết quả vào:\n{path}")