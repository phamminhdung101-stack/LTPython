"""
DocUni - Task 2: Service Phân Quyền Truy Cập Tài Liệu (ACL Service)
Kiểm tra quyền truy cập theo Khoa, theo Lớp và theo Người dùng.
"""

from typing import Tuple
from documents.models import Document
from .models import DocumentPermission


def can_user_access_document(user, document: Document) -> Tuple[bool, str]:
    """
    Kiểm tra xem một người dùng có quyền xem/mở tài liệu hay không (View Permission).
    """
    if not user or not user.is_authenticated:
        return False, "Yêu cầu đăng nhập để truy cập tài liệu."

    # 1. Quản trị viên & Giảng viên: Toàn quyền
    if getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False):
        return True, "Toàn quyền truy cập dành cho Cán bộ / Giảng viên."

    # 2. Tác giả của tài liệu luôn có quyền xem tài liệu của mình
    if document.uploader_id == user.id:
        return True, "Tác giả của tài liệu."

    # 3. Tài liệu công khai toàn trường đã duyệt
    if document.status == Document.APPROVED and document.is_public:
        return True, "Tài liệu công khai toàn trường."

    # 4. Kiểm tra quyền cá nhân (USER)
    user_perm = DocumentPermission.objects.filter(
        document=document,
        permission_type=DocumentPermission.USER,
        user=user,
        can_view=True,
    ).first()
    if user_perm:
        return True, "Được cấp quyền xem theo tài khoản cá nhân."

    # 5. Kiểm tra quyền theo Lớp học (CLASS)
    user_class = getattr(user, 'student_class', None)
    if user_class:
        class_perm = DocumentPermission.objects.filter(
            document=document,
            permission_type=DocumentPermission.CLASS,
            student_class=user_class,
            can_view=True,
        ).first()
        if class_perm:
            return True, f"Được cấp quyền xem theo lớp {user_class.class_name}."

    # 6. Kiểm tra quyền theo Khoa (DEPARTMENT)
    user_dept = getattr(user, 'department', None)
    if user_dept:
        dept_perm = DocumentPermission.objects.filter(
            document=document,
            permission_type=DocumentPermission.DEPARTMENT,
            department=user_dept,
            can_view=True,
        ).first()
        if dept_perm:
            return True, f"Được cấp quyền xem theo khoa {user_dept.department_name}."

    # 7. Bị từ chối
    allowed_classes = list(
        DocumentPermission.objects.filter(
            document=document,
            permission_type=DocumentPermission.CLASS,
            can_view=True,
        ).values_list('student_class__class_name', flat=True)
    )
    if allowed_classes:
        return False, f"Từ chối truy cập (403): Tài liệu này chỉ dành riêng cho các lớp: {', '.join(filter(None, allowed_classes))}."

    return False, "Từ chối truy cập (403): Bạn không có quyền xem tài liệu này."


def can_user_download_document(user, document: Document) -> Tuple[bool, str]:
    """
    Kiểm tra xem một người dùng có quyền tải tài liệu hay không (Download Permission).
    """
    if not user or not user.is_authenticated:
        return False, "Yêu cầu đăng nhập để tải tài liệu."

    # 1. Admin & Giảng viên
    if getattr(user, 'is_admin', False) or getattr(user, 'is_lecturer', False):
        return True, "Toàn quyền tải tài liệu dành cho Cán bộ / Giảng viên."

    # 2. Người upload
    if document.uploader_id == user.id:
        return True, "Tác giả của tài liệu."

    # 3. Tài liệu công khai toàn trường
    if document.status == Document.APPROVED and document.is_public:
        return True, "Tài liệu công khai toàn trường cho phép tải."

    # 4. Kiểm tra quyền cá nhân (USER)
    user_perm = DocumentPermission.objects.filter(
        document=document,
        permission_type=DocumentPermission.USER,
        user=user,
    ).first()
    if user_perm:
        if user_perm.can_download:
            return True, "Được cấp quyền tải theo tài khoản cá nhân."
        return False, "Từ chối tải xuống: Bạn chỉ có quyền xem tài liệu này, không được phép tải."

    # 5. Kiểm tra quyền theo Lớp học (CLASS)
    user_class = getattr(user, 'student_class', None)
    if user_class:
        class_perm = DocumentPermission.objects.filter(
            document=document,
            permission_type=DocumentPermission.CLASS,
            student_class=user_class,
        ).first()
        if class_perm:
            if class_perm.can_download:
                return True, f"Lớp {user_class.class_name} được phép tải tài liệu."
            return False, f"Từ chối tải xuống: Sinh viên lớp {user_class.class_name} chỉ có quyền xem, không được phép tải."

    # 6. Kiểm tra quyền theo Khoa (DEPARTMENT)
    user_dept = getattr(user, 'department', None)
    if user_dept:
        dept_perm = DocumentPermission.objects.filter(
            document=document,
            permission_type=DocumentPermission.DEPARTMENT,
            department=user_dept,
        ).first()
        if dept_perm:
            if dept_perm.can_download:
                return True, f"Khoa {user_dept.department_name} được phép tải tài liệu."
            return False, f"Từ chối tải xuống: Khoa {user_dept.department_name} chỉ có quyền xem, không được phép tải."

    return False, "Từ chối tải xuống (403): Bạn không có quyền tải tài liệu này."
