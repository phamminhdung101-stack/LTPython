"""
DocUni - Centralized Data Store & State Management (Reflex Full-Stack)
Hạt nhân lưu trữ và điều phối dữ liệu chung cho Task 2 (Folder Tree, Upload, ACL)
và Task 3 (Versioning, Tagging, Approval Workflow, Audit Logs).
"""

from datetime import datetime
from typing import List, Dict, Any
import reflex as rx


# ─── 1. Danh Sách Tài Khoản Người Dùng Giả Lập Chuẩn ────────────────────────

PRESET_USERS: List[Dict[str, Any]] = [
    {
        "id": "u1",
        "username": "nam_d21cn01",
        "full_name": "Lê Hoàng Nam",
        "role": "STUDENT",
        "role_label": "Sinh viên",
        "class_name": "Lớp D21CQCN01-A",
        "class_code": "CLASS_A",
        "department": "Khoa Công nghệ thông tin",
        "avatar_color": "blue",
    },
    {
        "id": "u2",
        "username": "mai_d21cn02",
        "full_name": "Trần Thị Mai",
        "role": "STUDENT",
        "role_label": "Sinh viên",
        "class_name": "Lớp D21CQCN02-B",
        "class_code": "CLASS_B",
        "department": "Khoa Công nghệ thông tin",
        "avatar_color": "indigo",
    },
    {
        "id": "u3",
        "username": "ts_an",
        "full_name": "TS. Nguyễn Văn An",
        "role": "LECTURER",
        "role_label": "Giảng viên",
        "class_name": "",
        "class_code": "",
        "department": "Khoa Công nghệ thông tin",
        "avatar_color": "purple",
    },
    {
        "id": "u4",
        "username": "admin",
        "full_name": "Quản trị viên Hệ thống",
        "role": "ADMIN",
        "role_label": "Quản trị viên",
        "class_name": "",
        "class_code": "",
        "department": "Phòng Đào tạo",
        "avatar_color": "gray",
    },
]


# ─── 2. Dữ Liệu Khởi Tạo Tài Liệu Đầy Đủ Phân Quyền & Phiên Bản ───────────────

