"""Sidebar component."""

import customtkinter as ctk


class SidebarItem(ctk.CTkButton):
    def __init__(self, parent, theme, text, command=None):
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            hover_color=theme.colors["surface"],
            text_color=theme.colors["muted"],
            anchor="w",
            font=theme.fonts["body"],
            corner_radius=theme.radius["md"],
        )

    def set_active(self, theme, active: bool):
        if active:
            self.configure(
                fg_color=theme.colors["primary"],
                hover_color=theme.colors["accent"],
                text_color=theme.colors["text"],
            )
        else:
            self.configure(
                fg_color="transparent",
                hover_color=theme.colors["surface"],
                text_color=theme.colors["muted"],
            )


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, controller, items, active_key):
        theme = controller.theme
        super().__init__(parent, fg_color=theme.colors["sidebar"], corner_radius=0)
        self.controller = controller
        self.theme = theme
        self.items = {}

        self.grid_rowconfigure(2, weight=1)

        logo = ctk.CTkLabel(
            self,
            text="QG",
            font=theme.fonts["title"],
            text_color=theme.colors["text"],
        )
        logo.grid(row=0, column=0, padx=16, pady=(18, 4), sticky="w")

        title = ctk.CTkLabel(
            self,
            text="QuizGen",
            font=theme.fonts["header"],
            text_color=theme.colors["text"],
        )
        title.grid(row=1, column=0, padx=16, sticky="w")

        subtitle = ctk.CTkLabel(
            self,
            text="Hệ thống tạo đề thi tự động",
            font=theme.fonts["small"],
            text_color=theme.colors["muted"],
            wraplength=180,
            justify="left",
        )
        subtitle.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="nw")

        menu = ctk.CTkFrame(self, fg_color="transparent")
        menu.grid(row=3, column=0, sticky="ew", padx=12)

        for label, key, icon in items:
            item = SidebarItem(menu, theme, text=f"{icon}  {label}",
                               command=lambda k=key: controller.show_screen(k))
            item.pack(fill="x", pady=4)
            self.items[key] = item

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=4, column=0, padx=16, pady=16, sticky="ew")

        ctk.CTkLabel(footer, text="Sinh viên",
                     font=theme.fonts["small"],
                     text_color=theme.colors["text"]).pack(anchor="w")
        ctk.CTkLabel(footer, text="MSSV: 2312682 · Lớp: KTPM",
                     font=theme.fonts["small"],
                     text_color=theme.colors["muted"]).pack(anchor="w")
        ctk.CTkLabel(footer, text="API: Online",
                     font=theme.fonts["small"],
                     text_color=theme.colors["success"]).pack(anchor="w")

        self.set_active(active_key)

    def set_active(self, active_key):
        for key, item in self.items.items():
            item.set_active(self.theme, key == active_key)
