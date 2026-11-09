"""
DocUni - Task 2 Automated Tests: Phân Quyền Truy Cập (ACL)
Kiểm chứng kịch bản bắt buộc: "Sinh viên Lớp A không mở được tài liệu Lớp B"
"""

from django.test import TestCase
from accounts.models import User, Role
from academics.models import Department, Class, Subject
from documents.models import Document, Folder
from permissions.models import DocumentPermission
from permissions.services import can_user_access_document


class DocumentACLTestCase(TestCase):
    def setUp(self):
        # 1. Tạo Roles
        self.role_admin = Role.objects.create(role_name=Role.ADMIN)
        self.role_lecturer = Role.objects.create(role_name=Role.LECTURER)
        self.role_student = Role.objects.create(role_name=Role.STUDENT)

        # 2. Tạo Khoa & Lớp
        self.dept_cntt = Department.objects.create(department_name="Khoa Công nghệ thông tin")
        self.class_a = Class.objects.create(class_name="Lớp D21CQCN01-A", department=self.dept_cntt)
        self.class_b = Class.objects.create(class_name="Lớp D21CQCN02-B", department=self.dept_cntt)

        # 3. Tạo Users
        # Sinh viên Nam (Lớp A)
        self.student_a = User.objects.create_user(
            username="nam_d21cn01",
            full_name="Lê Hoàng Nam",
            role=self.role_student,
            department=self.dept_cntt,
            student_class=self.class_a,
            password="password123",
        )
        # Sinh viên Mai (Lớp B)
        self.student_b = User.objects.create_user(
            username="mai_d21cn02",
            full_name="Trần Thị Mai",
            role=self.role_student,
            department=self.dept_cntt,
            student_class=self.class_b,
            password="password123",
        )
        # Giảng viên An
        self.lecturer = User.objects.create_user(
            username="ts_an",
            full_name="TS. Nguyễn Văn An",
            role=self.role_lecturer,
            department=self.dept_cntt,
            password="password123",
        )

        # 4. Môn học & Folder
        self.subject = Subject.objects.create(subject_name="Lập trình Web", department=self.dept_cntt)
        self.folder = Folder.objects.create(folder_name="Bài tập lớn", subject=self.subject, created_by=self.lecturer)

        # 5. Tạo tài liệu DÀNH RIÊNG CHO LỚP A (is_public = False)
        self.doc_class_a = Document.objects.create(
            title="[Bảo mật] Đề cương BTL Web Lớp A",
            description="Tài liệu chỉ lưu hành nội bộ Lớp D21CQCN01-A",
            subject=self.subject,
            folder=self.folder,
            uploader=self.lecturer,
            status=Document.APPROVED,
            is_public=False,
        )
        # Cấp quyền ACL cho Lớp A
        DocumentPermission.objects.create(
            document=self.doc_class_a,
            permission_type=DocumentPermission.CLASS,
            student_class=self.class_a,
            can_view=True,
            can_download=True,
            can_edit=False,
        )

        # 6. Tạo tài liệu CÔNG KHAI (is_public = True)
        self.doc_public = Document.objects.create(
            title="Giáo trình Lập trình Web 2026",
            subject=self.subject,
            folder=self.folder,
            uploader=self.lecturer,
            status=Document.APPROVED,
            is_public=True,
        )

    def test_student_class_a_can_access_class_a_document(self):
        """Sinh viên Lớp A CÓ QUYỀN mở tài liệu của Lớp A."""
        can_access, reason = can_user_access_document(self.student_a, self.doc_class_a)
        self.assertTrue(can_access)
        self.assertIn("Lớp D21CQCN01-A", reason)

    def test_student_class_b_CANNOT_access_class_a_document(self):
        """
        KỊCH BẢN DEMO BẮT BUỘC TASK 2:
        Sinh viên Lớp B KHÔNG ĐƯỢC PHÉP mở tài liệu chỉ dành cho Lớp A (Bị chặn 403).
        """
        can_access, reason = can_user_access_document(self.student_b, self.doc_class_a)
        self.assertFalse(can_access)
        self.assertIn("403", reason)
        self.assertIn("Lớp D21CQCN01-A", reason)

    def test_lecturer_can_access_all_documents(self):
        """Giảng viên có toàn quyền xem tài liệu dù có giới hạn theo lớp."""
        can_access, _ = can_user_access_document(self.lecturer, self.doc_class_a)
        self.assertTrue(can_access)

    def test_public_document_accessible_by_all_students(self):
        """Tài liệu công khai toàn trường thì cả Sinh viên Lớp A và Lớp B đều mở được."""
        can_access_a, _ = can_user_access_document(self.student_a, self.doc_public)
        can_access_b, _ = can_user_access_document(self.student_b, self.doc_public)
        self.assertTrue(can_access_a)
        self.assertTrue(can_access_b)