INITIAL_DOCUMENTS: List[Dict[str, Any]] = [
    # ── Doc 1: Phân quyền CHỈ DÀNH CHO LỚP A (D21CQCN01-A) -> Sinh viên lớp B mở sẽ bị 403 ──
    {
        "id": "doc_acl_class_a",
        "title": "[Lớp A] Đề cương & Mã nguồn BTL Lập trình Web Full-Stack",
        "subject_code": "IT410",
        "subject_name": "Lập trình Web",
        "faculty": "CNTT",
        "folder_path": "IT410 / Bài tập lớn / Nhóm A",
        "folder_name": "Bài tập lớn",
        "doc_type": "EXERCISE",
        "type_label": "Bài tập lớn",
        "type_color": "purple",
        "icon": "folder-git-2",
        "current_version": "v1.1",
        "file_name": "BTL_Web_D21CQCN01_A.zip",
        "file_size": "5.4 MB",
        "uploader_name": "TS. Nguyễn Văn An",
        "uploader_id": "u3",
        "uploader_class": "",
        "status": "APPROVED",
        "is_public": False,
        "allowed_classes": ["Lớp D21CQCN01-A"],
        "allowed_departments": ["Khoa Công nghệ thông tin"],
        "downloads": 45,
        "views": 120,
        "submitted_at": "2026-10-10 08:30",
        "reviewed_at": "2026-10-10 09:00",
        "reviewer": "TS. Nguyễn Văn An",
        "reject_reason": "",
        "description": "Đề bài và bộ khung starter template BTL Web dùng Python Reflex. Tài liệu bảo mật nội bộ chỉ dành cho sinh viên Lớp D21CQCN01-A.",
        "tags": ["web", "reflex", "btl", "lop-a"],
        "preview_text": (
            "=== HƯỚNG DẪN BÀI TẬP LỚN LỚP D21CQCN01-A ===\n\n"
            "1. Yêu cầu đồ án:\n"
            "Xây dựng hệ thống học liệu có phân quyền ACL theo lớp và lưu phiên bản tài liệu.\n\n"
            "2. Quy định nộp bài:\n"
            "Nộp mã nguồn kèm tệp hướng dẫn cài đặt và sơ đồ kiến trúc trước tuần 14.\n\n"
            "3. Lưu ý bảo mật:\n"
            "Tài liệu chỉ lưu hành nội bộ lớp D21CQCN01-A."
        ),
        "versions": [
            {
                "version": "v1.1",
                "file_name": "BTL_Web_D21CQCN01_A_v1.1.zip",
                "change_summary": "Bổ sung tiêu chí chấm điểm và deadline nộp bài",
                "uploaded_at": "2026-10-12 14:00",
                "file_size": "5.4 MB",
                "uploader_name": "TS. Nguyễn Văn An",
            },
            {
                "version": "v1.0",
                "file_name": "BTL_Web_D21CQCN01_A_v1.0.zip",
                "change_summary": "Bản phát hành khởi tạo",
                "uploaded_at": "2026-10-10 08:30",
                "file_size": "5.1 MB",
                "uploader_name": "TS. Nguyễn Văn An",
            },
        ],
        "activity_logs": [
            {
                "id": "log_1a",
                "action": "CREATE",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Tạo tài liệu và gán quyền nội bộ Lớp D21CQCN01-A",
                "timestamp": "2026-10-10 08:30",
            },
            {
                "id": "log_1b",
                "action": "CHANGE_PERMISSION",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Thiết lập quyền truy cập giới hạn theo Lớp D21CQCN01-A",
                "timestamp": "2026-10-10 08:35",
            },
            {
                "id": "log_1c",
                "action": "UPDATE",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Tải lên phiên bản cập nhật v1.1",
                "timestamp": "2026-10-12 14:00",
            },
        ],
    },

    # ── Doc 2: Phân quyền CHỈ DÀNH CHO LỚP B (D21CQCN02-B) -> Sinh viên lớp A mở sẽ bị 403 ──
    {
        "id": "doc_acl_class_b",
        "title": "[Lớp B] Tài liệu Thí nghiệm & Lab Cơ sở dữ liệu nâng cao",
        "subject_code": "IT305",
        "subject_name": "Cơ sở dữ liệu",
        "faculty": "CNTT",
        "folder_path": "IT305 / Script SQL / Lab Lớp B",
        "folder_name": "Script SQL",
        "doc_type": "EXERCISE",
        "type_label": "Bài tập thực hành",
        "type_color": "indigo",
        "icon": "database",
        "current_version": "v1.0",
        "file_name": "Lab_CSDL_D21CQCN02_B.pdf",
        "file_size": "3.2 MB",
        "uploader_name": "TS. Nguyễn Văn An",
        "uploader_id": "u3",
        "uploader_class": "",
        "status": "APPROVED",
        "is_public": False,
        "allowed_classes": ["Lớp D21CQCN02-B"],
        "allowed_departments": ["Khoa Công nghệ thông tin"],
        "downloads": 38,
        "views": 95,
        "submitted_at": "2026-10-09 10:15",
        "reviewed_at": "2026-10-09 10:30",
        "reviewer": "TS. Nguyễn Văn An",
        "reject_reason": "",
        "description": "Tài liệu thực hành chuyên sâu về tối ưu Index và Transaction isolation level dành riêng cho Lớp D21CQCN02-B.",
        "tags": ["csdl", "sql", "lab", "lop-b"],
        "preview_text": (
            "=== LAB CSDL NÂNG CAO - DÀNH CHO LỚP D21CQCN02-B ===\n\n"
            "Bài tập nghiên cứu Transaction Isolation Level:\n"
            "• Read Uncommitted (Dirty Read)\n"
            "• Read Committed (Non-repeatable Read)\n"
            "• Repeatable Read (Phantom Read)\n"
            "• Serializable\n\n"
            "Thực hành tạo B-Tree Index trên trường foreign key và đo execution plan."
        ),
        "versions": [
            {
                "version": "v1.0",
                "file_name": "Lab_CSDL_D21CQCN02_B.pdf",
                "change_summary": "Bản phát hành đầu tiên",
                "uploaded_at": "2026-10-09 10:15",
                "file_size": "3.2 MB",
                "uploader_name": "TS. Nguyễn Văn An",
            },
        ],
        "activity_logs": [
            {
                "id": "log_2a",
                "action": "CREATE",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Tạo tài liệu và cấp quyền riêng Lớp D21CQCN02-B",
                "timestamp": "2026-10-09 10:15",
            },
        ],
    },

    # ── Doc 3: Tài liệu Công Khai (PUBLIC) Toàn Trường (Đa Phiên Bản v1.0, v2.0, v2.1) ──
    {
        "id": "doc_public_ctdl",
        "title": "Giáo trình Cấu trúc dữ liệu và giải thuật 2026",
        "subject_code": "IT202",
        "subject_name": "Cấu trúc dữ liệu & GT",
        "faculty": "CNTT",
        "folder_path": "IT202 / Giáo trình / Giáo trình chính thức",
        "folder_name": "Giáo trình",
        "doc_type": "TEXTBOOK",
        "type_label": "Giáo trình",
        "type_color": "blue",
        "icon": "book",
        "current_version": "v2.1",
        "file_name": "GiaoTrinh_CTDL_GT_2026.pdf",
        "file_size": "15.8 MB",
        "uploader_name": "TS. Nguyễn Văn An",
        "uploader_id": "u3",
        "uploader_class": "",
        "status": "APPROVED",
        "is_public": True,
        "allowed_classes": [],
        "allowed_departments": [],
        "downloads": 1240,
        "views": 3150,
        "submitted_at": "2026-09-01 08:00",
        "reviewed_at": "2026-09-01 08:30",
        "reviewer": "TS. Nguyễn Văn An",
        "reject_reason": "",
        "description": "Giáo trình chính thức cập nhật lý thuyết cây AVL, B-Tree, bảng băm và thuật toán đồ thị Dijkstra.",
        "tags": ["ctdl", "python", "giao-trinh", "giai-thuat"],
        "preview_text": (
            "=== GIÁO TRÌNH CẤU TRÚC DỮ LIỆU & GIẢI THUẬT 2026 ===\n\n"
            "Chương 1: Phân tích độ phức tạp thuật toán O(n).\n"
            "Chương 2: Ngăn xếp (Stack) và Hàng đợi (Queue).\n"
            "Chương 3: Cây nhị phân tìm kiếm & Cây AVL tự cân bằng.\n"
            "Chương 4: Thuật toán đồ thị: DFS, BFS, Dijkstra, Kruskal."
        ),
        "versions": [
            {
                "version": "v2.1",
                "file_name": "GiaoTrinh_CTDL_GT_2026_v2.1.pdf",
                "change_summary": "Bổ sung thuật toán cây đỏ đen và bài tập Dijkstra",
                "uploaded_at": "2026-10-12 14:30",
                "file_size": "15.8 MB",
                "uploader_name": "TS. Nguyễn Văn An",
            },
            {
                "version": "v2.0",
                "file_name": "GiaoTrinh_CTDL_GT_2026_v2.0.pdf",
                "change_summary": "Tái cấu trúc toàn diện chương 4 và chương 5",
                "uploaded_at": "2026-09-15 09:15",
                "file_size": "14.2 MB",
                "uploader_name": "TS. Nguyễn Văn An",
            },
            {
                "version": "v1.0",
                "file_name": "GiaoTrinh_CTDL_GT_2026_v1.0.pdf",
                "change_summary": "Bản phát hành đầu tiên",
                "uploaded_at": "2026-09-01 08:00",
                "file_size": "12.0 MB",
                "uploader_name": "TS. Nguyễn Văn An",
            },
        ],
        "activity_logs": [
            {
                "id": "log_3a",
                "action": "CREATE",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Tạo tài liệu giáo trình chính thức",
                "timestamp": "2026-09-01 08:00",
            },
            {
                "id": "log_3b",
                "action": "APPROVE",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Phê duyệt xuất bản công khai toàn học viện",
                "timestamp": "2026-09-01 08:30",
            },
            {
                "id": "log_3c",
                "action": "UPDATE",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Cập nhật phiên bản lớn v2.0",
                "timestamp": "2026-09-15 09:15",
            },
            {
                "id": "log_3d",
                "action": "UPDATE",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Cập nhật phiên bản hiệu chỉnh v2.1",
                "timestamp": "2026-10-12 14:30",
            },
        ],
    },

    # ── Doc 4: Tài liệu ĐANG CHỜ DUYỆT (PENDING) -> Để demo luồng Giảng viên duyệt sang Public ──
    {
        "id": "doc_pending_avl",
        "title": "Slide Tóm tắt Chương 5: Cây nhị phân và Cây AVL",
        "subject_code": "IT202",
        "subject_name": "Cấu trúc dữ liệu & GT",
        "faculty": "CNTT",
        "folder_path": "IT202 / Slide bài giảng / Slide tóm tắt",
        "folder_name": "Slide bài giảng",
        "doc_type": "SLIDE",
        "type_label": "Slide Bài giảng",
        "type_color": "orange",
        "icon": "presentation",
        "current_version": "v1.0",
        "file_name": "IT202_Slide_CayNhiPhan_AVL.pptx",
        "file_size": "6.8 MB",
        "uploader_name": "Lê Hoàng Nam",
        "uploader_id": "u1",
        "uploader_class": "Lớp D21CQCN01-A",
        "status": "PENDING",
        "is_public": False,
        "allowed_classes": [],
        "allowed_departments": [],
        "downloads": 0,
        "views": 15,
        "submitted_at": "2026-10-15 08:30",
        "reviewed_at": "",
        "reviewer": "",
        "reject_reason": "",
        "description": "Em tổng hợp các thao tác xoay đơn LL, RR và xoay kép LR, RL trên cây AVL kèm mã giả thuật toán để các bạn dễ ôn thi.",
        "tags": ["ctdl", "cay-avl", "slide", "it202"],
        "preview_text": (
            "=== CHƯƠNG 5: CÂY NHỊ PHÂN TỰ CÂN BẰNG AVL ===\n\n"
            "Định nghĩa: Hệ số cân bằng BF(v) = height(left) - height(right) ∈ {-1, 0, 1}.\n"
            "Các phép xoay cơ bản:\n"
            "• Xoay đơn LL: Xoay phải tại gốc.\n"
            "• Xoay đơn RR: Xoay trái tại gốc.\n"
            "• Xoay kép LR: Xoay trái tại nút con trái, sau đó xoay phải tại gốc.\n"
            "• Xoay kép RL: Xoay phải tại nút con phải, sau đó xoay trái tại gốc."
        ),
        "versions": [
            {
                "version": "v1.0",
                "file_name": "IT202_Slide_CayNhiPhan_AVL.pptx",
                "change_summary": "Bản đóng góp khởi tạo của sinh viên",
                "uploaded_at": "2026-10-15 08:30",
                "file_size": "6.8 MB",
                "uploader_name": "Lê Hoàng Nam",
            },
        ],
        "activity_logs": [
            {
                "id": "log_4a",
                "action": "CREATE",
                "user_name": "Lê Hoàng Nam",
                "description": "Sinh viên nộp tài liệu vào hàng đợi kiểm duyệt",
                "timestamp": "2026-10-15 08:30",
            },
        ],
    },

    # ── Doc 5: Tài liệu TỪ CHỐI (REJECTED) -> Để demo xem phản hồi và nộp v2.0 ──
    {
        "id": "doc_rejected_sql",
        "title": "Bài tập thực hành SQL nâng cao - Lab 5 & 6",
        "subject_code": "IT305",
        "subject_name": "Cơ sở dữ liệu",
        "faculty": "CNTT",
        "folder_path": "IT305 / Script SQL / Thực hành",
        "folder_name": "Script SQL",
        "doc_type": "EXERCISE",
        "type_label": "Bài tập thực hành",
        "type_color": "red",
        "icon": "database",
        "current_version": "v1.0",
        "file_name": "SQL_Lab5_Lab6_NangCao.zip",
        "file_size": "3.1 MB",
        "uploader_name": "Lê Hoàng Nam",
        "uploader_id": "u1",
        "uploader_class": "Lớp D21CQCN01-A",
        "status": "REJECTED",
        "is_public": False,
        "allowed_classes": [],
        "allowed_departments": [],
        "downloads": 0,
        "views": 8,
        "submitted_at": "2026-10-03 11:10",
        "reviewed_at": "2026-10-04 08:45",
        "reviewer": "TS. Nguyễn Văn An",
        "reject_reason": "Tài liệu bị trùng lặp với bộ Lab có sẵn trong hệ thống. Vui lòng bổ sung bài tập phân tích query execution plan và nộp lại phiên bản v2.0.",
        "description": "Bộ bài tập thực hành SQL nâng cao về Trigger và Stored Procedure.",
        "tags": ["sql", "thực hành", "lab"],
        "preview_text": (
            "=== BÀI TẬP THỰC HÀNH SQL LAB 5 & 6 ===\n\n"
            "Tạo bảng và viết Stored Procedure quản lý đơn hàng."
        ),
        "versions": [
            {
                "version": "v1.0",
                "file_name": "SQL_Lab5_Lab6_NangCao.zip",
                "change_summary": "Bản nộp ban đầu",
                "uploaded_at": "2026-10-03 11:10",
                "file_size": "3.1 MB",
                "uploader_name": "Lê Hoàng Nam",
            },
        ],
        "activity_logs": [
            {
                "id": "log_5a",
                "action": "CREATE",
                "user_name": "Lê Hoàng Nam",
                "description": "Sinh viên nộp tài liệu",
                "timestamp": "2026-10-03 11:10",
            },
            {
                "id": "log_5b",
                "action": "REJECT",
                "user_name": "TS. Nguyễn Văn An",
                "description": "Từ chối duyệt: Yêu cầu bổ sung nội dung và nộp v2.0",
                "timestamp": "2026-10-04 08:45",
            },
        ],
    },
]

