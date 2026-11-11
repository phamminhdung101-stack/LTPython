# DocUni - Kho Tài Liệu Môn Học Có Phân Quyền & AI Tìm Kiếm Ngữ Cảnh

DocUni là nền tảng quản trị và chia sẻ tài liệu học tập dành cho sinh viên, giảng viên và cán bộ quản lý học viện. Dự án được xây dựng với kiến trúc kết hợp:
- **Backend**: Python Django & Django REST Framework (DRF) kết nối trực tiếp cơ sở dữ liệu **PostgreSQL 18**.
- **File Storage**: Django FileSystemStorage lưu trữ cục bộ tại thư mục `backend/media/documents/` (hoàn toàn miễn phí, không sử dụng AWS S3 hay Cloudflare R2).
- **Frontend**: Python Reflex (Full-Stack UI) tương tác với Backend qua HTTP REST API.
- **Bảo mật & Phân quyền**: RBAC (Role-Based Access Control) cho 3 vai trò: `ADMIN`, `LECTURER`, `STUDENT` kết hợp xác thực JWT & Session.

---

## 1. Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10/11 (hoặc macOS / Linux).
- **Python**: Phiên bản 3.10 trở lên (khuyên dùng Python 3.11 - 3.13).
- **PostgreSQL**: Phiên bản 16 - 18 đang chạy (mặc định cổng `5432`).
- **Node.js / Bun**: Hỗ trợ môi trường biên dịch Reflex frontend.

---

## 2. Cấu hình cơ sở dữ liệu & Lưu trữ (PostgreSQL & Storage)

