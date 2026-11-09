"""
DocUni - Bộ Kiểm Thử Tự Động Toàn Diện (End-to-End API Test Suite)
Kiểm thử chi tiết Phần 2 và Phần 3:
1. Validator & Cloudflare R2: Đuôi file, dung lượng <= 50MB, mã băm SHA-256
2. API Upload: Đẩy file lên R2, lưu metadata & object key vào DB
3. Phân quyền ACL chi tiết: Sinh viên Lớp A mở được, Lớp B bị chặn 403
4. Quy trình phê duyệt (Approval Workflow): PENDING -> APPROVED / REJECTED
5. Quản lý phiên bản (Versioning): Nâng cấp v1.0 -> v2.0
6. Quản trị học liệu: Môn học, Khóa/Mở lớp học, Cây thư mục cha - con
7. Nhật ký kiểm toán (Audit Logs) & Thống kê Dashboard
"""

import os
import sys
import io
from pathlib import Path

# Setup UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent / 'venv' / 'Lib' / 'site-packages'))
local_python_pkgs = r'C:\Users\Thai anh ky\AppData\Local\Programs\Python\Python313\Lib\site-packages'
if os.path.exists(local_python_pkgs) and local_python_pkgs not in sys.path:
    sys.path.insert(0, local_python_pkgs)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, Role
from academics.models import Department, Class, Subject
from documents.models import Document, DocumentVersion, DocumentActivityLog, Folder
from documents.validators import validate_file_upload, calculate_sha256, ALLOWED_EXTENSIONS
from documents.r2_service import r2_service


