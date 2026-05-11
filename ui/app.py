"""
ui/app.py
Cửa sổ chính — chứa và điều hướng giữa các màn hình (Frame)
Dùng pattern: ẩn/hiện Frame thay vì mở cửa sổ mới
"""

import tkinter as tk
from tkinter import font as tkfont


# Màu sắc chủ đạo — dễ thay đổi ở 1 chỗ
COLORS = {
    "bg":       "#1a1a2e",
    "surface":  "#16213e",
    "card":     "#0f3460",
    "accent":   "#e94560",
    "green":    "#4ecca3",
    "yellow":   "#f5a623",
    "text":     "#eaeaea",
    "muted":    "#8892a4",
    "border":   "#2a3a5c",
}


class QuizGenApp(tk.Tk):
    """
    Cửa sổ chính của ứng dụng.
    Quản lý việc chuyển giữa các màn hình bằng cách
    raise frame lên trên thay vì destroy/create mới.
    """

    def __init__(self):
        super().__init__()
        self.title("QuizGen — Hệ thống tạo đề thi tự động")
        self.geometry("1200x800")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        # Dữ liệu chia sẻ giữa các màn hình
        self.shared_data = {
            "raw_text": "",        # Text từ file/input
            "questions": [],       # Câu hỏi từ AI
            "settings": {},        # Cài đặt đề thi
            "result": {},          # Kết quả sau khi thi
        }

        self._setup_fonts()
        self._build_frames()
        self.show_screen("upload")

    def _setup_fonts(self):
        """Định nghĩa font dùng chung."""
        self.fonts = {
            "title":  tkfont.Font(family="Consolas", size=16, weight="bold"),
            "header": tkfont.Font(family="Consolas", size=12, weight="bold"),
            "body":   tkfont.Font(family="Segoe UI", size=11),
            "small":  tkfont.Font(family="Consolas", size=9),
            "btn":    tkfont.Font(family="Consolas", size=10, weight="bold"),
        }

    def _build_frames(self):
        """Tạo tất cả màn hình, xếp chồng lên nhau."""
        # Import ở đây để tránh circular import
        from ui.screen_upload   import ScreenUpload
        from ui.screen_settings import ScreenSettings
        from ui.screen_quiz     import ScreenQuiz
        from ui.screen_result   import ScreenResult
        from ui.screen_history  import ScreenHistory

        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.screens = {}
        for ScreenClass, name in [
            (ScreenUpload,   "upload"),
            (ScreenSettings, "settings"),
            (ScreenQuiz,     "quiz"),
            (ScreenResult,   "result"),
            (ScreenHistory,  "history"),
        ]:
            frame = ScreenClass(container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.screens[name] = frame

    def show_screen(self, name: str):
        """Chuyển sang màn hình theo tên."""
        screen = self.screens.get(name)
        if screen is None:
            raise ValueError(f"Màn hình '{name}' không tồn tại.")
        screen.on_enter()   # Hook để màn hình tự refresh khi được hiển thị
        screen.tkraise()

    def set_shared(self, key: str, value):
        """Lưu dữ liệu dùng chung giữa các màn hình."""
        self.shared_data[key] = value

    def get_shared(self, key: str):
        """Lấy dữ liệu dùng chung."""
        return self.shared_data.get(key)