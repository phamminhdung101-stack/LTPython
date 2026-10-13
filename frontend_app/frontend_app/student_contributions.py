"""
DocUni - Task 3.2: Trang Theo dõi Trạng thái Duyệt Tài liệu (My Contributions)
Route: /student/contributions
Framework: Reflex (Python Full-Stack)

State quản lý:
- Danh sách tài liệu đã đóng góp kèm trạng thái
- Bộ lọc tab: ALL / PENDING / APPROVED / REJECTED
- Modal xem lý do từ chối chi tiết
- Dialog nộp phiên bản v2.0 mới
- Thu hồi tài liệu đang chờ duyệt
- Thông báo kết quả qua rx.toast (Sonner)
"""

import reflex as rx
from typing import List, Optional
from .common_components import student_page_wrapper, kpi_card, status_badge

# ─── Dữ liệu Mock theo database/schema.sql ───────────────────────────────────

MOCK_CONTRIBUTIONS = [
    {
        "id": "doc_001",
        "title": "Slide Bài giảng CTDL - Chương 3: Hàng đợi và Ngăn xếp",
        "subject_code": "IT202",
        "subject_name": "Cấu trúc dữ liệu & giải thuật",
        "folder": "Slide bài giảng",
        "doc_type": "SLIDE",
        "type_label": "Slide Bài giảng",
        "status": "APPROVED",
        "submitted_at": "2026-10-05 09:30",
        "reviewed_at": "2026-10-06 14:15",
        "reviewer": "TS. Nguyễn Văn An",
        "reject_reason": "",
        "version": "1.0",
        "filename": "CTDL_C3_HangDoi_NganXep.pdf",
        "file_size": "2.4 MB",
        "view_count": 142,
        "download_count": 67,
        "tags": ["python", "cấu trúc dữ liệu", "bài tập"],
        "is_public": True,
    },
    {
        "id": "doc_002",
        "title": "Đề cương ôn tập Cơ sở dữ liệu cuối kỳ 2026",
        "subject_code": "IT305",
        "subject_name": "Cơ sở dữ liệu",
        "folder": "Đề thi & Đáp án",
        "doc_type": "EXAM",
        "type_label": "Đề thi / Đáp án",
        "status": "PENDING",
        "submitted_at": "2026-10-08 15:22",
        "reviewed_at": "",
        "reviewer": "",
        "reject_reason": "",
        "version": "1.0",
        "filename": "CSDL_DeOThiCuoiKy_2026.pdf",
        "file_size": "1.8 MB",
        "view_count": 0,
        "download_count": 0,
        "tags": ["sql", "csdl", "cuối kỳ"],
        "is_public": True,
    },
    {
        "id": "doc_003",
        "title": "Bài tập thực hành SQL nâng cao - Lab 5 & 6",
        "subject_code": "IT305",
        "subject_name": "Cơ sở dữ liệu",
        "folder": "Script SQL",
        "doc_type": "EXERCISE",
        "type_label": "Bài tập thực hành",
        "status": "REJECTED",
        "submitted_at": "2026-10-03 11:10",
        "reviewed_at": "2026-10-04 08:45",
        "reviewer": "TS. Nguyễn Văn An",
        "reject_reason": "Tài liệu bị trùng với bộ Lab đã có trong hệ thống (Tham khảo thư mục Script SQL). Bạn có thể bổ sung nội dung mới và nộp lại phiên bản v2.0 với ghi chú cụ thể về điểm khác biệt.",
        "version": "1.0",
        "filename": "SQL_Lab5_Lab6_NangCao.zip",
        "file_size": "3.1 MB",
        "view_count": 0,
        "download_count": 0,
        "tags": ["sql", "thực hành", "lab"],
        "is_public": True,
    },
    {
        "id": "doc_004",
        "title": "Tóm tắt lý thuyết Nhập môn lập trình - Ôn thi giữa kỳ",
        "subject_code": "IT101",
        "subject_name": "Nhập môn lập trình",
        "folder": "Bài tập thực hành",
        "doc_type": "REFERENCE",
        "type_label": "Tài liệu tham khảo",
        "status": "APPROVED",
        "submitted_at": "2026-09-20 14:05",
        "reviewed_at": "2026-09-21 10:30",
        "reviewer": "TS. Lê Thị Hương",
        "reject_reason": "",
        "version": "2.0",
        "filename": "IT101_TomTatLyThuyet_GiuaKy.pdf",
        "file_size": "0.9 MB",
        "view_count": 389,
        "download_count": 215,
        "tags": ["python", "giữa kỳ", "lý thuyết"],
        "is_public": True,
    },
    {
        "id": "doc_005",
        "title": "Slide Bài giảng Lập trình Web - HTML/CSS Cơ bản",
        "subject_code": "IT410",
        "subject_name": "Lập trình Web",
        "folder": "HTML/CSS/JS",
        "doc_type": "SLIDE",
        "type_label": "Slide Bài giảng",
        "status": "PENDING",
        "submitted_at": "2026-10-09 08:15",
        "reviewed_at": "",
        "reviewer": "",
        "reject_reason": "",
        "version": "1.0",
        "filename": "Web_HTMLCSS_Slide_C1.pptx",
        "file_size": "5.2 MB",
        "view_count": 0,
        "download_count": 0,
        "tags": ["html", "css", "web"],
        "is_public": False,
    },
]

