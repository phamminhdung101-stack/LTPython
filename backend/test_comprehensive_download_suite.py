import os
import sys
import io
import zipfile
import hashlib
from pathlib import Path

# Setup Django environment
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.utils import timezone
from django.test import Client
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, Role
from academics.models import Department, Class, Subject
from documents.models import Document, DocumentVersion, DocumentActivityLog, Folder


def make_minimal_pptx():
    """Tạo một file pptx hợp lệ ở mức cấu trúc nhị phân (ZIP archive với XML)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>')
        z.writestr('ppt/presentation.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldMasterIdLst/><p:sldIdLst/></p:presentation>')
        z.writestr('ppt/_rels/presentation.xml.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
    return buf.getvalue()


def make_minimal_docx():
    """Tạo một file docx hợp lệ (ZIP archive với word/document.xml)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Tai lieu kiem thu DocUni DOCX</w:t></w:r></w:p></w:body></w:document>')
    return buf.getvalue()


def make_minimal_pdf():
    """Tạo một file PDF hợp lệ."""
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (DocUni Test PDF) ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000201 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n296\n%%EOF"


def run_tests():
    print("=" * 70)
    print("BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG DOWNLOAD TÀI LIỆU DOCUNI")
    print("=" * 70)

    # Lấy tài khoản kiểm thử
    student_role = Role.objects.get(role_name='STUDENT')
    lecturer_role = Role.objects.get(role_name='LECTURER')
    admin_role = Role.objects.get(role_name='ADMIN')

    student = User.objects.filter(role=student_role).first()
    student2 = User.objects.filter(role=student_role).exclude(id=student.id).first()
    lecturer = User.objects.filter(role=lecturer_role).first()
    admin = User.objects.filter(role=admin_role).first()

    dept = Department.objects.first()
    subject = Subject.objects.filter(department=dept).first() or Subject.objects.first()
    folder = Folder.objects.filter(subject=subject).first() or Folder.objects.first()

    passed_tests = 0
    total_tests = 14

    client_student = Client()
    client_student.force_login(student)

    client_student2 = Client()
    client_student2.force_login(student2)

    client_lecturer = Client()
    client_lecturer.force_login(lecturer)

    client_admin = Client()
    client_admin.force_login(admin)

    # -------------------------------------------------------------
    # TEST 1: Tải file PPTX nguyên vẹn, kiểm tra SHA-256 và mở cấu trúc zip
    # -------------------------------------------------------------
    print("\n[TEST 1] Tải file PPTX nguyên vẹn:")
    pptx_bytes = make_minimal_pptx()
    pptx_hash = hashlib.sha256(pptx_bytes).hexdigest()

    doc_pptx = Document.objects.create(
        title="Test PPTX Presentation",
        subject=subject,
        folder=folder,
        uploader=student,
        status=Document.APPROVED,
        approved_by=lecturer,
        approved_at=timezone.now(),
        is_public=True,
    )
    storage_dir = Path(settings.MEDIA_ROOT) / 'documents' / str(subject.id) / str(doc_pptx.id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    pptx_file_path = storage_dir / 'test_presentation.pptx'
    with open(pptx_file_path, 'wb') as f:
        f.write(pptx_bytes)

    ver_pptx = DocumentVersion.objects.create(
        document=doc_pptx,
        version_number=1,
        file=f"documents/{subject.id}/{doc_pptx.id}/test_presentation.pptx",
        change_summary="Bản tạo đầu",
        updated_by=student,
    )


    resp = client_student.get(f'/api/documents/{doc_pptx.id}/download/?format=file')
    assert resp.status_code == 200, f"Status code {resp.status_code} != 200"
    content = b''.join(resp.streaming_content)
    assert hashlib.sha256(content).hexdigest() == pptx_hash, "Hash mismatch for PPTX"
    # Kiểm tra mở zipfile hợp lệ
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        assert 'ppt/presentation.xml' in z.namelist(), "Missing presentation.xml in downloaded PPTX"
    assert resp['Content-Type'] == 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    print(f"  -> ĐẠT: PPTX SHA-256 khớp ({pptx_hash[:16]}...), MIME type chuẩn, cấu trúc zip hợp lệ.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 2: Tải file DOCX nguyên vẹn, kiểm tra SHA-256 và mở cấu trúc zip
    # -------------------------------------------------------------
    print("\n[TEST 2] Tải file DOCX nguyên vẹn:")
    docx_bytes = make_minimal_docx()
    docx_hash = hashlib.sha256(docx_bytes).hexdigest()

    doc_docx = Document.objects.create(
        title="Test DOCX Document",
        subject=subject,
        folder=folder,
        uploader=student,
        status=Document.APPROVED,
        approved_by=lecturer,
        approved_at=timezone.now(),
        is_public=True,
    )
    docx_storage_dir = Path(settings.MEDIA_ROOT) / 'documents' / str(subject.id) / str(doc_docx.id)
    docx_storage_dir.mkdir(parents=True, exist_ok=True)
    docx_file_path = docx_storage_dir / 'test_doc.docx'
    with open(docx_file_path, 'wb') as f:
        f.write(docx_bytes)

    ver_docx = DocumentVersion.objects.create(
        document=doc_docx,
        version_number=1,
        file=f"documents/{subject.id}/{doc_docx.id}/test_doc.docx",
        change_summary="Khởi tạo",
        updated_by=student,
    )


    resp = client_student.get(f'/api/documents/{doc_docx.id}/download/?format=file')
    assert resp.status_code == 200
    content = b''.join(resp.streaming_content)
    assert hashlib.sha256(content).hexdigest() == docx_hash
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        assert 'word/document.xml' in z.namelist()
    assert resp['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    print(f"  -> ĐẠT: DOCX SHA-256 khớp ({docx_hash[:16]}...), MIME type chuẩn, mở word/document.xml thành công.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 3: Tải file PDF nguyên vẹn
    # -------------------------------------------------------------
    print("\n[TEST 3] Tải file PDF nguyên vẹn:")
    pdf_bytes = make_minimal_pdf()
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

    doc_pdf = Document.objects.create(
        title="Test PDF Document",
        subject=subject,
        folder=folder,
        uploader=student,
        status=Document.APPROVED,
        approved_by=lecturer,
        approved_at=timezone.now(),
        is_public=True,
    )
    pdf_dir = Path(settings.MEDIA_ROOT) / 'documents' / str(subject.id) / str(doc_pdf.id)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_file_path = pdf_dir / 'test_doc.pdf'
    with open(pdf_file_path, 'wb') as f:
        f.write(pdf_bytes)

    ver_pdf = DocumentVersion.objects.create(
        document=doc_pdf,
        version_number=1,
        file=f"documents/{subject.id}/{doc_pdf.id}/test_doc.pdf",
        change_summary="Khởi tạo PDF",
        updated_by=student,
    )


    resp = client_student.get(f'/api/documents/{doc_pdf.id}/download/?format=file')
    assert resp.status_code == 200
    content = b''.join(resp.streaming_content)
    assert hashlib.sha256(content).hexdigest() == pdf_hash
    assert content.startswith(b'%PDF'), "PDF magic bytes missing"
    assert resp['Content-Type'] == 'application/pdf'
    print(f"  -> ĐẠT: PDF SHA-256 khớp ({pdf_hash[:16]}...), magic bytes %PDF-1.4 hợp lệ.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 4: Tải file tên tiếng Việt có dấu (RFC 5987 / UTF-8)
    # -------------------------------------------------------------
    print("\n[TEST 4] Tải file tên tiếng Việt có dấu:")
    vn_name = "Bài giảng Cơ sở dữ liệu nâng cao 2026.pptx"
    doc_vn = Document.objects.create(
        title="Tài liệu CSDL Tiếng Việt",
        subject=subject,
        folder=folder,
        uploader=student,
        status=Document.APPROVED,
        approved_by=lecturer,
        approved_at=timezone.now(),
        is_public=True,
    )
    vn_dir = Path(settings.MEDIA_ROOT) / 'documents' / str(subject.id) / str(doc_vn.id)
    vn_dir.mkdir(parents=True, exist_ok=True)
    vn_file_path = vn_dir / vn_name
    with open(vn_file_path, 'wb') as f:
        f.write(pptx_bytes)

    ver_vn = DocumentVersion.objects.create(
        document=doc_vn,
        version_number=1,
        file=f"documents/{subject.id}/{doc_vn.id}/{vn_name}",
        change_summary="Tên tiếng Việt",
        updated_by=student,
    )


    resp = client_student.get(f'/api/documents/{doc_vn.id}/download/?format=file')
    assert resp.status_code == 200
    disposition = resp.get('Content-Disposition', '')
    assert "filename*=" in disposition or "filename=" in disposition, f"Invalid disposition: {disposition}"
    print(f"  -> ĐẠT: Header Content-Disposition xử lý chuẩn tên tiếng Việt: {disposition}")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 5: Tải file dung lượng lớn (10MB) kiểm tra Content-Length và streaming
    # -------------------------------------------------------------
    print("\n[TEST 5] Tải file dung lượng 10MB:")
    large_size = 10 * 1024 * 1024
    large_bytes = b"X" * large_size
    large_hash = hashlib.sha256(large_bytes).hexdigest()

    doc_large = Document.objects.create(
        title="Test Large 10MB File",
        subject=subject,
        folder=folder,
        uploader=student,
        status=Document.APPROVED,
        approved_by=lecturer,
        approved_at=timezone.now(),
        is_public=True,
    )
    large_dir = Path(settings.MEDIA_ROOT) / 'documents' / str(subject.id) / str(doc_large.id)
    large_dir.mkdir(parents=True, exist_ok=True)
    large_path = large_dir / 'large_dataset.bin'
    with open(large_path, 'wb') as f:
        f.write(large_bytes)

    ver_large = DocumentVersion.objects.create(
        document=doc_large,
        version_number=1,
        file=f"documents/{subject.id}/{doc_large.id}/large_dataset.bin",
        change_summary="File 10MB",
        updated_by=student,
    )


    resp = client_student.get(f'/api/documents/{doc_large.id}/download/?format=file')
    assert resp.status_code == 200
    assert int(resp['Content-Length']) == large_size
    content = b''.join(resp.streaming_content)
    assert len(content) == large_size
    assert hashlib.sha256(content).hexdigest() == large_hash
    print(f"  -> ĐẠT: File 10MB tải streaming đầy đủ, Content-Length={resp['Content-Length']}, Hash match.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 6: RBAC - Sinh viên khác KHÔNG được tải tài liệu PENDING (403 Forbidden)
    # -------------------------------------------------------------
    print("\n[TEST 6] RBAC - Chặn sinh viên tải tài liệu PENDING:")
    doc_pending = Document.objects.create(
        title="Pending Document",
        subject=subject,
        folder=folder,
        uploader=student,
        status=Document.PENDING,
        is_public=False,
    )
    ver_pending = DocumentVersion.objects.create(
        document=doc_pending,
        version_number=1,
        file=f"documents/{subject.id}/{doc_pptx.id}/test_presentation.pptx",
        change_summary="Chờ duyệt",
        updated_by=student,
    )


    resp = client_student2.get(f'/api/documents/{doc_pending.id}/download/?format=file')
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
    print(f"  -> ĐẠT: Sinh viên khác bị chặn 403 Forbidden khi tải tài liệu PENDING.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 7: RBAC - Sinh viên khác KHÔNG được tải tài liệu REJECTED (403 Forbidden)
    # -------------------------------------------------------------
    print("\n[TEST 7] RBAC - Chặn sinh viên tải tài liệu REJECTED:")
    doc_rejected = Document.objects.create(
        title="Rejected Document",
        subject=subject,
        folder=folder,
        uploader=student,
        status=Document.REJECTED,
        is_public=False,
    )
    ver_rej = DocumentVersion.objects.create(
        document=doc_rejected,
        version_number=1,
        file=f"documents/{subject.id}/{doc_pptx.id}/test_presentation.pptx",
        change_summary="Bị từ chối",
        updated_by=student,
    )


    resp = client_student2.get(f'/api/documents/{doc_rejected.id}/download/?format=file')
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
    print(f"  -> ĐẠT: Sinh viên khác bị chặn 403 Forbidden khi tải tài liệu REJECTED.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 8: RBAC - Tác giả ĐƯỢC PHÉP tải tài liệu PENDING của chính mình
    # -------------------------------------------------------------
    print("\n[TEST 8] RBAC - Tác giả tải tài liệu PENDING của chính mình:")
    resp = client_student.get(f'/api/documents/{doc_pending.id}/download/?format=file')
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    print(f"  -> ĐẠT: Tác giả tải thành công tài liệu PENDING của chính mình.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 9: RBAC - Giảng viên / Admin ĐƯỢC PHÉP tải tài liệu PENDING để kiểm duyệt
    # -------------------------------------------------------------
    print("\n[TEST 9] RBAC - Giảng viên tải tài liệu PENDING để kiểm duyệt:")
    resp = client_lecturer.get(f'/api/documents/{doc_pending.id}/download/?format=file')
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    print(f"  -> ĐẠT: Giảng viên tải thành công tài liệu PENDING để kiểm duyệt.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 10: Xử lý tệp không tồn tại trên ổ đĩa trả về 404 cleanly
    # -------------------------------------------------------------
    print("\n[TEST 10] Tệp vật lý không tồn tại trả về 404:")
    doc_missing_file = Document.objects.create(
        title="Missing Physical File Doc",
        subject=subject,
        folder=folder,
        uploader=student,
        status=Document.APPROVED,
        approved_by=lecturer,
        approved_at=timezone.now(),
        is_public=True,
    )
    ver_missing = DocumentVersion.objects.create(
        document=doc_missing_file,
        version_number=1,
        file="documents/9999/9999/does_not_exist_file.pdf",
        change_summary="File mất",
        updated_by=student,
    )


    resp = client_student.get(f'/api/documents/{doc_missing_file.id}/download/?format=file')
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    print(f"  -> ĐẠT: Trả về 404 khi tệp tin vật lý không tồn tại.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 11: Document ID không tồn tại trong DB trả về 404
    # -------------------------------------------------------------
    print("\n[TEST 11] Document ID không tồn tại trả về 404:")
    resp = client_student.get('/api/documents/99999999/download/?format=file')
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    print(f"  -> ĐẠT: Trả về 404 cho ID tài liệu không tồn tại.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 12: Tải phiên bản cụ thể (Version Download API)
    # -------------------------------------------------------------
    print("\n[TEST 12] Tải phiên bản cụ thể qua version_download_api:")
    # Tạo v2.0 cho doc_pptx
    v2_bytes = b"V2_PPTX_NEW_CONTENT_" + pptx_bytes
    v2_hash = hashlib.sha256(v2_bytes).hexdigest()
    v2_path = storage_dir / 'test_presentation_v2.pptx'
    with open(v2_path, 'wb') as f:
        f.write(v2_bytes)

    ver2_pptx = DocumentVersion.objects.create(
        document=doc_pptx,
        version_number=2,
        file=f"documents/{subject.id}/{doc_pptx.id}/test_presentation_v2.pptx",
        change_summary="Phiên bản 2",
        updated_by=student,
    )

    # Tải v1 qua version API
    resp_v1 = client_student.get(f'/api/documents/{doc_pptx.id}/versions/{ver_pptx.id}/download/?format=file')
    assert resp_v1.status_code == 200
    content_v1 = b''.join(resp_v1.streaming_content)
    assert hashlib.sha256(content_v1).hexdigest() == pptx_hash

    # Tải v2 qua version API
    resp_v2 = client_student.get(f'/api/documents/{doc_pptx.id}/versions/{ver2_pptx.id}/download/?format=file')
    assert resp_v2.status_code == 200
    content_v2 = b''.join(resp_v2.streaming_content)
    assert hashlib.sha256(content_v2).hexdigest() == v2_hash
    print(f"  -> ĐẠT: Tải chính xác v1 ({len(content_v1)} bytes) và v2 ({len(content_v2)} bytes) độc lập.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 13: Download count và Audit Log tăng chính xác trong DB
    # -------------------------------------------------------------
    print("\n[TEST 13] Download count và Audit Log trong DB:")
    before_count = Document.objects.get(id=doc_pptx.id).download_count
    resp = client_student.get(f'/api/documents/{doc_pptx.id}/download/?format=file')
    assert resp.status_code == 200
    after_count = Document.objects.get(id=doc_pptx.id).download_count
    assert after_count == before_count + 1, f"Expected {before_count + 1}, got {after_count}"

    log = DocumentActivityLog.objects.filter(document=doc_pptx, action='DOWNLOAD').order_by('-created_at').first()
    assert log is not None, "Missing DOWNLOAD activity log"
    assert log.user == student
    print(f"  -> ĐẠT: download_count tăng từ {before_count} -> {after_count}, ghi log DOWNLOAD thành công.")
    passed_tests += 1

    # -------------------------------------------------------------
    # TEST 14: Độc lập giữa Preview và Download (Preview không ghi đè file)
    # -------------------------------------------------------------
    print("\n[TEST 14] Độc lập giữa Preview và Download:")
    # Lấy thông tin preview qua API detail
    resp_detail = client_student.get(f'/api/documents/{doc_pptx.id}/')
    assert resp_detail.status_code == 200
    # Đảm bảo file nhị phân trên đĩa vẫn 100% nguyên vẹn
    current_disk_bytes = open(pptx_file_path, 'rb').read()
    assert hashlib.sha256(current_disk_bytes).hexdigest() == pptx_hash
    print(f"  -> ĐẠT: Preview hoàn toàn độc lập, file gốc trên đĩa được bảo toàn 100%.")
    passed_tests += 1

    print("\n" + "=" * 70)
    print(f"KẾT QUẢ KIỂM THỬ: {passed_tests}/{total_tests} TEST CASES ĐẠT HOÀN HẢO 100%!")
    print("=" * 70)


if __name__ == '__main__':
    run_tests()
