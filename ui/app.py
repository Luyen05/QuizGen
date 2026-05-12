"""
ui/app.py
CustomTkinter App chính.
"""

import customtkinter as ctk

from ui.theme.theme_manager import ThemeManager
from ui.utils.navigation import NavigationManager
from ui.screens.home import ScreenHome
from ui.screens.upload import ScreenUpload
from ui.screens.settings import ScreenSettings
from ui.screens.generate import ScreenGenerate
from ui.screens.quiz import ScreenQuiz
from ui.screens.result import ScreenResult
from ui.screens.history import ScreenHistory
from ui.screens.stats import ScreenStats


class QuizGenApp(ctk.CTk):
    def __init__(self):
        ThemeManager.init_global()
        super().__init__()

        self.title("QuizGen — Hệ thống tạo đề thi tự động")
        self.geometry("1400x900")
        self.minsize(1200, 780)
        self.configure(fg_color="#111111")

        self.theme = ThemeManager()
        self.nav = NavigationManager(self)

        self.shared_data = {
            "raw_text": "",
            "questions": [],
            "settings": {},
            "result": {},
            "quiz_manager": None,
        }

        self._build_frames()
        self.show_screen("home")

    def _build_frames(self):
        container = ctk.CTkFrame(self, fg_color=self.theme.colors["bg"])
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.screens = {}
        for ScreenClass, name in [
            (ScreenHome, "home"),
            (ScreenUpload, "upload"),
            (ScreenSettings, "settings"),
            (ScreenGenerate, "generate"),
            (ScreenQuiz, "quiz"),
            (ScreenResult, "result"),
            (ScreenHistory, "history"),
            (ScreenStats, "stats"),
        ]:
            frame = ScreenClass(container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.screens[name] = frame

    def show_screen(self, name: str):
        screen = self.screens.get(name)
        if screen is None:
            raise ValueError(f"Màn hình '{name}' không tồn tại.")
        screen.on_enter()
        screen.tkraise()

    def set_shared(self, key: str, value):
        self.shared_data[key] = value

    def get_shared(self, key: str):
        return self.shared_data.get(key)