DOC_TYPE_ICONS = {
    "SLIDE": "presentation",
    "TEXTBOOK": "book",
    "EXERCISE": "pencil-line",
    "EXAM": "file-check",
    "REFERENCE": "library",
    "OTHER": "file",
}

DOC_TYPE_COLORS = {
    "SLIDE": "orange",
    "TEXTBOOK": "blue",
    "EXERCISE": "violet",
    "EXAM": "red",
    "REFERENCE": "green",
    "OTHER": "gray",
}

# ─── State ───────────────────────────────────────────────────────────────────

class ContributionState(rx.State):
    """Quản lý toàn bộ logic trang Theo dõi trạng thái duyệt."""

    contributions: List[dict] = MOCK_CONTRIBUTIONS
    active_tab: str = "ALL"

    # Detail / Reject dialog
    show_detail_dialog: bool = False
    selected_doc: dict = {}

    # New version dialog
    show_version_dialog: bool = False
    version_doc_id: str = ""
    version_filename: str = ""
    version_summary: str = ""
    is_uploading_version: bool = False

    # Confirm revoke dialog
    show_revoke_confirm: bool = False
    revoke_doc_id: str = ""

    @rx.var
    def filtered_contributions(self) -> List[dict]:
        if self.active_tab == "ALL":
            return self.contributions
        return [c for c in self.contributions if c["status"] == self.active_tab]

    @rx.var
    def total_count(self) -> int:
        return len(self.contributions)

    @rx.var
    def pending_count(self) -> int:
        return len([c for c in self.contributions if c["status"] == "PENDING"])

    @rx.var
    def approved_count(self) -> int:
        return len([c for c in self.contributions if c["status"] == "APPROVED"])

    @rx.var
    def rejected_count(self) -> int:
        return len([c for c in self.contributions if c["status"] == "REJECTED"])

    @rx.var
    def total_downloads(self) -> int:
        return sum(c["download_count"] for c in self.contributions)

    # Tab switching
    def set_active_tab(self, tab: str):
        self.active_tab = tab

    # Detail dialog
    def open_detail(self, doc_id: str):
        doc = next((c for c in self.contributions if c["id"] == doc_id), {})
        self.selected_doc = doc
        self.show_detail_dialog = True

    def close_detail(self):
        self.show_detail_dialog = False
        self.selected_doc = {}

    # Version dialog
    def open_version_dialog(self, doc_id: str):
        self.version_doc_id = doc_id
        self.version_filename = ""
        self.version_summary = ""
        self.show_version_dialog = True

    def close_version_dialog(self):
        self.show_version_dialog = False
        self.version_doc_id = ""
        self.version_filename = ""
        self.version_summary = ""

    def set_version_summary(self, value: str):
        self.version_summary = value

    def handle_version_file(self, files: list[rx.UploadFile]):
        if files:
            self.version_filename = files[0].filename

    async def submit_new_version(self, files: list[rx.UploadFile] = None):
        if not self.version_summary.strip():
            return rx.toast.error("Vui lòng nhập ghi chú nội dung thay đổi!")
        if files:
            self.version_filename = files[0].filename
        return self._finalize_version()

    def _finalize_version(self):
        """Cập nhật version trong danh sách."""
        doc_id = self.version_doc_id
        updated = []
        for c in self.contributions:
            if c["id"] == doc_id:
                old_ver = float(c["version"])
                c = {**c, "version": f"{old_ver + 1.0:.1f}", "status": "PENDING",
                     "submitted_at": "2026-10-13 12:50", "reviewed_at": "", "reject_reason": ""}
            updated.append(c)
        self.contributions = updated
        self.is_uploading_version = False
        self.show_version_dialog = False
        return rx.toast.success("Đã nộp phiên bản mới thành công! Đang chờ kiểm duyệt lại.")

    # Revoke
    def open_revoke_confirm(self, doc_id: str):
        self.revoke_doc_id = doc_id
        self.show_revoke_confirm = True

    def cancel_revoke(self):
        self.show_revoke_confirm = False
        self.revoke_doc_id = ""

    def confirm_revoke(self):
        doc_id = self.revoke_doc_id
        self.contributions = [c for c in self.contributions if c["id"] != doc_id]
        self.show_revoke_confirm = False
        self.revoke_doc_id = ""
        return rx.toast.success("Đã thu hồi tài liệu thành công.")


