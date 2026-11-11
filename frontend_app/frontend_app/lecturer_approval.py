"""
DocUni - Trang Kiểm Duyệt Tài Liệu Sinh Viên Đóng Góp (Task 4.2)
Route: /lecturer/approval
Framework: Reflex (Python Full-Stack)

Cung cấp giao diện hàng đợi kiểm duyệt dành cho giảng viên:
- Bố cục xem trước kép (Side-by-Side Split View):
  - Cột trái: Hàng đợi duyệt tài liệu với bộ lọc trạng thái (Chờ duyệt, Đã duyệt, Từ chối).
  - Cột phải: Xem chi tiết thông tin sinh viên, metadata học liệu, khung đọc trước tài liệu.
- Quy trình phê duyệt / từ chối:
  - Nút "Phê duyệt": Xuất bản tài liệu vào kho học liệu chính thức.
  - Nút "Từ chối": Nhập lý do phản hồi gửi về cho sinh viên để nộp lại bản v2.0.
"""

import dataclasses
from datetime import datetime
from typing import List, Dict, Any
import reflex as rx
from .common_components import lecturer_page_wrapper, status_badge
from .data_store import GlobalDocState


# ─── Dataclass Models ────────────────────────────────────────────────────────

@dataclasses.dataclass
class PendingDoc:
    id: str = ""
    title: str = ""
    subject_code: str = ""
    subject_name: str = ""
    faculty: str = "CNTT"
    proposed_folder: str = ""
    doc_type: str = "SLIDE"  # "TEXTBOOK", "SLIDE", "EXAM", "EXERCISE", "REFERENCE"
    type_label: str = "Slide"
    type_color: str = "orange"
    file_name: str = ""
    file_size: str = ""
    description: str = ""
    tags: List[str] = dataclasses.field(default_factory=list)
    student_name: str = ""
    student_id: str = ""
    student_class: str = ""
    submitted_at: str = ""
    status: str = "PENDING"  # "PENDING", "APPROVED", "REJECTED"
    review_feedback: str = ""
    version: str = "v1.0"
    preview_text: str = ""


# ─── State ───────────────────────────────────────────────────────────────────