# Tự động sinh chuỗi hiển thị tag_str cho toàn bộ tài liệu khởi tạo
for _d in INITIAL_DOCUMENTS:
    if "tag_str" not in _d:
        _d["tag_str"] = "  ".join(f"#{t}" for t in _d.get("tags", []))


# ─── 3. Cấu Trúc Cây Thư Mục Đa Cấp ──────────────────────────────────────────

FOLDER_TREE_DATA: List[Dict[str, Any]] = [
    {
        "id": "fac_cntt",
        "name": "Khoa Công nghệ thông tin",
        "type": "FACULTY",
        "code": "CNTT",
        "children": [
            {
                "id": "sub_it101",
                "name": "IT101 - Nhập môn lập trình",
                "type": "SUBJECT",
                "code": "IT101",
                "children": [
                    {"id": "f_it101_slide", "name": "Slide bài giảng", "type": "FOLDER", "code": "IT101"},
                    {"id": "f_it101_ex", "name": "Bài tập thực hành", "type": "FOLDER", "code": "IT101"},
                    {"id": "f_it101_exam", "name": "Đề thi & Đáp án", "type": "FOLDER", "code": "IT101"},
                ],
            },
            {
                "id": "sub_it202",
                "name": "IT202 - Cấu trúc dữ liệu & GT",
                "type": "SUBJECT",
                "code": "IT202",
                "children": [
                    {"id": "f_it202_text", "name": "Giáo trình", "type": "FOLDER", "code": "IT202"},
                    {"id": "f_it202_slide", "name": "Slide bài giảng", "type": "FOLDER", "code": "IT202"},
                    {"id": "f_it202_btl", "name": "Bài tập lớn", "type": "FOLDER", "code": "IT202"},
                ],
            },
            {
                "id": "sub_it305",
                "name": "IT305 - Cơ sở dữ liệu",
                "type": "SUBJECT",
                "code": "IT305",
                "children": [
                    {"id": "f_it305_slide", "name": "Slide bài giảng", "type": "FOLDER", "code": "IT305"},
                    {"id": "f_it305_sql", "name": "Script SQL", "type": "FOLDER", "code": "IT305"},
                    {"id": "f_it305_exam", "name": "Đề thi & Đáp án", "type": "FOLDER", "code": "IT305"},
                ],
            },
            {
                "id": "sub_it410",
                "name": "IT410 - Lập trình Web",
                "type": "SUBJECT",
                "code": "IT410",
                "children": [
                    {"id": "f_it410_fe", "name": "HTML/CSS/JS", "type": "FOLDER", "code": "IT410"},
                    {"id": "f_it410_be", "name": "Backend Python", "type": "FOLDER", "code": "IT410"},
                    {"id": "f_it410_btl", "name": "Bài tập lớn", "type": "FOLDER", "code": "IT410"},
                ],
            },
        ],
    },
    {
        "id": "fac_kt",
        "name": "Khoa Kinh tế",
        "type": "FACULTY",
        "code": "KT",
        "children": [
            {
                "id": "sub_eco101",
                "name": "ECO101 - Kinh tế vi mô",
                "type": "SUBJECT",
                "code": "ECO101",
                "children": [
                    {"id": "f_eco101_slide", "name": "Slide bài giảng", "type": "FOLDER", "code": "ECO101"},
                    {"id": "f_eco101_ex", "name": "Bài tập kinh tế", "type": "FOLDER", "code": "ECO101"},
                ],
            },
        ],
    },
]


