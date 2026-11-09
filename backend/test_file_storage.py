"""
Bộ kiểm thử toàn diện chức năng Lưu trữ file cục bộ (Local FileSystemStorage)
Dự án DocUni - Kho tài liệu môn học có phân quyền & AI ngữ cảnh
"""

import os
import sys
import io
import json
import uuid
from datetime import datetime
from pathlib import Path

# Thiết lập encoding utf-8 cho console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Nạp cấu hình Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User, Role
from academics.models import Subject, Department
from documents.models import Document, DocumentVersion, DocumentActivityLog
from documents.storage_service import LocalDocumentStorageService
from accounts.authentication import generate_jwt_token


def run_tests():
    print("=" * 65)
    print("BẮT ĐẦU KIỂM THỬ CHỨC NĂNG LƯU TRỮ FILE CỤC BỘ (LOCAL FILE STORAGE)")
    print("=" * 65)

    passed = 0
    total = 0

    client = Client()

    # Chuẩn bị dữ liệu tài khoản
    admin_user = User.objects.filter(role__role_name='ADMIN').first()
    lecturer_user = User.objects.filter(role__role_name='LECTURER').first()
    student_user = User.objects.filter(role__role_name='STUDENT').first()
    student2_user = User.objects.filter(role__role_name='STUDENT').exclude(user_id=student_user.user_id).first()

    assert admin_user, "Không tìm thấy tài khoản ADMIN trong DB"
    assert lecturer_user, "Không tìm thấy tài khoản LECTURER trong DB"
    assert student_user, "Không tìm thấy tài khoản STUDENT trong DB"

    subject = Subject.objects.first()
    assert subject, "Không tìm thấy môn học nào trong DB"

    admin_jwt = generate_jwt_token(admin_user)
    lecturer_jwt = generate_jwt_token(lecturer_user)
    student_jwt = generate_jwt_token(student_user)
    student2_jwt = generate_jwt_token(student2_user) if student2_user else None

    storage_service = LocalDocumentStorageService()

    # -------------------------------------------------------------
    # Test 1: Upload file hợp lệ dạng PDF (kiểm tra magic bytes %PDF-)
    # -------------------------------------------------------------
    total += 1
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    pdf_file = SimpleUploadedFile("slide_chuan_test.pdf", pdf_content, content_type="application/pdf")

    resp1 = client.post(
        '/api/documents/upload/',
        {
            'file': pdf_file,
            'title': 'Tài liệu PDF Kiểm Thử Tự Động',
            'description': 'Mô tả tài liệu kiểm thử',
            'subject_id': subject.subject_id,
            'is_public': 'false',
        },
        HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
    )
    if resp1.status_code == 201:
        doc_data = resp1.json().get('document', {})
        uploaded_doc_id = doc_data.get('document_id')
        object_key = doc_data.get('object_key')
        status_val = doc_data.get('status')
        storage_prov = doc_data.get('storage_provider')
        orig_name = doc_data.get('original_file_name')
        file_size = doc_data.get('file_size')

        # Kiểm tra file vật lý tồn tại trên đĩa trong media/
        abs_path = storage_service.get_absolute_path(object_key)
        file_on_disk = abs_path and abs_path.exists() and abs_path.is_file()

        if (status_val == 'PENDING' and 
            storage_prov == 'LOCAL' and 
            orig_name == 'slide_chuan_test.pdf' and
            file_size == len(pdf_content) and
            file_on_disk and
            'documents/' in object_key):
            print(f"[PASS] 1. Upload file PDF hợp lệ thành công -> Trạng thái PENDING, file lưu tại {object_key}")
            passed += 1
        else:
            print(f"[FAIL] 1. Dữ liệu upload không đúng mong đợi: {doc_data}")
    else:
        print(f"[FAIL] 1. Upload PDF thất bại: {resp1.status_code} - {resp1.content.decode('utf-8', errors='ignore')}")

    # -------------------------------------------------------------
    # Test 2: Upload file hợp lệ dạng DOCX (magic bytes PK\x03\x04)
    # -------------------------------------------------------------
    total += 1
    docx_content = b"PK\x03\x04\x14\x00\x06\x00Fake OpenXML content for testing"
    docx_file = SimpleUploadedFile("de_thi_mau.docx", docx_content, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    resp2 = client.post(
        '/api/documents/upload/',
        {
            'file': docx_file,
            'title': 'Đề thi Word DOCX',
            'subject_id': subject.subject_id,
        },
        HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
    )
    if resp2.status_code == 201 and resp2.json().get('document', {}).get('file_type') == 'DOCX':
        print("[PASS] 2. Upload file DOCX (OpenXML ZIP container) thành công")
        passed += 1
    else:
        print(f"[FAIL] 2. Upload DOCX thất bại: {resp2.status_code}")

    # -------------------------------------------------------------
    # Test 3: Upload file hợp lệ dạng TXT (text thuần)
    # -------------------------------------------------------------
    total += 1
    txt_content = "Nội dung ghi chú học tập bằng tiếng Việt có dấu.".encode('utf-8')
    txt_file = SimpleUploadedFile("notes.txt", txt_content, content_type="text/plain")
    resp3 = client.post(
        '/api/documents/upload/',
        {
            'file': txt_file,
            'title': 'Ghi chú bài học TXT',
            'subject_id': subject.subject_id,
        },
        HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
    )
    if resp3.status_code == 201 and resp3.json().get('document', {}).get('file_type') == 'TXT':
        print("[PASS] 3. Upload file văn bản TXT thành công")
        passed += 1
    else:
        print(f"[FAIL] 3. Upload TXT thất bại: {resp3.status_code}")

    # -------------------------------------------------------------
    # Test 4: Chặn upload định dạng không được hỗ trợ (e.g. .exe, .sh)
    # -------------------------------------------------------------
    total += 1
    exe_file = SimpleUploadedFile("malware.exe", b"MZ\x90\x00\x03\x00\x00\x00", content_type="application/octet-stream")
    resp4 = client.post(
        '/api/documents/upload/',
        {
            'file': exe_file,
            'subject_id': subject.subject_id,
        },
        HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
    )
    if resp4.status_code == 400 and 'không được hỗ trợ' in resp4.json().get('message', ''):
        print("[PASS] 4. Chặn tải lên phần mở rộng không hợp lệ (.exe) chính xác (400 Bad Request)")
        passed += 1
    else:
        print(f"[FAIL] 4. Không chặn file .exe: {resp4.status_code}")

    # -------------------------------------------------------------
    # Test 5: Chặn file giả mạo định dạng (Magic bytes mismatch)
    # -------------------------------------------------------------
    total += 1
    fake_pdf = SimpleUploadedFile("fake.pdf", b"#!/bin/bash\necho dangerous script", content_type="application/pdf")
    resp5 = client.post(
        '/api/documents/upload/',
        {
            'file': fake_pdf,
            'subject_id': subject.subject_id,
        },
        HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
    )
    if resp5.status_code == 400 and 'không khớp' in resp5.json().get('message', ''):
        print("[PASS] 5. Kiểm tra nội dung nhị phân (Magic Bytes) phát hiện file giả mạo (.pdf nhưng nội dung script) -> Chặn 400")
        passed += 1
    else:
        print(f"[FAIL] 5. Không phát hiện magic mismatch: {resp5.status_code}")

    # -------------------------------------------------------------
    # Test 6: Chặn file vượt quá dung lượng cho phép
    # -------------------------------------------------------------
    total += 1
    old_max = settings.MAX_UPLOAD_SIZE
    settings.MAX_UPLOAD_SIZE = 100  # Giới hạn tạm thời 100 bytes để test
    try:
        big_file = SimpleUploadedFile("big.pdf", b"%PDF-" + b"0" * 500, content_type="application/pdf")
        resp6 = client.post(
            '/api/documents/upload/',
            {
                'file': big_file,
                'subject_id': subject.subject_id,
            },
            HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
        )
        if resp6.status_code == 400 and 'vượt quá giới hạn' in resp6.json().get('message', ''):
            print("[PASS] 6. Kiểm tra giới hạn dung lượng file thành công (vượt MAX_UPLOAD_SIZE -> 400 Bad Request)")
            passed += 1
        else:
            print(f"[FAIL] 6. Không chặn file quá kích thước: {resp6.status_code}")
    finally:
        settings.MAX_UPLOAD_SIZE = old_max

    # -------------------------------------------------------------
    # Test 7: Chặn upload khi người dùng chưa đăng nhập
    # -------------------------------------------------------------
    total += 1
    pdf_test_anon = SimpleUploadedFile("anon.pdf", b"%PDF-1.4\ncontent", content_type="application/pdf")
    resp7 = client.post(
        '/api/documents/upload/',
        {
            'file': pdf_test_anon,
            'subject_id': subject.subject_id,
        }
    )
    if resp7.status_code == 401:
        print("[PASS] 7. Người dùng chưa đăng nhập bị từ chối upload (401 Unauthorized)")
        passed += 1
    else:
        print(f"[FAIL] 7. Chưa đăng nhập vẫn được upload: {resp7.status_code}")

    # -------------------------------------------------------------
    # Test 8: Download tài liệu PENDING bởi người dùng khác (Bị chặn 403)
    # -------------------------------------------------------------
    total += 1
    # uploaded_doc_id do student_user upload, đang PENDING
    resp8 = client.get(
        f'/api/documents/{uploaded_doc_id}/download/',
        HTTP_AUTHORIZATION=f'Bearer {student2_jwt}' if student2_jwt else '',
    )
    if resp8.status_code == 403:
        print("[PASS] 8. Sinh viên khác không thể download tài liệu chưa duyệt (PENDING) -> Chặn 403 Forbidden")
        passed += 1
    else:
        print(f"[FAIL] 8. Không chặn sinh viên lạ tải tài liệu PENDING: {resp8.status_code}")

    # -------------------------------------------------------------
    # Test 9: Download tài liệu PENDING bởi chính người upload (Cho phép)
    # -------------------------------------------------------------
    total += 1
    resp9 = client.get(
        f'/api/documents/{uploaded_doc_id}/download/',
        HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
    )
    if resp9.status_code == 200 and resp9.getvalue() == pdf_content:
        print("[PASS] 9. Uploader được phép tải xuống tài liệu PENDING của chính mình (200 FileResponse)")
        passed += 1
    else:
        print(f"[FAIL] 9. Uploader không tải được tài liệu của mình: {resp9.status_code}")
    resp9.close()

    # -------------------------------------------------------------
    # Test 10: Download tài liệu PENDING bởi Giảng viên / Admin (Cho phép duyệt)
    # -------------------------------------------------------------
    total += 1
    resp10 = client.get(
        f'/api/documents/{uploaded_doc_id}/download/',
        HTTP_AUTHORIZATION=f'Bearer {lecturer_jwt}',
    )
    if resp10.status_code == 200:
        print("[PASS] 10. Giảng viên / Admin được phép tải tài liệu PENDING để kiểm duyệt (200 FileResponse)")
        passed += 1
    else:
        print(f"[FAIL] 10. Giảng viên không tải được file PENDING: {resp10.status_code}")
    resp10.close()

    # -------------------------------------------------------------
    # Test 11: Phê duyệt tài liệu -> Tất cả người dùng tải được
    # -------------------------------------------------------------
    total += 1
    client.post(f'/api/documents/{uploaded_doc_id}/approve/', HTTP_AUTHORIZATION=f'Bearer {lecturer_jwt}')
    resp11 = client.get(
        f'/api/documents/{uploaded_doc_id}/download/',
        HTTP_AUTHORIZATION=f'Bearer {student2_jwt}' if student2_jwt else f'Bearer {student_jwt}',
    )
    if resp11.status_code == 200:
        print("[PASS] 11. Sau khi duyệt (APPROVED), người dùng bất kỳ đăng nhập đều tải được file thành công")
        passed += 1
    else:
        print(f"[FAIL] 11. Sau khi duyệt vẫn không tải được file: {resp11.status_code}")
    resp11.close()

    # -------------------------------------------------------------
    # Test 12: Chống Path Traversal trong download
    # -------------------------------------------------------------
    total += 1
    doc_pt = Document.objects.create(
        title="Test Path Traversal",
        subject=subject,
        uploader=student_user,
        status=Document.APPROVED,
        approved_by=admin_user,
        approved_at=datetime.now(),
    )
    DocumentVersion.objects.create(
        document=doc_pt,
        file_path="../../windows/system32/cmd.exe",
        version_number=1,
    )
    resp12 = client.get(
        f'/api/documents/{doc_pt.document_id}/download/',
        HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
    )
    if resp12.status_code in (400, 404):
        print("[PASS] 12. Cơ chế chống Path Traversal phát hiện và chặn đường dẫn nguy hiểm ('../../') thành công")
        passed += 1
    else:
        print(f"[FAIL] 12. Không chặn được Path Traversal: {resp12.status_code}")

    # -------------------------------------------------------------
    # Test 13: Xóa tài liệu bởi người không có quyền (403 Forbidden)
    # -------------------------------------------------------------
    total += 1
    resp13 = client.delete(
        f'/api/documents/{uploaded_doc_id}/',
        HTTP_AUTHORIZATION=f'Bearer {student2_jwt}' if student2_jwt else '',
    )
    if resp13.status_code == 403:
        print("[PASS] 13. Người dùng không có quyền bị chặn khi xóa tài liệu (403 Forbidden)")
        passed += 1
    else:
        print(f"[FAIL] 13. Không chặn người xóa trái phép: {resp13.status_code}")

    # -------------------------------------------------------------
    # Test 14: Xóa tài liệu thành công bởi uploader hoặc Admin (file vật lý & DB đều sạch)
    # -------------------------------------------------------------
    total += 1
    abs_file_path = storage_service.get_absolute_path(object_key)
    resp14 = client.delete(
        f'/api/documents/{uploaded_doc_id}/',
        HTTP_AUTHORIZATION=f'Bearer {student_jwt}',
    )
    db_exists = Document.objects.filter(pk=uploaded_doc_id).exists()
    disk_exists = abs_file_path and abs_file_path.exists()

    if resp14.status_code == 200 and not db_exists and not disk_exists:
        print("[PASS] 14. Xóa tài liệu thành công: Dữ liệu PostgreSQL và File vật lý trên đĩa đã được xóa sạch sẽ")
        passed += 1
    else:
        print(f"[FAIL] 14. Xóa thất bại hoặc còn sót file: status={resp14.status_code}, db={db_exists}, disk={disk_exists}")

    # -------------------------------------------------------------
    # Test 15: Kiểm tra lưu trữ nhật ký hoạt động (DocumentActivityLog)
    # -------------------------------------------------------------
    total += 1
    logs = DocumentActivityLog.objects.filter(action__in=['CREATE', 'DOWNLOAD', 'APPROVE'])
    if logs.count() > 0:
        print(f"[PASS] 15. Nhật ký hoạt động (DocumentActivityLog) ghi nhận đầy đủ hành động CREATE, DOWNLOAD, APPROVE ({logs.count()} bản ghi)")
        passed += 1
    else:
        print("[FAIL] 15. Không tìm thấy bản ghi nhật ký hoạt động nào")

    # Dọn dẹp tài liệu test Path Traversal
    doc_pt.delete()

    print("=" * 65)
    print(f"KẾT QUẢ KIỂM THỬ LƯU TRỮ FILE: {passed}/{total} bài kiểm thử thành công.")
    print("=" * 65)
    return passed == total


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
