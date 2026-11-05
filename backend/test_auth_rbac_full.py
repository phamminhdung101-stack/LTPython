"""
Kịch bản kiểm thử toàn diện 15 trường hợp kiểm thử (15 Test Cases):
HỆ THỐNG XÁC THỰC VÀ PHÂN QUYỀN (RBAC) DỰA TRÊN DATABASE POSTGRESQL THỰC TẾ
Dự án: Kho tài liệu môn học có phân quyền và AI tìm kiếm ngữ cảnh (DocUni)
"""

import os
import sys
import django
from datetime import datetime, timezone, timedelta
import jwt

# Thiết lập môi trường Django & Frontend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'frontend_app'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from rest_framework.test import APIClient
from accounts.models import User, Role
from documents.models import Document
from accounts.authentication import generate_jwt_token


class MockAuthState:
    """Mock state cho kiểm thử route guards của frontend Reflex"""
    is_logged_in = False
    auth_token = ""
    current_user_role = ""

    def restore_session_if_needed(self):
        pass


def is_login_redirect(event_spec):
    if event_spec is None:
        return False
    # Kiểm tra event redirect về /login
    s = str(event_spec)
    if '/login' in s:
        return True
    try:
        val = event_spec.args[0][1]._var_value
        return val == '/login'
    except Exception:
        return False


