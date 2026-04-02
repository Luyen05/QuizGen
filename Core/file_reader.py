"""
core/file_reader.py
Nhiệm vụ: Đọc nội dung từ file PDF, TXT, DOCX
Trả về: chuỗi văn bản thuần (plain text)
"""

import os


def read_file(filepath: str) -> str:
    """
    Đọc file theo đuôi mở rộng, trả về nội dung dạng string.
    Raise ValueError nếu định dạng không hỗ trợ.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Không tìm thấy file: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        return _read_txt(filepath)
    elif ext == ".pdf":
        return _read_pdf(filepath)
    elif ext == ".docx":
        return _read_docx(filepath)
    else:
        raise ValueError(f"Định dạng '{ext}' chưa được hỗ trợ. Dùng TXT, PDF hoặc DOCX.")


def _read_txt(filepath: str) -> str:
    """Đọc file TXT, tự động nhận dạng encoding."""
    for encoding in ["utf-8", "utf-16", "latin-1"]:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
    raise ValueError("Không thể đọc file TXT — kiểm tra lại encoding.")


def _read_pdf(filepath: str) -> str:
    """Đọc file PDF, ghép tất cả trang lại."""
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("Thiếu thư viện: pip install PyPDF2")

    text = []
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text.append(content.strip())

    if not text:
        raise ValueError("File PDF không có nội dung văn bản (có thể là PDF scan ảnh).")

    return "\n".join(text)


def _read_docx(filepath: str) -> str:
    """Đọc file DOCX, lấy từng đoạn văn."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("Thiếu thư viện: pip install python-docx")

    doc = Document(filepath)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        raise ValueError("File DOCX không có nội dung.")

    return "\n".join(paragraphs)


def validate_text(text: str, min_chars: int = 100) -> bool:
    """
    Kiểm tra văn bản có đủ nội dung để tạo câu hỏi không.
    Tối thiểu 100 ký tự.
    """
    return len(text.strip()) >= min_chars