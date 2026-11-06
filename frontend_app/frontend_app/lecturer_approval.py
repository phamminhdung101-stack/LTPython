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
import httpx
from .common_components import lecturer_page_wrapper, status_badge
from .auth import AuthState


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
    """Quản lý hàng đợi và thao tác phê duyệt tài liệu sinh viên đóng góp kết nối PostgreSQL."""

    items: List[PendingDoc] = []
    selected_id: str = ""
    filter_status: str = "PENDING"  # "ALL", "PENDING", "APPROVED", "REJECTED"
    search_query: str = ""

    # Reject Dialog State
    show_reject_dialog: bool = False
    reject_reason_input: str = ""
    
    # Loading & Error States
    is_loading: bool = False
    error_message: str = ""

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
    
    async def load_pending_queue(self):
        """Load documents queue from PostgreSQL API."""
        self.is_loading = True
        self.error_message = ""
        
        try:
            auth = await self.get_state(AuthState)
            if not auth.auth_token:
                self.error_message = "Chưa đăng nhập. Vui lòng đăng nhập lại."
                self.is_loading = False
                return
            
            headers = {"Authorization": f"Bearer {auth.auth_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://127.0.0.1:8000/api/documents/",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    docs = data.get("documents", [])
                    
                    pending_docs = []
                    for doc in docs:
                        doc_id = str(doc.get("document_id", doc.get("id", "")))
                        title = doc.get("title", "Tài liệu không tên")
                        desc = doc.get("description", "") or ""
                        
                        doc_type = "REFERENCE"
                        type_label = "Tham khảo"
                        type_color = "green"
                        t_lower = title.lower()
                        d_lower = desc.lower()
                        
                        if "slide" in t_lower or "bài giảng" in t_lower:
                            doc_type = "SLIDE"
                            type_label = "Slide Bài giảng"
                            type_color = "orange"
                        elif "đề thi" in t_lower or "exam" in t_lower:
                            doc_type = "EXAM"
                            type_label = "Đề thi & Đáp án"
                            type_color = "red"
                        elif "bài tập" in t_lower or "btl" in t_lower:
                            doc_type = "EXERCISE"
                            type_label = "Bài tập lớn"
                            type_color = "purple"
                        elif "sách" in t_lower or "giáo trình" in t_lower:
                            doc_type = "TEXTBOOK"
                            type_label = "Sách giáo trình"
                            type_color = "blue"
                        
                        subj = doc.get("subject", {}) if isinstance(doc.get("subject"), dict) else {}
                        dept = subj.get("department", {}) if isinstance(subj.get("department"), dict) else {}
                        dept_name = dept.get("department_name", "")
                        dept_id_val = str(dept.get("department_id", ""))
                        dn = dept_name.lower()
                        faculty = "CNTT"
                        if dept_id_val == "2" or "kinh" in dn:
                            faculty = "KT"
                        elif dept_id_val == "3" or "ngoai" in dn:
                            faculty = "NN"
                        elif "dieu hanh" in dn or "điều hành" in dn or "dhb" in dn:
                            faculty = "DHB"
                        
                        status = doc.get("status", "PENDING")
                        student_name = doc.get("uploader_name") or "Sinh viên"
                        student_id = f"SV{doc.get('uploader_id', '01')}"
                        student_class = f"Khoa {dept_name}" if dept_name else "Đại trà"
                        
                        subject_code = f"SUBJ{subj.get('subject_id', '')}"
                        subject_name = subj.get("subject_name", "Chưa phân môn")
                        
                        file_size_bytes = doc.get("file_size", 0) or 0
                        if file_size_bytes > 1024*1024:
                            file_size = f"{file_size_bytes / (1024*1024):.1f} MB"
                        elif file_size_bytes > 1024:
                            file_size = f"{file_size_bytes / 1024:.1f} KB"
                        else:
                            file_size = f"{file_size_bytes} B"
                        
                        uploaded_at = (doc.get("created_at") or "")[:16].replace("T", " ")
                        tags = [t.get("tag_name") for t in doc.get("tags", [])] if isinstance(doc.get("tags"), list) else []
                        
                        pending_doc = PendingDoc(
                            id=doc_id,
                            title=title,
                            subject_code=subject_code,
                            subject_name=subject_name,
                            faculty=faculty,
                            proposed_folder="Tài liệu môn học",
                            doc_type=doc_type,
                            type_label=type_label,
                            type_color=type_color,
                            file_name=doc.get("original_file_name") or doc.get("file_name") or "document.pdf",
                            file_size=file_size,
                            description=desc,
                            tags=tags,
                            student_name=student_name,
                            student_id=student_id,
                            student_class=student_class,
                            submitted_at=uploaded_at,
                            status=status,
                            review_feedback="Tài liệu đã được phê duyệt." if status == "APPROVED" else ("Tài liệu bị từ chối." if status == "REJECTED" else ""),
                            version="v1.0",
                            preview_text=desc or "Nội dung tóm tắt học liệu được lấy trực tiếp từ cơ sở dữ liệu PostgreSQL DocUni.",
                        )
                        pending_docs.append(pending_doc)
                    
                    self.items = pending_docs
                    if pending_docs and not self.selected_id:
                        self.selected_id = pending_docs[0].id
                    
                elif response.status_code == 401:
                    self.error_message = "Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại."
                else:
                    self.error_message = f"Lỗi tải dữ liệu: {response.status_code}"
                    
        except httpx.TimeoutException:
            self.error_message = "Timeout: Không thể kết nối đến server."
        except Exception as e:
            self.error_message = f"Lỗi: {str(e)}"
        finally:
            self.is_loading = False
            self.is_loading = False

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
        # Return empty doc if not found or no items
        return PendingDoc()

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
    async def approve_doc(self, item_id: str):
        """Approve document via API."""
        try:
            auth = await self.get_state(AuthState)
            if not auth.auth_token:
                return rx.toast.error("Chưa đăng nhập. Vui lòng đăng nhập lại.")
            
            headers = {"Authorization": f"Bearer {auth.auth_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://127.0.0.1:8000/api/documents/{item_id}/approve/",
                    headers=headers,
                    json={"approval_notes": "Tài liệu đạt chuẩn chất lượng, đã được giảng viên phê duyệt đưa vào kho học liệu."},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    # Update local state
                    updated = []
                    for d in self.items:
                        if d.id == item_id:
                            d.status = "APPROVED"
                            d.review_feedback = "Tài liệu đạt chuẩn chất lượng, đã được giảng viên phê duyệt đưa vào kho học liệu."
                        updated.append(d)
                    self.items = updated
                    return rx.toast.success("Đã phê duyệt tài liệu! Học liệu đã được công khai trên kho.")
                elif response.status_code == 401:
                    return rx.toast.error("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.")
                else:
                    return rx.toast.error(f"Lỗi phê duyệt: {response.status_code}")
                    
        except Exception as e:
            return rx.toast.error(f"Lỗi kết nối: {str(e)}")

    # Thao tác Từ chối
    def open_reject_dialog(self, item_id: str):
        self.selected_id = item_id
        self.reject_reason_input = ""
        self.show_reject_dialog = True

    def close_reject_dialog(self):
        self.show_reject_dialog = False
        self.reject_reason_input = ""

    async def confirm_reject(self):
        """Reject document via API."""
        reason = self.reject_reason_input.strip()
        if not reason:
            return rx.toast.error("Vui lòng nhập lý do từ chối để phản hồi cho sinh viên!")

        doc_id = self.selected_id
        
        try:
            auth = await self.get_state(AuthState)
            if not auth.auth_token:
                return rx.toast.error("Chưa đăng nhập. Vui lòng đăng nhập lại.")
            
            headers = {"Authorization": f"Bearer {auth.auth_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://127.0.0.1:8000/api/documents/{doc_id}/reject/",
                    headers=headers,
                    json={"rejection_reason": reason},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    # Update local state
                    updated = []
                    for d in self.items:
                        if d.id == doc_id:
                            d.status = "REJECTED"
                            d.review_feedback = reason
                        updated.append(d)
                    self.items = updated
                    self.show_reject_dialog = False
                    self.reject_reason_input = ""
                    return rx.toast.warning("Đã từ chối tài liệu và gửi phản hồi nhận xét cho sinh viên!")
                elif response.status_code == 401:
                    return rx.toast.error("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.")
                else:
                    return rx.toast.error(f"Lỗi từ chối: {response.status_code}")
                    
        except Exception as e:
            return rx.toast.error(f"Lỗi kết nối: {str(e)}")


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
                    rx.cond(
                        LecturerApprovalState.is_loading,
                        rx.card(
                            rx.center(
                                rx.vstack(
                                    rx.spinner(size="3", color="var(--blue-9)"),
                                    rx.text("Đang tải hàng đợi kiểm duyệt...", size="2", color="slate.9"),
                                    spacing="2",
                                    align="center",
                                ),
                                padding="8",
                            ),
                            variant="surface",
                            width="100%",
                        ),
                        rx.cond(
                            LecturerApprovalState.error_message != "",
                            rx.card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("alert-circle", size=16, color="var(--red-9)"),
                                        rx.text("Lỗi tải dữ liệu", size="2", weight="bold", color="red.11"),
                                        align="center",
                                        spacing="2",
                                    ),
                                    rx.text(LecturerApprovalState.error_message, size="2", color="slate.11"),
                                    rx.button(
                                        rx.icon("refresh-cw", size=14),
                                        "Thử lại",
                                        size="2",
                                        variant="soft",
                                        color_scheme="blue",
                                        on_click=LecturerApprovalState.load_pending_queue,
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                variant="surface",
                                bg="var(--red-2)",
                                border="1px solid var(--red-5)",
                                padding="4",
                                width="100%",
                            ),
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
                        ),
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
                                on_click=rx.toast.info(f"Đang tải tệp: {active.file_name}"),
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
