"""
ui/layout.py
Khung layout dùng chung cho các màn hình dashboard.
"""

import tkinter as tk

from ui.app import COLORS
from ui.components import SidebarItem


def build_sidebar(parent, controller, active: str) -> tk.Frame:
    sidebar = tk.Frame(parent, bg=COLORS["sidebar"], width=240)
    sidebar.grid_propagate(False)

    logo_row = tk.Frame(sidebar, bg=COLORS["sidebar"])
    logo_row.pack(padx=16, pady=(24, 12), anchor="w")

    logo = tk.Canvas(logo_row, width=44, height=44,
                     bg=COLORS["sidebar"], highlightthickness=0)
    logo.create_oval(2, 2, 42, 42, fill=COLORS["accent"], outline="")
    logo.create_text(22, 22, text="QG", fill="white",
                     font=controller.fonts["header"])
    logo.pack(side="left")

    title_box = tk.Frame(logo_row, bg=COLORS["sidebar"])
    title_box.pack(side="left", padx=10)
    tk.Label(title_box, text="QuizGen",
             font=controller.fonts["header"], bg=COLORS["sidebar"],
             fg=COLORS["text"]).pack(anchor="w")
    tk.Label(title_box, text="Hệ thống tạo đề thi tự động",
             font=controller.fonts["small"], bg=COLORS["sidebar"],
             fg=COLORS["muted"], wraplength=160,
             justify="left").pack(anchor="w")

    menu = tk.Frame(sidebar, bg=COLORS["sidebar"])
    menu.pack(fill="x", padx=12, pady=(8, 6))

    items = [
        ("Tải lên", "upload", "↥"),
        ("Cài đặt", "settings", "⚙"),
        ("Thi thử", "quiz", "▶"),
        ("Kết quả", "result", "✓"),
        ("Lịch sử", "history", "⏳"),
    ]

    for label, name, icon in items:
        item = SidebarItem(
            menu,
            text=f"{icon}  {label}",
            command=lambda n=name: controller.show_screen(n),
            colors=COLORS,
            font=controller.fonts["small"],
            active=(name == active),
        )
        item.pack(fill="x", pady=4)

    spacer = tk.Frame(sidebar, bg=COLORS["sidebar"])
    spacer.pack(expand=True, fill="both")

    footer = tk.Frame(sidebar, bg=COLORS["sidebar"])
    footer.pack(side="bottom", fill="x", padx=16, pady=16)

    avatar = tk.Canvas(footer, width=40, height=40,
                       bg=COLORS["sidebar"], highlightthickness=0)
    avatar.create_oval(2, 2, 38, 38, fill=COLORS["card"],
                       outline=COLORS["border"])
    avatar.create_text(20, 20, text="SV",
                       fill=COLORS["text"], font=controller.fonts["small"])
    avatar.pack(side="left")

    user_box = tk.Frame(footer, bg=COLORS["sidebar"])
    user_box.pack(side="left", padx=10)
    tk.Label(user_box, text="Liêng Hót Ha luyến",
             font=controller.fonts["small"], bg=COLORS["sidebar"],
             fg=COLORS["text"]).pack(anchor="w")
    tk.Label(user_box, text="2312682 · Lớp: CTK47B",
             font=controller.fonts["small"], bg=COLORS["sidebar"],
             fg=COLORS["muted"]).pack(anchor="w")

    return sidebar


def build_title_block(parent, controller, title: str, subtitle: str) -> tk.Frame:
    frame = tk.Frame(parent, bg=COLORS["bg"])
    tk.Label(frame, text=title, font=controller.fonts["display"],
             bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
    tk.Label(frame, text=subtitle, font=controller.fonts["small"],
             bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")
    return frame