# ─── 4. Global State Reactive Store ──────────────────────────────────────────

class GlobalDocState(rx.State):
    """Trạng thái dùng chung toàn hệ thống DocUni."""

    # ── User Switcher ──
    users: List[Dict[str, Any]] = PRESET_USERS
    current_user_id: str = "u1"  # Mặc định Sinh viên Lê Hoàng Nam (Lớp D21CQCN01-A)

    # ── Danh sách tài liệu động ──
    documents: List[Dict[str, Any]] = INITIAL_DOCUMENTS

    # ── Bộ lọc & Điều hướng cây thư mục ──
    selected_faculty: str = "ALL"
    selected_subject: str = "ALL"
    selected_folder: str = "ALL"
    selected_tag: str = "ALL"
    search_query: str = ""

    # ── Modal Chi tiết & Kiểm tra quyền 403 ──
    detail_modal_open: bool = False
    active_doc: Dict[str, Any] = {}
    
    # ── Modal Cảnh Báo Từ Chối Truy Cập 403 (ACL Demo) ──
    acl_denied_open: bool = False
    acl_denied_doc_title: str = ""
    acl_denied_target_class: str = ""
    acl_denied_current_class: str = ""

    # ── Modal Lịch sử Phiên bản v1.0, v2.0... ──
    version_modal_open: bool = False
    active_version_doc: Dict[str, Any] = {}
    active_version_title: str = ""
    active_version_list: List[Dict[str, str]] = []
    new_version_summary: str = ""

    # ── Modal Nhật ký Hoạt động (Audit Log) ──
    audit_modal_open: bool = False
    active_audit_doc: Dict[str, Any] = {}
    active_audit_title: str = ""
    active_audit_list: List[Dict[str, str]] = []

    # ── Modal Từ chối duyệt (Reject Feedback) ──
    reject_modal_open: bool = False
    rejecting_doc_id: str = ""
    reject_feedback_input: str = ""

    # ── Computed Variables ───────────────────────────────────────────────────

    @rx.var
    def current_user(self) -> Dict[str, Any]:
        for u in self.users:
            if u["id"] == self.current_user_id:
                return u
        return self.users[0]

    @rx.var
    def current_user_name(self) -> str:
        return self.current_user.get("full_name", "")

    @rx.var
    def current_user_role(self) -> str:
        return self.current_user.get("role", "STUDENT")

    @rx.var
    def current_user_class(self) -> str:
        return self.current_user.get("class_name", "")

    @rx.var
    def is_student(self) -> bool:
        return self.current_user_role == "STUDENT"

    @rx.var
    def is_lecturer(self) -> bool:
        return self.current_user_role == "LECTURER"

    @rx.var
    def pending_docs(self) -> List[Dict[str, Any]]:
        """Hàng đợi tài liệu chờ duyệt (Dành cho Giảng viên)."""
        return [d for d in self.documents if d.get("status") == "PENDING"]

    @rx.var
    def pending_count(self) -> int:
        return len(self.pending_docs)

    @rx.var
    def my_contributions(self) -> List[Dict[str, Any]]:
        """Tài liệu sinh viên hiện tại đã đóng góp."""
        uid = self.current_user_id
        return [d for d in self.documents if d.get("uploader_id") == uid]

    @rx.var
    def public_documents(self) -> List[Dict[str, Any]]:
        """Kho học liệu chung: chỉ hiện các tài liệu đã được duyệt (APPROVED)."""
        docs = [d for d in self.documents if d.get("status") == "APPROVED"]
        
        # Lọc theo Khoa
        if self.selected_faculty != "ALL":
            docs = [d for d in docs if d.get("faculty") == self.selected_faculty]
        # Lọc theo Môn học
        if self.selected_subject != "ALL":
            docs = [d for d in docs if d.get("subject_code") == self.selected_subject]
        # Lọc theo Thư mục
        if self.selected_folder != "ALL":
            docs = [d for d in docs if self.selected_folder.lower() in d.get("folder_name", "").lower()]
        # Lọc theo Tag
        if self.selected_tag != "ALL":
            docs = [d for d in docs if self.selected_tag.lower() in [t.lower() for t in d.get("tags", [])]]
        # Lọc theo từ khóa tìm kiếm
        if self.search_query.strip():
            q = self.search_query.strip().lower()
            docs = [
                d for d in docs
                if q in d.get("title", "").lower()
                or q in d.get("subject_code", "").lower()
                or q in d.get("description", "").lower()
                or any(q in t.lower() for t in d.get("tags", []))
            ]
        return docs

    # ── Event Handlers ───────────────────────────────────────────────────────

    def switch_user(self, user_id: str):
        """Chuyển đổi profile người dùng (Demo Lớp A vs Lớp B vs Giảng viên)."""
        self.current_user_id = user_id
        target = self.current_user
        role_label = target.get("role_label", "")
        class_info = f" ({target.get('class_name')})" if target.get("class_name") else ""
        return rx.toast.info(f"Đã chuyển sang: {target.get('full_name')} - {role_label}{class_info}")

    def select_tree_filter(self, filter_type: str, value: str):
        """Lọc tài liệu theo cây thư mục."""
        if filter_type == "FACULTY":
            self.selected_faculty = value
            self.selected_subject = "ALL"
            self.selected_folder = "ALL"
        elif filter_type == "SUBJECT":
            self.selected_subject = value
            self.selected_folder = "ALL"
        elif filter_type == "FOLDER":
            self.selected_folder = value
        elif filter_type == "RESET":
            self.selected_faculty = "ALL"
            self.selected_subject = "ALL"
            self.selected_folder = "ALL"
            self.selected_tag = "ALL"
            self.search_query = ""

    def filter_by_tag(self, tag: str):
        if self.selected_tag == tag:
            self.selected_tag = "ALL"
        else:
            self.selected_tag = tag

    def set_search_query(self, value: str):
        self.search_query = value

    # ── XỬ LÝ PHÂN QUYỀN TRUY CẬP (ACL DEMO LỚP A VS LỚP B) ───────────────────

    def open_document(self, doc_id: str):
        """
        Nghiệp vụ mở tài liệu:
        - Nếu công khai (is_public=True): Cho phép tất cả.
        - Nếu phân quyền riêng (is_public=False):
          + Giảng viên / Admin: Luôn mở được.
          + Sinh viên: Chỉ mở được nếu Lớp của sinh viên nằm trong `allowed_classes`.
          + Nếu không thuộc lớp: Hiển thị Popup 403 Cảnh báo từ chối truy cập!
        """
        doc = next((d for d in self.documents if d["id"] == doc_id), None)
        if not doc:
            return rx.toast.error("Không tìm thấy tài liệu!")

        user = self.current_user
        role = user.get("role", "STUDENT")
        user_class = user.get("class_name", "")
        allowed = doc.get("allowed_classes", [])

        # Kiểm tra điều kiện mở
        has_access = False
        if doc.get("is_public", True):
            has_access = True
        elif role in ["LECTURER", "ADMIN"]:
            has_access = True
        elif user_class and user_class in allowed:
            has_access = True

        if has_access:
            # Ghi nhận lượt xem và audit log
            doc["views"] = doc.get("views", 0) + 1
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            doc.setdefault("activity_logs", []).insert(0, {
                "id": f"log_v_{datetime.now().timestamp()}",
                "action": "VIEW",
                "user_name": user.get("full_name", "Ẩn danh"),
                "description": f"Xem nội dung tài liệu (Quyền: {role})",
                "timestamp": now_str,
            })
            self.active_doc = doc
            self.detail_modal_open = True
        else:
            # 🚫 TỪ CHỐI TRUY CẬP (ACCESS DENIED - 403)
            self.acl_denied_doc_title = doc.get("title", "")
            self.acl_denied_target_class = ", ".join(allowed) if allowed else "Chỉ định bởi Giảng viên"
            self.acl_denied_current_class = user_class if user_class else "Chưa gán lớp"
            self.acl_denied_open = True
            return rx.toast.error(f"Từ chối truy cập (403): Bạn thuộc {user_class}, không có quyền mở tài liệu này!")

    def close_detail_modal(self):
        self.detail_modal_open = False

    def close_acl_denied(self):
        self.acl_denied_open = False

    def download_active_doc(self):
        """Tải tài liệu và ghi nhận audit log."""
        if self.active_doc:
            doc_id = self.active_doc.get("id")
            for d in self.documents:
                if d["id"] == doc_id:
                    d["downloads"] = d.get("downloads", 0) + 1
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    d.setdefault("activity_logs", []).insert(0, {
                        "id": f"log_d_{datetime.now().timestamp()}",
                        "action": "DOWNLOAD",
                        "user_name": self.current_user.get("full_name", ""),
                        "description": f"Tải xuống tệp {d.get('file_name')}",
                        "timestamp": now_str,
                    })
                    self.active_doc = dict(d)
                    break
            return [
                rx.download(url=f"/_upload/{self.active_doc.get('file_name')}"),
                rx.toast.success(f"Đã bắt đầu tải tệp: {self.active_doc.get('file_name')}"),
            ]

    # ── XỬ LÝ QUY TRÌNH DUYỆT (TASK 3: APPROVAL WORKFLOW) ─────────────────────

    def approve_document(self, doc_id: str):
        """Giảng viên phê duyệt tài liệu $\to$ Lập tức chuyển sang công khai."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        lecturer_name = self.current_user.get("full_name", "TS. Nguyễn Văn An")

        updated = []
        found_title = ""
        for d in self.documents:
            if d["id"] == doc_id:
                d["status"] = "APPROVED"
                d["is_public"] = True
                d["reviewer"] = lecturer_name
                d["reviewed_at"] = now_str
                d["reject_reason"] = ""
                d.setdefault("activity_logs", []).insert(0, {
                    "id": f"log_app_{datetime.now().timestamp()}",
                    "action": "APPROVE",
                    "user_name": lecturer_name,
                    "description": "Giảng viên phê duyệt và xuất bản công khai tài liệu",
                    "timestamp": now_str,
                })
                found_title = d.get("title", "")
            updated.append(d)

        self.documents = updated
        return rx.toast.success(f"Đã duyệt thành công: '{found_title}' hiện đã được xuất bản công khai!")

    def open_reject_modal(self, doc_id: str):
        self.rejecting_doc_id = doc_id
        self.reject_feedback_input = ""
        self.reject_modal_open = True

    def close_reject_modal(self):
        self.reject_modal_open = False
        self.rejecting_doc_id = ""

    def set_reject_feedback(self, value: str):
        self.reject_feedback_input = value

    def confirm_reject_document(self):
        """Giảng viên từ chối tài liệu kèm lý do phản hồi."""
        if not self.reject_feedback_input.strip():
            return rx.toast.error("Vui lòng nhập lý do từ chối để sinh viên biết cần chỉnh sửa gì!")

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        lecturer_name = self.current_user.get("full_name", "TS. Nguyễn Văn An")
        doc_id = self.rejecting_doc_id

        updated = []
        for d in self.documents:
            if d["id"] == doc_id:
                d["status"] = "REJECTED"
                d["is_public"] = False
                d["reviewer"] = lecturer_name
                d["reviewed_at"] = now_str
                d["reject_reason"] = self.reject_feedback_input.strip()
                d.setdefault("activity_logs", []).insert(0, {
                    "id": f"log_rej_{datetime.now().timestamp()}",
                    "action": "REJECT",
                    "user_name": lecturer_name,
                    "description": f"Từ chối duyệt: {self.reject_feedback_input.strip()}",
                    "timestamp": now_str,
                })
            updated.append(d)

        self.documents = updated
        self.reject_modal_open = False
        self.rejecting_doc_id = ""
        return rx.toast.warning("Đã gửi phản hồi từ chối tài liệu về cho sinh viên.")

    # ── XỬ LÝ QUẢN LÝ PHIÊN BẢN (TASK 3: VERSIONING) ───────────────────────────

    def open_version_modal(self, doc_id: str):
        doc = next((d for d in self.documents if d["id"] == doc_id), None)
        if doc:
            self.active_version_doc = doc
            self.active_version_title = doc.get("title", "")
            self.active_version_list = [
                {
                    "version": str(v.get("version", "")),
                    "file_name": str(v.get("file_name", "")),
                    "change_summary": str(v.get("change_summary", "")),
                    "uploaded_at": str(v.get("uploaded_at", "")),
                    "file_size": str(v.get("file_size", "")),
                    "uploader_name": str(v.get("uploader_name", "")),
                }
                for v in doc.get("versions", [])
            ]
            self.new_version_summary = ""
            self.version_modal_open = True

    def close_version_modal(self):
        self.version_modal_open = False

    def download_version_file(self, file_name: str):
        return [
            rx.download(url=f"/_upload/{file_name}"),
            rx.toast.info(f"Đang chuẩn bị tải về phiên bản: {file_name}"),
        ]

    def set_new_version_summary(self, value: str):
        self.new_version_summary = value

    def submit_new_version(self):
        """Nộp phiên bản nâng cấp (v2.0, v2.1...)."""
        if not self.new_version_summary.strip():
            return rx.toast.error("Vui lòng nhập tóm tắt nội dung thay đổi của phiên bản mới!")

        doc_id = self.active_version_doc.get("id")
        user = self.current_user
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        updated = []
        new_v_label = "v2.0"
        for d in self.documents:
            if d["id"] == doc_id:
                # Tính version tiếp theo
                cur = d.get("current_version", "v1.0").replace("v", "")
                try:
                    next_v = f"v{float(cur) + 1.0:.1f}"
                except Exception:
                    next_v = "v2.0"
                new_v_label = next_v

                new_file_name = f"{d.get('subject_code')}_CapNhat_{new_v_label}.pdf"
                new_ver_item = {
                    "version": new_v_label,
                    "file_name": new_file_name,
                    "change_summary": self.new_version_summary.strip(),
                    "uploaded_at": now_str,
                    "file_size": "8.5 MB",
                    "uploader_name": user.get("full_name", ""),
                }
                d.setdefault("versions", []).insert(0, new_ver_item)
                d["current_version"] = new_v_label
                d["file_name"] = new_file_name
                # Nếu là sinh viên nộp lại bản v2.0 sau khi bị từ chối -> Đưa lại vào PENDING
                if user.get("role") == "STUDENT":
                    d["status"] = "PENDING"
                    d["is_public"] = False
                    d["reject_reason"] = ""
                d.setdefault("activity_logs", []).insert(0, {
                    "id": f"log_up_{datetime.now().timestamp()}",
                    "action": "UPDATE",
                    "user_name": user.get("full_name", ""),
                    "description": f"Phát hành phiên bản mới {new_v_label}: {self.new_version_summary.strip()}",
                    "timestamp": now_str,
                })
                self.active_version_doc = dict(d)
                self.active_version_list = [
                    {
                        "version": str(v.get("version", "")),
                        "file_name": str(v.get("file_name", "")),
                        "change_summary": str(v.get("change_summary", "")),
                        "uploaded_at": str(v.get("uploaded_at", "")),
                        "file_size": str(v.get("file_size", "")),
                        "uploader_name": str(v.get("uploader_name", "")),
                    }
                    for v in d.get("versions", [])
                ]
            updated.append(d)

        self.documents = updated
        self.version_modal_open = False
        return rx.toast.success(f"Đã tải lên phiên bản mới {new_v_label} thành công!")

    # ── XỬ LÝ NHẬT KÝ KIỂM TOÁN (TASK 3: AUDIT LOGS) ──────────────────────────

    def open_audit_modal(self, doc_id: str):
        doc = next((d for d in self.documents if d["id"] == doc_id), None)
        if doc:
            self.active_audit_doc = doc
            self.active_audit_title = doc.get("title", "")
            self.active_audit_list = [
                {
                    "id": str(l.get("id", "")),
                    "action": str(l.get("action", "")),
                    "user_name": str(l.get("user_name", "")),
                    "description": str(l.get("description", "")),
                    "timestamp": str(l.get("timestamp", "")),
                }
                for l in doc.get("activity_logs", [])
            ]
            self.audit_modal_open = True

    def close_audit_modal(self):
        self.audit_modal_open = False

    # ── ĐÓNG GÓP TÀI LIỆU MỚI (TASK 2 UPLOAD & TASK 3 PENDING) ─────────────────

    def add_contribution(
        self,
        title: str,
        subject_code: str,
        folder_name: str,
        doc_type: str,
        tags: List[str],
        file_name: str,
        description: str,
        is_public: bool = True,
        allowed_class: str = "",
        file_size: str = "4.5 MB",
        file_url: str = "",
    ):
        """Sinh viên nộp tài liệu mới $\to$ Tạo bản ghi PENDING vào hàng đợi duyệt."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        user = self.current_user
        doc_id = f"doc_{int(datetime.now().timestamp())}"

        allowed_classes = [allowed_class] if allowed_class else []
        actual_fname = file_name if file_name else f"{subject_code}_TaiLieu_v1.pdf"
        actual_furl = file_url if file_url else f"/_upload/{actual_fname}"

        new_doc = {
            "id": doc_id,
            "title": title.strip(),
            "subject_code": subject_code,
            "subject_name": f"Môn học {subject_code}",
            "faculty": "CNTT",
            "folder_path": f"{subject_code} / {folder_name}",
            "folder_name": folder_name,
            "doc_type": doc_type,
            "type_label": "Tài liệu",
            "type_color": "blue",
            "icon": "file-text",
            "current_version": "v1.0",
            "file_name": actual_fname,
            "file_size": file_size if file_size else "4.5 MB",
            "file_url": actual_furl,
            "uploader_name": user.get("full_name", "Sinh viên"),
            "uploader_id": user.get("id", "u1"),
            "uploader_class": user.get("class_name", ""),
            "status": "PENDING",  # Mặc định Chờ duyệt
            "is_public": is_public,
            "allowed_classes": allowed_classes,
            "allowed_departments": ["Khoa Công nghệ thông tin"],
            "downloads": 0,
            "views": 0,
            "submitted_at": now_str,
            "reviewed_at": "",
            "reviewer": "",
            "reject_reason": "",
            "description": description.strip(),
            "tags": tags if tags else ["tai-lieu-moi"],
            "tag_str": "  ".join(f"#{t}" for t in (tags if tags else ["tai-lieu-moi"])),
            "preview_text": f"=== NỘI DUNG TÀI LIỆU: {title.strip()} ===\nTài liệu đóng góp bởi {user.get('full_name')}.",
            "versions": [
                {
                    "version": "v1.0",
                    "file_name": actual_fname,
                    "change_summary": "Bản đóng góp ban đầu của sinh viên",
                    "uploaded_at": now_str,
                    "file_size": file_size if file_size else "4.5 MB",
                    "file_url": actual_furl,
                    "uploader_name": user.get("full_name", ""),
                }
            ],
            "activity_logs": [
                {
                    "id": f"log_cr_{datetime.now().timestamp()}",
                    "action": "CREATE",
                    "user_name": user.get("full_name", ""),
                    "description": "Đóng góp tài liệu mới vào hàng đợi phê duyệt",
                    "timestamp": now_str,
                }
            ],
        }

        self.documents.insert(0, new_doc)
        return rx.toast.success("Tài liệu đã được gửi thành công! Đang chờ Giảng viên phê duyệt.")
