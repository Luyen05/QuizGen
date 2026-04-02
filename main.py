"""
main.py — Điểm khởi chạy của QuizGen
Chạy: python main.py
"""

import sys
import os

# Thêm thư mục gốc vào path để import hoạt động đúng
sys.path.insert(0, os.path.dirname(__file__))

from ui.app import QuizGenApp


if __name__ == "__main__":
    app = QuizGenApp()
    app.mainloop()