1. Đảm bảo dịch vụ PostgreSQL đang hoạt động.
2. Database sử dụng: `kho_tai_lieu_mon_hoc`.
3. Kiểm tra file cấu hình môi trường [`.env`](file:///d:/document_knowledge_base/backend/.env) trong thư mục `backend/` (sao chép từ [`.env.example`](file:///d:/document_knowledge_base/backend/.env.example)):

```env
SECRET_KEY=django-insecure-m+u%x!i3!z8k_9q1*p0#w$v^b@y(c)d-e=f+g_h%j^k&l*m(n)o
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Cấu hình kết nối PostgreSQL 18
DB_NAME=kho_tai_lieu_mon_hoc
DB_USER=postgres
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=5432

# CORS Frontend
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# File Storage & Upload
MEDIA_URL=/media/
# MEDIA_ROOT= (để trống sẽ mặc định là backend/media)
MAX_UPLOAD_SIZE=52428800  # 50MB (tính bằng bytes)
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

Để chạy toàn bộ hệ thống, mở **2 cửa sổ Terminal**:

### Terminal 1: Chạy Django Backend (REST API)
```powershell
cd d:\document_knowledge_base
.\venv\Scripts\Activate.ps1
cách 1:python backend\manage.py runserver 127.0.0.1:8000
cách 2:D:\document_knowledge_base\run_backend.bat
```
- **Backend API**: `http://127.0.0.1:8000/api/`
- **Health Check**: `http://127.0.0.1:8000/api/health/`

### Terminal 2: Chạy Reflex Frontend
```powershell
cd d:\document_knowledge_base\frontend_app
..\venv\Scripts\Activate.ps1
cách 1:reflex run
cách 2:D:\document_knowledge_base\run_frontend.bat
```
- **Giao diện Web**: [http://localhost:3000](http://localhost:3000)

> [!NOTE]
> Reflex sử dụng cổng nội bộ `8001` cho máy chủ đồng bộ giao diện (`backend_port = 8001` trong `rxconfig.py`), hoàn toàn tách biệt với cổng `8000` của Django REST API nhằm tránh xung đột kết nối.

---

## 5. Chức năng Lưu trữ File Cục bộ (Local File Storage)

DocUni lưu trữ toàn bộ file học liệu thực tế trực tiếp trên máy chủ bằng **Django FileSystemStorage**, không phụ thuộc vào bất kỳ dịch vụ đám mây trả phí nào:

### Cấu trúc thư mục lưu trữ:
```text
backend/media/
└── documents/
    └── 2026/
        └── 11/
            ├── a0a364b5ca8b_slide_chuan_test.pdf
            └── 9f50b076bef4_de_thi_mau.docx
```

### Các định dạng file hỗ trợ (Whitelist):
- **PDF**: `.pdf` (kiểm tra header `%PDF-`).
- **Word**: `.doc`, `.docx` (kiểm tra OLE2 / OpenXML container `PK\x03\x04`).
- **PowerPoint**: `.ppt`, `.pptx` (kiểm tra OLE2 / OpenXML container).
- **Excel**: `.xls`, `.xlsx` (kiểm tra OLE2 / OpenXML container).
- **Văn bản**: `.txt` (kiểm tra UTF-8 text không chứa null bytes).

### Metadata lưu trong PostgreSQL:
- `document_id`: Mã tài liệu định danh.
- `file_name`: Tên file được lưu trên đĩa (`{uuid}_{clean_name}`).
- `original_file_name`: Tên file gốc người dùng tải lên.
- `file_type`: Loại tệp (`PDF`, `DOCX`, `TXT`...).
- `file_size`: Kích thước file tính bằng bytes.
- `mime_type`: Chuỗi MIME chuẩn (e.g. `application/pdf`).
- `object_key`: Khóa đường dẫn tương đối (e.g. `documents/2026/11/{uuid}_{name}`).
- `storage_provider`: Đặt cố định là `'LOCAL'`.
- `uploader_id`, `subject_id`, `class_id`, `department_id`, `upload_date`, `document_status`, `description`.

### Danh mục API Lưu trữ & Quản lý File:
| Phương thức | Endpoint | Phân quyền (RBAC) | Mô tả |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/documents/upload/` | Đã đăng nhập | Upload file (PDF, DOCX, TXT...), kiểm tra magic bytes, lưu file vào `media/` và tạo metadata trạng thái `PENDING`. |
| `GET / POST` | `/api/documents/<id>/download/` | JWT / Session | Tải file thực tế. Tài liệu `APPROVED` cho phép tải; tài liệu `PENDING` chỉ uploader, giảng viên hoặc admin được tải. Chống Path Traversal. |
| `DELETE` | `/api/documents/<id>/` | Uploader / Admin | Xóa tài liệu khỏi PostgreSQL và tự động xóa file vật lý tương ứng trong `media/`. |
| `POST` | `/api/documents/<id>/approve/` | Giảng viên / Admin | Phê duyệt tài liệu từ `PENDING` sang `APPROVED`. |
| `POST` | `/api/documents/<id>/reject/` | Giảng viên / Admin | Từ chối tài liệu kèm lý do phản hồi. |

---

## 6. Tài khoản thử nghiệm phân quyền (Dữ liệu PostgreSQL thật)

Hệ thống bắt buộc đăng nhập trước khi truy cập các tính năng. Khi mở trình duyệt tại `http://localhost:3000`, bạn sẽ được tự động chuyển hướng đến `/login`.

| Tài khoản | Mật khẩu mẫu | Vai trò (Role) | Trang điều hướng tự động & Quyền hạn |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | **ADMIN** | Điều hướng về `/admin/users`: Quản lý tài khoản, phân quyền, quản lý tổ chức khoa/lớp, phê duyệt và xóa mọi tài liệu. |
| **`gv01`** | `gv123` | **LECTURER** | Điều hướng về `/lecturer/dashboard`: Duyệt tài liệu sinh viên (`/lecturer/approval`), quản lý học liệu giảng dạy. |
| **`sv01`** | `sv123` | **STUDENT** | Điều hướng về `/documents`: Tra cứu tài liệu đã duyệt, tải lên bài tập/đề thi (`/student/upload`), trợ lý AI (`/student/ai-assistant`). |

---

## 7. Bộ kiểm thử tự động (Automated Test Suites)

Hệ thống đi kèm 3 bộ script kiểm thử tự động toàn diện:

### 1. Kiểm thử Toàn diện Xác thực & Phân quyền RBAC (`test_auth_rbac_full.py`):
```powershell
python backend\test_auth_rbac_full.py
```
Kiểm tra đầy đủ 15 kịch bản theo yêu cầu nghiệp vụ:
1. URL gốc `/` khi chưa đăng nhập -> chuyển hướng về `/login`.
2. URL nội bộ (`/admin/users`, `/lecturer/dashboard`) khi chưa đăng nhập -> chuyển hướng về `/login`.
3. Đăng nhập ADMIN (`admin`) -> cấp JWT token, trả đúng role `ADMIN`, điều hướng `/admin/users`.
4. Đăng nhập LECTURER (`gv01`) -> cấp JWT token, trả đúng role `LECTURER`, điều hướng `/lecturer/dashboard`.
5. Đăng nhập STUDENT (`sv01`) -> cấp JWT token, trả đúng role `STUDENT`, điều hướng `/documents`.
6. Đăng nhập sai mật khẩu -> 401 Unauthorized kèm thông báo lỗi.
7. Đăng nhập tài khoản bị khóa (`sv11` thuộc lớp có `is_locked=True`) -> 403 Forbidden kèm thông báo tài khoản bị khóa.
8. Sinh viên gọi API Admin (`/api/users/`) -> 403 Forbidden.
9. Giảng viên gọi API Admin (`/api/users/`) -> 403 Forbidden.
10. Chưa đăng nhập gọi API nội bộ (`/api/auth/me/`) -> 401 Unauthorized.
11. Token JWT hết hạn / không hợp lệ -> 401 AuthenticationFailed.
12. Đăng xuất (`POST /api/auth/logout/`) -> 200 OK và hủy session.
13. Khôi phục phiên làm việc từ JWT token (`GET /api/auth/me/`) -> 200 OK, trả đúng role và thông tin người dùng.
14. Chặn leo thang đặc quyền (Sinh viên gửi `PATCH role_id=1`) -> bị lọc bỏ, role trong database không đổi.
15. Chặn sinh viên tải tài liệu chưa được phê duyệt (`PENDING`) -> 403 Forbidden.

### 2. Kiểm thử File Storage & Bảo mật (`test_file_storage.py`):
```powershell
python backend\test_file_storage.py
```
Kiểm tra 15 kịch bản lưu trữ file, whitelist định dạng, magic bytes, chống path traversal, download và xóa file.

### 3. Kiểm thử API Endpoints & RBAC (`test_api_endpoints.py`):
```powershell
python backend\test_api_endpoints.py
```
Kiểm tra 14 kịch bản xác thực, health check, phân quyền người dùng, chống tự nâng quyền.

---

## 8. Cấu trúc thư mục dự án

```text
document_knowledge_base/
├── backend/                      # Django REST API Backend
│   ├── config/                   # Cấu hình settings.py, urls.py
│   ├── accounts/                 # User, Role, Authentication, JWT
│   ├── academics/                # Quản lý Khoa (Departments), Lớp, Môn học
│   ├── documents/                # Quản lý Kho tài liệu, File storage, Phê duyệt
│   │   ├── storage_service.py    # Dịch vụ Local FileSystemStorage & Anti Path Traversal
│   │   ├── api_views.py          # API Upload, Download, Delete, Approve, List
│   │   ├── models.py             # Models ánh xạ PostgreSQL (managed = False)
│   │   └── serializers.py        # Serializers gồm 15 trường metadata
│   ├── media/                    # Thư mục lưu file vật lý cục bộ
│   │   └── documents/YYYY/MM/    # File thực tế lưu trữ theo năm/tháng
│   ├── ai_search/                # API tìm kiếm ngữ cảnh AI
│   ├── permissions/              # RBAC Permission classes
│   ├── .env.example              # Mẫu biến môi trường
│   ├── requirements.txt          # Thư viện phụ thuộc backend
│   ├── test_auth_rbac_full.py    # Bộ kiểm thử toàn diện xác thực & RBAC (15 ca)
│   ├── test_file_storage.py      # Bộ kiểm thử lưu trữ file cục bộ (15 ca)
│   └── test_api_endpoints.py     # Bộ kiểm thử API & Phân quyền (14 ca)
├── frontend_app/                 # Python Reflex Frontend
│   ├── frontend_app/             # Giao diện sinh viên, giảng viên, admin, auth
│   └── rxconfig.py               # Cấu hình cổng Reflex (backend_port = 8001)
├── database/                     # Script SQL khởi tạo schema mẫu
└── README.md                     # Hướng dẫn dự án
```
