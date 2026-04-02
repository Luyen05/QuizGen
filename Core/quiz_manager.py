"""
core/quiz_manager.py
Nhiệm vụ: Quản lý toàn bộ vòng đời của 1 bài thi
- Lưu đề thi ra file JSON
- Load đề thi từ file
- Ghi nhận câu trả lời
- Tính điểm, thống kê
- Lưu lịch sử thi
"""

import json
import os
from datetime import datetime


# ── Cấu trúc dữ liệu Quiz (toàn bộ 1 bài thi) ───────────────────────────────
# {
#   "title": "Đề thi Python OOP",
#   "created_at": "2025-04-02 15:30",
#   "settings": {
#       "num_questions": 10,
#       "difficulty": "medium",
#       "time_limit": 15
#   },
#   "questions": [ ...list câu hỏi... ]
# }
# ─────────────────────────────────────────────────────────────────────────────

# ── Cấu trúc dữ liệu Result (kết quả 1 lần thi) ─────────────────────────────
# {
#   "quiz_title": "Đề thi Python OOP",
#   "date": "2025-04-02 15:45",
#   "score": 8,
#   "total": 10,
#   "time_taken": "8 phút 22 giây",
#   "answers": {
#       "0": "A",   # index câu -> đáp án người dùng chọn
#       "1": "C",
#       ...
#   }
# }
# ─────────────────────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


class QuizManager:
    def __init__(self):
        self.current_quiz: dict = {}          # Đề thi hiện tại
        self.user_answers: dict[int, str] = {}  # {index: "A"/"B"/"C"/"D"}
        self._ensure_data_dir()

    # ── Tạo & lưu đề thi ─────────────────────────────────────────────────────

    def create_quiz(self, questions: list[dict], settings: dict, title: str = "") -> dict:
        """Tạo đối tượng quiz từ danh sách câu hỏi và cài đặt."""
        self.current_quiz = {
            "title": title or f"Đề thi {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "settings": settings,
            "questions": questions
        }
        self.user_answers = {}
        return self.current_quiz

    def save_quiz(self, filepath: str):
        """Lưu đề thi ra file JSON để dùng lại sau."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.current_quiz, f, ensure_ascii=False, indent=2)

    def load_quiz(self, filepath: str):
        """Load đề thi từ file JSON."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Không tìm thấy file đề: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            self.current_quiz = json.load(f)
        self.user_answers = {}

    # ── Xử lý trong lúc thi ──────────────────────────────────────────────────

    def get_questions(self) -> list[dict]:
        """Trả về danh sách câu hỏi của đề hiện tại."""
        return self.current_quiz.get("questions", [])

    def get_question(self, index: int) -> dict:
        """Lấy 1 câu hỏi theo index."""
        questions = self.get_questions()
        if index < 0 or index >= len(questions):
            raise IndexError(f"Câu hỏi index {index} không tồn tại.")
        return questions[index]

    def submit_answer(self, question_index: int, answer: str):
        """Ghi nhận đáp án người dùng chọn cho câu hỏi."""
        if answer not in ["A", "B", "C", "D"]:
            raise ValueError(f"Đáp án '{answer}' không hợp lệ.")
        self.user_answers[question_index] = answer

    def get_answer(self, question_index: int) -> str | None:
        """Lấy đáp án người dùng đã chọn (None nếu chưa chọn)."""
        return self.user_answers.get(question_index)

    # ── Tính điểm & thống kê ─────────────────────────────────────────────────

    def calculate_result(self, time_taken_seconds: int) -> dict:
        """
        Tính điểm và tạo dict kết quả đầy đủ.
        time_taken_seconds: thời gian làm bài tính bằng giây
        """
        questions = self.get_questions()
        total = len(questions)
        score = 0
        detail = []

        for i, q in enumerate(questions):
            user_ans = self.user_answers.get(i)
            correct_ans = q["answer"]
            is_correct = user_ans == correct_ans

            if is_correct:
                score += 1

            detail.append({
                "index": i,
                "question": q["question"],
                "user_answer": user_ans,
                "correct_answer": correct_ans,
                "is_correct": is_correct,
                "explanation": q.get("explanation", "")
            })

        result = {
            "quiz_title": self.current_quiz.get("title", ""),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "total": total,
            "percentage": round(score / total * 100, 1) if total > 0 else 0,
            "grade": self._get_grade(score, total),
            "time_taken": self._format_time(time_taken_seconds),
            "answers": {str(k): v for k, v in self.user_answers.items()},
            "detail": detail
        }
        return result

    def _get_grade(self, score: int, total: int) -> str:
        """Xếp loại dựa trên tỷ lệ điểm."""
        if total == 0:
            return "Không xác định"
        ratio = score / total
        if ratio >= 0.9:
            return "Xuất sắc"
        elif ratio >= 0.8:
            return "Giỏi"
        elif ratio >= 0.65:
            return "Khá"
        elif ratio >= 0.5:
            return "Trung bình"
        else:
            return "Yếu"

    def _format_time(self, seconds: int) -> str:
        """Chuyển giây sang chuỗi 'X phút Y giây'."""
        m, s = divmod(seconds, 60)
        return f"{m} phút {s} giây"

    # ── Lịch sử thi ──────────────────────────────────────────────────────────

    def save_history(self, result: dict):
        """Ghi kết quả vào file lịch sử history.json."""
        history = self._load_history()
        history.append(result)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def get_history(self) -> list[dict]:
        """Đọc toàn bộ lịch sử thi."""
        return self._load_history()

    def _load_history(self) -> list:
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _ensure_data_dir(self):
        """Tạo thư mục data/ nếu chưa có."""
        os.makedirs(DATA_DIR, exist_ok=True)