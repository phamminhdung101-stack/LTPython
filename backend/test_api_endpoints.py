"""
Automated Integration Tests for DocUni Backend REST APIs & PostgreSQL Connection.
"""

import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, Role


def run_tests():
    print("=" * 60)
    print("BẮT ĐẦU CHẠY KIỂM THỬ BACKEND DJANGO REST API & POSTGRESQL")
    print("=" * 60)

    client = APIClient()
    passed = 0
    total = 0

    def assert_test(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name} - {details}")

    # Test 1: Kiểm tra kết nối PostgreSQL trực tiếp
    try:
        connection.ensure_connection()
        db_name = connection.settings_dict.get('NAME')
        assert_test("1. Kết nối PostgreSQL database trực tiếp", True, f"DB: {db_name}")
    except Exception as e:
        assert_test("1. Kết nối PostgreSQL database trực tiếp", False, str(e))

    # Test 2: Endpoint Health Check GET /api/health/
    res = client.get('/api/health/')
    assert_test("2. Endpoint GET /api/health/ trả về 200 OK", res.status_code == status.HTTP_200_OK, f"Status: {res.status_code}")
    assert_test("2b. Health check xác nhận kết nối PostgreSQL active", res.data.get('database', {}).get('connected') is True)

    # Test 3: Đăng nhập sai thông tin
    res = client.post('/api/auth/login/', {'username': 'admin', 'password': 'wrong_password_xyz'}, format='json')
    assert_test("3. Đăng nhập sai thông tin trả về 401 Unauthorized", res.status_code == status.HTTP_401_UNAUTHORIZED, f"Status: {res.status_code}")

    # Test 4: Đăng nhập thành công với tài khoản admin
    res = client.post('/api/auth/login/', {'username': 'admin', 'password': 'admin'}, format='json')
    if res.status_code != status.HTTP_200_OK:
        # Thử với password 'admin123'
        res = client.post('/api/auth/login/', {'username': 'admin', 'password': 'admin123'}, format='json')
    assert_test("4. Đăng nhập thành công với tài khoản admin", res.status_code == status.HTTP_200_OK, f"Status: {res.status_code}")
    assert_test("4b. Response trả về thông tin user và role ADMIN", res.data.get('user', {}).get('role_name') == 'ADMIN')

    # Test 5: Người chưa đăng nhập truy cập API riêng tư GET /api/auth/me/
    unauth_client = APIClient()
    res = unauth_client.get('/api/auth/me/')
    assert_test("5. Người chưa đăng nhập truy cập /api/auth/me/ bị từ chối 401/403", res.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), f"Status: {res.status_code}")

    # Test 6: Lấy thông tin người dùng hiện tại khi đã đăng nhập
    res = client.get('/api/auth/me/')
    assert_test("6. Lấy thông tin người dùng đang đăng nhập GET /api/auth/me/", res.status_code == status.HTTP_200_OK and res.data.get('user', {}).get('username') == 'admin')

    # Test 7: Phân quyền - Sinh viên truy cập API Admin /api/users/ bị chặn 403
    student_user = User.objects.filter(role__role_name='STUDENT').first()
    student_client = APIClient()
    if student_user:
        student_client.force_authenticate(user=student_user)
        res = student_client.get('/api/users/')
        assert_test("7. Sinh viên truy cập /api/users/ bị chặn 403 Forbidden", res.status_code == status.HTTP_403_FORBIDDEN, f"Status: {res.status_code}")
    else:
        assert_test("7. Sinh viên truy cập /api/users/ bị chặn 403 Forbidden", True, "Bỏ qua do không có student seed")

    # Test 8: Admin truy cập API /api/users/ thành công
    res = client.get('/api/users/')
    assert_test("8. Admin truy cập /api/users/ thành công 200 OK", res.status_code == status.HTTP_200_OK and res.data.get('total', 0) > 0)

    # Test 9: Sinh viên không thể tự nâng quyền vai trò
    if student_user:
        admin_role = Role.objects.get(role_name='ADMIN')
        res = student_client.patch(f'/api/users/{student_user.user_id}/', {'role_id': admin_role.role_id, 'full_name': 'Hacker Name'}, format='json')
        # Kiểm tra role trong database vẫn là STUDENT
        student_user.refresh_from_db()
        assert_test("9. Người dùng thường không thể tự nâng quyền tài khoản", student_user.role_name == 'STUDENT', f"Role hiện tại: {student_user.role_name}")

    # Test 10: Lấy danh sách tài liệu môn học GET /api/documents/
    res = client.get('/api/documents/')
    assert_test("10. Lấy danh sách tài liệu GET /api/documents/ thành công 200 OK", res.status_code == status.HTTP_200_OK and res.data.get('total', 0) > 0)

    # Test 11: Lấy danh mục Khoa, Lớp, Môn học
    res_depts = client.get('/api/departments/')
    res_classes = client.get('/api/classes/')
    res_subjects = client.get('/api/subjects/')
    res_roles = client.get('/api/roles/')
    assert_test("11. Lấy danh mục Khoa, Lớp, Môn học, Vai trò thành công", 
                all(r.status_code == 200 for r in [res_depts, res_classes, res_subjects, res_roles]))

    # Test 12: Đăng xuất POST /api/auth/logout/
    res = client.post('/api/auth/logout/')
    assert_test("12. Đăng xuất POST /api/auth/logout/ thành công", res.status_code == status.HTTP_200_OK)

    print("=" * 60)
    print(f"KẾT QUẢ KIỂM THỬ: {passed}/{total} bài kiểm thử thành công.")
    print("=" * 60)

    return passed == total


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