class LecturerApprovalState(rx.State):
    """Quản lý hàng đợi và thao tác phê duyệt tài liệu sinh viên đóng góp từ PostgreSQL thực tế."""

    items: List[PendingDoc] = []

    def load_items(self):
        try:
            import httpx
            resp = httpx.get("http://127.0.0.1:8000/api/documents/", timeout=3.0)
            if resp.status_code == 200:
                raw_docs = resp.json().get("documents") or resp.json().get("data") or []
                loaded = []
                for d in raw_docs:
                    d_id = str(d.get("id") or d.get("document_id"))
                    title = d.get("title", "")
                    s_name = d.get("subject_name") or d.get("subject", {}).get("subject_name", "")
                    dept_name = d.get("department_name") or "CNTT"
                    status = str(d.get("status") or "PENDING").upper()
                    u_name = d.get("uploader_name") or "Sinh viên"
                    desc = d.get("description") or f"Tài liệu môn học {s_name}"
                    created = str(d.get("created_at") or "")[:16]
                    fname = d.get("file_name") or f"document_{d_id}.pdf"
                    fsize = f"{round(float(d.get('file_size', 2097152)) / (1024*1024), 1)} MB"
                    f_name = d.get("folder_name") or "Kho tài liệu"
                    tags_list = d.get("tags") or ["học liệu", "đóng góp"]
                    loaded.append(PendingDoc(
                        id=d_id,
                        title=title,
                        subject_code=f"SUB_{d.get('subject_id', 1)}",
                        subject_name=s_name,
                        faculty=dept_name,
                        proposed_folder=f_name,
                        doc_type="TEXTBOOK",
                        type_label="Học liệu",
                        type_color="blue",
                        file_name=fname,
                        file_size=fsize,
                        description=desc,
                        tags=tags_list,
                        student_name=u_name,
                        student_id=str(d.get("uploader_id") or "SV01"),
                        student_class="D21CQCN01-B",
                        submitted_at=created,
                        status=status,
                        review_feedback="",
                        version=str(d.get("latest_version") or "v1.0"),
                        preview_text=desc,
                    ))
                self.items = loaded
                if self.items and not self.selected_id:
                    self.selected_id = self.items[0].id
                return
        except Exception:
            pass

        try:
            import os, sys
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
            if backend_dir not in sys.path:
                sys.path.insert(0, backend_dir)
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            import django
            django.setup()
            from documents.models import Document
            loaded = []
            for d in Document.objects.select_related('subject__department', 'uploader').all():
                d_id = str(d.id)
                s_name = d.subject.subject_name if d.subject else ""
                dept_name = d.subject.department.department_name if (d.subject and d.subject.department) else "CNTT"
                u_name = d.uploader.full_name if (d.uploader and d.uploader.full_name) else (d.uploader.username if d.uploader else "Sinh viên")
                created = d.created_at.strftime("%Y-%m-%d %H:%M") if d.created_at else ""
                loaded.append(PendingDoc(
                    id=d_id,
                    title=d.title,
                    subject_code=f"SUB_{d.subject_id}",
                    subject_name=s_name,
                    faculty=dept_name,
                    proposed_folder="Kho tài liệu",
                    doc_type="TEXTBOOK",
                    type_label="Học liệu",
                    type_color="blue",
                    file_name=f"document_{d_id}.pdf",
                    file_size="2.5 MB",
                    description=d.description or f"Tài liệu môn học {s_name}",
                    tags=["học liệu"],
                    student_name=u_name,
                    student_id=str(d.uploader_id or "SV01"),
                    student_class="D21CQCN01-B",
                    submitted_at=created,
                    status=d.status,
                    review_feedback="",
                    version="v1.0",
                    preview_text=d.description or d.title,
                ))
            self.items = loaded
            if self.items and not self.selected_id:
                self.selected_id = self.items[0].id
        except Exception:
            self.items = []
    selected_id: str = "pdoc_1"
    filter_status: str = "PENDING"  # "ALL", "PENDING", "APPROVED", "REJECTED"
    search_query: str = ""

    # Reject Dialog State
    show_reject_dialog: bool = False
    reject_reason_input: str = ""

    def set_search_query(self, value: str):
        self.search_query = value

    def set_filter_status(self, value: str | list[str]):
        if isinstance(value, list):
            self.filter_status = str(value[0]) if value else "ALL"
        else:
            self.filter_status = str(value)

    def set_reject_reason(self, value: str):
        self.reject_reason_input = value

    def select_item(self, item_id: str):
        self.selected_id = item_id

    @rx.var
    def filtered_items(self) -> List[PendingDoc]:
        query = self.search_query.strip().lower()
        docs = self.items

        if self.filter_status != "ALL":
            docs = [d for d in docs if d.status == self.filter_status]

        if query:
            docs = [
                d for d in docs
                if query in d.title.lower()
                or query in d.student_name.lower()
                or query in d.student_id.lower()
                or query in d.subject_code.lower()
            ]
        return docs

    @rx.var
    def active_item(self) -> PendingDoc:
        for d in self.items:
            if d.id == self.selected_id:
                return d
        return self.items[0] if self.items else PendingDoc()

    # Thống kê KPI
    @rx.var
    def pending_count(self) -> int:
        return len([d for d in self.items if d.status == "PENDING"])

    @rx.var
    def approved_count(self) -> int:
        return len([d for d in self.items if d.status == "APPROVED"])

    @rx.var
    def rejected_count(self) -> int:
        return len([d for d in self.items if d.status == "REJECTED"])

    @rx.var
    def total_count(self) -> int:
        return len(self.items)

    @rx.var
    def approval_rate(self) -> str:
        total = len(self.items)
        if total == 0:
            return "0%"
        approved = len([d for d in self.items if d.status == "APPROVED"])
        return f"{int((approved / total) * 100)}%"

    # Thao tác Phê duyệt
    def approve_doc(self, item_id: str):
        try:
            import httpx
            httpx.post(f"http://127.0.0.1:8000/api/documents/{item_id}/approve/", timeout=5.0)
        except Exception:
            try:
                from documents.models import Document as DjDoc
                DjDoc.objects.filter(id=item_id).update(status="APPROVED", is_public=True)
            except Exception:
                pass

        updated = []
        for d in self.items:
            if d.id == item_id:
                d.status = "APPROVED"
                d.review_feedback = "Tài liệu đạt chuẩn chất lượng, đã được giảng viên phê duyệt đưa vào kho học liệu."
            updated.append(d)
        self.items = updated
        return [
            GlobalDocState.approve_document(item_id),
            rx.toast.success("Đã phê duyệt tài liệu! Học liệu đã được xuất bản công khai trên kho."),
        ]

    # Thao tác Từ chối
    def open_reject_dialog(self, item_id: str):
        self.selected_id = item_id
        self.reject_reason_input = ""
        self.show_reject_dialog = True

    def close_reject_dialog(self):
        self.show_reject_dialog = False
        self.reject_reason_input = ""

    def confirm_reject(self):
        reason = self.reject_reason_input.strip()
        if not reason:
            return rx.toast.error("Vui lòng nhập lý do từ chối để phản hồi cho sinh viên!")

        doc_id = self.selected_id
        try:
            import httpx
            httpx.post(f"http://127.0.0.1:8000/api/documents/{doc_id}/reject/", json={"reason": reason}, timeout=5.0)
        except Exception:
            try:
                from documents.models import Document as DjDoc
                DjDoc.objects.filter(id=doc_id).update(status="REJECTED")
            except Exception:
                pass

        updated = []
        for d in self.items:
            if d.id == doc_id:
                d.status = "REJECTED"
                d.review_feedback = reason
            updated.append(d)
        self.items = updated
        self.show_reject_dialog = False
        self.reject_reason_input = ""
        return [
            GlobalDocState.confirm_reject_document,
            rx.toast.warning("Đã từ chối tài liệu và gửi phản hồi nhận xét cho sinh viên!"),
        ]


