"""
DocUni - Task 2 & Task 3: Service Layer Nghiệp Vụ Tài Liệu
- Task 2: Quản lý Cây thư mục (Folder Tree) & Upload file/folder
- Task 3: Phê duyệt (Approval Workflow), Quản lý phiên bản (Versioning) & Nhật ký kiểm toán (Audit Logs)
"""

from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError

from .models import Document, DocumentVersion, DocumentActivityLog, Folder, Tag
from academics.models import Subject


# ─── 1. TASK 2: QUẢN LÝ CÂY THƯ MỤC & UPLOAD ─────────────────────────────────

def get_folder_tree(subject_id=None):
    """
    Trả về cấu trúc cây thư mục phân cấp cha - con.
    """
    qs = Folder.objects.all()
    if subject_id:
        qs = qs.filter(subject_id=subject_id)

    folders = qs.select_related('subject', 'parent_folder')
    # Build tree structure
    folder_map = {}
    roots = []

    for f in folders:
        node = {
            'id': f.id,
            'name': f.folder_name,
            'subject_id': f.subject_id,
            'parent_id': f.parent_folder_id,
            'children': [],
        }
        folder_map[f.id] = node

    for f in folders:
        node = folder_map[f.id]
        if f.parent_folder_id and f.parent_folder_id in folder_map:
            folder_map[f.parent_folder_id]['children'].append(node)
        else:
            roots.append(node)

    return roots


def create_folder(folder_name: str, subject_id: int, parent_folder_id=None, user=None) -> Folder:
    """Tạo thư mục mới phân cấp."""
    if not folder_name.strip():
        raise ValidationError("Tên thư mục không được để trống.")

    subject = Subject.objects.get(pk=subject_id)
    parent = Folder.objects.get(pk=parent_folder_id) if parent_folder_id else None

    folder = Folder.objects.create(
        folder_name=folder_name.strip(),
        subject=subject,
        parent_folder=parent,
        created_by=user,
    )
    return folder


# ─── 2. TASK 3: QUY TRÌNH DUYỆT TÀI LIỆU (APPROVAL WORKFLOW) ─────────────────

@transaction.atomic
def approve_document(document: Document, lecturer_user) -> Document:
    """
    Giảng viên phê duyệt tài liệu:
    - Chuyển trạng thái sang APPROVED
    - Đặt is_public = True (hoặc công khai theo cấu hình)
    - Ghi nhận người duyệt và thời điểm duyệt
    - Ghi nhận nhật ký hoạt động (Audit Activity Log)
    """
    if not getattr(lecturer_user, 'is_lecturer', False) and not getattr(lecturer_user, 'is_admin', False):
        raise PermissionDenied("Chỉ có Giảng viên hoặc Quản trị viên mới có quyền phê duyệt tài liệu.")

    document.status = Document.APPROVED
    document.is_public = True
    document.approved_by = lecturer_user
    document.approved_at = timezone.now()
    document.save(update_fields=['status', 'is_public', 'approved_by', 'approved_at'])

    # Ghi nhận Audit Log
    DocumentActivityLog.objects.create(
        document=document,
        user=lecturer_user,
        action='APPROVE',
        description=f"Giảng viên {lecturer_user.full_name} đã phê duyệt và xuất bản công khai tài liệu.",
    )
    return document


@transaction.atomic
def reject_document(document: Document, lecturer_user, feedback_reason: str) -> Document:
    """
    Giảng viên từ chối tài liệu kèm lý do phản hồi cho sinh viên:
    - Chuyển trạng thái sang REJECTED
    - Đặt is_public = False
    - Ghi nhận lý do từ chối vào nhật ký kiểm toán
    """
    if not getattr(lecturer_user, 'is_lecturer', False) and not getattr(lecturer_user, 'is_admin', False):
        raise PermissionDenied("Chỉ có Giảng viên hoặc Quản trị viên mới có quyền từ chối duyệt.")

    if not feedback_reason.strip():
        raise ValidationError("Vui lòng cung cấp lý do từ chối để sinh viên chỉnh sửa.")

    document.status = Document.REJECTED
    document.is_public = False
    document.save(update_fields=['status', 'is_public'])

    # Ghi nhận Audit Log
    DocumentActivityLog.objects.create(
        document=document,
        user=lecturer_user,
        action='REJECT',
        description=f"Từ chối duyệt: {feedback_reason.strip()}",
    )
    return document


# ─── 3. TASK 3: QUẢN LÝ PHIÊN BẢN (VERSIONING) ────────────────────────────────

@transaction.atomic
def create_new_version(document: Document, file_obj, change_summary: str, user) -> DocumentVersion:
    """
    Tải lên phiên bản nâng cấp (v2.0, v3.0...):
    - Tự động tăng version_number
    - Lưu file mới và tóm tắt thay đổi (change_summary)
    - Nếu là sinh viên nộp lại bản v2.0 sau khi bị từ chối -> đưa lại về PENDING
    - Ghi nhận nhật ký hoạt động
    """
    latest = document.latest_version
    next_ver_number = (latest.version_number + 1) if latest else 1

    version = DocumentVersion.objects.create(
        document=document,
        file=file_obj,
        version_number=next_ver_number,
        change_summary=change_summary.strip(),
        updated_by=user,
    )

    # Nếu sinh viên nộp phiên bản mới sau khi bị reject -> chuyển lại PENDING
    if getattr(user, 'is_student', False) and document.status == Document.REJECTED:
        document.status = Document.PENDING
        document.save(update_fields=['status'])

    # Ghi log
    DocumentActivityLog.objects.create(
        document=document,
        user=user,
        action='UPDATE',
        description=f"Phát hành phiên bản v{next_ver_number}.0: {change_summary.strip()}",
    )
    return version


# ─── 4. TASK 3: QUẢN LÝ THẺ PHÂN LOẠI (TAGGING) ───────────────────────────────

@transaction.atomic
def add_tag_to_document(document: Document, tag_name: str, user=None) -> Tag:
    """Gắn tag vào tài liệu và ghi log."""
    tag_clean = tag_name.strip().lower()
    tag, _ = Tag.objects.get_or_create(tag_name=tag_clean)
    document.tags.add(tag)

    DocumentActivityLog.objects.create(
        document=document,
        user=user,
        action='ADD_TAG',
        description=f"Gắn thẻ #{tag_clean} vào tài liệu.",
    )
    return tag


@transaction.atomic
def remove_tag_from_document(document: Document, tag_name: str, user=None):
    """Gỡ tag khỏi tài liệu và ghi log."""
    tag_clean = tag_name.strip().lower()
    tag = Tag.objects.filter(tag_name=tag_clean).first()
    if tag:
        document.tags.remove(tag)
        DocumentActivityLog.objects.create(
            document=document,
            user=user,
            action='REMOVE_TAG',
            description=f"Gỡ thẻ #{tag_clean} khỏi tài liệu.",
        )