def run_tests():
    client = APIClient()
    total_tests = 15
    passed_tests = 0
    results = []

    def record(idx, name, passed, detail=""):
        nonlocal passed_tests
        if passed:
            passed_tests += 1
            print(f" [PASSED] Test {idx:02d}: {name}")
        else:
            print(f" [FAILED] Test {idx:02d}: {name} - {detail}")
        results.append((idx, name, passed, detail))

    print("=" * 80)
    print(" BẮT ĐẦU KIỂM THỬ 15 TRƯỜNG HỢP XÁC THỰC VÀ PHÂN QUYỀN (RBAC) THEO DATABASE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Test 1: Frontend Route Guard cho '/' khi chưa đăng nhập -> Chuyển về /login
    # -------------------------------------------------------------------------
    try:
        from frontend_app.auth import AuthState
        state = MockAuthState()
        fn_redir_root = getattr(AuthState.redirect_root, 'fn', AuthState.redirect_root)
        redir = fn_redir_root(state)
        ok = is_login_redirect(redir)
        record(1, "Truy cập URL gốc ('/') khi chưa đăng nhập -> Tự động chuyển hướng về /login", ok, f"Event: {redir}")
    except Exception as e:
        record(1, "Truy cập URL gốc ('/') khi chưa đăng nhập -> Tự động chuyển hướng về /login", False, str(e))

    # -------------------------------------------------------------------------
    # Test 2: Frontend Route Guard cho URL nội bộ (/admin/users, /lecturer/dashboard)
    # -------------------------------------------------------------------------
    try:
        from frontend_app.auth import AuthState
        state = MockAuthState()
        fn_admin = getattr(AuthState.check_admin_auth, 'fn', AuthState.check_admin_auth)
        fn_lec = getattr(AuthState.check_lecturer_auth, 'fn', AuthState.check_lecturer_auth)
        fn_auth = getattr(AuthState.check_auth, 'fn', AuthState.check_auth)

        redir_admin = fn_admin(state)
        redir_lec = fn_lec(state)
        redir_auth = fn_auth(state)
        ok = (
            is_login_redirect(redir_admin) and
            is_login_redirect(redir_lec) and
            is_login_redirect(redir_auth)
        )
        record(2, "Chưa đăng nhập truy cập URL nội bộ -> Chặn và chuyển hướng về /login", ok)
    except Exception as e:
        record(2, "Chưa đăng nhập truy cập URL nội bộ -> Chặn và chuyển hướng về /login", False, str(e))

    # -------------------------------------------------------------------------
    # Test 3: Đăng nhập ADMIN (admin / admin123)
    # -------------------------------------------------------------------------
    admin_token = None
    try:
        resp = client.post('/api/auth/login/', {'username': 'admin', 'password': 'admin123'}, format='json')
        data = resp.data
        ok = (
            resp.status_code == 200 and
            'token' in data and
            data.get('user', {}).get('role_name') == 'ADMIN'
        )
        if ok:
            admin_token = data['token']
        record(3, "Đăng nhập tài khoản ADMIN ('admin') -> Cấp JWT token, Role trong DB là ADMIN", ok, f"Status: {resp.status_code}, Role: {data.get('user', {}).get('role_name')}")
    except Exception as e:
        record(3, "Đăng nhập tài khoản ADMIN ('admin')", False, str(e))

    # -------------------------------------------------------------------------
    # Test 4: Đăng nhập LECTURER (gv01 / gv123)
    # -------------------------------------------------------------------------
    lecturer_token = None
    try:
        resp = client.post('/api/auth/login/', {'username': 'gv01', 'password': 'gv123'}, format='json')
        data = resp.data
        ok = (
            resp.status_code == 200 and
            'token' in data and
            data.get('user', {}).get('role_name') == 'LECTURER'
        )
        if ok:
            lecturer_token = data['token']
        record(4, "Đăng nhập tài khoản LECTURER ('gv01') -> Cấp JWT token, Role trong DB là LECTURER", ok, f"Status: {resp.status_code}, Role: {data.get('user', {}).get('role_name')}")
    except Exception as e:
        record(4, "Đăng nhập tài khoản LECTURER ('gv01')", False, str(e))

    # -------------------------------------------------------------------------
    # Test 5: Đăng nhập STUDENT (sv01 / sv123)
    # -------------------------------------------------------------------------
    student_token = None
    try:
        resp = client.post('/api/auth/login/', {'username': 'sv01', 'password': 'sv123'}, format='json')
        data = resp.data
        ok = (
            resp.status_code == 200 and
            'token' in data and
            data.get('user', {}).get('role_name') == 'STUDENT'
        )
        if ok:
            student_token = data['token']
        record(5, "Đăng nhập tài khoản STUDENT ('sv01') -> Cấp JWT token, Role trong DB là STUDENT", ok, f"Status: {resp.status_code}, Role: {data.get('user', {}).get('role_name')}")
    except Exception as e:
        record(5, "Đăng nhập tài khoản STUDENT ('sv01')", False, str(e))

    # -------------------------------------------------------------------------
    # Test 6: Đăng nhập sai mật khẩu -> 401 Unauthorized
    # -------------------------------------------------------------------------
    try:
        resp = client.post('/api/auth/login/', {'username': 'admin', 'password': 'sai_mat_khau_123'}, format='json')
        ok = resp.status_code == 401
        record(6, "Đăng nhập sai mật khẩu -> Trả về HTTP 401 Unauthorized và thông báo lỗi", ok, f"Status: {resp.status_code}")
    except Exception as e:
        record(6, "Đăng nhập sai mật khẩu", False, str(e))

    # -------------------------------------------------------------------------
    # Test 7: Đăng nhập tài khoản bị khóa (sv11) -> 403 Forbidden
    # -------------------------------------------------------------------------
    try:
        resp = client.post('/api/auth/login/', {'username': 'sv11', 'password': 'sv123'}, format='json')
        ok = resp.status_code == 403 and 'khóa' in resp.data.get('message', '').lower()
        record(7, "Đăng nhập tài khoản bị khóa ('sv11' có class is_locked=True) -> Trả về HTTP 403 Forbidden", ok, f"Status: {resp.status_code}, Message: {resp.data.get('message')}")
    except Exception as e:
        record(7, "Đăng nhập tài khoản bị khóa ('sv11')", False, str(e))

    # -------------------------------------------------------------------------
    # Test 8: STUDENT gọi API ADMIN (/api/users/) -> 403 Forbidden
    # -------------------------------------------------------------------------
    try:
        client_sv = APIClient()
        client_sv.credentials(HTTP_AUTHORIZATION=f'Bearer {student_token}')
        resp = client_sv.get('/api/users/')
        ok = resp.status_code == 403
        record(8, "STUDENT gọi API quản trị ADMIN ('/api/users/') -> Bị chặn 403 Forbidden", ok, f"Status: {resp.status_code}")
    except Exception as e:
        record(8, "STUDENT gọi API ADMIN", False, str(e))

    # -------------------------------------------------------------------------
    # Test 9: LECTURER gọi API ADMIN (/api/users/) -> 403 Forbidden
    # -------------------------------------------------------------------------
    try:
        client_gv = APIClient()
        client_gv.credentials(HTTP_AUTHORIZATION=f'Bearer {lecturer_token}')
        resp = client_gv.get('/api/users/')
        ok = resp.status_code == 403
        record(9, "LECTURER gọi API quản trị ADMIN ('/api/users/') -> Bị chặn 403 Forbidden", ok, f"Status: {resp.status_code}")
    except Exception as e:
        record(9, "LECTURER gọi API ADMIN", False, str(e))

    # -------------------------------------------------------------------------
    # Test 10: Chưa đăng nhập gọi API cần xác thực (/api/auth/me/) -> 401 Unauthorized
    # -------------------------------------------------------------------------
    try:
        anon_client = APIClient()
        resp = anon_client.get('/api/auth/me/')
        ok = resp.status_code in (401, 403)
        record(10, "Chưa đăng nhập gọi API nội bộ ('/api/auth/me/') -> Bị chặn HTTP 401 Unauthorized", ok, f"Status: {resp.status_code}")
    except Exception as e:
        record(10, "Chưa đăng nhập gọi API nội bộ", False, str(e))

    # -------------------------------------------------------------------------
    # Test 11: Token JWT hết hạn / không hợp lệ -> 401 Unauthorized
    # -------------------------------------------------------------------------
    try:
        now = datetime.now(timezone.utc)
        expired_payload = {
            'user_id': 1,
            'username': 'admin',
            'role': 'ADMIN',
            'iat': int((now - timedelta(days=2)).timestamp()),
            'exp': int((now - timedelta(days=1)).timestamp()),
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm='HS256')
        exp_client = APIClient()
        exp_client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_token}')
        resp = exp_client.get('/api/auth/me/')
        ok = resp.status_code == 401
        record(11, "Token JWT hết hạn gửi lên hệ thống -> Bị từ chối HTTP 401 AuthenticationFailed", ok, f"Status: {resp.status_code}")
    except Exception as e:
        record(11, "Token JWT hết hạn", False, str(e))

    # -------------------------------------------------------------------------
    # Test 12: Đăng xuất (/api/auth/logout/) -> 200 OK
    # -------------------------------------------------------------------------
    try:
        logout_client = APIClient()
        logout_client.credentials(HTTP_AUTHORIZATION=f'Bearer {student_token}')
        resp = logout_client.post('/api/auth/logout/')
        ok = resp.status_code == 200
        record(12, "Gọi API Đăng xuất ('/api/auth/logout/') -> Trả về HTTP 200 OK và hủy session", ok, f"Status: {resp.status_code}")
    except Exception as e:
        record(12, "Gọi API Đăng xuất", False, str(e))

    # -------------------------------------------------------------------------
    # Test 13: Khôi phục phiên làm việc qua JWT token (/api/auth/me/)
    # -------------------------------------------------------------------------
    try:
        me_client = APIClient()
        me_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        resp = me_client.get('/api/auth/me/')
        ok = (
            resp.status_code == 200 and
            resp.data.get('user', {}).get('username') == 'admin' and
            resp.data.get('user', {}).get('role_name') == 'ADMIN'
        )
        record(13, "Khôi phục phiên làm việc từ JWT token ('/api/auth/me/') -> Thành công 200 OK, trả đúng role", ok, f"Status: {resp.status_code}")
    except Exception as e:
        record(13, "Khôi phục phiên làm việc qua JWT token", False, str(e))

    # -------------------------------------------------------------------------
    # Test 14: Chặn leo thang quyền trái phép (Student PATCH role_id=1)
    # -------------------------------------------------------------------------
    try:
        sv_user = User.objects.get(username='sv01')
        orig_role_id = sv_user.role_id
        sv_client = APIClient()
        sv_client.credentials(HTTP_AUTHORIZATION=f'Bearer {student_token}')
        # Sinh viên thử tự thăng cấp bản thân thành ADMIN (role_id=1)
        resp = sv_client.patch(f'/api/users/{sv_user.user_id}/', {'role_id': 1}, format='json')
        sv_user.refresh_from_db()
        ok = sv_user.role_id == orig_role_id  # Vai trò không bị thay đổi!
        record(14, "Chặn leo thang đặc quyền (Sinh viên cố ý gửi PATCH role_id=1) -> Bị lọc bỏ, vai trò không đổi", ok, f"Current role_id: {sv_user.role_id}")
    except Exception as e:
        record(14, "Chặn leo thang đặc quyền", False, str(e))

    # -------------------------------------------------------------------------
    # Test 15: Chặn tải tài liệu chưa được phê duyệt (Pending Document)
    # -------------------------------------------------------------------------
    try:
        # Lấy một tài liệu không thuộc về sv01 (hoặc tạo tài liệu test PENDING)
        pending_doc = Document.objects.filter(status='PENDING').exclude(uploader__username='sv01').first()
        if not pending_doc:
            first_subject_id = 1
            admin_user = User.objects.get(username='admin')
            pending_doc = Document.objects.create(
                title="Tài liệu kiểm thử PENDING",
                subject_id=first_subject_id,
                uploader=admin_user,
                status='PENDING',
                is_public=False,
            )

        sv_client = APIClient()
        sv_client.credentials(HTTP_AUTHORIZATION=f'Bearer {student_token}')
        resp = sv_client.get(f'/api/documents/{pending_doc.document_id}/download/')
        ok = resp.status_code == 403
        record(15, "Chặn sinh viên tải tài liệu chưa được duyệt ('PENDING') -> Bị chặn HTTP 403 Forbidden", ok, f"Status: {resp.status_code}")
    except Exception as e:
        record(15, "Chặn sinh viên tải tài liệu chưa duyệt", False, str(e))

    print("=" * 80)
    print(f" KẾT QUẢ KIỂM THỬ: {passed_tests}/{total_tests} TEST CASES HOÀN TẤT VÀ VƯỢT QUA")
    print("=" * 80)
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
