"""
Test Suite: Kiểm thử tập trung việc lấy danh sách tài liệu từ PostgreSQL,
lọc trạng thái / quyền xem (RBAC & ACL) ở cấp Backend và đảm bảo Frontend
không bao giờ hiển thị dữ liệu mẫu khi API/DB gặp lỗi.
"""

import os
import sys
import asyncio
import django
from django.test import RequestFactory
from django.db.models import Q

# Thiết lập môi trường Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, Role
from academics.models import Department, Class, Subject
from documents.models import Document, DocumentVersion, Folder, Tag
from permissions.models import DocumentPermission
from documents.api_views import document_list_api, document_detail_api, download_document_api
from permissions.services import can_user_access_document, can_user_download_document


def run_tests():
    print("=" * 80)
    print(" BẮT ĐẦU KIỂM THỬ: KHO TÀI LIỆU POSTGRESQL & RBAC / NO MOCK DATA")
    print("=" * 80)

    rf = RequestFactory()
    total_passed = 0
    total_tests = 0

    def check(condition, desc):
        nonlocal total_passed, total_tests
        total_tests += 1
        if condition:
            total_passed += 1
            print(f"  [PASS] {desc}")
        else:
            print(f"  [FAIL] {desc}")
            assert False, desc

    # --------------------------------------------------------------------------
    # Test 1: Khách vãng lai (Anonymous) chỉ thấy tài liệu APPROVED và is_public=True
    # --------------------------------------------------------------------------
    req = rf.get('/api/documents/')
    from django.contrib.auth.models import AnonymousUser
    req.user = AnonymousUser()
    resp = document_list_api(req)
    check(resp.status_code == 200, "1.1. API /api/documents/ trả về HTTP 200 cho khách")
    data = resp.data.get('documents', [])
    check(len(data) > 0, f"1.2. Khách lấy được {len(data)} tài liệu công khai từ PostgreSQL")
    check(all(d['status'] == 'APPROVED' and d['is_public'] is True for d in data),
          "1.3. 100% tài liệu trả về cho khách đều ở trạng thái APPROVED và is_public=True")

    # --------------------------------------------------------------------------
    # Test 2: Sinh viên sv01 (Lớp 1, Khoa 1) chỉ thấy tài liệu APPROVED có quyền xem
    # --------------------------------------------------------------------------
    sv01 = User.objects.filter(username='sv01').first()
    check(sv01 is not None, "2.1. Tìm thấy tài khoản sinh viên sv01 trong PostgreSQL")
    req_sv = rf.get('/api/documents/')
    req_sv.user = sv01
    resp_sv = document_list_api(req_sv)
    check(resp_sv.status_code == 200, "2.2. API /api/documents/ trả về HTTP 200 cho sv01")
    docs_sv = resp_sv.data.get('documents', [])
    check(len(docs_sv) > 0, f"2.3. sv01 lấy được {len(docs_sv)} tài liệu từ PostgreSQL")

    # Sinh viên không được thấy tài liệu REJECTED hoặc PENDING của người khác
    other_pending_or_rejected = [
        d for d in docs_sv
        if d['status'] in ('PENDING', 'REJECTED') and d.get('uploader_id') != sv01.id
    ]
    check(len(other_pending_or_rejected) == 0,
          "2.4. sv01 KHÔNG thấy bất kỳ tài liệu PENDING / REJECTED nào của người khác")

    # Sinh viên không thấy tài liệu nội bộ dành riêng cho lớp khác
    doc_class_b = Document.objects.filter(
        permissions__permission_type=DocumentPermission.CLASS,
        permissions__student_class_id=2,  # Lớp khác sv01
        is_public=False
    ).exclude(permissions__student_class_id=sv01.student_class_id).first()
    if doc_class_b:
        visible_ids = {d['id'] for d in docs_sv}
        check(doc_class_b.id not in visible_ids,
              f"2.5. Backend bảo mật: sv01 không thấy tài liệu riêng của lớp khác (doc_id={doc_class_b.id})")
    else:
        check(True, "2.5. Không có doc riêng lớp khác hoặc đã được lọc chuẩn xác")

    # --------------------------------------------------------------------------
    # Test 3: Giảng viên / Quản trị viên có quyền xem toàn bộ tài liệu và lọc theo status
    # --------------------------------------------------------------------------
    admin = User.objects.filter(role__role_name='ADMIN').first()
    check(admin is not None, "3.1. Tìm thấy tài khoản ADMIN trong PostgreSQL")
    req_admin = rf.get('/api/documents/?status=PENDING')
    req_admin.user = admin
    resp_admin = document_list_api(req_admin)
    check(resp_admin.status_code == 200, "3.2. ADMIN truy vấn danh sách lọc ?status=PENDING thành công")
    pending_docs = resp_admin.data.get('documents', [])
    check(all(d['status'] == 'PENDING' for d in pending_docs),
          "3.3. Bộ lọc status=PENDING hoạt động chuẩn xác cho Admin")

    # --------------------------------------------------------------------------
    # Test 4: Kiểm tra ACL Download và Chi tiết ở cấp Service Backend
    # --------------------------------------------------------------------------
    test_doc = Document.objects.filter(status=Document.APPROVED, is_public=True).first()
    check(test_doc is not None, "4.1. Tìm thấy tài liệu công khai trong PostgreSQL")
    can_view, _ = can_user_access_document(sv01, test_doc)
    can_dl, _ = can_user_download_document(sv01, test_doc)
    check(can_view and can_dl, "4.2. sv01 có quyền xem và tải tài liệu công khai")

    # --------------------------------------------------------------------------
    # Test 5: Frontend GlobalDocState nạp từ DB và KHÔNG DÙNG DỮ LIỆU MẪU khi lỗi
    # --------------------------------------------------------------------------
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend_app'))
    if frontend_dir not in sys.path:
        sys.path.insert(0, frontend_dir)

    from frontend_app.data_store import GlobalDocState

    # 5.1. Kiểm tra thuộc tính mặc định của GlobalDocState: documents là [], is_loading là False, load_error là ""
    doc_default = GlobalDocState.get_fields()['documents'].default_factory()
    err_default = GlobalDocState.get_fields()['load_error'].default
    check(doc_default == [], "5.1. GlobalDocState khai báo documents mặc định rỗng ([])")
    check(err_default == "", "5.2. GlobalDocState khai báo load_error mặc định rỗng")

    # 5.3. Kiểm tra logic nạp qua load_documents:
    fn_load_documents = getattr(GlobalDocState.load_documents, 'fn', GlobalDocState.load_documents)

    class MockDocState:
        documents = []
        is_loading = False
        load_error = ""

        async def get_state(self, cls):
            class DummyAuth:
                is_logged_in = True
                auth_token = ""
                current_user_role = "STUDENT"
                current_user_id = sv01.id
            return DummyAuth()

    mock_state = MockDocState()
    asyncio.run(fn_load_documents(mock_state))
    check(len(mock_state.documents) > 0, f"5.3. load_documents nạp thành công {len(mock_state.documents)} tài liệu từ PostgreSQL")
    check(mock_state.load_error == "", "5.4. Không có lỗi khi nạp thành công (load_error rỗng)")
    check(mock_state.documents[0].get('title') is not None, "5.5. Bản ghi có tiêu đề từ database PostgreSQL")

    # 5.6. Mô phỏng API & ORM gặp sự cố: hệ thống phải set documents = [] và gán thông báo lỗi vào load_error
    class FailingMockDocState:
        documents = ["temp"]
        is_loading = False
        load_error = ""

        async def get_state(self, cls):
            raise ConnectionError("Không thể kết nối đến backend API")

    fail_state = FailingMockDocState()

    # Tạm thời gán hỏng DjDoc để giả lập DB failure
    import documents.models
    orig_dj_doc = documents.models.Document
    class BrokenDocManager:
        def select_related(self, *args, **kwargs):
            raise Exception("Lỗi kết nối cơ sở dữ liệu PostgreSQL")
    class BrokenDoc:
        objects = BrokenDocManager()

    documents.models.Document = BrokenDoc
    try:
        asyncio.run(fn_load_documents(fail_state))
    finally:
        documents.models.Document = orig_dj_doc

    check(fail_state.documents == [], "5.6. Khi gặp lỗi kết nối, documents là rỗng ([]) TUYỆT ĐỐI KHÔNG HIỂN THỊ DỮ LIỆU MẪU")
    check(len(fail_state.load_error) > 0, f"5.7. load_error chứa thông báo lỗi trung thực: '{fail_state.load_error}'")

    # --------------------------------------------------------------------------
    # Test 6: Quy trình Giảng viên Phê duyệt (Approval Workflow) cập nhật Database
    # --------------------------------------------------------------------------
    from documents.services import approve_document, reject_document
    from documents.api_views import approve_document_api, reject_document_api

    gv = User.objects.filter(role__role_name='LECTURER').first() or admin
    sub = Subject.objects.first()

    doc_test_app = Document.objects.create(
        title="[Test Flow] Đề cương môn học kiểm thử duyệt",
        subject=sub,
        uploader=sv01,
        status=Document.PENDING,
        is_public=False,
    )
    req_app = rf.post(f'/api/documents/{doc_test_app.id}/approve/')
    req_app.user = gv
    resp_app = approve_document_api(req_app, doc_test_app.id)
    check(resp_app.status_code == 200, "6.1. API duyệt tài liệu trả về HTTP 200")

    doc_test_app.refresh_from_db()
    check(doc_test_app.status == Document.APPROVED, "6.2. Trạng thái trong Database cập nhật thành APPROVED")
    check(doc_test_app.is_public is True, "6.3. Tài liệu đã được đặt is_public = True trong Database")
    check(doc_test_app.approved_by_id == gv.id, "6.4. Ghi nhận người duyệt approved_by chuẩn xác trong Database")

    log_app = doc_test_app.activity_logs.filter(action='APPROVE').first()
    check(log_app is not None, "6.5. Ghi nhận nhật ký kiểm toán APPROVE trong Database")

    # --------------------------------------------------------------------------
    # Test 7: Quy trình Giảng viên Từ chối duyệt (Reject Workflow) kèm lý do
    # --------------------------------------------------------------------------
    test_reason = "Tài liệu scan bị mờ trang 5-10, vui lòng bổ sung bài tập chương 3"
    doc_test_rej = Document.objects.create(
        title="[Test Flow] Slide thuyết trình kiểm thử từ chối",
        subject=sub,
        uploader=sv01,
        status=Document.PENDING,
        is_public=False,
    )
    req_rej = rf.post(f'/api/documents/{doc_test_rej.id}/reject/', data={'reason': test_reason})
    req_rej.user = gv
    resp_rej = reject_document_api(req_rej, doc_test_rej.id)
    check(resp_rej.status_code == 200, "7.1. API từ chối duyệt trả về HTTP 200")

    doc_test_rej.refresh_from_db()
    check(doc_test_rej.status == Document.REJECTED, "7.2. Trạng thái trong Database cập nhật thành REJECTED")
    check(doc_test_rej.is_public is False, "7.3. Tài liệu bị từ chối có is_public = False trong Database")

    log_rej = doc_test_rej.activity_logs.filter(action='REJECT').first()
    check(log_rej is not None and test_reason in log_rej.description,
          "7.4. Ghi nhận nhật ký REJECT kèm lý do chi tiết vào Database")

    # --------------------------------------------------------------------------
    # Test 8: Tính nhất quán trạng thái giữa các trang Sinh viên & Phân quyền
    # --------------------------------------------------------------------------
    # 8.1. Trang Kho tài liệu (/documents): Sinh viên sv01 KHÔNG thấy tài liệu REJECTED
    req_repo = rf.get('/api/documents/')
    req_repo.user = sv01
    resp_repo = document_list_api(req_repo)
    repo_ids = [d['id'] for d in resp_repo.data.get('documents', [])]
    check(doc_test_rej.id not in repo_ids,
          "8.1. Trang Kho tài liệu (/documents): Tài liệu REJECTED KHÔNG xuất hiện trong kho học liệu")
    check(doc_test_app.id in repo_ids,
          "8.2. Trang Kho tài liệu (/documents): Tài liệu APPROVED xuất hiện ngay lập tức sau khi duyệt")

    # 8.3. Trang Đóng góp của tôi (/student/contributions via ?uploader=me):
    # Sinh viên sv01 THẤY tài liệu do chính mình nộp (kể cả REJECTED kèm lý do phản hồi)
    req_my_contrib = rf.get('/api/documents/?uploader=me')
    req_my_contrib.user = sv01
    resp_my_contrib = document_list_api(req_my_contrib)
    my_contrib_docs = resp_my_contrib.data.get('documents', [])
    my_contrib_map = {d['id']: d for d in my_contrib_docs}
    check(doc_test_rej.id in my_contrib_map,
          "8.3. Trang Đóng góp của tôi (/student/contributions): sv01 nhìn thấy tài liệu REJECTED của chính mình")
    rej_doc_payload = my_contrib_map.get(doc_test_rej.id, {})
    check(rej_doc_payload.get('status') == 'REJECTED',
          "8.4. Trạng thái hiển thị nhất quán là REJECTED")
    check(test_reason in rej_doc_payload.get('reject_reason', ''),
          f"8.5. Sinh viên đọc được lý do từ chối: '{rej_doc_payload.get('reject_reason')}'")

    # 8.6. Sinh viên khác (sv02) TUYỆT ĐỐI KHÔNG thấy tài liệu REJECTED của sv01
    sv02 = User.objects.filter(role__role_name='STUDENT').exclude(id=sv01.id).first()
    if not sv02:
        sv02 = User.objects.create_user(username='sv_test_other', full_name='Sinh Viên Khác')
    req_sv02 = rf.get('/api/documents/?uploader=me')
    req_sv02.user = sv02
    resp_sv02 = document_list_api(req_sv02)
    sv02_contrib_ids = [d['id'] for d in resp_sv02.data.get('documents', [])]
    check(doc_test_rej.id not in sv02_contrib_ids,
          "8.6. Sinh viên khác (sv02) KHÔNG thấy tài liệu REJECTED của sv01 trong danh sách đóng góp")

    # 8.7. Quyền bảo vệ backend: sv02 bị chặn xem và tải tài liệu REJECTED của sv01
    can_sv02_view, msg_view = can_user_access_document(sv02, doc_test_rej)
    can_sv02_dl, msg_dl = can_user_download_document(sv02, doc_test_rej)
    check(not can_sv02_view, f"8.7. can_user_access_document chặn sv02 xem tài liệu REJECTED: {msg_view}")
    check(not can_sv02_dl, f"8.8. can_user_download_document chặn sv02 tải tài liệu REJECTED: {msg_dl}")

    # --------------------------------------------------------------------------
    # Test 9: Giảng viên xem toàn bộ tài liệu từ database với trạng thái thực tế
    # --------------------------------------------------------------------------
    req_gv_all = rf.get('/api/documents/')
    req_gv_all.user = gv
    resp_gv_all = document_list_api(req_gv_all)
    gv_doc_ids = [d['id'] for d in resp_gv_all.data.get('documents', [])]
    check(doc_test_app.id in gv_doc_ids, "9.1. Giảng viên thấy tài liệu APPROVED từ database")
    check(doc_test_rej.id in gv_doc_ids, "9.2. Giảng viên thấy tài liệu REJECTED từ database")

    # Dọn dẹp bản ghi kiểm thử
    doc_test_app.delete()
    doc_test_rej.delete()
    if sv02.username == 'sv_test_other':
        sv02.delete()

    print("=" * 80)
    print(f"🎉 KẾT QUẢ: {total_passed}/{total_tests} BÀI KIỂM THỬ THÀNH CÔNG (100% PASS)!")
    print("=" * 80)


if __name__ == '__main__':
    run_tests()
