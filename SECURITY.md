# QuizGen - Hướng dẫn Bảo mật

## ⚠️ Bảo vệ API Keys

### Vấn đề
API keys là thông tin nhạy cảm. Nếu bạn commit trực tiếp vào GitHub, bất cứ ai có quyền truy cập repository cũng có thể sử dụng API keys của bạn.

### Giải pháp

#### 1. **Sử dụng file `.env` (Khuyến nghị) ✅**

File `.env` được liệt kê trong `.gitignore`, nên nó **KHÔNG BỊ PUSH** lên GitHub.

**Các bước:**
```bash
# 1. Sao chép .env.example thành .env
cp .env.example .env

# 2. Mở .env và điền API keys của bạn
GROQ_API_KEY=your_actual_key_here
GEMINI_API_KEY=your_actual_key_here
```

**Ưu điểm:**
- ✅ API keys không bị lộ
- ✅ Mỗi máy có cấu hình riêng
- ✅ Dễ quản lý nhiều environments (dev, prod, etc)
- ✅ Tự động load bởi `config.py`

#### 2. **GitHub Secrets (Cho CI/CD)**

Nếu bạn sử dụng GitHub Actions, hãy thêm secrets vào repo settings:
```
Settings > Secrets > New repository secret
```

### ✅ Checklist trước khi push

- [ ] `.env` không bị committed (nằm trong `.gitignore`)
- [ ] `.env.example` có sẵn để hướng dẫn
- [ ] Không có hardcoded API keys trong source code
- [ ] Chạy `git status` để kiểm tra không có `.env`

### 🚨 Nếu đã commit API keys

Nếu bạn vô tình commit API keys, hãy:
1. **Xoá keys ngay** từ trang web API provider
2. **Tạo keys mới**
3. **Rewrite Git history:**
   ```bash
   git filter-branch --tree-filter "rm -f config.py" HEAD
   git push -f origin main
   ```

---
Lưu ý: `.gitignore` đã được cấu hình đúng cách trong project này!
