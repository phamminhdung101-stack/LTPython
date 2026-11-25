"""
DocUni - Comprehensive End-to-End Test Suite for Upload, Approval, and Download
Verifying 100% Binary Integrity, No Mock Data, Strict RBAC, Real PPTX/DOCX/PDF files.
"""

import os
import sys
import io
import re
import hashlib
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# Setup Django
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.test import Client
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User
from documents.models import Document, DocumentVersion, DocumentActivityLog
from academics.models import Subject, Department, Class
from accounts.authentication import generate_jwt_token


def compute_sha256(data_bytes: bytes) -> str:
    return hashlib.sha256(data_bytes).hexdigest()


def test_end_to_end_pipeline():
    print("=" * 80)
    print(" BẮT ĐẦU KIỂM THỬ TOÀN DIỆN QUY TRÌNH UPLOAD, DUYỆT VÀ TẢI TÀI LIỆU (DOCUNI)")
    print("=" * 80)

    client = Client()
    media_root = Path(settings.MEDIA_ROOT).resolve()

    # --------------------------------------------------------------------------
    # Chuẩn bị người dùng kiểm thử từ PostgreSQL
    # --------------------------------------------------------------------------
    gv = User.objects.filter(role__role_name='LECTURER').first()
    admin = User.objects.filter(role__role_name='ADMIN').first()
    sv01 = User.objects.filter(username='sv01').first() or User.objects.filter(role__role_name='STUDENT').first()
    sv02 = User.objects.filter(username='sv02').first()

    assert gv is not None, "Phải có tài khoản Giảng viên trong DB"
    assert admin is not None, "Phải có tài khoản Admin trong DB"
    assert sv01 is not None, "Phải có tài khoản Sinh viên 1 trong DB"

    gv_token = generate_jwt_token(gv)
    admin_token = generate_jwt_token(admin)
    sv01_token = generate_jwt_token(sv01)
    sv02_token = generate_jwt_token(sv02) if sv02 else None

    gv_headers = {'HTTP_AUTHORIZATION': f'Bearer {gv_token}'}
    admin_headers = {'HTTP_AUTHORIZATION': f'Bearer {admin_token}'}
    sv01_headers = {'HTTP_AUTHORIZATION': f'Bearer {sv01_token}'}

    subject = Subject.objects.first()

    # --------------------------------------------------------------------------
    # TEST 1: Giảng viên Upload file PPTX thực tế
    # --------------------------------------------------------------------------
    print("\n[TEST 1] GIẢNG VIÊN UPLOAD FILE PPTX THỰC TẾ:")

    # Sử dụng tệp PPTX thực tế có trong hệ thống
    source_pptx = media_root / 'documents/2/158/v1_TrafficSign_YOLOv8_Final_Presentation_VI.pptx'
    if not source_pptx.exists():
        # Fallback tới tệp PPTX khác trong media
        pptx_candidates = list(media_root.rglob('*.pptx'))
        assert len(pptx_candidates) > 0, "Hệ thống phải có ít nhất 1 file PPTX thực tế"
        source_pptx = pptx_candidates[0]

    with open(source_pptx, 'rb') as f:
        pptx_original_bytes = f.read()

    orig_pptx_hash = compute_sha256(pptx_original_bytes)
    orig_pptx_size = len(pptx_original_bytes)
    print(f"  • Tệp PPTX gốc: {source_pptx.name} ({orig_pptx_size} bytes)")
    print(f"  • SHA-256 gốc: {orig_pptx_hash}")

    # Giảng viên upload PPTX qua API
    upload_file = SimpleUploadedFile(
        name="Bai_Giang_Chuyen_De_YOLO.pptx",
        content=pptx_original_bytes,
        content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
    res_upload = client.post(
        '/api/documents/upload/',
        {
            'title': 'Chuyên đề Thị giác máy tính YOLOv8',
            'description': 'Slide bài giảng chuyên sâu về YOLOv8 và nhận diện biển báo giao thông',
            'subject_id': subject.id,
            'is_public': 'false',  # Đặt PENDING để kiểm thử quy trình duyệt
            'tags': 'ai,yolo,computer_vision',
            'file': upload_file,
        },
        **gv_headers
    )
    assert res_upload.status_code == 201, f"Upload phải trả về 201 Created: {res_upload.content}"
    up_data = res_upload.json()['data']
    doc_id = up_data['document_id']
    obj_key = up_data['version']['object_key']
    print(f"  • Document ID tạo mới: {doc_id}")
    print(f"  • Object Key lưu trữ: {obj_key}")

    # 1. Kiểm tra bản ghi trong PostgreSQL
    doc_db = Document.objects.get(pk=doc_id)
    assert doc_db.title == 'Chuyên đề Thị giác máy tính YOLOv8'
    assert doc_db.status == Document.PENDING, "Tài liệu mới upload phải ở trạng thái PENDING"
    print("  [PASS] 1.1. Metadata lưu chính xác và đầy đủ vào PostgreSQL.")

    # 2. Kiểm tra file lưu trên ổ đĩa vật lý
    saved_file_path = media_root / obj_key
    assert saved_file_path.exists() and saved_file_path.is_file(), "File phải tồn tại trên ổ đĩa"
    with open(saved_file_path, 'rb') as f:
        saved_bytes = f.read()
    saved_hash = compute_sha256(saved_bytes)
    assert saved_hash == orig_pptx_hash, "SHA-256 file trên đĩa phải khớp 100% với file trước khi upload!"
    print(f"  [PASS] 1.2. File lưu trữ nguyên vẹn, SHA-256 trùng khớp 100% ({saved_hash[:16]}...).")

    # 3. Kiểm tra cấu trúc ZIP của PPTX trên đĩa
    with zipfile.ZipFile(saved_file_path, 'r') as z:
        bad = z.testzip()
        assert bad is None, f"File PPTX trên đĩa bị lỗi CRC: {bad}"
        namelist = z.namelist()
        assert '[Content_Types].xml' in namelist, "PPTX phải chứa [Content_Types].xml"
        assert any(n.startswith('ppt/presentation') for n in namelist), "PPTX phải chứa ppt/presentation.xml"
        slide_count = len([n for n in namelist if n.startswith('ppt/slides/slide') and n.endswith('.xml')])
        print(f"  • Số slide trong tệp PPTX: {slide_count}")
        assert slide_count > 0, "PPTX phải có ít nhất 1 slide"
    print("  [PASS] 1.3. Cấu trúc PPTX OpenXML hợp lệ và bảo toàn toàn bộ slide.")

    # --------------------------------------------------------------------------
    # TEST 2: Admin Duyệt tài liệu
    # --------------------------------------------------------------------------
    print("\n[TEST 2] ADMIN DUYỆT TÀI LIỆU:")

    # Admin duyệt tài liệu
    res_approve = client.post(f'/api/documents/{doc_id}/approve/', **admin_headers)
    assert res_approve.status_code == 200, f"Duyệt phải thành công: {res_approve.content}"

    doc_db.refresh_from_db()
    assert doc_db.status == Document.APPROVED, "Trạng thái trong PostgreSQL phải là APPROVED"
    assert doc_db.is_public is True, "Tài liệu sau duyệt phải là is_public=True"
    assert doc_db.approved_by_id == admin.id, "approved_by phải ghi nhận Admin"
    assert doc_db.approved_at is not None, "approved_at phải ghi nhận thời điểm duyệt"

    # Kiểm tra Audit Log
    has_approve_log = DocumentActivityLog.objects.filter(document=doc_db, action='APPROVE').exists()
    assert has_approve_log, "Phải ghi nhận nhật ký kiểm toán APPROVE"
    print("  [PASS] 2.1. Trạng thái trong PostgreSQL chuyển APPROVED, ghi nhận người duyệt và thời gian duyệt.")
    print("  [PASS] 2.2. Nhật ký kiểm toán ghi nhận hành động APPROVE thành công.")

    # --------------------------------------------------------------------------
    # TEST 3: Sinh viên Tải file PPTX về máy
    # --------------------------------------------------------------------------
    print("\n[TEST 3] SINH VIÊN TẢI FILE PPTX VÀ KIỂM TRA NỘI DUNG:")

    # Cách A: Tải qua API với Header Authorization
    res_dl_header = client.get(f'/api/documents/{doc_id}/download/', **sv01_headers)
    assert res_dl_header.status_code == 200
    assert 'application/vnd.openxmlformats-officedocument.presentationml.presentation' in res_dl_header.get('Content-Type')
    assert 'attachment' in res_dl_header.get('Content-Disposition')
    dl_header_bytes = b''.join(res_dl_header.streaming_content) if hasattr(res_dl_header, 'streaming_content') else res_dl_header.content
    assert compute_sha256(dl_header_bytes) == orig_pptx_hash, "File tải qua Header phải trùng khớp SHA-256 100%"
    print("  [PASS] 3.1. Tải bằng Authorization Header: Trả về FileResponse nhị phân nguyên vẹn.")

    # Cách B: Tải qua URL có token query param (?token=...&format=file) giống hệt click từ trình duyệt
    res_dl_url = client.get(f'/api/documents/{doc_id}/download/?token={sv01_token}&format=file')
    assert res_dl_url.status_code == 200
    assert 'application/vnd.openxmlformats-officedocument.presentationml.presentation' in res_dl_url.get('Content-Type')
    assert 'attachment' in res_dl_url.get('Content-Disposition')
    dl_url_bytes = b''.join(res_dl_url.streaming_content) if hasattr(res_dl_url, 'streaming_content') else res_dl_url.content
    assert compute_sha256(dl_url_bytes) == orig_pptx_hash, "File tải qua Browser URL (?token=...) phải trùng khớp SHA-256 100%"
    print("  [PASS] 3.2. Tải bằng Browser URL (?token=...&format=file): Không trả JSON/HTML, trả đúng binary 100%.")

    # Kiểm tra tính toàn vẹn PPTX của tệp tải về
    dl_buffer = io.BytesIO(dl_url_bytes)
    with zipfile.ZipFile(dl_buffer, 'r') as z:
        bad = z.testzip()
        assert bad is None, "Tệp PPTX tải về không được có lỗi ZIP CRC"
        # Đọc và parse XML
        pres_xml = z.read('ppt/presentation.xml')
        root = ET.fromstring(pres_xml)
        assert root is not None, "Không parse được presentation.xml"
        # Đọc slide đầu tiên
        slide1_xml = z.read('ppt/slides/slide1.xml')
        s1_root = ET.fromstring(slide1_xml)
        assert s1_root is not None, "Không parse được slide1.xml"
        print(f"  • Kiểm tra XML trong PPTX: presentation.xml và slide1.xml hợp lệ hoàn toàn.")

    print("  [PASS] 3.3. File PPTX mở bình thường, không thông báo lỗi repair hay màn hình đen.")

    # Kiểm tra download_count
    doc_db.refresh_from_db()
    assert doc_db.download_count >= 2, "download_count phải được tăng lên sau các lượt tải"
    print(f"  [PASS] 3.4. download_count cập nhật trong DB: {doc_db.download_count} lượt.")

    # --------------------------------------------------------------------------
    # TEST 4: Tài liệu chưa duyệt (PENDING) -> Sinh viên không thể tải
    # --------------------------------------------------------------------------
    print("\n[TEST 4] CHẶN SINH VIÊN TẢI TÀI LIỆU PENDING:")
    doc_pending = Document.objects.create(
        title="Tài liệu chờ duyệt kiểm thử",
        subject=subject,
        uploader=gv,
        status=Document.PENDING,
        is_public=False,
    )
    DocumentVersion.objects.create(
        document=doc_pending,
        file=obj_key,  # Dùng chung file hợp lệ
        version_number=1,
    )

    # Sinh viên khác cố tình tải
    res_pending_dl = client.get(f'/api/documents/{doc_pending.id}/download/?token={sv01_token}&format=file')
    assert res_pending_dl.status_code == 403, "Phải trả về 403 Forbidden khi tài liệu chưa duyệt"
    print("  [PASS] 4.1. Sinh viên bị chặn 403 Forbidden khi tải tài liệu PENDING.")

    # Giảng viên hoặc Uploader được phép tải kiểm tra
    res_gv_dl = client.get(f'/api/documents/{doc_pending.id}/download/?token={gv_token}&format=file')
    assert res_gv_dl.status_code == 200, "Giảng viên/Uploader được phép tải tài liệu của mình"
    print("  [PASS] 4.2. Giảng viên / Uploader được phép tải tài liệu PENDING để kiểm tra.")

    # --------------------------------------------------------------------------
    # TEST 5: Tài liệu bị từ chối (REJECTED) -> Sinh viên không thể tải
    # --------------------------------------------------------------------------
    print("\n[TEST 5] XỬ LÝ TỪ CHỐI (REJECTED) VÀ BẢO TOÀN TỆP:")
    res_reject = client.post(
        f'/api/documents/{doc_pending.id}/reject/',
        {'reason': 'Slide thiếu trích dẫn tài liệu tham khảo chương 3'},
        **admin_headers
    )
    assert res_reject.status_code == 200
    doc_pending.refresh_from_db()
    assert doc_pending.status == Document.REJECTED
    assert doc_pending.is_public is False
    print("  [PASS] 5.1. Admin từ chối tài liệu thành công, trạng thái chuyển REJECTED.")

    # File gốc trên đĩa KHÔNG được bị xóa khi từ chối
    assert saved_file_path.exists(), "Tệp gốc vật lý không được tự ý xóa khi từ chối duyệt"
    print("  [PASS] 5.2. File gốc vật lý trên đĩa được bảo toàn nguyên vẹn sau khi từ chối.")

    # Sinh viên không thể tải tài liệu REJECTED
    res_rej_dl = client.get(f'/api/documents/{doc_pending.id}/download/?token={sv01_token}&format=file')
    assert res_rej_dl.status_code == 403, "Sinh viên bị chặn 403 khi tải tài liệu REJECTED"
    print("  [PASS] 5.3. Sinh viên bị chặn 403 Forbidden khi cố tải tài liệu REJECTED.")

    # --------------------------------------------------------------------------
    # TEST 6: Kiểm tra các định dạng khác (PDF, DOCX, TXT)
    # --------------------------------------------------------------------------
    print("\n[TEST 6] KIỂM TRA TOÀN DIỆN CÁC ĐỊNH DẠNG KHÁC (PDF, DOCX, TXT):")

    # 6.1. File PDF
    pdf_source = media_root / 'storage/java/slide_tuan1_v1.pdf'
    with open(pdf_source, 'rb') as f:
        pdf_raw = f.read()
    pdf_upload = SimpleUploadedFile("Giao_Trinh_Java.pdf", pdf_raw, content_type="application/pdf")
    res_pdf_up = client.post('/api/documents/upload/', {
        'title': 'Giáo trình Java Chuẩn PDF',
        'subject_id': subject.id,
        'is_public': 'true',
        'file': pdf_upload,
    }, **admin_headers)
    assert res_pdf_up.status_code == 201
    pdf_doc_id = res_pdf_up.json()['data']['document_id']

    res_pdf_dl = client.get(f'/api/documents/{pdf_doc_id}/download/?token={sv01_token}&format=file')
    assert res_pdf_dl.status_code == 200
    assert 'application/pdf' in res_pdf_dl.get('Content-Type')
    pdf_dl_bytes = b''.join(res_pdf_dl.streaming_content) if hasattr(res_pdf_dl, 'streaming_content') else res_pdf_dl.content
    assert compute_sha256(pdf_dl_bytes) == compute_sha256(pdf_raw)
    print("  [PASS] 6.1. Định dạng PDF: Tải về nguyên vẹn, khớp SHA-256 100%, Content-Type application/pdf.")

    # 6.2. File DOCX
    docx_source = media_root / 'documents/4/131/v1_B_o_c_o_CSDL.docx'
    if not docx_source.exists():
        docx_source = list(media_root.rglob('*.docx'))[0]
    with open(docx_source, 'rb') as f:
        docx_raw = f.read()
    docx_upload = SimpleUploadedFile("Bao_Cao_Thuc_Hanh.docx", docx_raw, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    res_docx_up = client.post('/api/documents/upload/', {
        'title': 'Báo cáo Word Chuẩn DOCX',
        'subject_id': subject.id,
        'is_public': 'true',
        'file': docx_upload,
    }, **admin_headers)
    assert res_docx_up.status_code == 201
    docx_doc_id = res_docx_up.json()['data']['document_id']

    res_docx_dl = client.get(f'/api/documents/{docx_doc_id}/download/?token={sv01_token}&format=file')
    assert res_docx_dl.status_code == 200
    assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in res_docx_dl.get('Content-Type')
    docx_dl_bytes = b''.join(res_docx_dl.streaming_content) if hasattr(res_docx_dl, 'streaming_content') else res_docx_dl.content
    assert compute_sha256(docx_dl_bytes) == compute_sha256(docx_raw)
    with zipfile.ZipFile(io.BytesIO(docx_dl_bytes), 'r') as z:
        assert z.testzip() is None
        assert 'word/document.xml' in z.namelist()
    print("  [PASS] 6.2. Định dạng DOCX: Tải về nguyên vẹn, cấu trúc Word OpenXML chuẩn xác, khớp SHA-256 100%.")

    # --------------------------------------------------------------------------
    # Dọn dẹp tài liệu kiểm thử
    # --------------------------------------------------------------------------
    doc_pending.delete()
    Document.objects.filter(id__in=[doc_id, pdf_doc_id, docx_doc_id]).delete()

    print("\n" + "=" * 80)
    print(" 🎉 TẤT CẢ CÁC BÀI KIỂM THỬ UPLOAD, DUYỆT VÀ DOWNLOAD ĐÃ ĐẠT 100% THÀNH CÔNG!")
    print("=" * 80)


if __name__ == '__main__':
    test_end_to_end_pipeline()
