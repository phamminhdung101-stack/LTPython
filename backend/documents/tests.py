"""
DocUni - Task 3 Automated Tests: Versioning, Tag, Duyệt Public & Nhật Ký
Kiểm chứng kịch bản bắt buộc: "Gửi duyệt, Giảng viên phê duyệt và tài liệu hiện công khai"
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, Role
from academics.models import Department, Class, Subject
from documents.models import Document, DocumentVersion, DocumentActivityLog, Folder, Tag
from documents.services import (
    approve_document,
    reject_document,
    create_new_version,
    add_tag_to_document,
    remove_tag_from_document,
    create_folder,
    get_folder_tree,
)


class DocumentTask3TestCase(TestCase):
    def setUp(self):
        # Roles
        self.role_lecturer = Role.objects.create(role_name=Role.LECTURER)
        self.role_student = Role.objects.create(role_name=Role.STUDENT)

        # Department & Class
        self.dept = Department.objects.create(department_name="Khoa Công nghệ thông tin")
        self.student_class = Class.objects.create(class_name="Lớp D21CQCN01-A", department=self.dept)

        # Users
        self.student = User.objects.create_user(
            username="nam_d21cn01",
            full_name="Lê Hoàng Nam",
            role=self.role_student,
            department=self.dept,
            student_class=self.student_class,
            password="password123",
        )
        self.lecturer = User.objects.create_user(
            username="ts_an",
            full_name="TS. Nguyễn Văn An",
            role=self.role_lecturer,
            department=self.dept,
            password="password123",
        )

        # Subject & Folder
        self.subject = Subject.objects.create(subject_name="Cấu trúc dữ liệu & GT", department=self.dept)
        self.folder = Folder.objects.create(folder_name="Slide bài giảng", subject=self.subject, created_by=self.lecturer)

    def test_document_initial_submission_is_pending_and_not_public(self):
        """Khi sinh viên nộp tài liệu mới, mặc định trạng thái là PENDING và chưa công khai."""
        doc = Document.objects.create(
            title="Slide Tóm tắt Cây AVL - Nhóm 3",
            subject=self.subject,
            folder=self.folder,
            uploader=self.student,
            status=Document.PENDING,
            is_public=False,
        )
        self.assertEqual(doc.status, Document.PENDING)
        self.assertFalse(doc.is_public)
        self.assertIsNone(doc.approved_by)

    def test_approval_workflow_makes_document_public_and_logs_audit(self):
        """
        KỊCH BẢN DEMO BẮT BUỘC TASK 3:
        Giảng viên phê duyệt tài liệu PENDING -> Chuyển thành APPROVED, is_public=True và ghi log APPROVE.
        """
        doc = Document.objects.create(
            title="Đề cương ôn tập CTDL 2026",
            subject=self.subject,
            folder=self.folder,
            uploader=self.student,
            status=Document.PENDING,
            is_public=False,
        )

        # Giảng viên thực hiện phê duyệt
        approved_doc = approve_document(doc, self.lecturer)

        self.assertEqual(approved_doc.status, Document.APPROVED)
        self.assertTrue(approved_doc.is_public)
        self.assertEqual(approved_doc.approved_by, self.lecturer)
        self.assertIsNotNone(approved_doc.approved_at)

        # Kiểm tra ghi nhận Nhật ký kiểm toán (Audit Log)
        log = DocumentActivityLog.objects.filter(document=doc, action="APPROVE").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.lecturer)

    def test_reject_document_sets_rejected_status_and_logs(self):
        """Giảng viên từ chối tài liệu kèm lý do phản hồi."""
        doc = Document.objects.create(
            title="Bài tập SQL chưa hoàn thiện",
            subject=self.subject,
            folder=self.folder,
            uploader=self.student,
            status=Document.PENDING,
            is_public=False,
        )

        feedback = "Nội dung còn thiếu bài tập Transaction, vui lòng bổ sung và nộp lại v2.0."
        rejected_doc = reject_document(doc, self.lecturer, feedback)

        self.assertEqual(rejected_doc.status, Document.REJECTED)
        self.assertFalse(rejected_doc.is_public)

        # Kiểm tra log REJECT
        log = DocumentActivityLog.objects.filter(document=doc, action="REJECT").first()
        self.assertIsNotNone(log)
        self.assertIn(feedback, log.description)

    def test_versioning_increments_version_number_and_records_history(self):
        """Upload version mới tự động tăng version_number (v1 -> v2) và ghi log."""
        doc = Document.objects.create(
            title="Giáo trình CTDL",
            subject=self.subject,
            folder=self.folder,
            uploader=self.lecturer,
            status=Document.APPROVED,
            is_public=True,
        )

        file1 = SimpleUploadedFile("ctdl_v1.pdf", b"Noi dung v1", content_type="application/pdf")
        v1 = create_new_version(doc, file1, "Bản phát hành đầu tiên", self.lecturer)
        self.assertEqual(v1.version_number, 1)

        file2 = SimpleUploadedFile("ctdl_v2.pdf", b"Noi dung v2", content_type="application/pdf")
        v2 = create_new_version(doc, file2, "Cập nhật chương cây AVL và Đồ thị", self.lecturer)
        self.assertEqual(v2.version_number, 2)

        self.assertEqual(doc.versions.count(), 2)
        self.assertEqual(doc.latest_version.version_number, 2)

    def test_tagging_add_and_remove(self):
        """Gắn và gỡ tag cho tài liệu ghi nhận nhật ký tương ứng."""
        doc = Document.objects.create(
            title="Tài liệu Python",
            subject=self.subject,
            folder=self.folder,
            uploader=self.lecturer,
        )

        tag = add_tag_to_document(doc, "python", self.lecturer)
        self.assertIn(tag, doc.tags.all())
        self.assertTrue(DocumentActivityLog.objects.filter(document=doc, action="ADD_TAG").exists())

        remove_tag_from_document(doc, "python", self.lecturer)
        self.assertNotIn(tag, doc.tags.all())
        self.assertTrue(DocumentActivityLog.objects.filter(document=doc, action="REMOVE_TAG").exists())

    def test_folder_tree_structure(self):
        """Kiểm tra tạo cấu trúc thư mục lồng nhau cha - con."""
        root_folder = create_folder("Chương 1 - Giới thiệu", self.subject.id, user=self.lecturer)
        sub_folder = create_folder("Bài tập Lab tuần 1", self.subject.id, parent_folder_id=root_folder.id, user=self.lecturer)

        tree = get_folder_tree(self.subject.id)
        # Find root node
        root_node = next((node for node in tree if node['id'] == root_folder.id), None)
        self.assertIsNotNone(root_node)
        self.assertEqual(len(root_node['children']), 1)
        self.assertEqual(root_node['children'][0]['id'], sub_folder.id)