# ─── UI Helper Components ────────────────────────────────────────────────────

def queue_item_card(doc: PendingDoc) -> rx.Component:
    """Thẻ yêu cầu kiểm duyệt trong cột bên trái."""
    is_active = LecturerApprovalState.selected_id == doc.id

    return rx.card(
        rx.vstack(
            # Top row: Subject code + Status badge
            rx.hstack(
                rx.badge(doc.subject_code, color_scheme="blue", variant="surface", size="1"),
                rx.badge(doc.type_label, color_scheme=doc.type_color, variant="surface", size="1"),
                rx.spacer(),
                status_badge(doc.status),
                align="center",
                width="100%",
            ),

            # Document Title
            rx.text(doc.title, size="2", weight="bold", color="slate.12", line_clamp=2),

            # Student info
            rx.hstack(
                rx.avatar(fallback=doc.student_name[:2], size="1", radius="full", color_scheme="indigo"),
                rx.vstack(
                    rx.text(doc.student_name, size="1", weight="bold", color="slate.11"),
                    rx.text(f"MSSV: {doc.student_id} • {doc.student_class}", size="1", color="slate.8"),
                    spacing="0",
                ),
                align="center",
                spacing="2",
            ),

            # Timestamp & File size
            rx.hstack(
                rx.icon("clock", size=12, color="var(--slate-7)"),
                rx.text(doc.submitted_at, size="1", color="slate.8"),
                rx.spacer(),
                rx.text(doc.file_size, size="1", color="slate.8"),
                align="center",
                width="100%",
            ),

            spacing="2",
            align="start",
            width="100%",
        ),
        variant=rx.cond(is_active, "classic", "surface"),
        border=rx.cond(is_active, "2px solid var(--indigo-8)", "1px solid var(--slate-4)"),
        bg=rx.cond(is_active, "var(--indigo-2)", "white"),
        padding="3",
        _hover={"cursor": "pointer", "border_color": "var(--indigo-7)"},
        transition="all 0.15s ease",
        on_click=LecturerApprovalState.select_item(doc.id),
        width="100%",
    )


