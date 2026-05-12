"""
ui/components.py
Các component UI tái sử dụng cho QuizGen (dark mode dashboard).
"""

import tkinter as tk


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def blend(color_a: str, color_b: str, t: float) -> str:
    """Trộn 2 màu hex theo t (0..1)."""
    r1, g1, b1 = _hex_to_rgb(color_a)
    r2, g2, b2 = _hex_to_rgb(color_b)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return _rgb_to_hex((r, g, b))


def draw_rounded_rect(canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int,
                      radius: int, **kwargs) -> int:
    """Vẽ hình chữ nhật bo góc bằng polygon."""
    radius = max(0, radius)
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class RoundedCard(tk.Canvas):
    """Card bo góc với shadow mềm, chứa inner Frame để đặt nội dung."""

    def __init__(self, parent, bg: str, border: str, shadow: str,
                 radius: int = 16, padding: int = 14,
                 shadow_offset: int = 4, **kwargs):
        super().__init__(parent, bg=parent.cget("bg"), highlightthickness=0, **kwargs)
        self.card_bg = bg
        self.border = border
        self.shadow = shadow
        self.radius = radius
        self.padding = padding
        self.shadow_offset = shadow_offset
        self.inner = tk.Frame(self, bg=bg)
        self._window = self.create_window((padding, padding), window=self.inner, anchor="nw")
        self.bind("<Configure>", self._redraw)

    def _redraw(self, _event=None):
        self.delete("card")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 4 or h <= 4:
            return
        shadow_offset = self.shadow_offset
        radius = min(self.radius, max(0, (min(w, h) - 2) // 2))

        if self.shadow:
            draw_rounded_rect(
                self,
                shadow_offset,
                shadow_offset,
                w - 1,
                h - 1,
                radius,
                fill=self.shadow,
                outline="",
                tags="card",
            )

        draw_rounded_rect(
            self,
            0,
            0,
            w - 1 - shadow_offset,
            h - 1 - shadow_offset,
            radius,
            fill=self.card_bg,
            outline=self.border,
            tags="card",
        )

        inner_w = max(0, w - shadow_offset - self.padding * 2)
        inner_h = max(0, h - shadow_offset - self.padding * 2)
        self.itemconfigure(self._window, width=inner_w, height=inner_h)
        self.coords(self._window, self.padding, self.padding)


class GlowProgress(tk.Canvas):
    """Progress bar dạng line có glow nhẹ."""

    def __init__(self, parent, height: int, bg: str, fill: str, glow: str, **kwargs):
        super().__init__(parent, height=height, bg=bg, highlightthickness=0, **kwargs)
        self._value = 0.0
        self._height = height
        self._bg = bg
        self._fill = fill
        self._glow = glow
        self._anim_id = None
        self.bind("<Configure>", self._draw)

    def set(self, value: float, animate: bool = False):
        value = max(0.0, min(1.0, value))
        if not animate:
            self._value = value
            self._draw()
            return

        start = self._value
        delta = value - start
        steps = 12

        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None

        def _step(i=0):
            self._value = start + delta * (i / steps)
            self._draw()
            if i < steps:
                self._anim_id = self.after(15, lambda: _step(i + 1))

        _step()

    def _draw(self, _event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self._height
        if w <= 0:
            return
        fill_w = int(w * self._value)
        self.create_rectangle(0, 0, w, h, fill=self._bg, outline="")
        if fill_w > 0:
            self.create_rectangle(0, 0, fill_w, h, fill=self._glow, outline="")
            self.create_rectangle(0, 1, fill_w, h - 1, fill=self._fill, outline="")


class PillButton(tk.Canvas):
    """Button bo góc lớn, hỗ trợ hover."""

    def __init__(self, parent, text: str, command, bg: str, hover_bg: str,
                 fg: str, hover_fg: str, font,
                 radius: int = 16, padding: tuple[int, int] = (16, 10), **kwargs):
        super().__init__(parent, highlightthickness=0, bg=parent.cget("bg"), **kwargs)
        self._text = text
        self._command = command
        self._bg = bg
        self._hover_bg = hover_bg
        self._fg = fg
        self._hover_fg = hover_fg
        self._font = font
        self._radius = radius
        self._padx, self._pady = padding
        self._enabled = True
        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.configure(cursor="hand2")

    def set_text(self, text: str):
        self._text = text
        self._draw()

    def set_colors(self, bg: str, hover_bg: str, fg: str, hover_fg: str):
        self._bg = bg
        self._hover_bg = hover_bg
        self._fg = fg
        self._hover_fg = hover_fg
        self._draw()

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def _on_enter(self, _event):
        if self._enabled:
            self._draw(hover=True)

    def _on_leave(self, _event):
        self._draw()

    def _on_click(self, _event):
        if self._enabled and self._command:
            self._command()

    def _draw(self, _event=None, hover: bool = False):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return
        bg = self._hover_bg if hover and self._enabled else self._bg
        fg = self._hover_fg if hover and self._enabled else self._fg
        if not self._enabled:
            bg = blend(bg, "#000000", 0.4)
            fg = blend(fg, "#000000", 0.4)
        radius = min(self._radius, max(0, (min(w, h) - 2) // 2))
        draw_rounded_rect(self, 0, 0, w - 1, h - 1, radius, fill=bg, outline="")
        self.create_text(
            w // 2,
            h // 2,
            text=self._text,
            fill=fg,
            font=self._font,
        )


class GradientButton(tk.Canvas):
    """Button gradient bo góc, dùng cho CTA."""

    def __init__(self, parent, text: str, command,
                 left_color: str, right_color: str,
                 hover_left: str, hover_right: str,
                 fg: str, font, radius: int = 18,
                 padding: tuple[int, int] = (18, 10), **kwargs):
        super().__init__(parent, highlightthickness=0, bg=parent.cget("bg"), **kwargs)
        self._text = text
        self._command = command
        self._left = left_color
        self._right = right_color
        self._hover_left = hover_left
        self._hover_right = hover_right
        self._fg = fg
        self._font = font
        self._radius = radius
        self._padx, self._pady = padding
        self._hover = False
        self._enabled = True
        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.configure(cursor="hand2")

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def _on_enter(self, _event):
        self._hover = True
        self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._draw()

    def _on_click(self, _event):
        if self._enabled and self._command:
            self._command()

    def _draw(self, _event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return
        left = self._hover_left if self._hover else self._left
        right = self._hover_right if self._hover else self._right
        if not self._enabled:
            left = blend(left, "#000000", 0.45)
            right = blend(right, "#000000", 0.45)
        radius = min(self._radius, max(0, (min(w, h) - 2) // 2))

        for x in range(w):
            t = x / max(w - 1, 1)
            color = blend(left, right, t)
            y_offset = 0
            if x < radius:
                dx = radius - x
                y_offset = int(radius - (radius ** 2 - dx ** 2) ** 0.5)
            elif x > w - radius:
                dx = x - (w - radius)
                y_offset = int(radius - (radius ** 2 - dx ** 2) ** 0.5)
            self.create_line(x, y_offset, x, h - y_offset, fill=color)

        draw_rounded_rect(self, 0, 0, w - 1, h - 1, radius, fill="", outline="")
        self.create_text(
            w // 2,
            h // 2,
            text=self._text,
            fill=self._fg,
            font=self._font,
        )


class SidebarItem(tk.Frame):
    """Item trong sidebar với hover + active."""

    def __init__(self, parent, text: str, command, colors: dict,
                 font, active: bool = False):
        super().__init__(parent, bg=colors["sidebar"])
        self._command = command
        self._colors = colors
        self._font = font
        self._active = active

        self._indicator = tk.Frame(self, width=4, bg=colors["sidebar"])
        self._indicator.pack(side="left", fill="y")

        self._label = tk.Label(
            self,
            text=text,
            font=font,
            bg=colors["sidebar"],
            fg=colors["muted"],
            anchor="w",
            padx=12,
            pady=8,
        )
        self._label.pack(side="left", fill="x", expand=True)

        for widget in (self, self._label, self._indicator):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

        self.set_active(active)

    def set_active(self, active: bool):
        self._active = active
        if active:
            bg = self._colors["accent"]
            fg = "white"
            self._indicator.config(bg=self._colors["accent2"])
        else:
            bg = self._colors["sidebar"]
            fg = self._colors["muted"]
            self._indicator.config(bg=self._colors["sidebar"])
        self._label.config(bg=bg, fg=fg)
        self.config(bg=bg)

    def _on_enter(self, _event):
        if self._active:
            return
        self._label.config(bg=self._colors["surface_alt"], fg=self._colors["text"])
        self.config(bg=self._colors["surface_alt"])

    def _on_leave(self, _event):
        if self._active:
            return
        self._label.config(bg=self._colors["sidebar"], fg=self._colors["muted"])
        self.config(bg=self._colors["sidebar"])

    def _on_click(self, _event):
        if self._command:
            self._command()


class QuestionListItem(tk.Frame):
    """Item cho danh sách câu hỏi (trạng thái + click)."""

    def __init__(self, parent, text: str, command, colors: dict, font):
        super().__init__(parent, bg=colors["card"], highlightthickness=1,
                         highlightbackground=colors["border"])
        self._command = command
        self._colors = colors
        self._text = text
        self._status_color = colors["muted"]
        self._active = False

        self._dot = tk.Canvas(self, width=8, height=8,
                              bg=colors["card"], highlightthickness=0)
        self._dot_id = self._dot.create_oval(1, 1, 7, 7, fill=self._status_color, outline="")
        self._dot.pack(side="left", padx=(10, 6))

        self._label = tk.Label(self, text=text, font=font,
                               bg=colors["card"], fg=colors["text"])
        self._label.pack(side="left", fill="x", expand=True, pady=6)

        for widget in (self, self._label, self._dot):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def set_state(self, status_color: str, active: bool):
        self._status_color = status_color
        self._active = active
        self._apply_state()

    def _apply_state(self):
        self._dot.itemconfig(self._dot_id, fill=self._status_color)
        if self._active:
            bg = blend(self._colors["accent"], self._colors["card"], 0.7)
            fg = "white"
        else:
            bg = self._colors["card"]
            fg = self._colors["text"]
        self.config(bg=bg, highlightbackground=self._colors["border"])
        self._label.config(bg=bg, fg=fg)
        self._dot.config(bg=bg)

    def _on_enter(self, _event):
        self.config(bg=self._colors["surface_alt"])
        self._label.config(bg=self._colors["surface_alt"])
        self._dot.config(bg=self._colors["surface_alt"])

    def _on_leave(self, _event):
        self._apply_state()

    def _on_click(self, _event):
        if self._command:
            self._command()


class AnswerCard(tk.Frame):
    """Card đáp án với hover + trạng thái đúng/sai."""

    def __init__(self, parent, key: str, text: str, command,
                 colors: dict, font, wraplength: int = 520):
        super().__init__(parent, bg=colors["surface"], highlightthickness=1,
                         highlightbackground=colors["border"])
        self._command = command
        self._colors = colors
        self.key = key
        self._wraplength = wraplength

        self._key_label = tk.Label(self, text=key, font=font,
                                   bg=colors["surface"], fg=colors["muted"],
                                   width=3, anchor="center")
        self._key_label.pack(side="left", padx=(10, 6))

        self._text_label = tk.Label(self, text=text, font=font,
                                    bg=colors["surface"], fg=colors["text"],
                                    wraplength=wraplength, justify="left")
        self._text_label.pack(side="left", fill="x", expand=True, pady=10)

        self._icon_label = tk.Label(self, text="", font=font,
                                    bg=colors["surface"], fg=colors["green"],
                                    width=3)
        self._icon_label.pack(side="right", padx=(6, 10))

        for widget in (self, self._key_label, self._text_label, self._icon_label):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def set_text(self, text: str):
        self._text_label.config(text=text)

    def set_state(self, selected: bool, correct: bool, incorrect: bool):
        if correct:
            border = self._colors["green"]
            icon = "✓"
            icon_fg = self._colors["green"]
        elif incorrect:
            border = self._colors["danger"]
            icon = "✕"
            icon_fg = self._colors["danger"]
        elif selected:
            border = self._colors["accent"]
            icon = ""
            icon_fg = self._colors["accent"]
        else:
            border = self._colors["border"]
            icon = ""
            icon_fg = self._colors["muted"]

        self.config(highlightbackground=border)
        self._icon_label.config(text=icon, fg=icon_fg)

    def _on_enter(self, _event):
        self.config(bg=self._colors["surface_alt"])
        self._key_label.config(bg=self._colors["surface_alt"])
        self._text_label.config(bg=self._colors["surface_alt"])
        self._icon_label.config(bg=self._colors["surface_alt"])

    def _on_leave(self, _event):
        self.config(bg=self._colors["surface"])
        self._key_label.config(bg=self._colors["surface"])
        self._text_label.config(bg=self._colors["surface"])
        self._icon_label.config(bg=self._colors["surface"])

    def _on_click(self, _event):
        if self._command:
            self._command(self.key)
