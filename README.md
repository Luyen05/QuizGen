# 📚 QuizGen - Ứng dụng Tạo Quiz Tự Động bằng AI
## 👤 Tác Giả
- **Họ Tên**: Liêng Hót Ha Luyến
- **Mã SV**: 2312682
- **Năm**: 3
- **Kỳ**: HK2
## 📖 Mô Tả

**QuizGen** là một ứng dụng GUI hiện đại giúp tạo bộ câu hỏi trắc nghiệm tự động từ các tập tin (PDF, DOCX, TXT) bằng công nghệ AI. Ứng dụng hỗ trợ hai nền tảng AI mạnh mẽ: **Groq** và **Google Gemini**, với khả năng tự động chuyển đổi khi một dịch vụ gặp vấn đề.

## ✨ Tính Năng

- ✅ **Tải tệp đa dạng**: Hỗ trợ PDF, DOCX, TXT
- ✅ **Tạo quiz tự động**: AI phân tích nội dung và tạo câu hỏi trắc nghiệm
- ✅ **Cấu hình linh hoạt**: Điều chỉnh số lượng câu, số option, độ khó, ngôn ngữ
- ✅ **Hai nền tảng AI**: Groq (nhanh) + Google Gemini (dự phòng)
- ✅ **Ghi lịch sử**: Lưu và quản lý các bài quiz đã tạo
- ✅ **Giao diện thân thiện**: GUI dễ sử dụng với Tkinter

## 🚀 Yêu Cầu Hệ Thống

- **Python**: 3.9 hoặc cao hơn
- **OS**: Windows, macOS, Linux
- **RAM**: Tối thiểu 512 MB

## 📥 Hướng Dẫn Cài Đặt

### 1. Clone hoặc Tải Dự Án

```bash
git clone https://github.com/Luyen05/QuizGen
cd QuizGen
```

### 2. Tạo Virtual Environment (Khuyến nghị)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

Hoặc cài thủ công:
```bash
pip install google-generativeai groq pypdf PyPDF2 python-dotenv
```

### 4. Cấu Hình API Keys

**Tạo file `.env` từ template:**

```bash
cp .env.example .env
```

**Điền API keys vào file `.env`:**

```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

**Cách lấy API keys:**

- **Groq API**: https://console.groq.com/
- **Google Gemini API**: https://makersuite.google.com/app/apikey

### 5. Chạy Ứng Dụng

```bash
python main.py
```

## 📖 Hướng Dẫn Sử Dụng

### Màn Hình Upload

1. Nhấn **"Chọn File"** để tải lên tệp (PDF, DOCX, TXT)
2. Nội dung tệp sẽ được hiển thị trong vùng xem trước
3. Nhấn **"Tiếp Tục"** để chuyển sang cấu hình quiz

### Màn Hình Settings (Cấu Hình)

Điều chỉnh các tham số:

| Tham số | Giá Trị Mặc Định | Phạm Vi |
|---------|-----------------|--------|
| Số lượng câu | 10 | 1-50 |
| Số lựa chọn | 4 | 2-8 |
| Độ khó | Trung bình | Dễ / Trung bình / Khó |
| Ngôn ngữ | Tiếng Việt | Bất kỳ ngôn ngữ nào |
| Thời gian (phút) | 15 | 1-120 |

Nhấn **"Tạo Quiz"** để AI tạo câu hỏi.

### Màn Hình Làm Quiz

- Đọc câu hỏi và lựa chọn đáp án
- Nhấn **"Câu Tiếp Theo"** để chuyển sang câu khác
- Nhấn **"Hoàn Thành"** khi kết thúc

### Màn Hình Kết Quả

- Xem **điểm số** và **thống kê**
- Nhấn **"Quay Lại"** để làm quiz khác hoặc **"Đóng"** để thoát

## 📁 Cấu Trúc Dự Án

```
QuizGen/
├── main.py                 # Điểm vào chính
├── config.py              # Cấu hình (API keys, hằng số)
├── requirements.txt       # Dependencies
├── .env                   # API keys (KHÔNG commit)
├── .env.example          # Template cho .env
├── .gitignore            # Bỏ qua các tệp nhạy cảm
├── SECURITY.md           # Hướng dẫn bảo mật
├── README.md             # File này
│
├── Core/                 # Logic xử lý chính
│   ├── ai_generator.py   # Tạo câu hỏi bằng AI
│   ├── file_reader.py    # Đọc tệp (PDF, DOCX, TXT)
│   └── quiz_manager.py   # Quản lý quiz
│
├── ui/                   # Giao diện người dùng
│   ├── app.py            # Ứng dụng chính (Tkinter)
│   ├── screen_upload.py  # Màn hình upload tệp
│   ├── screen_settings.py # Màn hình cấu hình
│   ├── screen_quiz.py    # Màn hình làm quiz
│   ├── screen_history.py # Màn hình lịch sử
│   └── screen_result.py  # Màn hình kết quả
│
└── Data/                 # Dữ liệu
    └── history.json      # Lịch sử quiz
```

## 🔧 Kỹ Thuật Sử Dụng

- **Frontend**: Tkinter (GUI) - Đi kèm với Python
- **Backend**: Python 3.9+
- **AI Services**: 
  - Groq API (mô hình LLaMA)
  - Google Gemini API
- **PDF Processing**: pypdf, PyPDF2
- **Environment Management**: python-dotenv

## 🔐 Bảo Mật

⚠️ **IMPORTANT**: Không bao giờ commit file `.env` lên GitHub!

Các bước bảo vệ đã được áp dụng:
- ✅ API keys được lưu trong file `.env` (nằm trong `.gitignore`)
- ✅ File `.env.example` hướng dẫn cách setup
- ✅ Import từ `config.py` tự động load từ `.env`

Xem [SECURITY.md](SECURITY.md) để biết thêm chi tiết.

## 📊 Workflow

```
[Upload File] 
    ↓
[Configure Settings]
    ↓
[Generate Questions (AI)]
    ↓
[Take Quiz]
    ↓
[View Results]
    ↓
[Save to History]
```

## 🐛 Troubleshooting

### Lỗi: `ModuleNotFoundError: No module named 'dotenv'`

**Giải pháp:**
```bash
pip install python-dotenv
```

### Lỗi: API Key không hợp lệ

**Giải pháp:**
1. Kiểm tra file `.env` có đúng format không
2. Xác nhận API key hợp lệ từ Groq/Gemini
3. Đảm bảo không có dấu cách thừa

### Ứng dụng chạy chậm

**Nguyên nhân & Giải pháp:**
- Tệp quá lớn → Chia thành các phần nhỏ hơn
- API bận → Thử lại sau
- Máy tính yếu → Giảm số lượng câu hỏi

## 📝 Ví Dụ Sử Dụng

```python
from Core.ai_generator import generate_questions

# Tạo quiz từ text
text = "Python là một ngôn ngữ lập trình bậc cao..."
questions = generate_questions(
    text,
    num_questions=5,
    num_options=4,
    difficulty="medium",
    language="Tiếng Việt"
)

for q in questions:
    print(q['question'])
    print(q['options'])
```


## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 🙏 Cảm Ơn

- Groq API - Cung cấp nền tảng LLM nhanh
- Google Gemini API - Cung cấp nền tảng backup
- Python community

## 📧 Liên Hệ & Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra [Troubleshooting](#-troubleshooting) section
2. Xem file [SECURITY.md](SECURITY.md)
3. Liên hệ tác giả hoặc tạo GitHub Issue

---

**Happy Quiz Generation! 🎉**

*Cập nhật lần cuối: April 2, 2026*
