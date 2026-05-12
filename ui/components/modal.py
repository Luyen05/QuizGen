"""Modal dialog."""

import customtkinter as ctk


class ModalDialog(ctk.CTkToplevel):
    def __init__(self, parent, theme, title, message, on_confirm=None):
        super().__init__(parent)
        self.theme = theme
        self.on_confirm = on_confirm
        self.title(title)
        self.geometry("420x220")
        self.configure(fg_color=theme.colors["surface"])
        self.resizable(False, False)

        self.label = ctk.CTkLabel(
            self,
            text=message,
            font=theme.fonts["body"],
            text_color=theme.colors["text"],
            wraplength=360,
            justify="left",
        )
        self.label.pack(padx=24, pady=(24, 16))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=(0, 16))

        ctk.CTkButton(
            btn_row,
            text="Hủy",
            fg_color=theme.colors["surface"],
            hover_color=theme.colors["card"],
            text_color=theme.colors["text"],
            command=self.destroy,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row,
            text="Xác nhận",
            fg_color=theme.colors["primary"],
            hover_color=theme.colors["accent"],
            text_color=theme.colors["text"],
            command=self._confirm,
        ).pack(side="left", padx=8)

    def _confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()