# ─── UI Helper Components ────────────────────────────────────────────────────

def doc_type_badge(doc_type: str, type_label: str) -> rx.Component:
    return rx.match(
        doc_type,
        ("SLIDE", rx.badge(rx.icon("presentation", size=11), type_label, color_scheme="orange", variant="surface", size="1")),
        ("TEXTBOOK", rx.badge(rx.icon("book", size=11), type_label, color_scheme="blue", variant="surface", size="1")),
        ("EXERCISE", rx.badge(rx.icon("pencil-line", size=11), type_label, color_scheme="violet", variant="surface", size="1")),
        ("EXAM", rx.badge(rx.icon("file-check", size=11), type_label, color_scheme="red", variant="surface", size="1")),
        ("REFERENCE", rx.badge(rx.icon("library", size=11), type_label, color_scheme="green", variant="surface", size="1")),
        rx.badge(type_label, color_scheme="gray", variant="surface", size="1"),
    )


def tab_btn(label: str, tab_value: str, count, color: str = "gray") -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.text(label, size="2", weight="medium"),
            rx.badge(count.to_string(), color_scheme=color, variant=rx.cond(ContributionState.active_tab == tab_value, "solid", "surface"), size="1"),
            align="center",
            spacing="2",
        ),
        variant=rx.cond(ContributionState.active_tab == tab_value, "solid", "ghost"),
        color_scheme=rx.cond(ContributionState.active_tab == tab_value, color, "gray"),
        on_click=ContributionState.set_active_tab(tab_value),
        radius="full",
        size="2",
    )


