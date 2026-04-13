"""
Core/ai_generator.py
Nhiệm vụ: Gọi AI tạo câu hỏi + verify độ chính xác
- Ưu tiên Groq, tự động fallback sang Gemini nếu lỗi
- Sau khi tạo xong, gửi AI kiểm tra lại để loại câu sai
"""

import json
import re
from groq import Groq
from google import genai
from config import GROQ_API_KEY, GEMINI_API_KEY, DIFFICULTY_MAP


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def generate_questions(text: str, num_questions: int = 10, num_options: int = 4,
                       difficulty: str = "medium", language: str = "Tiếng Việt",
                       verify: bool = True) -> list[dict]:
    """
    Tạo câu hỏi trắc nghiệm từ văn bản.
    Thử Groq trước, fallback sang Gemini nếu lỗi.
    Nếu verify=True, gửi AI kiểm tra lại độ chính xác.
    """
    # Bước 1: Sinh câu hỏi
    try:
        print("[AI] Đang dùng Groq...")
        questions = _generate_with_groq(text, num_questions, num_options, difficulty, language)
    except Exception as e:
        print(f"[AI] Groq lỗi: {e} → Chuyển sang Gemini...")
        questions = _generate_with_gemini(text, num_questions, num_options, difficulty, language)

    # Bước 2: Verify nếu được yêu cầu
    if verify and questions:
        print(f"[AI] Đang verify {len(questions)} câu hỏi...")
        questions = verify_questions(questions, text)

    return questions


def verify_questions(questions: list[dict], original_text: str) -> list[dict]:
    """
    Gửi câu hỏi vừa tạo cho AI kiểm tra lại.
    Loại bỏ câu hỏi AI đánh dấu là sai/không chính xác.
    Trả về danh sách câu hỏi đã được xác thực.
    """
    prompt = f"""Dưới đây là nội dung tài liệu gốc:
\"\"\"{original_text[:2000]}\"\"\"

Đây là các câu hỏi trắc nghiệm vừa được tạo ra từ tài liệu trên:
{json.dumps(questions, ensure_ascii=False, indent=2)}

Hãy kiểm tra TỪNG câu hỏi:
1. Đáp án có chính xác dựa trên nội dung tài liệu không?
2. Câu hỏi có rõ ràng, không gây hiểu nhầm không?
3. Các đáp án nhiễu có hợp lý không?

Trả về ĐÚNG định dạng JSON sau, KHÔNG thêm text nào khác:
{{
  "verified": [
    {{
      "index": 0,
      "is_valid": true,
      "confidence": "high",
      "reason": ""
    }},
    {{
      "index": 1,
      "is_valid": false,
      "confidence": "low",
      "reason": "Đáp án đúng phải là B vì tài liệu nêu rõ..."
    }}
  ]
}}

confidence có 3 mức: "high", "medium", "low"
"""
    try:
        result = _call_ai_for_verify(prompt)
        verified_list = result.get("verified", [])
        return _filter_by_verify(questions, verified_list)
    except Exception as e:
        print(f"[WARN] Verify thất bại: {e} — dùng toàn bộ câu hỏi gốc")
        return questions


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL — Sinh câu hỏi
# ─────────────────────────────────────────────────────────────────────────────

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
- Câu hỏi phải dựa TRỰC TIẾP vào nội dung tài liệu

Trả về ĐÚNG định dạng JSON sau, KHÔNG thêm bất kỳ text nào khác:
{{
  "questions": [
    {{
      "question": "Nội dung câu hỏi?",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "A",
      "explanation": "Giải thích ngắn gọn tại sao đáp án đúng"
    }}
  ]
}}"""


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL — Verify
# ─────────────────────────────────────────────────────────────────────────────

def _call_ai_for_verify(prompt: str) -> dict:
    """Gọi AI để verify — thử Groq trước, fallback Gemini."""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Thấp hơn để verify chính xác hơn
        )
        raw = response.choices[0].message.content
    except Exception:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        raw = response.text

    # Parse JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        if match:
            return json.loads(match.group(1))
        raise ValueError("Verify response không phải JSON hợp lệ")


def _filter_by_verify(questions: list[dict], verified_list: list[dict]) -> list[dict]:
    """
    Lọc câu hỏi dựa trên kết quả verify.
    Giữ lại câu is_valid=True hoặc confidence="high"/"medium".
    Gắn thêm field 'verified' và 'confidence' vào mỗi câu.
    """
    verify_map = {v["index"]: v for v in verified_list}
    result = []

    for i, q in enumerate(questions):
        v = verify_map.get(i)
        if v is None:
            # Không có thông tin verify → giữ lại
            q["verified"] = True
            q["confidence"] = "medium"
            result.append(q)
        elif v.get("is_valid", True) and v.get("confidence") != "low":
            q["verified"] = True
            q["confidence"] = v.get("confidence", "medium")
            q["verify_note"] = v.get("reason", "")
            result.append(q)
        else:
            print(f"[VERIFY] Loại câu {i+1}: {v.get('reason', 'không hợp lệ')}")

    if not result:
        print("[WARN] Tất cả câu bị loại sau verify — dùng lại câu gốc")
        return questions

    print(f"[VERIFY] Giữ lại {len(result)}/{len(questions)} câu hợp lệ")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL — Parse & Validate
# ─────────────────────────────────────────────────────────────────────────────

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
            print(f"[WARN] Câu {i+1} thiếu field — bỏ qua")
            continue
        if not isinstance(q["options"], list) or len(q["options"]) < 2:
            print(f"[WARN] Câu {i+1} options không hợp lệ — bỏ qua")
            continue
        if q["answer"] not in ["A", "B", "C", "D"]:
            print(f"[WARN] Câu {i+1} answer '{q['answer']}' không hợp lệ — bỏ qua")
            continue
        valid.append(q)

    if not valid:
        raise ValueError("Không có câu hỏi hợp lệ nào từ AI.")
    return valid