
import os
from dotenv import load_dotenv

load_dotenv()  # Tải API keys từ file .env

GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DEFAULT_NUM_QUESTIONS = 10
DEFAULT_NUM_OPTIONS = 4
DEFAULT_DIFFICULTY = "medium"
DEFAULT_LANGUAGE = "Tiếng Việt"
DEFAULT_TIME_MINUTES = 15

DIFFICULTY_MAP = {
    "easy":   "dễ, kiến thức cơ bản",
    "medium": "trung bình, cần hiểu sâu",
    "hard":   "khó, cần tư duy phân tích"
}