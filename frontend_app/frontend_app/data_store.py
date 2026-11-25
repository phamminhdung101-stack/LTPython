"""
DocUni - Centralized Data Store & State Management (Reflex Full-Stack)
Hạt nhân lưu trữ và điều phối dữ liệu chung cho Task 2 (Folder Tree, Upload, ACL)
và Task 3 (Versioning, Tagging, Approval Workflow, Audit Logs).
"""

from datetime import datetime
from typing import List, Dict, Any
import reflex as rx


def trigger_browser_download(url: str, filename: str = "") -> rx.event.EventSpec:
    """Kích hoạt tải file từ trình duyệt, tương thích hoàn toàn với URL tuyệt đối và tránh lỗi của rx.download.
    
    Tránh lỗi: 'ValueError: The URL argument should start with a /'
    Đảm bảo file nhị phân nguyên vẹn được trình duyệt tải trực tiếp từ Django FileResponse.
    """
    import json
    safe_url = json.dumps(url)
    safe_name = json.dumps(filename) if filename else '""'
    script = (
        f"(() => {{ "
        f"const link = document.createElement('a'); "
        f"link.href = {safe_url}; "
        f"if ({safe_name}) {{ link.setAttribute('download', {safe_name}); }} "
        f"link.style.display = 'none'; "
        f"document.body.appendChild(link); "
        f"link.click(); "
        f"setTimeout(() => link.remove(), 1000); "
        f"}})();"
    )
    return rx.call_script(script)



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
        "department": "Cong nghe thong tin",
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
        "department": "Cong nghe thong tin",
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
        "department": "Cong nghe thong tin",
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
        "department": "Cong nghe thong tin",
        "avatar_color": "gray",
    },
]


# ─── 2. Dữ Liệu Khởi Tạo Tài Liệu Đầy Đủ Phân Quyền & Phiên Bản ───────────────

