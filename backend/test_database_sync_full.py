"""
Kiểm thử toàn diện việc thay thế Mock Data bằng dữ liệu PostgreSQL thực tế
và đồng bộ dữ liệu giữa Frontend (Reflex) và Backend (Django REST).
"""

import os
import sys
import glob
import django

# Thiết lập môi trường Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from accounts.models import User, Role
from academics.models import Department, Subject, Class
from documents.models import Document, Folder, DocumentActivityLog
from ai_search.models import AIQuery


def run_comprehensive_check():
    print("=" * 80)
    print(" BẮT ĐẦU KIỂM THỬ ĐỒNG BỘ DỮ LIỆU POSTGRESQL & LOẠI BỎ MOCK DATA TOÀN DIỆN")
    print("=" * 80)
    client = APIClient()

    passed = 0
    total = 0

    def _get_data(res):
        if hasattr(res, 'data') and res.data is not None:
            return res.data
        try:
            return res.json()
        except Exception:
            import json
            return json.loads(res.content.decode('utf-8'))

    # -------------------------------------------------------------
    # 1. KIỂM TRA MÃ NGUỒN FRONTEND: KHÔNG CÒN MOCK DATA
    # -------------------------------------------------------------
    total += 1
    frontend_files = glob.glob("frontend_app/frontend_app/*.py")
    mock_found = []
    for f in frontend_files:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
            for line in content.splitlines():
                if "MOCK_" in line:
                    mock_found.append(f"{f}: {line.strip()}")

    if not mock_found:
        print("[PASSED] Test 01: Toàn bộ mã nguồn Frontend không còn bất kỳ hằng số MOCK_ nào.")
        passed += 1
    else:
        print(f"[FAILED] Test 01: Vẫn còn Mock Data: {mock_found}")

    # -------------------------------------------------------------
    # 2. XÁC THỰC VÀ LẤY TOKEN CỦA 3 VAI TRÒ
    # -------------------------------------------------------------
    total += 1
    login_admin = client.post('/api/auth/login/', {'username': 'admin', 'password': 'admin123'}, format='json')
    admin_data = _get_data(login_admin)
    admin_token = admin_data.get('token')

    login_lecturer = client.post('/api/auth/login/', {'username': 'gv01', 'password': 'gv123'}, format='json')
    lecturer_data = _get_data(login_lecturer)
    lecturer_token = lecturer_data.get('token')

    login_student = client.post('/api/auth/login/', {'username': 'sv01', 'password': 'sv123'}, format='json')
    student_data = _get_data(login_student)
    student_token = student_data.get('token')

    if admin_token and lecturer_token and student_token:
        print("[PASSED] Test 02: Xác thực tài khoản ADMIN, LECTURER, STUDENT từ PostgreSQL thành công.")
        passed += 1
    else:
        print("[FAILED] Test 02: Không thể xác thực đủ 3 vai trò.")

    # -------------------------------------------------------------
    # 3. KHU VỰC 1: TRANG CHỦ & DANH SÁCH TÀI LIỆU (GET /api/documents/)
    # -------------------------------------------------------------
    total += 1
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {student_token}')
    res_docs = client.get('/api/documents/')
    docs_data = _get_data(res_docs)
    if res_docs.status_code == 200 and 'documents' in docs_data:
        doc_count = len(docs_data['documents'])
        print(f"[PASSED] Test 03: API /api/documents/ trả về {doc_count} tài liệu thực tế từ PostgreSQL.")
        passed += 1
    else:
        print(f"[FAILED] Test 03: Lỗi API /api/documents/: {res_docs.status_code}")

    # -------------------------------------------------------------
    # 4. KHU VỰC 2: QUẢN LÝ MÔN HỌC (GET /api/subjects/)
    # -------------------------------------------------------------
    total += 1
    res_subjs = client.get('/api/subjects/')
    subjs_data = _get_data(res_subjs)
    if res_subjs.status_code == 200 and 'subjects' in subjs_data:
        subj_count = len(subjs_data['subjects'])
        print(f"[PASSED] Test 04: API /api/subjects/ trả về {subj_count} môn học thực tế từ bảng subjects.")
        passed += 1
    else:
        print(f"[FAILED] Test 04: Lỗi API /api/subjects/: {res_subjs.status_code}")

    # -------------------------------------------------------------
    # 5. KHU VỰC 3: QUẢN LÝ KHOA & LỚP (GET /api/departments/ & /api/classes/)
    # -------------------------------------------------------------
    total += 1
    res_depts = client.get('/api/departments/')
    res_classes = client.get('/api/classes/')
    depts_data = _get_data(res_depts)
    classes_data = _get_data(res_classes)
    if res_depts.status_code == 200 and res_classes.status_code == 200:
        dept_count = len(depts_data.get('departments', []))
        class_count = len(classes_data.get('classes', []))
        print(f"[PASSED] Test 05: API Khoa ({dept_count} khoa) & Lớp ({class_count} lớp) lấy từ PostgreSQL.")
        passed += 1
    else:
        print(f"[FAILED] Test 05: Lỗi API Khoa hoặc Lớp")

    # -------------------------------------------------------------
    # 6. KHU VỰC 4: QUẢN LÝ NGƯỜI DÙNG & VAI TRÒ (GET /api/users/ & /api/roles/)
    # -------------------------------------------------------------
    total += 1
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    res_users = client.get('/api/users/')
    res_roles = client.get('/api/roles/')
    users_data = _get_data(res_users)
    roles_data = _get_data(res_roles)
    if res_users.status_code == 200 and res_roles.status_code == 200:
        user_count = len(users_data.get('users', []))
        role_count = len(roles_data.get('roles', []))
        print(f"[PASSED] Test 06: Admin quản lý {user_count} người dùng và {role_count} vai trò từ PostgreSQL.")
        passed += 1
    else:
        print(f"[FAILED] Test 06: Lỗi API người dùng hoặc vai trò")

    # -------------------------------------------------------------
    # 7. KHU VỰC 5: NHẬT KÝ HOẠT ĐỘNG (GET /api/activity-logs/)
    # -------------------------------------------------------------
    total += 1
    res_logs = client.get('/api/activity-logs/')
    logs_data = _get_data(res_logs)
    if res_logs.status_code == 200 and 'logs' in logs_data:
        log_count = len(logs_data['logs'])
        print(f"[PASSED] Test 07: Lấy {log_count} nhật ký hoạt động từ bảng document_activity_logs.")
        passed += 1
    else:
        print(f"[FAILED] Test 07: Lỗi API nhật ký hoạt động")

    # -------------------------------------------------------------
    # 8. KHU VỰC 6: DASHBOARD STATS (GET /api/dashboard/stats/)
    # -------------------------------------------------------------
    total += 1
    res_stats = client.get('/api/dashboard/stats/')
    stats_data = _get_data(res_stats)
    if res_stats.status_code == 200 and 'stats' in stats_data:
        stats = stats_data['stats']
        print(f"[PASSED] Test 08: Thống kê Dashboard thực tế: {stats['total_documents']} tài liệu, {stats['total_views']} views, {stats['total_downloads']} downloads.")
        passed += 1
    else:
        print(f"[FAILED] Test 08: Lỗi API thống kê Dashboard")

    # -------------------------------------------------------------
    # 9. KHU VỰC 7: AI RAG SEARCH (POST /api/ai/query/ & GET /api/ai/history/)
    # -------------------------------------------------------------
    total += 1
    res_ai = client.post('/api/ai/query/', {'query': 'Cấu trúc dữ liệu cây nhị phân'}, format='json')
    res_ai_hist = client.get('/api/ai/history/')
    ai_data = _get_data(res_ai)
    ai_hist_data = _get_data(res_ai_hist)
    if res_ai.status_code == 200 and res_ai_hist.status_code == 200:
        ans = ai_data.get('answer', '')
        srcs = len(ai_data.get('sources', []))
        print(f"[PASSED] Test 09: Trợ lý AI kết nối tài liệu PostgreSQL: {srcs} nguồn trích dẫn, lưu lịch sử thành công.")
        passed += 1
    else:
        print(f"[FAILED] Test 09: Lỗi API Trợ lý AI")

    # -------------------------------------------------------------
    # 10. ĐỒNG BỘ THÊM, SỬA, XÓA DỮ LIỆU THỰC TẾ VÀO DATABASE
    # -------------------------------------------------------------
    total += 1
    # Tạo tài liệu mới
    create_res = client.post('/api/documents/', {
        'title': 'Test Sync PostgreSQL Document',
        'description': 'Tài liệu kiểm thử đồng bộ thực tế',
        'subject_id': 1,
        'is_public': True
    }, format='json')
    create_data = _get_data(create_res)
    new_doc_id = create_data.get('document', {}).get('document_id')

    # Chỉnh sửa tài liệu trong database
    patch_res = client.patch(f'/api/documents/{new_doc_id}/', {
        'title': 'Test Sync PostgreSQL Document (Updated)',
        'description': 'Đã cập nhật mô tả thành công'
    }, format='json')

    # Kiểm tra lại trong DB
    doc_in_db = Document.objects.filter(pk=new_doc_id).first()
    title_updated = doc_in_db.title if doc_in_db else ""

    # Xóa tài liệu khỏi database
    del_res = client.delete(f'/api/documents/{new_doc_id}/')
    doc_exists_after = Document.objects.filter(pk=new_doc_id).exists()

    if (create_res.status_code in (200, 201) and
        patch_res.status_code == 200 and
        title_updated == 'Test Sync PostgreSQL Document (Updated)' and
        del_res.status_code == 200 and
        not doc_exists_after):
        print("[PASSED] Test 10: Đồng bộ CRUD Thêm -> Sửa -> Xóa trực tiếp vào PostgreSQL thành công 100%.")
        passed += 1
    else:
        print(f"[FAILED] Test 10: Thất bại trong quy trình CRUD PostgreSQL.")

    print("=" * 80)
    print(f" TỔNG KẾT: {passed}/{total} BÀI KIỂM THỬ THÀNH CÔNG VƯỢT QUA!")
    print("=" * 80)


if __name__ == '__main__':
    run_comprehensive_check()
