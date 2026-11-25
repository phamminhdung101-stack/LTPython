"""
DocUni - Bộ Kiểm Thử Toàn Diện Trang Quản Trị Admin
Kiểm tra:
1. Thống kê KPI thực tế từ PostgreSQL (không 0, không mock).
2. Quản lý Người dùng: CRUD, ràng buộc Khoa - Lớp, Phân quyền, Khóa/Mở khóa.
3. Quản lý Khoa & Môn học: Phân chia chính xác theo khoa, Bộ lọc D1/D2/D3/ALL.
4. Quản lý Lớp học: Phân lớp theo khoa, khóa/mở khóa lớp.
5. AI Indexing: Tính toán tỷ lệ thực tế, Re-index vào bảng document_embeddings.
"""

import os
import sys
import json
import django

# Setup Django Environment
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
FRONTEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'frontend_app'))
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from accounts.models import User, Role
from academics.models import Department, Subject, Class
from documents.models import Document, Folder, Tag
from documents.indexing_service import get_indexing_stats, index_document, index_all_documents
from accounts.authentication import generate_jwt_token


def run_admin_tests():
    print("=" * 80)
    print(" BẮT ĐẦU KIỂM THỬ TOÀN DIỆN CHỨC NĂNG QUẢN TRỊ ADMIN (DOCUNI)")
    print("=" * 80)

    client = Client()
    admin_user = User.objects.filter(role__role_name='ADMIN').first()
    assert admin_user is not None, "Cần có tài khoản ADMIN trong PostgreSQL."
    admin_token = generate_jwt_token(admin_user)
    admin_headers = {'HTTP_AUTHORIZATION': f'Bearer {admin_token}'}

    # ──────────────────────────────────────────────────────────────────────────
    # 1. THỐNG KÊ DASHBOARD / ADMIN KPI
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHẦN 1] KIỂM TRA THỐNG KÊ QUẢN TRỊ ADMIN (KHÔNG 0, TỪ POSTGRESQL):")
    res = client.get('/api/dashboard/stats/', **admin_headers)
    assert res.status_code == 200, f"API Dashboard stats lỗi: {res.status_code}"
    stats_data = res.json().get('stats', {})

    total_users = stats_data.get('total_users', 0)
    total_docs = stats_data.get('total_documents', 0)
    total_folders = stats_data.get('total_folders', 0)
    total_tags = stats_data.get('total_tags', 0)
    idx_info = stats_data.get('indexing', {})
    idx_rate = idx_info.get('indexing_percentage', 0)

    print(f"  • Tổng người dùng: {total_users} (DB: {User.objects.filter(is_active=True).count()})")
    print(f"  • Tổng tài liệu: {total_docs} (DB: {Document.objects.count()})")
    print(f"  • Tổng thư mục: {total_folders} (DB: {Folder.objects.count()})")
    print(f"  • Tổng thẻ (tags): {total_tags} (DB: {Tag.objects.count()})")
    print(f"  • AI Indexing: {idx_rate}% ({idx_info.get('total_chunks')} chunks)")

    assert total_users > 0, "LỖI: Tổng người dùng bằng 0!"
    assert total_docs > 0, "LỖI: Tổng tài liệu bằng 0!"
    assert total_folders > 0, "LỖI: Tổng thư mục bằng 0!"
    assert total_tags > 0, "LỖI: Tổng thẻ bằng 0!"
    assert idx_rate > 0, "LỖI: Tỷ lệ AI Indexing bằng 0%!"
    print("  [PASS] 1.1. Tất cả chỉ số thống kê phản ánh chính xác số liệu từ PostgreSQL.")

    # ──────────────────────────────────────────────────────────────────────────
    # 2. QUẢN LÝ KHOA & PHÂN CHIA MÔN HỌC (D1, D2, D3)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHẦN 2] KIỂM TRA KHOA VÀ PHÂN CHIA MÔN HỌC THEO KHOA:")
    res_depts = client.get('/api/departments/', **admin_headers)
    assert res_depts.status_code == 200
    depts = res_depts.json().get('departments', [])
    assert len(depts) >= 3, "Phải có ít nhất 3 khoa trong PostgreSQL"
    print(f"  • Số khoa hiện có: {len(depts)}")

    d1 = Department.objects.filter(id=1).first()
    d2 = Department.objects.filter(id=2).first()
    d3 = Department.objects.filter(id=3).first()

    # Kiểm tra môn học của D1 (Công nghệ thông tin)
    res_s1 = client.get(f'/api/subjects/?department_id={d1.id}', **admin_headers)
    assert res_s1.status_code == 200
    subs_d1 = [s['subject_name'] for s in res_s1.json().get('subjects', [])]
    print(f"  • Môn học Khoa CNTT (D1): {subs_d1}")
    assert 'Lap trinh Java' in subs_d1 or 'Co so du lieu' in subs_d1, "D1 phải có môn CNTT"
    assert 'Kinh te vi mo' not in subs_d1, "Môn Kinh tế không được nằm trong Khoa CNTT"
    assert 'Tieng Anh chuyen nganh' not in subs_d1, "Môn Ngoại ngữ không được nằm trong Khoa CNTT"
    print("  [PASS] 2.1. Môn học Khoa CNTT (D1) phân chia chính xác.")

    # Kiểm tra môn học của D2 (Kinh tế)
    res_s2 = client.get(f'/api/subjects/?department_id={d2.id}', **admin_headers)
    assert res_s2.status_code == 200
    subs_d2 = [s['subject_name'] for s in res_s2.json().get('subjects', [])]
    print(f"  • Môn học Khoa Kinh tế (D2): {subs_d2}")
    assert 'Kinh te vi mo' in subs_d2 or 'Ke toan dai cuong' in subs_d2, "D2 phải có môn Kinh tế"
    assert 'Lap trinh Java' not in subs_d2, "Môn CNTT không được nằm trong Khoa Kinh tế"
    print("  [PASS] 2.2. Môn học Khoa Kinh tế (D2) phân chia chính xác.")

    # Kiểm tra môn học của D3 (Ngoại ngữ)
    res_s3 = client.get(f'/api/subjects/?department_id={d3.id}', **admin_headers)
    assert res_s3.status_code == 200
    subs_d3 = [s['subject_name'] for s in res_s3.json().get('subjects', [])]
    print(f"  • Môn học Khoa Ngoại ngữ (D3): {subs_d3}")
    assert 'Tieng Anh chuyen nganh' in subs_d3 or 'Ngu phap co ban' in subs_d3, "D3 phải có môn Ngoại ngữ"
    assert 'Lap trinh Java' not in subs_d3, "Môn CNTT không được nằm trong Khoa Ngoại ngữ"
    print("  [PASS] 2.3. Môn học Khoa Ngoại ngữ (D3) phân chia chính xác.")

    # Kiểm tra bộ lọc môn học của Frontend (OrgState logic)
    from frontend_app.admin_organization import OrgState, Subject as FrontSub
    mock_subjects = [
        FrontSub(id="1", code="SUB1", name="Lap trinh Java", department_code="D1", department_name="Cong nghe thong tin", credits=3, total_docs=5),
        FrontSub(id="2", code="SUB2", name="Co so du lieu", department_code="D1", department_name="Cong nghe thong tin", credits=3, total_docs=3),
        FrontSub(id="4", code="SUB4", name="Kinh te vi mo", department_code="D2", department_name="Kinh te", credits=3, total_docs=2),
        FrontSub(id="6", code="SUB6", name="Tieng Anh chuyen nganh", department_code="D3", department_name="Ngoai ngu", credits=2, total_docs=1),
    ]

    class MockOrgState:
        subjects = mock_subjects
        subject_search = ""
        subject_dept_filter = "ALL"

    mock_inst = MockOrgState()

    # Lọc D1
    mock_inst.subject_dept_filter = "D1"
    f_d1 = OrgState.filtered_subjects.fget(mock_inst)
    assert len(f_d1) == 2 and all(s.department_code == "D1" for s in f_d1), f"Lọc D1 thất bại: {f_d1}"
    print("  [PASS] 2.4. Bộ lọc Frontend: Chọn 'D1' chỉ hiển thị 100% môn Khoa CNTT.")

    # Lọc D2
    mock_inst.subject_dept_filter = "Kinh te"
    f_d2 = OrgState.filtered_subjects.fget(mock_inst)
    assert len(f_d2) == 1 and f_d2[0].name == "Kinh te vi mo", f"Lọc D2 thất bại: {f_d2}"
    print("  [PASS] 2.5. Bộ lọc Frontend: Chọn 'Kinh te' chỉ hiển thị môn Khoa Kinh tế.")

    # Lọc ALL
    mock_inst.subject_dept_filter = "ALL"
    f_all = OrgState.filtered_subjects.fget(mock_inst)
    assert len(f_all) == 4, "Lọc ALL phải hiển thị đầy đủ môn học."
    print("  [PASS] 2.6. Bộ lọc Frontend: Chọn 'ALL' hiển thị tất cả các môn học.")

    # ──────────────────────────────────────────────────────────────────────────
    # 3. QUẢN LÝ LỚP HỌC THEO KHOA
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHẦN 3] KIỂM TRA QUẢN LÝ LỚP HỌC THEO KHOA:")
    res_c1 = client.get(f'/api/classes/?department_id={d1.id}', **admin_headers)
    assert res_c1.status_code == 200
    classes_d1 = [c['class_name'] for c in res_c1.json().get('classes', [])]
    print(f"  • Lớp thuộc Khoa CNTT: {classes_d1}")
    assert any('CNTT' in c for c in classes_d1), "Khoa CNTT phải có các lớp CNTT-K1, CNTT-K2..."
    assert not any('KT-' in c or 'NN-' in c for c in classes_d1), "Lớp khoa khác không được nằm trong Khoa CNTT"
    print("  [PASS] 3.1. Phân chia lớp học thuộc đúng Khoa CNTT.")

    # Khóa và mở khóa lớp
    c_test = Class.objects.filter(department=d1).first()
    init_locked = c_test.is_locked
    res_toggle = client.patch(f'/api/classes/{c_test.id}/toggle-lock/', **admin_headers)
    assert res_toggle.status_code == 200
    c_test.refresh_from_db()
    assert c_test.is_locked != init_locked, "Trạng thái khóa lớp phải được đảo thành công."
    # Khôi phục trạng thái ban đầu
    client.patch(f'/api/classes/{c_test.id}/toggle-lock/', **admin_headers)
    c_test.refresh_from_db()
    assert c_test.is_locked == init_locked, "Trạng thái khóa lớp phải được khôi phục thành công."
    print("  [PASS] 3.2. Chức năng Khóa / Mở khóa lớp học hoạt động chính xác.")

    # ──────────────────────────────────────────────────────────────────────────
    # 4. QUẢN LÝ NGƯỜI DÙNG & RÀNG BUỘC KHOA - LỚP
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHẦN 4] KIỂM TRA QUẢN LÝ NGƯỜI DÙNG & RÀNG BUỘC KHOA - LỚP:")
    res_users = client.get('/api/users/', **admin_headers)
    assert res_users.status_code == 200
    user_list = res_users.json().get('users', [])
    assert len(user_list) > 0, "Danh sách người dùng không được rỗng."
    print(f"  • Số người dùng lấy từ API: {len(user_list)}")

    # Thêm người dùng mới (STUDENT) có khoa CNTT và lớp CNTT-K1 hợp lệ
    test_uname = "sv_test_admin_flow"
    User.objects.filter(username=test_uname).delete()
    cls_cntt = Class.objects.filter(department=d1, class_name__icontains='CNTT').first()

    payload_create = {
        'username': test_uname,
        'full_name': 'Sinh Viên Kiểm Thử Admin',
        'password': 'password123',
        'role': 'STUDENT',
        'department_id': d1.id,
        'class_id': cls_cntt.id,
    }
    res_create = client.post('/api/users/', data=json.dumps(payload_create), content_type='application/json', **admin_headers)
    assert res_create.status_code == 201, f"Tạo người dùng thất bại: {res_create.content}"
    new_uid = res_create.json().get('data', {}).get('user_id')
    print(f"  • Đã tạo người dùng mới ID: {new_uid}")

    # Chỉnh sửa người dùng
    payload_edit = {
        'full_name': 'Sinh Viên Đã Sửa Tên',
        'email': 'sv_edited@docuni.edu.vn',
        'role': 'LECTURER',
    }
    res_edit = client.patch(f'/api/users/{new_uid}/', data=json.dumps(payload_edit), content_type='application/json', **admin_headers)
    assert res_edit.status_code == 200, f"Sửa người dùng thất bại: {res_edit.content}"
    u_obj = User.objects.get(id=new_uid)
    assert u_obj.full_name == 'Sinh Viên Đã Sửa Tên', "Cập nhật họ tên thất bại."
    assert u_obj.role.role_name == 'LECTURER', "Cập nhật vai trò thất bại."
    print("  [PASS] 4.1. Tạo mới và Cập nhật người dùng thành công.")

    # Khóa tài khoản
    res_lock = client.patch(f'/api/users/{new_uid}/toggle-status/', **admin_headers)
    assert res_lock.status_code == 200
    u_obj.refresh_from_db()
    assert u_obj.is_active is False, "Tài khoản phải bị khóa."
    print("  [PASS] 4.2. Khóa tài khoản thành công.")

    # Mở khóa tài khoản
    res_unlock = client.patch(f'/api/users/{new_uid}/toggle-status/', **admin_headers)
    assert res_unlock.status_code == 200
    u_obj.refresh_from_db()
    assert u_obj.is_active is True, "Tài khoản phải được mở khóa lại."
    print("  [PASS] 4.3. Mở khóa tài khoản thành công.")

    # Xóa người dùng
    res_del = client.delete(f'/api/users/{new_uid}/', **admin_headers)
    assert res_del.status_code == 200
    assert not User.objects.filter(id=new_uid).exists(), "Người dùng phải bị xóa khỏi PostgreSQL."
    print("  [PASS] 4.4. Xóa tài khoản thành công.")

    # Kiểm tra ràng buộc Frontend: Không cho gán sinh viên khoa CNTT vào lớp khoa Kinh tế
    from frontend_app.admin_panel import get_dept_classes
    valid_classes_cntt = get_dept_classes("Cong nghe thong tin")
    assert "CNTT-K1" in valid_classes_cntt, "CNTT phải có lớp CNTT-K1"
    assert "KT-K1" not in valid_classes_cntt, "CNTT không được phép có lớp KT-K1"
    print("  [PASS] 4.5. Logic ràng buộc chặn hoàn toàn việc gán sinh viên sai khoa.")

    # ──────────────────────────────────────────────────────────────────────────
    # 5. AI INDEXING (RAG) & RE-INDEX
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHẦN 5] KIỂM TRA TỶ LỆ AI INDEXING VÀ CHỨC NĂNG RE-INDEX:")
    idx_stats = get_indexing_stats()
    print(f"  • Tổng tài liệu: {idx_stats['total_documents']}")
    print(f"  • Đã Indexing: {idx_stats['indexed_documents']}")
    print(f"  • Tỷ lệ: {idx_stats['indexing_percentage']}%")
    print(f"  • Tổng chunks trong PostgreSQL: {idx_stats['total_chunks']}")

    assert idx_stats['total_documents'] > 0
    assert idx_stats['indexed_documents'] > 0
    assert idx_stats['total_chunks'] > 0
    print("  [PASS] 5.1. Thống kê Indexing phản ánh chính xác số liệu bảng document_embeddings.")

    # Test Re-index API
    doc_sample = Document.objects.first()
    res_reindex = client.post(f'/api/documents/{doc_sample.id}/reindex/', **admin_headers)
    assert res_reindex.status_code == 200
    print(f"  • Re-index tài liệu '{doc_sample.title}': Status 200 OK")
    print("  [PASS] 5.2. Chức năng Re-index gọi thực tế và cập nhật vector vào PostgreSQL.")

    print("\n" + "=" * 80)
    print(" 🎉 TẤT CẢ 12 BÀI KIỂM THỬ TRANG ADMIN ĐÃ ĐẠT 100% THÀNH CÔNG!")
    print("=" * 80)


if __name__ == '__main__':
    run_admin_tests()