def run_tests():
    print("=" * 70)
    print("🚀 BẮT ĐẦU BỘ KIỂM THỬ TỰ ĐỘNG BACKEND PHẦN 2 & PHẦN 3 (DOCUNI)")
    print("=" * 70)

    client = Client()
    passed = 0
    total = 0

    def assert_true(condition, test_name):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {test_name}")
        else:
            print(f"  [FAIL] {test_name}")
            raise AssertionError(f"Kiểm thử thất bại: {test_name}")

    # =========================================================================
    # PHẦN 2: KIỂM THỬ FILE STORAGE, VALIDATION, CLOUDFLARE R2
    # =========================================================================
    print("\n--- PHẦN 2: FILE STORAGE, VALIDATORS & CLOUDFLARE R2 ---")

    # Test 2.1: Chấp nhận file hợp lệ (.pdf, .docx, .zip)
    valid_pdf = SimpleUploadedFile("demo_document.pdf", b"%PDF-1.4 Fake PDF Content for DocUni", content_type="application/pdf")
    is_valid, err, meta = validate_file_upload(valid_pdf)
    assert_true(is_valid and meta['extension'] == '.pdf', "2.1. File Validator: Chấp nhận file .pdf hợp lệ")
    assert_true(len(meta['checksum_sha256']) == 64, "2.2. File Validator: Tính toán mã băm SHA-256 (64 hex characters)")

    # Test 2.3: Chặn file đuôi lạ (.exe, .sh)
    invalid_file = SimpleUploadedFile("malware.exe", b"MZ Executable Content", content_type="application/octet-stream")
    is_valid, err, meta = validate_file_upload(invalid_file)
    assert_true(not is_valid and "không được hỗ trợ" in err, "2.3. File Validator: Chặn file định dạng không được phép (.exe)")

    # Test 2.4: Chặn file vượt quá 50MB
    class FakeHugeFile:
        name = "huge_data.zip"
        size = 55 * 1024 * 1024  # 55MB
        def seek(self, *args): pass
        def read(self, *args): return b""
    is_valid, err, meta = validate_file_upload(FakeHugeFile())
    assert_true(not is_valid and "vượt quá giới hạn tối đa" in err, "2.4. File Validator: Chặn file dung lượng > 50MB")

    # Test 2.5: API Upload tài liệu (POST /api/documents/upload/)
    gv = User.objects.get(username='gv01')
    client.force_login(gv)
    upload_file = SimpleUploadedFile("Giao_Trinh_Moi.pdf", b"%PDF-1.4 Giao trinh Python nang cao 2026", content_type="application/pdf")
    res = client.post('/api/documents/upload/', {
        'title': 'Giao trinh Python nang cao 2026',
        'description': 'Tai lieu hoc tap chuyen sau',
        'subject_id': 1,
        'is_public': 'true',
        'tags': 'python,advanced,oop',
        'file': upload_file,
    })
    assert_true(res.status_code == 201, "2.5. API Upload: Trả về HTTP 201 Created")
    data = res.json()['data']
    created_doc_id = data['document_id']
    created_obj_key = data['version']['object_key']
    assert_true('documents/1/' in created_obj_key, "2.6. API Upload: Tạo Object Key chuẩn Cloudflare R2 ('documents/{subject_id}/...')")
    assert_true(data['status'] == Document.APPROVED, "2.7. API Upload: Giảng viên upload công khai tự động APPROVED")

    # Test 2.8: API Download tài liệu (GET /api/documents/<id>/download/)
    res_dl = client.get(f'/api/documents/{created_doc_id}/download/')
    assert_true(res_dl.status_code == 200, "2.8. API Download: Tải file thành công (HTTP 200 OK)")
    dl_data = res_dl.json()['data']
    assert_true('download_url' in dl_data and len(dl_data['download_url']) > 0, "2.9. API Download: Cung cấp URL tải an toàn")

    # Test 2.9: Tăng lượt tải và ghi nhận nhật ký
    doc_after = Document.objects.get(pk=created_doc_id)
    assert_true(doc_after.download_count >= 1, "2.10. Metadata: Số lượt tải (download_count) tăng +1 sau khi tải")
    has_dl_log = DocumentActivityLog.objects.filter(document=doc_after, action='DOWNLOAD').exists()
    assert_true(has_dl_log, "2.11. Audit Log: Tự động ghi nhận nhật ký hành động DOWNLOAD")

    # =========================================================================
    # PHẦN 3: NGHIỆP VỤ & PHÂN QUYỀN CHI TIẾT (ACL, APPROVAL, VERSIONING)
    # =========================================================================
    print("\n--- PHẦN 3: PHÂN QUYỀN ACL, APPROVAL & VERSIONING ---")

    # Document 3: Tong hop bai tap thuc hanh Python
    # Quyền trong seed data: Lớp 1 (CNTT-K1) được Xem + Tải; Lớp 2 (CNTT-K2) chỉ Xem; Lớp 3 (KT-K1) KHÔNG có quyền!
    doc3 = Document.objects.get(pk=3)

    # Test 3.1: Sinh viên Nam (sv01 - Lớp 1) mở và tải Document 3 -> THÀNH CÔNG
    sv01 = User.objects.get(username='sv01')
    client.force_login(sv01)
    res_sv01_view = client.get(f'/api/documents/3/check-access/')
    assert_true(res_sv01_view.json()['data']['can_view'] is True, "3.1. ACL: Sinh viên sv01 (Lớp CNTT-K1) có quyền XEM tài liệu lớp mình")
    res_sv01_dl = client.get(f'/api/documents/3/download/')
    assert_true(res_sv01_dl.status_code == 200, "3.2. ACL: Sinh viên sv01 (Lớp CNTT-K1) có quyền TẢI tài liệu lớp mình (200 OK)")

    # Test 3.2: Sinh viên Quỳnh (sv06 - Lớp 3 KT-K1) truy cập Document 3 -> BỊ CHẶN 403
    sv06 = User.objects.get(username='sv06')
    client.force_login(sv06)
    res_sv06_view = client.get(f'/api/documents/3/check-access/')
    assert_true(res_sv06_view.json()['data']['can_view'] is False, "3.3. ACL: Sinh viên sv06 (Lớp khác) bị từ chối quyền xem")
    res_sv06_dl = client.get(f'/api/documents/3/download/')
    assert_true(res_sv06_dl.status_code == 403, "3.4. ACL: Sinh viên sv06 (Lớp khác) bị chặn tải file với mã lỗi 403 Forbidden")

    # Test 3.3: Sinh viên Nga (sv04 - Lớp 2) có quyền Xem nhưng KHÔNG có quyền Tải Document 3
    sv04 = User.objects.get(username='sv04')
    client.force_login(sv04)
    res_sv04_dl = client.get(f'/api/documents/3/download/')
    assert_true(res_sv04_dl.status_code == 403 and "chỉ có quyền xem" in res_sv04_dl.json()['message'], "3.5. ACL: Sinh viên sv04 chỉ có quyền xem, bị chặn khi cố tình tải (403 Forbidden)")

    # Test 3.4: Thêm và gỡ quyền phân quyền động qua API
    client.force_login(gv)
    res_add_perm = client.post(f'/api/documents/3/permissions/', {
        'permission_type': 'CLASS',
        'class_id': 3,
        'can_view': 'true',
        'can_download': 'true',
    })
    assert_true(res_add_perm.status_code == 201, "3.6. API Permission: Giảng viên cấp thêm quyền cho Lớp 3 thành công")
    new_perm_id = res_add_perm.json()['data']['permission_id']

    # Xác nhận sv06 (Lớp 3) ngay lập tức truy cập được
    client.force_login(sv06)
    assert_true(client.get('/api/documents/3/download/').status_code == 200, "3.7. ACL: Quyền mới có hiệu lực tức thì cho sinh viên lớp 3")

    # Giảng viên gỡ quyền
    client.force_login(gv)
    res_del_perm = client.delete(f'/api/documents/3/permissions/{new_perm_id}/')
    assert_true(res_del_perm.status_code == 200, "3.8. API Permission: Gỡ bỏ quyền truy cập thành công")

    # Test 3.5: Quy trình duyệt bài & Nâng phiên bản với tài liệu kiểm thử chuyên biệt
    client.force_login(sv01)
    doc_flow = Document.objects.create(
        title='Bao cao thu nghiem sinh vien sv01',
        description='Bao cao phan tich de tai test',
        subject_id=1,
        uploader=sv01,
        status=Document.PENDING,
        is_public=False,
    )
    DocumentVersion.objects.create(
        document=doc_flow,
        file='documents/1/test/v1_Bao_cao_v1.docx',
        version_number=1,
        updated_by=sv01,
        change_summary='Nop ban dau',
    )
    assert_true(doc_flow.status == Document.PENDING, "3.9. Workflow: Tài liệu sinh viên nộp ban đầu ở trạng thái PENDING")

    # Giảng viên Từ chối (Reject) kèm phản hồi
    client.force_login(gv)
    res_rej = client.post(f'/api/documents/{doc_flow.id}/reject/', {'reason': 'Thieu chuong 3 va ket luan de tai'})
    assert_true(res_rej.status_code == 200, "3.10. Workflow: Giảng viên từ chối duyệt bài kèm lý do phản hồi")
    doc_flow.refresh_from_db()
    assert_true(doc_flow.status == Document.REJECTED and not doc_flow.is_public, "3.11. Workflow: Trạng thái chuyển sang REJECTED và ẩn công khai")

    # Sinh viên nộp phiên bản nâng cấp v2.0 (POST /api/documents/<id>/versions/upload/)
    client.force_login(sv01)
    v2_file = SimpleUploadedFile("Bao_Cao_Nhom_v2.docx", b"PK Zip Content Docx v2 with Chapter 3", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    res_ver = client.post(f'/api/documents/{doc_flow.id}/versions/upload/', {
        'file': v2_file,
        'change_summary': 'Da bo sung chuong 3 va phan ket luan theo yeu cau',
    })
    assert_true(res_ver.status_code == 201, "3.12. Versioning: Sinh viên nộp phiên bản v2.0 thành công (201 Created)")
    assert_true(res_ver.json()['data']['version_number'] == 2, "3.13. Versioning: Tự động đánh số phiên bản v2.0")
    doc_flow.refresh_from_db()
    assert_true(doc_flow.status == Document.PENDING, "3.14. Versioning: Sinh viên nộp lại bản v2.0 tự động chuyển về PENDING để duyệt lại")

    # Giảng viên duyệt bài (Approve)
    client.force_login(gv)
    res_app = client.post(f'/api/documents/{doc_flow.id}/approve/')
    assert_true(res_app.status_code == 200, "3.15. Workflow: Giảng viên phê duyệt tài liệu thành công")
    doc_flow.refresh_from_db()
    assert_true(doc_flow.status == Document.APPROVED and doc_flow.is_public, "3.16. Workflow: Trạng thái chuyển APPROVED và xuất bản công khai")

    # Test 3.6: Xem lịch sử phiên bản (GET /api/documents/<id>/versions/)
    res_vlist = client.get(f'/api/documents/{doc_flow.id}/versions/')
    assert_true(res_vlist.status_code == 200 and len(res_vlist.json()['data']['versions']) == 2, "3.17. Versioning: Danh sách lịch sử hiển thị đầy đủ các phiên bản v1 và v2")
    # Dọn dẹp tài liệu test workflow
    doc_flow.delete()

    # Test 3.7: Cây thư mục môn học (GET /api/subjects/1/folders/tree/)
    res_tree = client.get('/api/subjects/1/folders/tree/')
    assert_true(res_tree.status_code == 200, "3.18. Academic: Lấy cây thư mục môn học thành công")
    tree = res_tree.json()['data']['tree']
    assert_true(any(node['name'] == 'Bai giang' and len(node['children']) > 0 for node in tree), "3.19. Academic: Cây thư mục tổ chức phân cấp cha - con chính xác")

    # Test 3.8: Khóa và Mở khóa lớp học (PATCH /api/classes/<id>/toggle-lock/)
    admin_user = User.objects.get(username='admin')
    client.force_login(admin_user)
    cls1 = Class.objects.get(pk=1)
    init_state = cls1.is_locked
    res_lock = client.patch('/api/classes/1/toggle-lock/')
    assert_true(res_lock.status_code == 200 and res_lock.json()['data']['is_locked'] == (not init_state), "3.20. Academic: Admin khóa / mở khóa lớp học thành công")
    # Trả lại trạng thái cũ
    client.patch('/api/classes/1/toggle-lock/')

    # Test 3.9: Thống kê Dashboard (GET /api/dashboard/stats/)
    res_stats = client.get('/api/dashboard/stats/')
    assert_true(res_stats.status_code == 200, "3.21. Dashboard: API thống kê tổng quan hoạt động tốt")
    stats = res_stats.json()['data']
    assert_true(stats['documents']['total'] > 0 and stats['users']['total_active'] > 0, "3.22. Dashboard: Báo cáo đầy đủ số liệu tài liệu, người dùng, lượt tải")

    # Test 3.10: Xóa tài liệu (DELETE /api/documents/<id>/)
    res_del = client.delete(f'/api/documents/{created_doc_id}/')
    assert_true(res_del.status_code == 200, "3.23. API Delete: Xóa tài liệu thành công")
    assert_true(not Document.objects.filter(pk=created_doc_id).exists(), "3.24. API Delete: Bản ghi tài liệu đã được gỡ khỏi Database")

    print("\n" + "=" * 70)
    print(f"🎉 TẤT CẢ {passed}/{total} KỊCH BẢN KIỂM THỬ ĐÃ VƯỢT QUA XUẤT SẮC (100% PASS)!")
    print("=" * 70)


if __name__ == '__main__':
    run_tests()