def contribution_row(doc: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            # Header row: title + status
            rx.hstack(
                rx.hstack(
                    rx.icon("file-text", size=16, color="var(--slate-9)"),
                    rx.vstack(
                        rx.text(doc["title"], size="2", weight="bold", color="slate.12", max_width="460px", overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                        rx.hstack(
                            rx.text(doc["subject_code"], size="1", color="slate.9", weight="medium"),
                            rx.text("•", size="1", color="slate.6"),
                            rx.text(doc["folder"], size="1", color="slate.8"),
                            rx.text("•", size="1", color="slate.6"),
                            rx.text(f"v{doc['version']}", size="1", color="indigo.10", weight="bold"),
                            align="center",
                            spacing="1",
                        ),
                        spacing="1",
                    ),
                    align="start",
                    spacing="2",
                ),
                rx.spacer(),
                rx.hstack(
                    doc_type_badge(doc["doc_type"], doc["type_label"]),
                    status_badge(doc["status"]),
                    spacing="2",
                ),
                align="start",
                width="100%",
            ),

            # REJECTED: show reason banner
            rx.cond(
                doc["status"] == "REJECTED",
                rx.callout.root(
                    rx.callout.icon(rx.icon("message-square-warning", size=15)),
                    rx.callout.text(
                        rx.vstack(
                            rx.text("Lý do từ chối:", size="1", weight="bold"),
                            rx.text(doc["reject_reason"], size="1"),
                            spacing="1",
                        )
                    ),
                    color="red",
                    variant="surface",
                    size="1",
                    width="100%",
                ),
                rx.fragment(),
            ),

            # APPROVED: stats row
            rx.cond(
                doc["status"] == "APPROVED",
                rx.hstack(
                    rx.hstack(
                        rx.icon("eye", size=13, color="var(--blue-9)"),
                        rx.text(str(doc["view_count"]), size="1", color="slate.10"),
                        rx.text("lượt xem", size="1", color="slate.8"),
                        align="center",
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.icon("download", size=13, color="var(--green-9)"),
                        rx.text(str(doc["download_count"]), size="1", color="slate.10"),
                        rx.text("lượt tải", size="1", color="slate.8"),
                        align="center",
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.icon("user", size=13, color="var(--slate-8)"),
                        rx.text("Duyệt bởi:", size="1", color="slate.8"),
                        rx.text(doc["reviewer"], size="1", color="indigo.10", weight="medium"),
                        align="center",
                        spacing="1",
                    ),
                    spacing="5",
                ),
                rx.fragment(),
            ),

            # Footer: meta + actions
            rx.hstack(
                # Timestamps
                rx.hstack(
                    rx.icon("clock", size=13, color="var(--slate-7)"),
                    rx.text(f"Nộp: {doc['submitted_at']}", size="1", color="slate.8"),
                    rx.cond(
                        doc["reviewed_at"] != "",
                        rx.hstack(
                            rx.text("•", size="1", color="slate.6"),
                            rx.icon("circle-check", size=13, color="var(--green-8)"),
                            rx.text(f"Duyệt: {doc['reviewed_at']}", size="1", color="slate.8"),
                            align="center",
                            spacing="1",
                        ),
                        rx.fragment(),
                    ),
                    align="center",
                    spacing="1",
                ),
                rx.spacer(),
                # Actions
                rx.hstack(
                    # Detail button always
                    rx.button(
                        rx.icon("eye", size=14),
                        "Chi tiết",
                        size="1",
                        variant="ghost",
                        color_scheme="gray",
                        on_click=ContributionState.open_detail(doc["id"]),
                    ),
                    # Nộp v2.0 for REJECTED
                    rx.cond(
                        doc["status"] == "REJECTED",
                        rx.button(
                            rx.icon("refresh-cw", size=14),
                            "Nộp phiên bản v2.0",
                            size="1",
                            variant="surface",
                            color_scheme="blue",
                            on_click=ContributionState.open_version_dialog(doc["id"]),
                        ),
                        rx.fragment(),
                    ),
                    # Revoke for PENDING
                    rx.cond(
                        doc["status"] == "PENDING",
                        rx.button(
                            rx.icon("trash-2", size=14),
                            "Thu hồi",
                            size="1",
                            variant="ghost",
                            color_scheme="red",
                            on_click=ContributionState.open_revoke_confirm(doc["id"]),
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                ),
                align="center",
                width="100%",
            ),

            spacing="3",
            width="100%",
        ),
        variant="surface",
        size="2",
        width="100%",
    )


def detail_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("file-text", size=20, color="var(--indigo-10)"),
                    rx.text("Chi tiết tài liệu đóng góp", weight="bold"),
                    align="center",
                    spacing="2",
                ),
            ),
            rx.dialog.description(
                rx.vstack(
                    # Title + status
                    rx.hstack(
                        rx.heading(ContributionState.selected_doc.get("title", ""), size="4", color="slate.12"),
                        rx.spacer(),
                        status_badge(ContributionState.selected_doc.get("status", "")),
                        align="start",
                        width="100%",
                    ),
                    rx.divider(color_scheme="gray"),
                    # Info grid
                    rx.grid(
                        *[
                            rx.vstack(
                                rx.text(label, size="1", color="slate.9", weight="medium"),
                                rx.text(ContributionState.selected_doc.get(key, "—"), size="2", color="slate.12", weight="bold"),
                                spacing="1",
                            )
                            for label, key in [
                                ("Môn học", "subject_name"),
                                ("Thư mục", "folder"),
                                ("Phiên bản", "version"),
                                ("Tệp đính kèm", "filename"),
                                ("Kích thước", "file_size"),
                                ("Ngày nộp", "submitted_at"),
                                ("Lượt xem", "view_count"),
                                ("Lượt tải", "download_count"),
                            ]
                        ],
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    # Reject reason
                    rx.cond(
                        ContributionState.selected_doc.get("status", "") == "REJECTED",
                        rx.callout.root(
                            rx.callout.icon(rx.icon("message-square-warning", size=15)),
                            rx.callout.text(
                                rx.vstack(
                                    rx.text("Lý do từ chối:", size="2", weight="bold"),
                                    rx.text(ContributionState.selected_doc.get("reject_reason", ""), size="2"),
                                    spacing="1",
                                )
                            ),
                            color="red",
                            variant="surface",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    spacing="4",
                    width="100%",
                )
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Đóng", variant="soft", color_scheme="gray", on_click=ContributionState.close_detail),
                ),
                rx.cond(
                    ContributionState.selected_doc.get("status", "") == "REJECTED",
                    rx.button(
                        rx.icon("refresh-cw", size=15),
                        "Nộp phiên bản v2.0",
                        color_scheme="blue",
                        on_click=ContributionState.open_version_dialog(ContributionState.selected_doc.get("id", "")),
                    ),
                    rx.fragment(),
                ),
                spacing="3",
                justify="end",
                margin_top="4",
            ),
            max_width="540px",
        ),
        open=ContributionState.show_detail_dialog,
        on_open_change=ContributionState.close_detail,
    )


