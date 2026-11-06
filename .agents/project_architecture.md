# Kiến Trúc Dự Án: DocUni (LTPython)

## 1. Tổng Quan Dự Án
- **Tên dự án**: DocUni (Hệ thống Quản lý Tài liệu Học tập & Tìm kiếm AI).
- **Mục tiêu**: Cung cấp nền tảng quản trị tài liệu học thuật theo khoa, lớp, môn học; kiểm soát quyền truy cập chi tiết; quản lý phiên bản tài liệu và hỗ trợ tìm kiếm tài liệu thông minh / hỏi đáp RAG bằng AI.
- **Đối tượng người dùng**: Admin (Quản trị viên hệ thống), Lecturer (Giảng viên), Student (Sinh viên).

## 2. Tech Stack & Công Nghệ
- **Backend**: Python 3.13 / Django 6.1.1, Django REST Framework 3.18.1.
- **Background Tasks & Caching**: Celery 5.6.3, Redis 8.1.0.
- **Database**: PostgreSQL (`psycopg2-binary 2.9.13`), Schema SQL chuẩn hóa tại `database/schema.sql`.
- **AI / Embeddings**: OpenAI API, Vector search (RAG), Pydantic.
- **Frontend**: HTML5, Tailwind CSS (CDN), FontAwesome, Vanilla JavaScript (kiến trúc SPA mockup chuyển dần sang tích hợp Django templates / REST APIs).

## 3. Cấu Trúc Thư Mục
```
LTPython/
├── backend/                  # Mã nguồn backend Django
│   ├── manage.py
│   ├── config/               # Cấu hình dự án Django (settings, urls, wsgi, asgi)
│   ├── accounts/             # Quản lý tài khoản, vai trò, xác thực
│   ├── academics/            # Quản lý Khoa, Lớp, Môn học
│   ├── documents/            # Quản lý Thư mục, Tài liệu, Phiên bản (Version), Tags
│   ├── permissions/          # Quản lý Phân quyền động (Department, Class, User)
│   ├── dashboard/            # Thống kê, giám sát hoạt động & kiểm toán
│   └── ai_search/            # Chunking, Vector Embeddings & RAG Chatbot
├── database/
│   └── schema.sql            # Schema PostgreSQL 13 bảng & dữ liệu mẫu (seed data)
├── frontend/
│   ├── static/               # File tĩnh: CSS, JS (mock data & logic xử lý giao diện), hình ảnh
│   └── templates/            # Giao diện HTML (Admin tổ chức, người dùng, giao diện sinh viên)
├── requirements.txt          # Danh sách thư viện Python phụ thuộc
└── .agents/
    └── project_architecture.md # Tài liệu kiến trúc và bộ nhớ ngữ cảnh dự án
```

## 4. Mô Hình Dữ Liệu (13 Bảng Chính)
1. `roles`: ADMIN, LECTURER, STUDENT.
2. `departments`: Danh mục Khoa/Viện.
3. `classes`: Danh sách Lớp học (liên kết Khoa, cờ `is_locked`).
4. `subjects`: Môn học theo từng Khoa.
5. `users`: Tài khoản người dùng (username, password_hash, full_name, role_id, department_id, class_id).
6. `folders`: Cây thư mục lưu trữ theo từng môn học.
7. `documents`: Tài liệu (title, description, subject_id, folder_id, uploader_id, status: PENDING/APPROVED/REJECTED, is_public, view/download count).
8. `document_versions`: Lịch sử phiên bản file (file_path, version_number, updated_by, change_summary).
9. `tags` & `document_tags`: Gắn nhãn phân loại tài liệu đa chiều.
10. `document_permissions`: Phân quyền chi tiết (theo DEPARTMENT / CLASS / USER với quyền xem, tải, chỉnh sửa).
11. `document_activity_logs`: Kiểm toán hoạt động (CREATE, UPDATE, DELETE, APPROVE, VIEW, DOWNLOAD...).
12. `document_embeddings`: Vector embeddings của từng đoạn văn bản (chunk).
13. `ai_queries` & `ai_query_sources`: Lịch sử câu hỏi AI và liên kết nguồn dữ liệu trích dẫn.

## 5. Trạng Thái Hiện Tại & Công Việc Cần Triển Khai
- [x] Thiết kế xong Database Schema hoàn chỉnh với ràng buộc và dữ liệu mẫu (`database/schema.sql`).
- [x] Thiết kế xong giao diện cơ bản (Admin Quản lý tổ chức, Quản lý người dùng, Giao diện sinh viên tra cứu tài liệu).
- [x] **Task 3.1**: Trang Đóng góp tài liệu (`document_upload.html` & `student_upload.js`: kéo thả file, phân cấp Khoa/Môn/Thư mục, tạo thư mục động, gắn thẻ tag chips, validation).
- [x] **Task 3.2**: Trang Theo dõi trạng thái duyệt tài liệu (`my_contributions.html` & `student_contributions.js`: thẻ KPI, lọc tabs PENDING/APPROVED/REJECTED, hiển thị lý do từ chối, modal nộp phiên bản v2.0, thu hồi tài liệu).
- [x] **Task 3.3**: Trang Trợ lý học tập AI (`ai_assistant.html` & `ai_assistant.js`: Chatbot hội thoại & RAG Semantic Search đối soát tri thức trích dẫn nguồn).
- [x] **Task 3.4**: Đồng bộ toàn diện hệ thống điều hướng Navbar trên các trang Sinh viên (`home.html`, `document_list.html`, `document_detail.html`, `document_upload.html`, `my_contributions.html`, `ai_assistant.html`).
- [x] **Task 4.1**: Thiết lập phong cách giao diện & CSS dùng chung Lecturer Portal (`lecturer.css`: sidebar, portal table, modal, badges).
- [x] **Task 4.2**: Trang Quản lý kho tài liệu (`document_management.html` & `lecturer_documents.js`: bảng danh mục tài liệu, modal CRUD thêm/sửa/xóa, quản lý dòng lịch sử phiên bản versioning, modal cấu hình phân quyền chi tiết theo Lớp/Khoa).
- [x] **Task 4.3**: Trang Kiểm duyệt tài liệu đóng góp từ sinh viên (`document_approval.html` & `lecturer_approval.js`: hàng đợi duyệt PENDING, xem trước kép side-by-side, modal Approve & Reject kèm nhận xét, đồng bộ ngược về sinh viên).
- [x] **Task 4.4**: Trang Dashboard Giảng viên & Biểu đồ Chart.js (`dashboard.html` & `lecturer_dashboard.js`: KPI thẻ tóm tắt, biểu đồ đường Line Chart xu hướng theo tuần/tháng, biểu đồ cột Bar Chart top tài liệu, biểu đồ tròn Doughnut Chart cơ cấu học liệu, feed hoạt động).
- [x] **Task 4.5**: Đồng bộ toàn diện hệ thống điều hướng liên kết giữa Admin Portal, Lecturer Portal và Student Portal.
- [ ] Chuyển đổi Schema SQL thành Django Models trong các app tương ứng.
- [ ] Cấu hình kết nối PostgreSQL trong `backend/config/settings.py` và đăng ký apps.
- [ ] Xây dựng REST API Views / Serializers trong Django.
- [ ] Tích hợp API vào JavaScript frontend thay thế mock data.
- [ ] Triển khai pipeline Celery + OpenAI Embedding cho tính năng AI Search.
