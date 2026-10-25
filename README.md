# DocUni - Kho Tài Liệu Môn Học Có Phân Quyền & AI Tìm Kiếm Ngữ Cảnh

DocUni là nền tảng quản trị và chia sẻ tài liệu học tập dành cho sinh viên, giảng viên và cán bộ quản lý học viện. Dự án được xây dựng với kiến trúc kết hợp:
- **Backend**: Python Django & Django REST Framework (DRF) kết nối trực tiếp cơ sở dữ liệu **PostgreSQL 18**.
- **Frontend**: Python Reflex (Full-Stack UI) tương tác với Backend qua HTTP REST API.
- **Bảo mật & Phân quyền**: RBAC (Role-Based Access Control) cho 3 vai trò: `ADMIN`, `LECTURER`, `STUDENT`.

---

## 1. Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10/11 (hoặc macOS / Linux).
- **Python**: Phiên bản 3.10 trở lên (khuyên dùng Python 3.11 - 3.13).
- **PostgreSQL**: Phiên bản 16 - 18 đang chạy (mặc định cổng `5432`).
- **Node.js / Bun**: Hỗ trợ môi trường biên dịch Reflex frontend.

---

## 2. Cấu hình cơ sở dữ liệu (PostgreSQL)

1. Đảm bảo dịch vụ PostgreSQL đang hoạt động.
2. Database sử dụng: `kho_tai_lieu_mon_hoc`.
3. Kiểm tra file cấu hình môi trường [`.env`](file:///d:/document_knowledge_base/backend/.env) trong thư mục `backend/` (nếu chưa có, sao chép từ [`.env.example`](file:///d:/document_knowledge_base/backend/.env.example)):

```env
SECRET_KEY=django-insecure-m+u%x!i3!z8k_9q1*p0#w$v^b@y(c)d-e=f+g_h%j^k&l*m(n)o
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Cấu hình kết nối PostgreSQL
DB_NAME=kho_tai_lieu_mon_hoc
DB_USER=postgres
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=5432

# CORS Frontend
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 3. Cài đặt môi trường

Mở **PowerShell** tại thư mục gốc của dự án (`d:\document_knowledge_base`):

```powershell
# Kích hoạt môi trường ảo Python
.\venv\Scripts\Activate.ps1

# Cài đặt các thư viện cần thiết cho Backend & Frontend
pip install -r backend\requirements.txt
```

---

## 4. Hướng dẫn khởi chạy dự án

Để chạy toàn bộ hệ thống, bạn cần mở **2 cửa sổ Terminal**:

### Terminal 1: Chạy Django Backend (REST API)
```powershell
cd d:\document_knowledge_base
.\venv\Scripts\Activate.ps1
python backend\manage.py runserver 127.0.0.1:8000
```
- **Backend API**: `http://127.0.0.1:8000/api/`
- **Health Check**: `http://127.0.0.1:8000/api/health/`

### Terminal 2: Chạy Reflex Frontend
```powershell
cd d:\document_knowledge_base\frontend_app
..\venv\Scripts\Activate.ps1
reflex run
```
- **Giao diện Web**: [http://localhost:3000](http://localhost:3000)

> [!NOTE]
> Reflex sử dụng cổng nội bộ `8001` cho máy chủ đồng bộ giao diện (`backend_port = 8001` trong `rxconfig.py`), hoàn toàn tách biệt với cổng `8000` của Django REST API nhằm tránh xung đột kết nối.

---

## 5. Tài khoản thử nghiệm phân quyền (Dữ liệu PostgreSQL thật)

Hệ thống bắt buộc đăng nhập trước khi truy cập các tính năng. Khi mở trình duyệt tại `http://localhost:3000`, bạn sẽ được tự động chuyển hướng đến `/login`.

| Tài khoản | Mật khẩu mẫu | Vai trò (Role) | Trang điều hướng tự động & Quyền hạn |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | **ADMIN** | Điều hướng về `/admin/users`: Quản lý tài khoản, phân quyền, quản lý tổ chức khoa/lớp. |
| **`gv01`** | `gv123` | **LECTURER** | Điều hướng về `/lecturer/dashboard`: Duyệt tài liệu sinh viên (`/lecturer/approval`), quản lý học liệu giảng dạy. |
| **`sv01`** | `sv123` | **STUDENT** | Điều hướng về `/documents`: Tra cứu tài liệu đã duyệt, tải lên bài tập/đề thi (`/student/upload`), trợ lý AI (`/student/ai-assistant`). |

---

## 6. Kiểm tra kết nối & Kiểm thử tự động (Test Suite)

Bạn có thể chạy kiểm thử tự động 14 ca kiểm thử (kiểm tra kết nối PostgreSQL, xác thực mật khẩu, phân quyền RBAC và chống leo quyền):

```powershell
python backend\test_api_endpoints.py
```

Kết quả mong đợi:
```text
============================================================
BẮT ĐẦU CHẠY KIỂM THỬ BACKEND DJANGO REST API & POSTGRESQL
============================================================
[PASS] 1. Kết nối PostgreSQL database trực tiếp
[PASS] 2. Endpoint GET /api/health/ trả về 200 OK
...
[PASS] 12. Đăng xuất POST /api/auth/logout/ thành công
============================================================
KẾT QUẢ KIỂM THỬ: 14/14 bài kiểm thử thành công.
============================================================
```

---

## 7. Cấu trúc thư mục chính

```text
document_knowledge_base/
├── backend/                  # Django REST API Backend
│   ├── config/               # Cấu hình settings.py, urls.py
│   ├── accounts/             # Quản lý User, Role, Authentication backend
│   ├── academics/            # Quản lý Khoa (Departments), Lớp, Môn học
│   ├── documents/            # Quản lý Kho tài liệu, phê duyệt, lịch sử
│   ├── ai_search/            # API tìm kiếm ngữ cảnh AI
│   ├── permissions/          # RBAC Permission classes
│   ├── .env.example          # Mẫu biến môi trường
│   ├── requirements.txt      # Thư viện phụ thuộc backend
│   └── test_api_endpoints.py # Bộ script kiểm thử tự động
├── frontend_app/             # Python Reflex Frontend
│   ├── frontend_app/         # Giao diện sinh viên, giảng viên, admin, auth
│   └── rxconfig.py           # Cấu hình cổng Reflex (backend_port = 8001)
├── database/                 # Script SQL khởi tạo schema mẫu
└── README.md                 # Hướng dẫn dự án
```

