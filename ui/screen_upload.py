"""
ui/screen_upload.py
Màn hình 1: Người dùng chọn file hoặc nhập text trực tiếp
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Core.file_reader import read_file, validate_text
from ui.app import COLORS


class ScreenUpload(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.filepath_var = tk.StringVar(value="Chưa chọn file...")
        self._build_ui()

    def on_enter(self):
        """Gọi mỗi khi màn hình được hiển thị."""
        self.text_input.delete("1.0", tk.END)
        self.filepath_var.set("Chưa chọn file...")

    def _build_ui(self):
        c = self.controller

        # Tiêu đề
        tk.Label(self, text="QuizGen", font=c.fonts["title"],
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=(30, 4))
        tk.Label(self, text="Hệ thống tạo đề thi tự động từ bài giảng",
                 font=c.fonts["small"], bg=COLORS["bg"], fg=COLORS["muted"]).pack()

        # Nav bar
        self._build_nav(active="upload")

        # ── Khu vực chọn file ──
        frame_file = tk.LabelFrame(self, text=" Chọn file tài liệu ",
                                   bg=COLORS["surface"], fg=COLORS["text"],
                                   font=c.fonts["small"], padx=16, pady=12,
                                   bd=1, relief="solid")
        frame_file.pack(fill="x", padx=40, pady=(16, 8))

        tk.Label(frame_file, text="Hỗ trợ: PDF · TXT · DOCX",
                 font=c.fonts["small"], bg=COLORS["surface"],
                 fg=COLORS["muted"]).pack(anchor="w")

        row = tk.Frame(frame_file, bg=COLORS["surface"])
        row.pack(fill="x", pady=(8, 0))

        tk.Label(row, textvariable=self.filepath_var,
                 font=c.fonts["small"], bg=COLORS["surface"],
                 fg=COLORS["text"], width=50, anchor="w").pack(side="left")

        tk.Button(row, text="📂 Chọn file",
                  font=c.fonts["btn"], bg=COLORS["card"],
                  fg=COLORS["text"], relief="flat", cursor="hand2",
                  command=self._browse_file).pack(side="right")

        # ── Khu vực nhập text ──
        frame_text = tk.LabelFrame(self, text=" Hoặc nhập văn bản trực tiếp ",
                                   bg=COLORS["surface"], fg=COLORS["text"],
                                   font=c.fonts["small"], padx=16, pady=12,
                                   bd=1, relief="solid")
        frame_text.pack(fill="both", expand=True, padx=40, pady=8)

        self.text_input = tk.Text(frame_text, height=8,
                                  font=c.fonts["body"],
                                  bg=COLORS["card"], fg=COLORS["text"],
                                  insertbackground=COLORS["text"],
                                  relief="flat", wrap="word",
                                  padx=8, pady=8)
        self.text_input.pack(fill="both", expand=True)
        self.text_input.insert("1.0", "Dán nội dung bài giảng vào đây...")
        self.text_input.bind("<FocusIn>", self._clear_placeholder)

        # ── Nút tiếp theo ──
        tk.Button(self, text="Tiếp theo — Cài đặt đề thi  ▶",
                  font=c.fonts["btn"], bg=COLORS["accent"],
                  fg="white", relief="flat", cursor="hand2",
                  padx=20, pady=10,
                  command=self._go_next).pack(pady=16)

    def _build_nav(self, active: str):
        """Thanh điều hướng 4 bước."""
        nav = tk.Frame(self, bg=COLORS["bg"])
        nav.pack(pady=(12, 0))
        steps = [("📂 Tải lên", "upload"),
                 ("⚙️ Cài đặt", "settings"),
                 ("📝 Thi thử", "quiz"),
                 ("📊 Kết quả", "result")]
        for label, name in steps:
            bg = COLORS["accent"] if name == active else COLORS["surface"]
            fg = "white" if name == active else COLORS["muted"]
            tk.Label(nav, text=label, font=self.controller.fonts["small"],
                     bg=bg, fg=fg, padx=12, pady=5).pack(side="left", padx=2)

    def _browse_file(self):
        """Mở hộp thoại chọn file."""
        path = filedialog.askopenfilename(
            title="Chọn file tài liệu",
            filetypes=[("Tài liệu", "*.pdf *.txt *.docx"),
                       ("PDF", "*.pdf"), ("Text", "*.txt"),
                       ("Word", "*.docx"), ("Tất cả", "*.*")]
        )
        if path:
            self.filepath_var.set(path)

    def _clear_placeholder(self, event):
        """Xóa placeholder khi click vào text area."""
        if self.text_input.get("1.0", tk.END).strip() == "Dán nội dung bài giảng vào đây...":
            self.text_input.delete("1.0", tk.END)

    def _go_next(self):
        """Xử lý khi bấm Tiếp theo."""
        text = ""

        # Ưu tiên file nếu đã chọn
        filepath = self.filepath_var.get()
        if filepath and filepath != "Chưa chọn file...":
            try:
                text = read_file(filepath)
            except Exception as e:
                messagebox.showerror("Lỗi đọc file", str(e))
                return

        # Nếu không có file, dùng text nhập tay
        if not text:
            text = self.text_input.get("1.0", tk.END).strip()
            if text == "Dán nội dung bài giảng vào đây...":
                text = ""

        # Kiểm tra trường hợp biên: text rỗng hoặc quá ngắn
        if not text:
            messagebox.showwarning("Thiếu nội dung",
                                   "Vui lòng chọn file hoặc nhập văn bản trước.")
            return

        if not validate_text(text):
            messagebox.showwarning("Nội dung quá ngắn",
                                   "Văn bản cần ít nhất 100 ký tự để tạo câu hỏi.")
            return

        # Lưu text vào shared data rồi chuyển màn hình
        self.controller.set_shared("raw_text", text)
        self.controller.show_screen("settings")