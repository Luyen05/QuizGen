"""Upload screen."""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from Core.file_reader import read_file, validate_text
from ui.components import Card, AppButton, TextArea, TextInput, GlowProgressBar
from ui.screens.base import BaseScreen


class ScreenUpload(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "upload", "Tải lên",
                         "Chọn tài liệu hoặc dán nội dung bài giảng")
        self.filepath_var = tk.StringVar(value="Chưa chọn file...")
        self._build_ui()

    def on_enter(self):
        self.filepath_var.set("Chưa chọn file...")
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", "Dán nội dung bài giảng vào đây...")

    def _build_ui(self):
        theme = self.theme

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        info_row = ctk.CTkFrame(self.content, fg_color="transparent")
        info_row.grid(row=0, column=0, columnspan=2, sticky="ew")
        for i in range(3):
            info_row.grid_columnconfigure(i, weight=1)

        info_cards = [
            ("Tài liệu rõ ràng", "Giữ bố cục dễ đọc để AI hiểu tốt hơn"),
            ("Chất lượng AI", "Nội dung đủ dài sẽ tăng độ chính xác"),
            ("Bảo mật", "Dữ liệu chỉ dùng trong phiên hiện tại"),
        ]

        info_colors = [
            theme.colors["card_blue"],
            theme.colors["card_purple"],
            theme.colors["card_green"],
        ]

        for idx, (title, desc) in enumerate(info_cards):
            card = Card(info_row, theme, fg_color=info_colors[idx])
            card.grid(row=0, column=idx, padx=8, sticky="nsew")
            ctk.CTkLabel(card, text=title, font=theme.fonts["small"],
                         text_color=theme.colors["muted"]).pack(anchor="w", padx=12, pady=(10, 0))
            ctk.CTkLabel(card, text=desc, font=theme.fonts["body"],
                         text_color=theme.colors["text"], wraplength=220,
                         justify="left").pack(anchor="w", padx=12, pady=(4, 10))

        left = Card(self.content, theme, fg_color=theme.colors["card_alt"])
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(16, 0))
        right = Card(self.content, theme, fg_color=theme.colors["card_blue"])
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(16, 0))

        ctk.CTkLabel(left, text="Upload tài liệu", font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))
        ctk.CTkLabel(left, text="PDF · DOCX · TXT",
                     font=theme.fonts["small"], text_color=theme.colors["muted"]).pack(anchor="w", padx=12)

        drop_zone = ctk.CTkFrame(left, fg_color=theme.colors["card"],
                                 border_color=theme.colors["border"],
                                 border_width=1, corner_radius=theme.radius["lg"])
        drop_zone.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(drop_zone, text="Kéo & thả file vào đây",
                     font=theme.fonts["body"],
                     text_color=theme.colors["muted"]).pack(pady=(18, 6))

        self.file_entry = TextInput(drop_zone, theme, placeholder="Chưa chọn file...")
        self.file_entry.pack(fill="x", padx=12, pady=(0, 10))
        self.file_entry.configure(textvariable=self.filepath_var)

        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(0, 12))
        AppButton(btn_row, theme, text="Chọn file", command=self._browse_file).pack(side="left")

        ctk.CTkLabel(right, text="Nhập văn bản", font=theme.fonts["header"],
                     text_color=theme.colors["text"]).pack(anchor="w", padx=12, pady=(10, 6))
        ctk.CTkLabel(right, text="Dán nội dung bài giảng để AI xử lý",
                     font=theme.fonts["small"], text_color=theme.colors["muted"]).pack(anchor="w", padx=12)

        self.text_input = TextArea(right, theme, height=220)
        self.text_input.pack(fill="both", expand=True, padx=12, pady=(10, 12))
        self.text_input.insert("1.0", "Dán nội dung bài giảng vào đây...")

        footer = ctk.CTkFrame(self.content, fg_color="transparent")
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        footer.grid_columnconfigure(0, weight=1)

        self.progress = GlowProgressBar(footer, theme)
        self.progress.pack(fill="x", padx=8, pady=(0, 8))
        self.progress.set(0)

        AppButton(footer, theme, text="Tiếp tục", command=self._go_next,
                  variant="primary", height=40).pack(anchor="e")

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Chọn file tài liệu",
            filetypes=[("Tài liệu", "*.pdf *.txt *.docx"),
                       ("PDF", "*.pdf"), ("Text", "*.txt"),
                       ("Word", "*.docx"), ("Tất cả", "*.*")]
        )
        if path:
            self.filepath_var.set(path)

    def _go_next(self):
        text = ""
        filepath = self.filepath_var.get()
        if filepath and filepath != "Chưa chọn file...":
            try:
                text = read_file(filepath)
            except Exception as e:
                messagebox.showerror("Lỗi đọc file", str(e))
                return

        if not text:
            text = self.text_input.get("1.0", "end").strip()
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
