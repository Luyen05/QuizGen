import json
import re
from groq import Groq
import google.generativeai as genai
from config import GROQ_API_KEY, GEMINI_API_KEY, DIFFICULTY_MAP


def generate_questions(text, num_questions=10, num_options=4,
                       difficulty="medium", language="Tiếng Việt") -> list[dict]:
    """Thử Groq trước, nếu lỗi tự động chuyển sang Gemini."""

    try:
        print("[AI] Đang dùng Groq...")
        return _generate_with_groq(text, num_questions, num_options, difficulty, language)
    except Exception as e:
        print(f"[AI] Groq lỗi: {e} → Chuyển sang Gemini...")
        return _generate_with_gemini(text, num_questions, num_options, difficulty, language)


def _generate_with_groq(text, num_questions, num_options, difficulty, language):
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": _build_prompt(text, num_questions, num_options, difficulty, language)}],
        temperature=0.7,
    )
    return _parse_response(response.choices[0].message.content, num_questions)


def _generate_with_gemini(text, num_questions, num_options, difficulty, language):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=_build_prompt(text, num_questions, num_options, difficulty, language)
    )
    return _parse_response(response.text, num_questions)


def _build_prompt(text, num_questions, num_options, difficulty, language) -> str:
    difficulty_desc = DIFFICULTY_MAP.get(difficulty, "trung bình")
    return f"""Bạn là công cụ tạo câu hỏi trắc nghiệm chuyên nghiệp.

Dưới đây là nội dung bài giảng:
\"\"\"
{text[:3000]}
\"\"\"

Hãy tạo CHÍNH XÁC {num_questions} câu hỏi trắc nghiệm với các yêu cầu:
- Ngôn ngữ: {language}
- Độ khó: {difficulty_desc}
- Mỗi câu có {num_options} đáp án (A, B, C, D)
- Chỉ có 1 đáp án đúng

Trả về ĐÚNG định dạng JSON sau, KHÔNG thêm bất kỳ text nào khác:
{{
  "questions": [
    {{
      "question": "Nội dung câu hỏi?",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "A",
      "explanation": "Giải thích ngắn gọn"
    }}
  ]
}}"""


def _parse_response(raw_text: str, expected_count: int) -> list[dict]:
    try:
        data = json.loads(raw_text)
        return _validate_questions(data.get("questions", []))
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
    if match:
        try:
            data = json.loads(match.group(1))
            return _validate_questions(data.get("questions", []))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"AI trả về không đúng format JSON.\n{raw_text[:300]}")


def _validate_questions(questions: list[dict]) -> list[dict]:
    valid = []
    required_fields = {"question", "options", "answer", "explanation"}
    for i, q in enumerate(questions):
        if not required_fields.issubset(q.keys()):
            continue
        if not isinstance(q["options"], list) or len(q["options"]) < 2:
            continue
        if q["answer"] not in ["A", "B", "C", "D"]:
            continue
        valid.append(q)
    if not valid:
        raise ValueError("Không có câu hỏi hợp lệ nào từ AI.")
    return valid