def version_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("git-branch", size=20, color="var(--blue-10)"),
                    rx.text("Nộp phiên bản mới", weight="bold"),
                    align="center",
                    spacing="2",
                ),
            ),
            rx.dialog.description(
                rx.vstack(
                    rx.callout.root(
                        rx.callout.icon(rx.icon("info", size=15)),
                        rx.callout.text("Nộp phiên bản mới sẽ đặt tài liệu về trạng thái Chờ duyệt. Vui lòng ghi rõ các thay đổi để giảng viên xem xét thuận tiện hơn."),
                        color="blue",
                        variant="surface",
                    ),
                    # Upload new file
                    rx.vstack(
                        rx.text("Tệp phiên bản mới *", size="2", weight="bold", color="slate.12"),
                        rx.upload(
                            rx.box(
                                rx.cond(
                                    ContributionState.version_filename == "",
                                    rx.vstack(
                                        rx.icon("upload", size=28, color="var(--blue-8)"),
                                        rx.text("Chọn tệp phiên bản mới", size="2", color="slate.10"),
                                        rx.text("PDF, DOCX, PPTX, XLSX, ZIP", size="1", color="slate.7"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    rx.hstack(
                                        rx.icon("file-check", size=22, color="var(--green-10)"),
                                        rx.text(ContributionState.version_filename, size="2", color="green.11", weight="bold"),
                                        align="center",
                                        spacing="2",
                                    ),
                                ),
                                border="2px dashed var(--blue-5)",
                                border_radius="xl",
                                padding="5",
                                bg="var(--blue-1)",
                                _hover={"border_color": "var(--blue-7)"},
                                cursor="pointer",
                                width="100%",
                            ),
                            id="version_upload",
                            multiple=False,
                            
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    # Summary
                    rx.vstack(
                        rx.text("Tóm tắt nội dung thay đổi *", size="2", weight="bold", color="slate.12"),
                        rx.text_area(
                            placeholder="VD: Bổ sung thêm ví dụ minh họa chương 3, sửa lỗi chính tả slide 12-15, cập nhật theo giáo trình mới nhất...",
                            value=ContributionState.version_summary,
                            on_change=ContributionState.set_version_summary,
                            resize="vertical",
                            rows="3",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Hủy", variant="ghost", color_scheme="gray", on_click=ContributionState.close_version_dialog),
                ),
                rx.button(
                    rx.cond(ContributionState.is_uploading_version, rx.spinner(size="2"), rx.icon("send", size=15)),
                    "Nộp phiên bản mới",
                    color_scheme="blue",
                    loading=ContributionState.is_uploading_version,
                    on_click=ContributionState.submit_new_version(rx.upload_files(upload_id="version_upload")),
                ),
                spacing="3",
                justify="end",
                margin_top="4",
            ),
            max_width="480px",
        ),
        open=ContributionState.show_version_dialog,
        on_open_change=ContributionState.close_version_dialog,
    )


def revoke_confirm_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Thu hồi tài liệu"),
            rx.alert_dialog.description(
                "Bạn có chắc chắn muốn thu hồi tài liệu đang chờ duyệt này không? Hành động này không thể hoàn tác."
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Hủy", variant="ghost", color_scheme="gray", on_click=ContributionState.cancel_revoke),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        rx.icon("trash-2", size=15),
                        "Thu hồi tài liệu",
                        color_scheme="red",
                        on_click=ContributionState.confirm_revoke,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="4",
            ),
        ),
        open=ContributionState.show_revoke_confirm,
    )


def empty_state(tab: str) -> rx.Component:
    messages = {
        "ALL": ("Chưa có tài liệu nào", "Hãy đóng góp tài liệu đầu tiên của bạn!", "upload"),
        "PENDING": ("Không có tài liệu chờ duyệt", "Tất cả tài liệu đã được xem xét.", "clock"),
        "APPROVED": ("Chưa có tài liệu được duyệt", "Tiếp tục đóng góp tài liệu chất lượng!", "circle-check"),
        "REJECTED": ("Không có tài liệu bị từ chối", "Tất cả tài liệu đều đạt tiêu chuẩn.", "shield-check"),
    }
    title, desc, icon = messages.get(tab, ("Trống", "", "file"))
    return rx.center(
        rx.vstack(
            rx.icon(icon, size=48, color="var(--slate-6)"),
            rx.text(title, size="4", weight="bold", color="slate.10"),
            rx.text(desc, size="2", color="slate.8"),
            rx.link(
                rx.button(rx.icon("plus", size=15), "Đóng góp tài liệu mới", color_scheme="blue", size="2"),
                href="/student/upload",
            ),
            spacing="3",
            align="center",
        ),
        padding_y="16",
    )


# ─── Main Page ───────────────────────────────────────────────────────────────

def student_contributions_page() -> rx.Component:
    return student_page_wrapper(
        rx.vstack(
            # ── Page Header ──
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("list-checks", size=28, color="white"),
                        bg="indigo.9",
                        padding="3",
                        border_radius="xl",
                    ),
                    rx.vstack(
                        rx.heading("Tài liệu đóng góp của tôi", size="7", weight="bold", color="slate.12"),
                        rx.text("Theo dõi trạng thái duyệt và quản lý tất cả tài liệu bạn đã đóng góp", size="3", color="slate.9"),
                        spacing="1",
                    ),
                    align="center",
                    spacing="3",
                ),
                rx.spacer(),
                rx.link(
                    rx.button(
                        rx.icon("plus", size=16),
                        "Đóng góp mới",
                        color_scheme="blue",
                        size="3",
                        variant="solid",
                    ),
                    href="/student/upload",
                ),
                align="center",
                width="100%",
            ),

            rx.divider(color_scheme="gray"),

            # ── KPI Cards ──
            rx.grid(
                kpi_card("Tổng đóng góp", ContributionState.total_count.to_string(), "files", "blue"),
                kpi_card("Đang chờ duyệt", ContributionState.pending_count.to_string(), "clock", "amber", "Trong hàng đợi"),
                kpi_card("Đã được duyệt", ContributionState.approved_count.to_string(), "circle-check", "green", "Thành công"),
                kpi_card("Bị từ chối", ContributionState.rejected_count.to_string(), "circle-x", "red", "Cần chỉnh sửa"),
                columns="4",
                spacing="4",
                width="100%",
            ),

            # ── Tab Filter ──
            rx.card(
                rx.hstack(
                    rx.text("Lọc theo trạng thái:", size="2", color="slate.9", weight="medium"),
                    rx.hstack(
                        tab_btn("Tất cả", "ALL", ContributionState.total_count, "blue"),
                        tab_btn("Chờ duyệt", "PENDING", ContributionState.pending_count, "amber"),
                        tab_btn("Đã duyệt", "APPROVED", ContributionState.approved_count, "green"),
                        tab_btn("Từ chối", "REJECTED", ContributionState.rejected_count, "red"),
                        spacing="2",
                    ),
                    align="center",
                    spacing="4",
                ),
                variant="surface",
                padding="3",
            ),

            # ── Contribution List ──
            rx.cond(
                ContributionState.filtered_contributions.length() > 0,
                rx.vstack(
                    rx.foreach(
                        ContributionState.filtered_contributions,
                        contribution_row,
                    ),
                    spacing="3",
                    width="100%",
                ),
                empty_state(ContributionState.active_tab),
            ),

            # ── Dialogs ──
            detail_dialog(),
            version_dialog(),
            revoke_confirm_dialog(),

            spacing="5",
            width="100%",
        ),
        active_route="/student/contributions",
    )