def reject_reason_modal() -> rx.Component:
    """Dialog nhập lý do phản hồi khi từ chối bài đóng góp."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("circle-x", size=20, color="var(--red-9)"),
                        bg="red.3",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.heading("Từ Chối & Phản Hồi Chỉnh Sửa", size="4", weight="bold", color="red.11"),
                        rx.text("Gửi lý do nhận xét chi tiết để sinh viên hoàn thiện lại tài liệu", size="2", color="slate.9"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(rx.icon("x", size=16), variant="ghost", color_scheme="gray", size="1"),
                    ),
                    align="center",
                    width="100%",
                ),

                rx.divider(color_scheme="gray"),

                rx.vstack(
                    rx.text("Lý do từ chối / Hướng dẫn chỉnh sửa:", size="2", weight="bold", color="slate.11"),
                    rx.text_area(
                        placeholder="VD: Tài liệu chưa có đáp án câu 4; Cần định dạng lại trang bìa; Đính kèm thêm slide tóm tắt...",
                        value=LecturerApprovalState.reject_reason_input,
                        on_change=LecturerApprovalState.set_reject_reason,
                        size="3",
                        rows="4",
                        width="100%",
                    ),
                    rx.text("Nhận xét này sẽ hiển thị trực tiếp tại trang 'Theo dõi trạng thái duyệt' của sinh viên.", size="1", color="slate.8"),
                    spacing="2",
                    width="100%",
                ),

                # Actions
                rx.hstack(
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button("Hủy bỏ", variant="surface", color_scheme="gray", size="2"),
                    ),
                    rx.button(
                        rx.icon("send", size=14),
                        "Gửi phản hồi từ chối",
                        color_scheme="red",
                        size="2",
                        variant="solid",
                        on_click=LecturerApprovalState.confirm_reject,
                    ),
                    align="center",
                    spacing="2",
                    width="100%",
                    padding_top="2",
                ),

                spacing="4",
                width="100%",
            ),
            max_width="500px",
            padding="5",
        ),
        open=LecturerApprovalState.show_reject_dialog,
        on_open_change=LecturerApprovalState.close_reject_dialog,
    )


# ─── Main Page ───────────────────────────────────────────────────────────────

def lecturer_approval_page() -> rx.Component:
    active = LecturerApprovalState.active_item

    return lecturer_page_wrapper(
        rx.vstack(
            # ── Header Bar ──
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Kiểm Duyệt Học Liệu Đóng Góp Từ Sinh Viên", size="6", weight="bold", color="slate.12"),
                        rx.badge(
                            rx.hstack(
                                rx.icon("clock", size=12),
                                rx.text(LecturerApprovalState.pending_count.to_string(), " chờ duyệt", size="1", weight="bold"),
                                align="center",
                                spacing="1",
                            ),
                            color_scheme="amber",
                            variant="surface",
                            size="2",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    rx.text("Đánh giá nội dung, phê duyệt xuất bản vào kho tài liệu hoặc gửi phản hồi nhận xét cho sinh viên", size="2", color="slate.9"),
                    spacing="1",
                ),
                align="center",
                width="100%",
            ),

            rx.divider(color_scheme="gray"),

            # ── KPI Cards ──
            rx.grid(
                rx.card(
                    rx.hstack(
                        rx.box(
                            rx.icon("clock", size=20, color="var(--amber-9)"),
                            bg="amber.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Chờ kiểm duyệt", size="1", color="slate.8"),
                            rx.text(LecturerApprovalState.pending_count.to_string(), size="5", weight="bold", color="amber.11"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    padding="3",
                ),
                rx.card(
                    rx.hstack(
                        rx.box(
                            rx.icon("circle-check", size=20, color="var(--green-9)"),
                            bg="green.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Đã phê duyệt", size="1", color="slate.8"),
                            rx.text(LecturerApprovalState.approved_count.to_string(), size="5", weight="bold", color="green.11"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    padding="3",
                ),
                rx.card(
                    rx.hstack(
                        rx.box(
                            rx.icon("circle-x", size=20, color="var(--red-9)"),
                            bg="red.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Đã từ chối", size="1", color="slate.8"),
                            rx.text(LecturerApprovalState.rejected_count.to_string(), size="5", weight="bold", color="red.11"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    padding="3",
                ),
                rx.card(
                    rx.hstack(
                        rx.box(
                            rx.icon("check-check", size=20, color="var(--indigo-9)"),
                            bg="indigo.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Tỷ lệ duyệt", size="1", color="slate.8"),
                            rx.text(LecturerApprovalState.approval_rate, size="5", weight="bold", color="indigo.11"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    padding="3",
                ),
                columns="4",
                spacing="3",
                width="100%",
            ),

            # ── Main Side-by-Side Split View ──
            rx.hstack(
                # ── Left Column: Hàng Đợi Kiểm Duyệt (400px) ──
                rx.vstack(
                    # Search & Tabs
                    rx.card(
                        rx.vstack(
                            rx.input(
                                rx.input.slot(rx.icon("search", size=15, color="var(--slate-8)")),
                                placeholder="Tìm theo tên bài, tên sinh viên, MSSV...",
                                value=LecturerApprovalState.search_query,
                                on_change=LecturerApprovalState.set_search_query,
                                size="2",
                                width="100%",
                            ),
                            rx.segmented_control.root(
                                rx.segmented_control.item("Chờ duyệt", value="PENDING"),
                                rx.segmented_control.item("Đã duyệt", value="APPROVED"),
                                rx.segmented_control.item("Từ chối", value="REJECTED"),
                                rx.segmented_control.item("Tất cả", value="ALL"),
                                value=LecturerApprovalState.filter_status,
                                on_change=LecturerApprovalState.set_filter_status,
                                size="1",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        variant="surface",
                        padding="3",
                        width="100%",
                    ),

                    # Danh sách thẻ hàng đợi cuộn mượt mà
                    rx.box(
                        rx.vstack(
                            rx.foreach(
                                LecturerApprovalState.filtered_items,
                                queue_item_card,
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        max_height="620px",
                        overflow_y="auto",
                        width="100%",
                    ),

                    spacing="3",
                    width=["100%", "100%", "400px"],
                    align="start",
                ),

                # ── Right Column: Khung Xem Chi Tiết & Duyệt (Flex 1) ──
                rx.card(
                    rx.vstack(
                        # 1. Header chi tiết: Sinh viên + Trạng thái
                        rx.hstack(
                            rx.hstack(
                                rx.avatar(fallback=active.student_name[:2], size="3", radius="full", color_scheme="indigo"),
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(active.student_name, size="3", weight="bold", color="slate.12"),
                                        rx.badge(active.student_class, color_scheme="indigo", variant="surface", size="1"),
                                        align="center",
                                        spacing="2",
                                    ),
                                    rx.text(f"Mã sinh viên: {active.student_id} • Khoa: {active.faculty} • Nộp: {active.submitted_at}", size="1", color="slate.9"),
                                    spacing="0",
                                ),
                                align="center",
                                spacing="3",
                            ),
                            rx.spacer(),
                            status_badge(active.status),
                            align="center",
                            width="100%",
                            padding_bottom="3",
                            border_bottom="1px solid var(--slate-4)",
                        ),

                        # 2. Metadata tài liệu đóng góp
                        rx.grid(
                            rx.vstack(
                                rx.text("Tên tài liệu:", size="1", color="slate.8"),
                                rx.text(active.title, size="2", weight="bold", color="slate.12"),
                                spacing="0",
                            ),
                            rx.vstack(
                                rx.text("Môn học:", size="1", color="slate.8"),
                                rx.hstack(
                                    rx.badge(active.subject_code, color_scheme="blue", variant="surface", size="1"),
                                    rx.text(active.subject_name, size="1", color="slate.10", weight="medium"),
                                    align="center",
                                    spacing="1",
                                ),
                                spacing="0",
                            ),
                            rx.vstack(
                                rx.text("Thư mục đề xuất:", size="1", color="slate.8"),
                                rx.badge(active.proposed_folder, color_scheme="gray", variant="surface", size="1"),
                                spacing="0",
                            ),
                            rx.vstack(
                                rx.text("Loại học liệu & Tệp:", size="1", color="slate.8"),
                                rx.hstack(
                                    rx.badge(active.type_label, color_scheme=active.type_color, variant="surface", size="1"),
                                    rx.text(f"{active.file_name} ({active.file_size})", size="1", color="slate.10"),
                                    align="center",
                                    spacing="1",
                                ),
                                spacing="0",
                            ),
                            columns="2",
                            spacing="3",
                            width="100%",
                            padding_y="2",
                        ),

                        # 3. Mô tả của sinh viên
                        rx.vstack(
                            rx.text("Ghi chú của sinh viên:", size="1", weight="bold", color="slate.11"),
                            rx.box(
                                rx.text(active.description, size="2", color="slate.11", line_height="1.5"),
                                bg="var(--slate-2)",
                                padding="3",
                                border_radius="md",
                                border="1px solid var(--slate-4)",
                                width="100%",
                            ),
                            spacing="1",
                            width="100%",
                        ),

                        # 4. Tags
                        rx.hstack(
                            rx.text("Tags:", size="1", weight="bold", color="slate.11"),
                            rx.foreach(
                                active.tags,
                                lambda t: rx.badge(t, color_scheme="blue", variant="surface", size="1"),
                            ),
                            align="center",
                            spacing="2",
                        ),

                        # 5. Khung Preview giả lập tài liệu
                        rx.vstack(
                            rx.hstack(
                                rx.icon("file-text", size=15, color="var(--indigo-9)"),
                                rx.text("Bản Xem Trước Tài Liệu (Document Reader Preview):", size="2", weight="bold", color="indigo.11"),
                                rx.spacer(),
                                rx.badge("Trang 1 / 15", color_scheme="gray", variant="surface", size="1"),
                                align="center",
                                width="100%",
                            ),
                            rx.box(
                                rx.text(
                                    active.preview_text,
                                    size="2",
                                    color="slate.12",
                                    font_family="monospace",
                                    white_space="pre-wrap",
                                    line_height="1.6",
                                ),
                                bg="var(--slate-1)",
                                border="1px solid var(--slate-5)",
                                border_radius="lg",
                                padding="4",
                                max_height="240px",
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                            padding_y="2",
                        ),

                        # 6. Nhận xét phản hồi nếu đã có
                        rx.cond(
                            active.review_feedback != "",
                            rx.card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("message-square", size=14, color="var(--indigo-9)"),
                                        rx.text("Ý kiến nhận xét của giảng viên:", size="1", weight="bold", color="indigo.11"),
                                        align="center",
                                        spacing="1",
                                    ),
                                    rx.text(active.review_feedback, size="2", color="slate.11"),
                                    spacing="1",
                                    width="100%",
                                ),
                                bg="var(--indigo-2)",
                                border="1px solid var(--indigo-5)",
                                padding="3",
                                width="100%",
                            ),
                            rx.fragment(),
                        ),

                        # 7. Thanh thao tác (Action Bar)
                        rx.hstack(
                            rx.cond(
                                active.status == "PENDING",
                                rx.hstack(
                                    rx.button(
                                        rx.icon("circle-check", size=15),
                                        "Phê duyệt & Xuất bản",
                                        color_scheme="green",
                                        size="3",
                                        variant="solid",
                                        on_click=LecturerApprovalState.approve_doc(active.id),
                                    ),
                                    rx.button(
                                        rx.icon("circle-x", size=15),
                                        "Từ chối đóng góp",
                                        color_scheme="red",
                                        size="3",
                                        variant="surface",
                                        on_click=LecturerApprovalState.open_reject_dialog(active.id),
                                    ),
                                    spacing="3",
                                ),
                                rx.badge(
                                    rx.hstack(
                                        rx.icon("info", size=13),
                                        rx.text(f"Hồ sơ này đã ở trạng thái {active.status}", size="1", weight="bold"),
                                        align="center",
                                        spacing="1",
                                    ),
                                    color_scheme=rx.cond(active.status == "APPROVED", "green", "red"),
                                    variant="surface",
                                    size="2",
                                    padding="2",
                                ),
                            ),
                            rx.spacer(),
                            rx.button(
                                rx.icon("download", size=14),
                                "Tải tệp gốc về máy",
                                color_scheme="gray",
                                size="2",
                                variant="surface",
                                on_click=rx.download(url=f"/_upload/{active.file_name}"),
                            ),
                            align="center",
                            width="100%",
                            padding_top="3",
                            border_top="1px solid var(--slate-4)",
                        ),

                        spacing="3",
                        width="100%",
                    ),
                    variant="surface",
                    padding="5",
                    flex="1",
                ),

                spacing="4",
                align="start",
                width="100%",
            ),

            # Reject Dialog
            reject_reason_modal(),

            spacing="4",
            width="100%",
        ),
        current_route="/lecturer/approval",
    )
