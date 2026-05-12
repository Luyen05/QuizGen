"""
ui/screen_upload.py
Màn hình 1: Tải lên tài liệu hoặc nhập văn bản
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Core.file_reader import read_file, validate_text
from ui.app import COLORS
from ui.components import RoundedCard, GradientButton, PillButton, blend
from ui.layout import build_sidebar, build_title_block


class ScreenUpload(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg"])
        self.controller = controller
        self.filepath_var = tk.StringVar(value="Chưa chọn file...")
        self._build_ui()

    def on_enter(self):
        """Gọi mỗi khi màn hình được hiển thị."""
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", "Dán nội dung bài giảng vào đây...")
        self.filepath_var.set("Chưa chọn file...")

    def _build_ui(self):
        c = self.controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = build_sidebar(self, c, active="upload")
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
            "Tải lên",
            "Chọn tài liệu nguồn hoặc dán nội dung bài giảng để bắt đầu",
        )
        title_block.grid(row=0, column=0, sticky="w")

        quick_card = RoundedCard(
            top,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=14,
            padding=10,
            height=72,
            width=220,
        )
        quick_card.grid(row=0, column=1, sticky="e")
        tk.Label(quick_card.inner, text="Định dạng hỗ trợ",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")
        tk.Label(quick_card.inner, text="PDF · DOCX · TXT",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(4, 0))

        info_row = tk.Frame(self.main, bg=COLORS["bg"])
        info_row.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        info_row.grid_columnconfigure(0, weight=1)
        info_row.grid_columnconfigure(1, weight=1)
        info_row.grid_columnconfigure(2, weight=1)

        card_specs = [
            ("Nguồn tài liệu", "Ưu tiên bài giảng rõ ràng, đủ ngữ cảnh"),
            ("Gợi ý chất lượng", "Nội dung trên 100 ký tự giúp AI tối ưu hơn"),
            ("Bảo mật", "Tài liệu chỉ dùng nội bộ cho phiên hiện tại"),
        ]

        for i, (title, desc) in enumerate(card_specs):
            card = RoundedCard(
                info_row,
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
            tk.Label(card.inner, text=desc, font=c.fonts["body"],
                     bg=COLORS["card"], fg=COLORS["text"],
                     wraplength=240, justify="left").pack(anchor="w", pady=(4, 0))

        content = tk.Frame(self.main, bg=COLORS["bg"])
        content.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 12))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        file_card = RoundedCard(
            content,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=14,
        )
        file_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(file_card.inner, text="Chọn file tài liệu",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w")
        tk.Label(file_card.inner, text="PDF, DOCX hoặc TXT",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w", pady=(4, 10))

        path_box = tk.Frame(file_card.inner, bg=COLORS["card"])
        path_box.pack(fill="x", pady=(0, 8))

        tk.Label(path_box, textvariable=self.filepath_var,
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["text"], anchor="w", wraplength=280,
                 justify="left").pack(side="left", fill="x", expand=True)

        self.btn_browse = PillButton(
            path_box,
            text="Chọn file",
            command=self._browse_file,
            bg=COLORS["surface"],
            hover_bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            hover_fg="white",
            font=c.fonts["small"],
            height=32,
            width=110,
        )
        self.btn_browse.pack(side="right", padx=(10, 0))

        tips = tk.Frame(file_card.inner, bg=COLORS["card"])
        tips.pack(fill="x", pady=(6, 0))
        tk.Label(tips, text="• Giữ bố cục rõ ràng để AI hiểu tốt hơn",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")
        tk.Label(tips, text="• Tránh ảnh scan chất lượng thấp",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w")

        text_card = RoundedCard(
            content,
            bg=COLORS["card"],
            border=COLORS["border"],
            shadow=COLORS["shadow"],
            radius=18,
            padding=14,
        )
        text_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(text_card.inner, text="Nhập văn bản trực tiếp",
                 font=c.fonts["header"], bg=COLORS["card"],
                 fg=COLORS["text"]).pack(anchor="w")
        tk.Label(text_card.inner, text="Dán nội dung bài giảng để AI tạo câu hỏi",
                 font=c.fonts["small"], bg=COLORS["card"],
                 fg=COLORS["muted"]).pack(anchor="w", pady=(4, 10))

        self.text_input = tk.Text(
            text_card.inner,
            font=c.fonts["body"],
            bg=COLORS["card_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            wrap="word",
            height=12,
            padx=10,
            pady=10,
        )
        self.text_input.pack(fill="both", expand=True)
        self.text_input.insert("1.0", "Dán nội dung bài giảng vào đây...")
        self.text_input.bind("<FocusIn>", self._clear_placeholder)

        footer = tk.Frame(self.main, bg=COLORS["bg"])
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 18))
        footer.grid_columnconfigure(0, weight=1)

        self.btn_next = GradientButton(
            footer,
            text="Tiếp theo — Cài đặt đề thi",
            command=self._go_next,
            left_color=COLORS["accent"],
            right_color=COLORS["accent2"],
            hover_left=blend(COLORS["accent"], "#FFFFFF", 0.08),
            hover_right=blend(COLORS["accent2"], "#FFFFFF", 0.08),
            fg="white",
            font=c.fonts["btn"],
            height=44,
            width=260,
        )
        self.btn_next.pack(anchor="e")

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

    def _clear_placeholder(self, _event):
        """Xóa placeholder khi click vào text area."""
        if self.text_input.get("1.0", tk.END).strip() == "Dán nội dung bài giảng vào đây...":
            self.text_input.delete("1.0", tk.END)

    def _go_next(self):
        """Xử lý khi bấm Tiếp theo."""
        text = ""

        filepath = self.filepath_var.get()
        if filepath and filepath != "Chưa chọn file...":
            try:
                text = read_file(filepath)
            except Exception as e:
                messagebox.showerror("Lỗi đọc file", str(e))
                return

        if not text:
            text = self.text_input.get("1.0", tk.END).strip()
            if text == "Dán nội dung bài giảng vào đây...":
                text = ""

        if not text:
            messagebox.showwarning("Thiếu nội dung",
                                   "Vui lòng chọn file hoặc nhập văn bản trước.")
            return

        if not validate_text(text):
            messagebox.showwarning("Nội dung quá ngắn",
                                   "Văn bản cần ít nhất 100 ký tự để tạo câu hỏi.")
            return

        self.controller.set_shared("raw_text", text)
        self.controller.show_screen("settings")