INITIAL_DOCUMENTS: List[Dict[str, Any]] = [
    # ── Doc 1: Phân quyền CHỈ DÀNH CHO LỚP A (D21CQCN01-A) -> Sinh viên lớp B mở sẽ bị 403 ──
    {
        "id": "doc_acl_class_a",
        "title": "[Lớp A] Đề cương & Mã nguồn BTL Lập trình Web Full-Stack",
        "subject_code": "Lap trinh Java",
        "subject_name": "Lap trinh Java",
        "faculty": "Cong nghe thong tin",
        "folder_path": "Lap trinh Java / Bai tap",
        "folder_name": "Bai tap",
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
        "allowed_departments": ["Cong nghe thong tin"],
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
        "subject_code": "Co so du lieu",
        "subject_name": "Co so du lieu",
        "faculty": "Cong nghe thong tin",
        "folder_path": "Co so du lieu / Bai giang",
        "folder_name": "Bai giang",
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
        "allowed_departments": ["Cong nghe thong tin"],
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
        "title": "Giáo trình Mạng máy tính và truyền thông dữ liệu 2026",
        "subject_code": "Mang may tinh",
        "subject_name": "Mang may tinh",
        "faculty": "Cong nghe thong tin",
        "folder_path": "Mang may tinh / Bai giang",
        "folder_name": "Bai giang",
        "doc_type": "TEXTBOOK",
        "type_label": "Giáo trình",
        "type_color": "blue",
        "icon": "book",
        "current_version": "v2.1",
        "file_name": "GiaoTrinh_MangMayTinh_2026.pdf",
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
        "description": "Giáo trình chính thức cập nhật lý thuyết mô hình OSI, giao thức TCP/IP và định tuyến mạng.",
        "tags": ["mang", "tcp-ip", "giao-trinh"],
        "preview_text": (
            "=== GIÁO TRÌNH MẠNG MÁY TÍNH & TRUYỀN THÔNG DỮ LIỆU ===\n\n"
            "Chương 1: Tổng quan về mạng máy tính và Internet.\n"
            "Chương 2: Tầng ứng dụng (Application Layer): HTTP, DNS, SMTP.\n"
            "Chương 3: Tầng giao vận (Transport Layer): TCP và UDP.\n"
            "Chương 4: Tầng mạng (Network Layer): Định tuyến IP, OSPF, BGP."
        ),
        "versions": [
            {
                "version": "v2.1",
                "file_name": "GiaoTrinh_MangMayTinh_2026_v2.1.pdf",
                "change_summary": "Bổ sung giao thức định tuyến OSPF và bài tập Wireshark",
                "uploaded_at": "2026-10-12 14:30",
                "file_size": "15.8 MB",
                "uploader_name": "TS. Nguyễn Văn An",
            },
            {
                "version": "v2.0",
                "file_name": "GiaoTrinh_MangMayTinh_2026_v2.0.pdf",
                "change_summary": "Tái cấu trúc toàn diện chương 4 và chương 5",
                "uploaded_at": "2026-09-15 09:15",
                "file_size": "14.2 MB",
                "uploader_name": "TS. Nguyễn Văn An",
            },
            {
                "version": "v1.0",
                "file_name": "GiaoTrinh_MangMayTinh_2026_v1.0.pdf",
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
        "title": "Slide Bài giảng Kinh tế vi mô Chương 1-5",
        "subject_code": "Kinh te vi mo",
        "subject_name": "Kinh te vi mo",
        "faculty": "Kinh te",
        "folder_path": "Kinh te vi mo / Bai giang",
        "folder_name": "Bai giang",
        "doc_type": "SLIDE",
        "type_label": "Slide Bài giảng",
        "type_color": "orange",
        "icon": "presentation",
        "current_version": "v1.0",
        "file_name": "KinhTeViMo_Slide_Chuong1_5.pptx",
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
        "description": "Tổng hợp lý thuyết cung cầu, độ co giãn và hành vi người tiêu dùng môn Kinh tế vi mô.",
        "tags": ["kinh-te", "vi-mo", "slide"],
        "preview_text": (
            "=== CHƯƠNG 1: TỔNG QUAN VỀ KINH TẾ VI MÔ ===\n\n"
            "Quy luật Cung - Cầu và Điểm cân bằng thị trường.\n"
            "Độ co giãn của cầu theo giá và thu nhập."
        ),
        "versions": [
            {
                "version": "v1.0",
                "file_name": "KinhTeViMo_Slide_Chuong1_5.pptx",
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
        "title": "Tài liệu tham khảo Kế toán đại cương cho người mới bắt đầu",
        "subject_code": "Ke toan dai cuong",
        "subject_name": "Ke toan dai cuong",
        "faculty": "Kinh te",
        "folder_path": "Ke toan dai cuong / Tai lieu tham khao",
        "folder_name": "Tai lieu tham khao",
        "doc_type": "REFERENCE",
        "type_label": "Tài liệu tham khảo",
        "type_color": "red",
        "icon": "database",
        "current_version": "v1.0",
        "file_name": "KeToanDaiCuong_ThamKhao.zip",
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
        "reject_reason": "Tài liệu bị thiếu phần định khoản kế toán. Vui lòng bổ sung bài tập định khoản và nộp lại phiên bản v2.0.",
        "description": "Tài liệu hệ thống hóa nguyên lý kế toán và bài tập định khoản.",
        "tags": ["ke-toan", "nguyen-ly", "tham-khao"],
        "preview_text": (
            "=== NGUYÊN LÝ KẾ TOÁN ĐẠI CƯƠNG ===\n\n"
            "Phương trình kế toán: Tài sản = Nợ phải trả + Vốn chủ sở hữu."
        ),
        "versions": [
            {
                "version": "v1.0",
                "file_name": "KeToanDaiCuong_ThamKhao.zip",
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


# ─── 3. Cấu Trúc Cây Thư Mục Đa Cấp Từ PostgreSQL Database ────────────────────

def build_db_folder_tree() -> List[Dict[str, Any]]:
    """Xây dựng Cây thư mục học liệu phân cấp đa tầng trực tiếp từ PostgreSQL."""
    try:
        import httpx
        r_d = httpx.get("http://127.0.0.1:8000/api/departments/", timeout=2.0)
        r_s = httpx.get("http://127.0.0.1:8000/api/subjects/", timeout=2.0)
        r_f = httpx.get("http://127.0.0.1:8000/api/folders/", timeout=2.0)
        if r_d.status_code == 200 and r_s.status_code == 200:
            depts = r_d.json().get("departments") or r_d.json().get("data") or []
            subs = r_s.json().get("subjects") or r_s.json().get("data") or []
            folders = r_f.json().get("folders") or r_f.json().get("data") or [] if r_f.status_code == 200 else []

            tree = []
            for d in depts:
                d_id = d.get("id") or d.get("department_id")
                d_name = d.get("department_name")
                d_subs = [s for s in subs if str(s.get("department_id")) == str(d_id)]
                sub_nodes = []
                for s in d_subs:
                    s_id = s.get("id") or s.get("subject_id")
                    s_name = s.get("subject_name")
                    s_folders = [f for f in folders if str(f.get("subject_id")) == str(s_id)]
                    folder_nodes = [
                        {
                            "id": f"f_{f.get('id') or f.get('folder_id')}",
                            "name": f.get("folder_name"),
                            "type": "FOLDER",
                            "code": s_name,
                        }
                        for f in s_folders
                    ]
                    if not folder_nodes:
                        folder_nodes = [{"id": f"f_default_{s_id}", "name": "Tài liệu chung", "type": "FOLDER", "code": s_name}]
                    sub_nodes.append({
                        "id": f"sub_{s_id}",
                        "name": s_name,
                        "type": "SUBJECT",
                        "code": s_name,
                        "children": folder_nodes,
                    })
                tree.append({
                    "id": f"fac_{d_id}",
                    "name": d_name,
                    "type": "FACULTY",
                    "code": d_name,
                    "children": sub_nodes,
                })
            if tree:
                return tree
    except Exception:
        pass

    try:
        from academics.models import Department
        tree = []
        for d in Department.objects.prefetch_related('subjects__folders').order_by('department_name'):
            sub_nodes = []
            for s in d.subjects.all().order_by('subject_name'):
                folder_nodes = [
                    {
                        "id": f"f_{f.id}",
                        "name": f.folder_name,
                        "type": "FOLDER",
                        "code": s.subject_name,
                    }
                    for f in s.folders.all().order_by('folder_name')
                ]
                if not folder_nodes:
                    folder_nodes = [{"id": f"f_default_{s.id}", "name": "Tài liệu chung", "type": "FOLDER", "code": s.subject_name}]
                sub_nodes.append({
                    "id": f"sub_{s.id}",
                    "name": s.subject_name,
                    "type": "SUBJECT",
                    "code": s.subject_name,
                    "children": folder_nodes,
                })
            tree.append({
                "id": f"fac_{d.id}",
                "name": d.department_name,
                "type": "FACULTY",
                "code": d.department_name,
                "children": sub_nodes,
            })
        if tree:
            return tree
    except Exception:
        pass

    return []

FOLDER_TREE_DATA: List[Dict[str, Any]] = build_db_folder_tree()


# ─── 4. Global State Reactive Store ──────────────────────────────────────────

class GlobalDocState(rx.State):
    """Trạng thái dùng chung toàn hệ thống DocUni."""

    # ── User Switcher ──
    users: List[Dict[str, Any]] = PRESET_USERS
    current_user_id: str = "u1"  # Mặc định Sinh viên Lê Hoàng Nam (Lớp D21CQCN01-A)

    # ── Danh sách tài liệu động (Chỉ lấy từ PostgreSQL qua API/ORM, mặc định rỗng) ──
    documents: List[Dict[str, Any]] = []
    is_loading: bool = False
    load_error: str = ""

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

    async def load_documents(self):
        """Tải toàn bộ tài liệu thực tế từ cơ sở dữ liệu PostgreSQL qua Django API / ORM."""
        self.is_loading = True
        self.load_error = ""
        api_error_detail = ""

        # 1. Nạp từ REST API Backend
        try:
            import httpx
            token = ""
            try:
                from .auth import AuthState
                auth = await self.get_state(AuthState)
                if auth and auth.is_logged_in:
                    token = getattr(auth, 'auth_token', '')
            except Exception:
                pass

            headers = {"Authorization": f"Bearer {token}"} if token else {}
            resp = httpx.get("http://127.0.0.1:8000/api/documents/", headers=headers, timeout=4.0)
            if resp.status_code == 200:
                raw_docs = resp.json().get("documents") or resp.json().get("data") or []
                loaded = []
                for d in raw_docs:
                    d_id = str(d.get("id") or d.get("document_id"))
                    title = d.get("title", "")
                    s_name = d.get("subject_name") or d.get("subject", {}).get("subject_name", "")
                    dept_name = d.get("department_name") or "Cong nghe thong tin"
                    status = str(d.get("status") or "APPROVED").upper()
                    u_name = d.get("uploader_name") or "DocUni"
                    created = str(d.get("created_at") or "")[:16]
                    fname = d.get("file_name") or f"document_{d_id}.pdf"
                    fsize = f"{round(float(d.get('file_size', 2097152)) / (1024*1024), 1)} MB"
                    f_name = d.get("folder_name") or "Tài liệu chung"
                    tags_list = d.get("tags") or ["học liệu", "docuni"]
                    tag_str = "  ".join(f"#{t}" for t in tags_list)
                    allowed_classes = d.get("allowed_classes") or []
                    allowed_depts = d.get("allowed_departments") or []
                    matched_snippet = str(d.get("matched_snippet") or "")
                    is_public = bool(d.get("is_public", True))

                    loaded.append({
                        "id": d_id,
                        "title": title,
                        "subject_code": s_name,
                        "subject_name": s_name,
                        "faculty": dept_name,
                        "folder_path": f"{s_name} / {f_name}",
                        "folder_name": f_name,
                        "doc_type": "TEXTBOOK",
                        "type_label": "Học liệu",
                        "type_color": "blue",
                        "icon": "file-text",
                        "current_version": str(d.get("latest_version") or "v1.0"),
                        "file_name": fname,
                        "file_size": fsize,
                        "uploader_name": u_name,
                        "uploader_id": str(d.get("uploader_id") or "1"),
                        "uploader_class": "Lớp D21CQCN01-A",
                        "status": status,
                        "is_public": is_public,
                        "allowed_classes": allowed_classes,
                        "allowed_departments": allowed_depts,
                        "downloads": int(d.get("download_count", 0)),
                        "views": int(d.get("view_count", 0)),
                        "submitted_at": created,
                        "reviewed_at": created,
                        "reviewer": "TS. Nguyễn Văn An",
                        "reject_reason": str(d.get("reject_reason") or ""),
                        "description": d.get("description") or f"Tài liệu môn học {s_name}",
                        "tags": tags_list,
                        "tag_str": tag_str,
                        "preview_text": d.get("description") or title,
                        "matched_snippet": matched_snippet,
                        "versions": [{"version": str(d.get("latest_version") or "v1.0"), "file_name": fname, "change_summary": "Bản khởi tạo", "uploaded_at": created, "file_size": fsize, "uploader_name": u_name}],
                        "activity_logs": [{"id": f"log_{d_id}", "action": "CREATE", "user_name": u_name, "description": "Tải lên học liệu", "timestamp": created}],
                    })
                self.documents = loaded
                self.is_loading = False
                self.load_error = ""
                return
            else:
                api_error_detail = f"API trả về mã trạng thái {resp.status_code}"
        except Exception as e:
            api_error_detail = str(e)

        # 2. Dự phòng trực tiếp qua Django ORM với cơ sở dữ liệu PostgreSQL
        try:
            import os, sys, asyncio
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
            if backend_dir not in sys.path:
                sys.path.insert(0, backend_dir)
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            import django
            django.setup()

            auth_user_id = None
            auth_role = None
            try:
                from .auth import AuthState
                auth = await self.get_state(AuthState)
                if auth and auth.is_logged_in:
                    auth_user_id = auth.current_user_id
                    auth_role = auth.current_user_role
            except Exception:
                pass

            def _fetch_from_orm(u_id, r_name):
                from documents.models import Document as DjDoc
                from permissions.models import DocumentPermission
                from django.db.models import Q
                from accounts.models import User as DjUser

                qs = DjDoc.objects.select_related('subject', 'subject__department', 'folder', 'uploader').prefetch_related(
                    'versions', 'permissions__student_class', 'permissions__department', 'tags', 'activity_logs'
                ).all().order_by('-id')

                # Phân quyền theo vai trò
                is_staff = r_name in ("ADMIN", "LECTURER")
                if not is_staff:
                    if u_id:
                        u_obj = DjUser.objects.filter(id=u_id).first()
                        perm_q = Q(permission_type=DocumentPermission.USER, user_id=u_id, can_view=True)
                        if u_obj and u_obj.student_class_id:
                            perm_q |= Q(permission_type=DocumentPermission.CLASS, student_class_id=u_obj.student_class_id, can_view=True)
                        if u_obj and u_obj.department_id:
                            perm_q |= Q(permission_type=DocumentPermission.DEPARTMENT, department_id=u_obj.department_id, can_view=True)
                        permitted_ids = set(DocumentPermission.objects.filter(perm_q).values_list('document_id', flat=True))

                        qs = qs.filter(
                            Q(status=DjDoc.APPROVED, is_public=True) |
                            Q(status=DjDoc.APPROVED, id__in=permitted_ids)
                        ).distinct()
                    else:
                        qs = qs.filter(status=DjDoc.APPROVED, is_public=True)

                loaded_docs = []
                for d in qs:
                    d_id = str(d.id)
                    s_name = d.subject.subject_name if d.subject else "Tài liệu chung"
                    dept_name = d.subject.department.department_name if (d.subject and d.subject.department) else "Cong nghe thong tin"
                    f_name = d.folder.folder_name if d.folder else "Tài liệu chung"
                    status = str(d.status).upper()
                    u_name = d.uploader.full_name if (d.uploader and hasattr(d.uploader, 'full_name') and d.uploader.full_name) else (d.uploader.username if d.uploader else "DocUni")
                    created = d.created_at.strftime('%Y-%m-%d %H:%M') if d.created_at else ""

                    latest_ver = d.latest_version
                    str_file = str(latest_ver.file) if (latest_ver and latest_ver.file) else ""
                    fname = os.path.basename(str_file) if str_file else f"document_{d_id}.pdf"
                    fsize = "2.0 MB"

                    tags_list = [t.tag_name for t in d.tags.all()] if hasattr(d, 'tags') else ["học liệu"]
                    if not tags_list:
                        tags_list = ["học liệu", "docuni"]
                    tag_str = "  ".join(f"#{t}" for t in tags_list)

                    doc_perms = [p for p in d.permissions.all() if p.can_view]
                    allowed_classes = [p.student_class.class_name for p in doc_perms if p.student_class]
                    allowed_departments = [p.department.department_name for p in doc_perms if p.department]

                    versions_list = []
                    for v in d.versions.all():
                        v_str = str(v.file) if v.file else ""
                        v_fname = os.path.basename(v_str) if v_str else fname
                        v_user = v.updated_by.full_name if (v.updated_by and hasattr(v.updated_by, 'full_name') and v.updated_by.full_name) else (v.updated_by.username if v.updated_by else u_name)
                        versions_list.append({
                            "version": f"v{v.version_number}.0",
                            "file_name": v_fname,
                            "change_summary": v.change_summary or "Bản cập nhật",
                            "uploaded_at": v.updated_at.strftime('%Y-%m-%d %H:%M') if v.updated_at else created,
                            "file_size": fsize,
                            "uploader_name": v_user,
                        })
                    if not versions_list:
                        versions_list = [{"version": "v1.0", "file_name": fname, "change_summary": "Bản khởi tạo", "uploaded_at": created, "file_size": fsize, "uploader_name": u_name}]

                    act_list = []
                    for log in d.activity_logs.all():
                        log_u = log.user.full_name if (log.user and hasattr(log.user, 'full_name') and log.user.full_name) else (log.user.username if log.user else "Hệ thống")
                        act_list.append({
                            "id": f"log_{log.id}",
                            "action": log.action,
                            "user_name": log_u,
                            "description": log.description or "",
                            "timestamp": log.created_at.strftime('%Y-%m-%d %H:%M') if log.created_at else created,
                        })
                    if not act_list:
                        act_list = [{"id": f"log_{d_id}", "action": "CREATE", "user_name": u_name, "description": "Tải lên học liệu", "timestamp": created}]

                    reject_reason = ""
                    if d.status == 'REJECTED':
                        rej_log = next((l for l in d.activity_logs.all() if l.action == 'REJECT'), None)
                        if rej_log and rej_log.description:
                            desc = rej_log.description
                            reject_reason = desc.replace('Từ chối duyệt: ', '').strip() if desc.startswith('Từ chối duyệt: ') else desc

                    loaded_docs.append({
                        "id": d_id,
                        "title": d.title,
                        "subject_code": s_name,
                        "subject_name": s_name,
                        "faculty": dept_name,
                        "folder_path": f"{s_name} / {f_name}",
                        "folder_name": f_name,
                        "doc_type": "TEXTBOOK",
                        "type_label": "Học liệu",
                        "type_color": "blue",
                        "icon": "file-text",
                        "current_version": f"v{latest_ver.version_number}.0" if latest_ver else "v1.0",
                        "file_name": fname,
                        "file_size": fsize,
                        "uploader_name": u_name,
                        "uploader_id": str(d.uploader_id or "1"),
                        "uploader_class": "Lớp D21CQCN01-A",
                        "status": status,
                        "is_public": bool(d.is_public),
                        "allowed_classes": allowed_classes,
                        "allowed_departments": allowed_departments,
                        "downloads": int(d.download_count or 0),
                        "views": int(d.view_count or 0),
                        "submitted_at": created,
                        "reviewed_at": created,
                        "reviewer": "TS. Nguyễn Văn An",
                        "reject_reason": reject_reason,
                        "description": d.description or f"Tài liệu môn học {s_name}",
                        "tags": tags_list,
                        "tag_str": tag_str,
                        "preview_text": d.description or d.title,
                        "matched_snippet": "",
                        "versions": versions_list,
                        "activity_logs": act_list,
                    })
                return loaded_docs

            self.documents = await asyncio.to_thread(_fetch_from_orm, auth_user_id, auth_role)
            self.is_loading = False
            self.load_error = ""
            return
        except Exception as exc:
            # Cả API lẫn ORM đều gặp lỗi -> Tuyệt đối không hiển thị INITIAL_DOCUMENTS hoặc mock data
            self.documents = []
            self.is_loading = False
            self.load_error = f"Không thể tải dữ liệu từ PostgreSQL qua API backend ({api_error_detail or str(exc)}). Vui lòng kiểm tra kết nối hệ thống."

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
    def total_downloads_count(self) -> int:
        return sum(int(d.get("downloads", 0)) for d in self.documents)

    @rx.var
    def recent_approved_docs(self) -> List[Dict[str, Any]]:
        """Lấy 4 tài liệu đã duyệt mới nhất để hiển thị tại trang chủ sinh viên."""
        approved = [d for d in self.documents if d.get("status") == "APPROVED"]
        return approved[:4]

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
          + Sinh viên: Chỉ mở được nếu Lớp / Khoa của sinh viên nằm trong danh sách cấp quyền hoặc là tác giả.
          + Nếu không thuộc quyền: Hiển thị Popup 403 Cảnh báo từ chối truy cập!
        """
        doc = next((d for d in self.documents if str(d.get("id")) == str(doc_id)), None)
        if not doc:
            return rx.toast.error("Không tìm thấy tài liệu!")

        user = self.current_user
        role = getattr(self, "current_user_role", "") or user.get("role", "STUDENT")
        user_name = getattr(self, "current_user_name", "") or user.get("full_name", "")
        user_class = user.get("class_name", "")
        user_dept = user.get("department", "")
        current_uid = str(user.get("id", ""))
        uploader_id = str(doc.get("uploader_id", ""))

        allowed = doc.get("allowed_classes", [])
        allowed_depts = doc.get("allowed_departments", [])

        # Kiểm tra điều kiện mở
        has_access = False
        if doc.get("is_public", True):
            has_access = True
        elif role in ["LECTURER", "ADMIN"]:
            has_access = True
        elif current_uid and current_uid == uploader_id:
            has_access = True
        elif user_class and user_class in allowed:
            has_access = True
        elif not allowed and user_dept and user_dept in allowed_depts:
            has_access = True

        if has_access:
            # Ghi nhận lượt xem và audit log
            doc["views"] = doc.get("views", 0) + 1
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            doc.setdefault("activity_logs", []).insert(0, {
                "id": f"log_v_{datetime.now().timestamp()}",
                "action": "VIEW",
                "user_name": user_name,
                "description": f"Xem nội dung tài liệu (Quyền: {role})",
                "timestamp": now_str,
            })
            self.active_doc = doc
            self.detail_modal_open = True
            self.acl_denied_open = False
        else:
            # 🚫 TỪ CHỐI TRUY CẬP (ACCESS DENIED - 403)
            self.detail_modal_open = False
            self.acl_denied_doc_title = doc.get("title", "")
            self.acl_denied_target_class = ", ".join(allowed) if allowed else (", ".join(allowed_depts) if allowed_depts else "Chỉ định bởi Giảng viên")
            self.acl_denied_current_class = user_class if user_class else "Chưa gán lớp"
            self.acl_denied_open = True
            return rx.toast.error(f"Từ chối truy cập (403): Bạn thuộc {user_class or 'lớp khác'}, không có quyền mở tài liệu này!")

    def close_detail_modal(self):
        self.detail_modal_open = False

    def close_acl_denied(self):
        self.acl_denied_open = False

    async def download_active_doc(self):
        """Tải tài liệu nhị phân nguyên vẹn từ Django Backend qua API download."""
        if not self.active_doc:
            return rx.toast.error("Không có tài liệu nào đang được chọn.")

        doc_id = self.active_doc.get("id")
        doc_status = self.active_doc.get("status", "")
        file_name = self.active_doc.get("file_name") or f"document_{doc_id}"

        from .auth import AuthState
        auth = await self.get_state(AuthState)
        token = auth.auth_token
        user_role = getattr(auth, 'user_role', 'STUDENT')

        # Kiểm tra trạng thái: Sinh viên không được tải tài liệu chưa duyệt / bị từ chối của người khác
        if user_role == 'STUDENT' and doc_status != 'APPROVED' and str(self.active_doc.get("uploader_id", "")) != str(auth.current_user_id):
            return rx.toast.error("Tài liệu chưa được phê duyệt hoặc đã bị từ chối, không thể tải xuống!")

        for d in self.documents:
            if str(d.get("id")) == str(doc_id):
                d["downloads"] = d.get("downloads", 0) + 1
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                d.setdefault("activity_logs", []).insert(0, {
                    "id": f"log_d_{datetime.now().timestamp()}",
                    "action": "DOWNLOAD",
                    "user_name": self.current_user.get("full_name", ""),
                    "description": f"Tải xuống tệp {file_name}",
                    "timestamp": now_str,
                })
                self.active_doc = dict(d)
                break

        # Tải trực tiếp file nhị phân nguyên vẹn từ Backend API
        download_url = f"http://127.0.0.1:8000/api/documents/{doc_id}/download/?format=file"
        if token:
            download_url += f"&token={token}"

        return [
            trigger_browser_download(download_url, file_name),
            rx.toast.success(f"Đang bắt đầu tải tệp: {file_name}"),
        ]

    # ── XỬ LÝ QUY TRÌNH DUYỆT (TASK 3: APPROVAL WORKFLOW) ─────────────────────

    def approve_document(self, doc_id: str):
        """Giảng viên phê duyệt tài liệu -> Lập tức chuyển sang công khai."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        lecturer_name = self.current_user.get("full_name", "TS. Nguyễn Văn An")

        try:
            import httpx
            from .auth import AuthState
            token = getattr(AuthState, 'auth_token', '')
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            httpx.post(f"http://127.0.0.1:8000/api/documents/{doc_id}/approve/", headers=headers, timeout=5.0)
        except Exception:
            try:
                from documents.models import Document as DjDoc
                DjDoc.objects.filter(id=doc_id).update(status="APPROVED", is_public=True)
            except Exception:
                pass

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
        reason_val = self.reject_feedback_input.strip()

        try:
            import httpx
            from .auth import AuthState
            token = getattr(AuthState, 'auth_token', '')
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            httpx.post(f"http://127.0.0.1:8000/api/documents/{doc_id}/reject/", json={"reason": reason_val}, headers=headers, timeout=5.0)
        except Exception:
            try:
                from documents.models import Document as DjDoc
                DjDoc.objects.filter(id=doc_id).update(status="REJECTED")
            except Exception:
                pass

        updated = []
        for d in self.documents:
            if d["id"] == doc_id:
                d["status"] = "REJECTED"
                d["is_public"] = False
                d["reviewer"] = lecturer_name
                d["reviewed_at"] = now_str
                d["reject_reason"] = reason_val
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

    async def download_version_file(self, file_name: str):
        from .auth import AuthState
        auth = await self.get_state(AuthState)
        token = auth.auth_token

        doc_id = ""
        if self.active_version_doc:
            doc_id = str(self.active_version_doc.get("id", ""))
        elif self.active_doc:
            doc_id = str(self.active_doc.get("id", ""))

        if doc_id:
            download_url = f"http://127.0.0.1:8000/api/documents/{doc_id}/download/?format=file"
        else:
            download_url = f"http://127.0.0.1:8000/api/documents/1/download/?format=file"

        if token and "?" in download_url:
            download_url += f"&token={token}"

        return [
            trigger_browser_download(download_url, file_name),
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
        uploader_id: int = 0,
        uploader_name: str = "",
    ):
        """Sinh viên nộp tài liệu mới $\to$ Tạo bản ghi PENDING vào hàng đợi duyệt."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        user = self.current_user
        doc_id = f"doc_{int(datetime.now().timestamp())}"

        allowed_classes = [allowed_class] if allowed_class else []
        actual_fname = file_name if file_name else f"{subject_code}_TaiLieu_v1.pdf"
        actual_furl = file_url if file_url else f"/_upload/{actual_fname}"

        eff_uploader_name = uploader_name or user.get("full_name", "Sinh viên")
        eff_uploader_id = str(uploader_id) if uploader_id else str(user.get("id", "u1"))

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
            "uploader_name": eff_uploader_name,
            "uploader_id": eff_uploader_id,
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

        # Persist to database PostgreSQL
        try:
            from documents.models import Document as DjDoc, DocumentVersion as DjVer, DocumentActivityLog as DjLog, Folder as DjFolder, Tag as DjTag
            from academics.models import Subject as DjSub
            from accounts.models import User as DjUser
            from documents.indexing_service import index_document

            sub_id = 1
            if subject_code.startswith("SUB_") or subject_code.isdigit():
                sub_id = int(subject_code.replace("SUB_", ""))
            else:
                s_obj = DjSub.objects.filter(subject_name__icontains=subject_code).first()
                if s_obj:
                    sub_id = s_obj.id

            uploader = None
            if uploader_id:
                uploader = DjUser.objects.filter(id=uploader_id).first()
            if not uploader:
                uploader = DjUser.objects.filter(role_id=3).first() or DjUser.objects.first()
            folder_obj = DjFolder.objects.filter(folder_name__icontains=folder_name, subject_id=sub_id).first()
            folder_id = folder_obj.id if folder_obj else None

            dj_doc = DjDoc.objects.create(
                title=title.strip(),
                description=description.strip(),
                subject_id=sub_id,
                folder_id=folder_id,
                uploader=uploader,
                status="PENDING",
                is_public=is_public,
            )
            doc_id = str(dj_doc.id)
            new_doc["id"] = doc_id

            DjVer.objects.create(
                document=dj_doc,
                version_number="v1.0",
                file_name=actual_fname,
                file_size=2097152,
                change_summary="Bản đóng góp ban đầu của sinh viên",
                uploader=uploader,
            )

            for tag_name in tags:
                tag_obj, _ = DjTag.objects.get_or_create(tag_name=tag_name.strip())
                dj_doc.tags.add(tag_obj)

            DjLog.objects.create(
                document=dj_doc,
                user=uploader,
                action="UPLOAD",
                details=f"Đóng góp tài liệu mới '{title.strip()}' vào hàng đợi phê duyệt.",
            )

            index_document(dj_doc.id)
        except Exception:
            pass

        self.documents.insert(0, new_doc)
        return rx.toast.success("Tài liệu đã được gửi thành công! Đang chờ Giảng viên phê duyệt.")
