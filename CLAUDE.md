# Project Instructions: DocUni (LTPython)

## Tech Stack
- **Language**: Python 3.13+
- **Backend**: Django 6.1.1, Django REST Framework 3.18.1
- **Database**: PostgreSQL (psycopg2-binary 2.9.13), schema file at `database/schema.sql`
- **Async & Queue**: Celery 5.6.3, Redis 8.1.0
- **AI / LLM**: OpenAI API, Vector search embeddings, Pydantic 2.13.5
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript

## Project Structure
- `backend/config/`: Cấu hình chính của Django (settings, urls, wsgi, asgi).
- `backend/accounts/`: Module quản lý người dùng, phân quyền vai trò (Admin, Giảng viên, Sinh viên).
- `backend/academics/`: Module quản lý Khoa, Lớp, Môn học.
- `backend/documents/`: Module quản lý thư mục, tài liệu, phiên bản tệp, tags, quy trình duyệt.
- `backend/permissions/`: Module quản lý ma trận phân quyền tài liệu theo Khoa/Lớp/Cá nhân.
- `backend/dashboard/`: Module thống kê số liệu và nhật ký hoạt động (audit logs).
- `backend/ai_search/`: Module xử lý trích xuất văn bản, chunking, embeddings và tìm kiếm RAG.
- `database/schema.sql`: Định nghĩa 13 bảng quan hệ, ràng buộc toàn vẹn và dữ liệu mẫu.
- `frontend/`: Giao diện web gồm `templates/` và `static/` (CSS, JS mock data).

## Development Commands
- Kích hoạt virtualenv (nếu có): `.\venv\Scripts\Activate.ps1`
- Cài đặt thư viện: `pip install -r requirements.txt`
- Chạy migrations: `python backend/manage.py migrate`
- Chạy development server: `python backend/manage.py runserver`
- Chạy Celery worker: `celery -A config worker --loglevel=info`

## Conventions
- Tuân thủ PEP 8 cho mã nguồn Python.
- Model fields và foreign keys phải phản ánh đúng ràng buộc trong `database/schema.sql`.
- Mã lỗi và status codes của API phải rõ ràng, chuẩn RESTful.
- Không lưu credentials hoặc API keys trực tiếp trong mã nguồn; sử dụng biến môi trường qua `python-dotenv`.
