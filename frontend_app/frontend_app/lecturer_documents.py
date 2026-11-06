"""
DocUni - Trang Quản Lý Kho Tài Liệu Giảng Viên (Task 4.1)
Route: /lecturer/documents
Framework: Reflex (Python Full-Stack)

Cung cấp đầy đủ các nghiệp vụ quản trị học liệu cho giảng viên:
- CRUD Tài liệu: Xem bảng, thêm mới, chỉnh sửa thông tin, xóa an toàn.
- Quản lý phiên bản: Xem lịch sử các version v1.0, v2.0, nộp bản cập nhật mới.
- Quản lý phân quyền động: Cấp quyền xem/tải/sửa theo Khoa, theo Lớp hoặc Công khai.
"""

import dataclasses
from datetime import datetime
from typing import List, Dict, Any
import reflex as rx
from .common_components import lecturer_page_wrapper


# ─── Dataclass Models ────────────────────────────────────────────────────────

@dataclasses.dataclass
class DocVersion:
    version: str = "v1.0"
    file_name: str = ""
    change_summary: str = ""
    uploaded_at: str = ""
    file_size: str = ""


@dataclasses.dataclass
class DocPermission:
    id: str = ""
    scope_type: str = "DEPARTMENT"  # "PUBLIC", "DEPARTMENT", "CLASS"
    target_name: str = ""
    can_view: bool = True
    can_download: bool = True
    can_edit: bool = False


@dataclasses.dataclass
class LecturerDoc:
    id: str = ""
    title: str = ""
    subject_code: str = ""
    subject_name: str = ""
    faculty: str = "CNTT"
    folder_name: str = ""
    doc_type: str = "TEXTBOOK"  # "TEXTBOOK", "SLIDE", "EXAM", "EXERCISE", "REFERENCE"
    type_label: str = "Giáo trình"
    type_color: str = "blue"
    current_version: str = "v1.0"
    file_name: str = ""
    file_size: str = "12.4 MB"
    downloads: int = 0
    views: int = 0
    is_public: bool = True
    permission_summary: str = "Công khai toàn trường"
    updated_at: str = ""
    description: str = ""
    tags: List[str] = dataclasses.field(default_factory=list)
    versions: List[DocVersion] = dataclasses.field(default_factory=list)
    permissions: List[DocPermission] = dataclasses.field(default_factory=list)


# ─── Initial Mock Data ───────────────────────────────────────────────────────

MOCK_LECTURER_DOCS = [
    LecturerDoc(
        id="ld1",
        title="Giáo trình Cấu trúc dữ liệu và giải thuật 2026",
        subject_code="IT202",
        subject_name="Cấu trúc dữ liệu & GT",
        faculty="CNTT",
        folder_name="Giáo trình chính thức",
        doc_type="TEXTBOOK",
        type_label="Giáo trình",
        type_color="blue",
        current_version="v2.1",
        file_name="GiaoTrinh_CTDL_GT_2026.pdf",
        file_size="15.8 MB",
        downloads=1240,
        views=3150,
        is_public=True,
        permission_summary="Công khai toàn trường",
        updated_at="2026-10-12 14:30",
        description="Giáo trình cập nhật cấu trúc cây nhị phân, thuật toán đồ thị Dijkstra và bảng băm.",
        tags=["ctdl", "python", "giai-thuat"],
        versions=[
            DocVersion("v2.1", "GiaoTrinh_CTDL_GT_2026.pdf", "Cập nhật bài tập cây AVL và Đồ thị", "2026-10-12 14:30", "15.8 MB"),
            DocVersion("v2.0", "GiaoTrinh_CTDL_GT_v2.pdf", "Tái cấu trúc chương 4 cây nhị phân", "2026-09-01 09:15", "14.2 MB"),
            DocVersion("v1.0", "GiaoTrinh_CTDL_GT_v1.pdf", "Bản phát hành đầu tiên", "2026-01-15 10:00", "12.0 MB"),
        ],
        permissions=[
            DocPermission("p1", "PUBLIC", "Toàn bộ sinh viên học viện", True, True, False),
        ],
    ),
    LecturerDoc(
        id="ld2",
        title="Bộ Slide Bài giảng: Cơ sở dữ liệu nâng cao",
        subject_code="IT305",
        subject_name="Cơ sở dữ liệu",
        faculty="CNTT",
        folder_name="Slide Bài giảng",
        doc_type="SLIDE",
        type_label="Slide Bài giảng",
        type_color="orange",
        current_version="v1.2",
        file_name="Slide_CSDL_Chuong1_8.pptx",
        file_size="28.4 MB",
        downloads=890,
        views=2100,
        is_public=False,
        permission_summary="Khoa CNTT (Lớp D21CQCN01-B)",
        updated_at="2026-10-10 16:20",
        description="Tổng hợp slide bài giảng chuẩn hóa 3NF, BCNF, Stored Procedures và Indexing.",
        tags=["csdl", "sql", "slide"],
        versions=[
            DocVersion("v1.2", "Slide_CSDL_Chuong1_8.pptx", "Bổ sung ví dụ Transaction và ACID", "2026-10-10 16:20", "28.4 MB"),
            DocVersion("v1.0", "Slide_CSDL_v1.pptx", "Slide cơ bản", "2026-08-20 08:30", "24.0 MB"),
        ],
        permissions=[
            DocPermission("p2", "CLASS", "Lớp D21CQCN01-B", True, True, False),
            DocPermission("p3", "DEPARTMENT", "Bộ môn Hệ thống thông tin", True, True, True),
        ],
    ),
    LecturerDoc(
        id="ld3",
        title="Đề thi cuối kỳ Nhập môn lập trình (Kèm Đáp án)",
        subject_code="IT101",
        subject_name="Nhập môn lập trình",
        faculty="CNTT",
        folder_name="Đề thi & Đáp án",
        doc_type="EXAM",
        type_label="Đề thi & Đáp án",
        type_color="red",
        current_version="v1.0",
        file_name="IT101_DeThi_HocKy1_2025.pdf",
        file_size="4.2 MB",
        downloads=1650,
        views=4200,
        is_public=True,
        permission_summary="Công khai toàn trường",
        updated_at="2026-10-05 11:10",
        description="Đề thi 4 mã đề kèm đáp án thang điểm chi tiết cho sinh viên khóa 2024-2025.",
        tags=["de-thi", "it101", "python"],
        versions=[
            DocVersion("v1.0", "IT101_DeThi_HocKy1_2025.pdf", "Bản chính thức", "2026-10-05 11:10", "4.2 MB"),
        ],
        permissions=[
            DocPermission("p4", "PUBLIC", "Toàn trường", True, True, False),
        ],
    ),
    LecturerDoc(
        id="ld4",
        title="Bài tập lớn Lập trình Web Full-Stack với Python & Reflex",
        subject_code="IT410",
        subject_name="Lập trình Web",
        faculty="CNTT",
        folder_name="Bài tập & Đồ án",
        doc_type="EXERCISE",
        type_label="Bài tập lớn",
        type_color="purple",
        current_version="v1.1",
        file_name="BTL_Web_FullStack_Reflex.docx",
        file_size="2.1 MB",
        downloads=540,
        views=1350,
        is_public=False,
        permission_summary="Lớp D21CQCN02-B",
        updated_at="2026-10-08 09:40",
        description="Đề cương yêu cầu đồ án môn học: Xây dựng hệ thống học liệu số với Reflex và Django REST.",
        tags=["web", "btl", "reflex"],
        versions=[
            DocVersion("v1.1", "BTL_Web_FullStack_Reflex.docx", "Cập nhật tiêu chí chấm điểm và deadline", "2026-10-08 09:40", "2.1 MB"),
            DocVersion("v1.0", "BTL_Web_Init.docx", "Đề bài ban đầu", "2026-09-15 14:00", "1.8 MB"),
        ],
        permissions=[
            DocPermission("p5", "CLASS", "Lớp D21CQCN02-B", True, True, False),
        ],
    ),
    LecturerDoc(
        id="ld5",
        title="Sách tham khảo: Thiết kế Hệ thống phân tán và Microservices",
        subject_code="IT420",
        subject_name="Kiến trúc phần mềm",
        faculty="CNTT",
        folder_name="Sách tham khảo",
        doc_type="REFERENCE",
        type_label="Tham khảo",
        type_color="green",
        current_version="v1.0",
        file_name="Distributed_Systems_Reference.pdf",
        file_size="42.5 MB",
        downloads=380,
        views=920,
        is_public=True,
        permission_summary="Công khai toàn trường",
        updated_at="2026-09-28 15:00",
        description="Tài liệu chuyên khảo về CAP theorem, Event-Driven Architecture và Message Queue.",
        tags=["microservices", "distributed", "kien-truc"],
        versions=[
            DocVersion("v1.0", "Distributed_Systems_Reference.pdf", "Bản dịch tham khảo", "2026-09-28 15:00", "42.5 MB"),
        ],
        permissions=[
            DocPermission("p6", "PUBLIC", "Toàn trường", True, True, False),
        ],
    ),
]

SUBJECT_LIST = [
    {"code": "ALL", "name": "Tất cả môn học"},
    {"code": "IT202", "name": "IT202 - Cấu trúc dữ liệu & GT"},
    {"code": "IT305", "name": "IT305 - Cơ sở dữ liệu"},
    {"code": "IT101", "name": "IT101 - Nhập môn lập trình"},
    {"code": "IT410", "name": "IT410 - Lập trình Web"},
    {"code": "IT420", "name": "IT420 - Kiến trúc phần mềm"},
]

DOC_TYPES_SELECT = [
    {"value": "TEXTBOOK", "label": "Giáo trình", "color": "blue"},
    {"value": "SLIDE", "label": "Slide Bài giảng", "color": "orange"},
    {"value": "EXAM", "label": "Đề thi & Đáp án", "color": "red"},
    {"value": "EXERCISE", "label": "Bài tập lớn", "color": "purple"},
    {"value": "REFERENCE", "label": "Sách tham khảo", "color": "green"},
]


# ─── State ───────────────────────────────────────────────────────────────────

class LecturerDocState(rx.State):
    """Quản trị toàn bộ vòng đời tài liệu của giảng viên."""

    documents: List[LecturerDoc] = MOCK_LECTURER_DOCS
    search_query: str = ""
    selected_subject: str = "ALL"
    selected_type: str = "ALL"

    # ── Edit / Create Document Modal ──
    show_edit_modal: bool = False
    is_create_mode: bool = False
    edit_doc_id: str = ""
    edit_title: str = ""
    edit_subject: str = "IT202"
    edit_folder: str = "Giáo trình chính thức"
    edit_type: str = "TEXTBOOK"
    edit_desc: str = ""
    edit_tags: List[str] = ["giao-trinh", "cntt"]
    new_tag_input: str = ""

    # ── Version History Modal ──
    show_version_modal: bool = False
    active_version_doc: LecturerDoc = LecturerDoc()
    new_version_file_name: str = ""
    new_version_summary: str = ""

    # ── Permission Modal ──
    show_permission_modal: bool = False
    active_perm_doc: LecturerDoc = LecturerDoc()
    new_perm_scope: str = "CLASS"
    new_perm_target: str = "Lớp D21CQCN01-B"
    new_perm_can_view: bool = True
    new_perm_can_download: bool = True
    new_perm_can_edit: bool = False

    # ── Delete Confirm Modal ──
    show_delete_modal: bool = False
    delete_doc_id: str = ""
    delete_doc_title: str = ""

    # Search & Filter
    def set_search_query(self, value: str):
        self.search_query = value

    def set_selected_subject(self, value: str):
        self.selected_subject = value

    def set_selected_type(self, value: str):
        self.selected_type = value

    @rx.var
    def filtered_docs(self) -> List[LecturerDoc]:
        query = self.search_query.strip().lower()
        docs = self.documents
        if self.selected_subject != "ALL":
            docs = [d for d in docs if d.subject_code == self.selected_subject]
        if self.selected_type != "ALL":
            docs = [d for d in docs if d.doc_type == self.selected_type]
        if query:
            docs = [
                d for d in docs
                if query in d.title.lower()
                or query in d.subject_code.lower()
                or query in d.folder_name.lower()
                or query in d.description.lower()
            ]
        return docs

    @rx.var
    def total_docs_count(self) -> int:
        return len(self.documents)

    @rx.var
    def total_downloads(self) -> int:
        return sum(d.downloads for d in self.documents)

    @rx.var
    def total_views(self) -> int:
        return sum(d.views for d in self.documents)

    # ── CRUD Modals Logic ──
    def open_create_modal(self):
        self.is_create_mode = True
        self.edit_doc_id = ""
        self.edit_title = ""
        self.edit_subject = "IT202"
        self.edit_folder = "Giáo trình chính thức"
        self.edit_type = "TEXTBOOK"
        self.edit_desc = ""
        self.edit_tags = ["học-liệu-mới"]
        self.new_tag_input = ""
        self.show_edit_modal = True

    def open_edit_modal(self, doc: LecturerDoc):
        self.is_create_mode = False
        self.edit_doc_id = doc.id
        self.edit_title = doc.title
        self.edit_subject = doc.subject_code
        self.edit_folder = doc.folder_name
        self.edit_type = doc.doc_type
        self.edit_desc = doc.description
        self.edit_tags = list(doc.tags)
        self.new_tag_input = ""
        self.show_edit_modal = True

    def close_edit_modal(self):
        self.show_edit_modal = False

    def set_edit_title(self, value: str):
        self.edit_title = value

    def set_edit_subject(self, value: str):
        self.edit_subject = value

    def set_edit_folder(self, value: str):
        self.edit_folder = value

    def set_edit_type(self, value: str):
        self.edit_type = value

    def set_edit_desc(self, value: str):
        self.edit_desc = value

    def set_new_tag_input(self, value: str):
        self.new_tag_input = value

    def add_edit_tag(self):
        tag = self.new_tag_input.strip().lower()
        if tag and tag not in self.edit_tags:
            self.edit_tags.append(tag)
            self.new_tag_input = ""

    def remove_edit_tag(self, tag: str):
        self.edit_tags = [t for t in self.edit_tags if t != tag]

    def save_document(self):
        if not self.edit_title.strip():
            return rx.toast.error("Vui lòng nhập tiêu đề tài liệu!")

        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        type_info = next((t for t in DOC_TYPES_SELECT if t["value"] == self.edit_type), DOC_TYPES_SELECT[0])

        if self.is_create_mode:
            new_id = f"ld_{len(self.documents) + 1}"
            subj_name = next((s["name"] for s in SUBJECT_LIST if s["code"] == self.edit_subject), self.edit_subject)
            new_doc = LecturerDoc(
                id=new_id,
                title=self.edit_title,
                subject_code=self.edit_subject,
                subject_name=subj_name,
                faculty="CNTT",
                folder_name=self.edit_folder,
                doc_type=self.edit_type,
                type_label=type_info["label"],
                type_color=type_info["color"],
                current_version="v1.0",
                file_name=f"{self.edit_subject}_{self.edit_title[:15]}.pdf",
                file_size="8.5 MB",
                downloads=0,
                views=1,
                is_public=True,
                permission_summary="Công khai toàn trường",
                updated_at=time_now,
                description=self.edit_desc,
                tags=list(self.edit_tags),
                versions=[
                    DocVersion("v1.0", f"{self.edit_subject}_Init.pdf", "Bản phát hành đầu tiên", time_now, "8.5 MB")
                ],
                permissions=[
                    DocPermission(f"p_{new_id}", "PUBLIC", "Toàn trường", True, True, False)
                ],
            )
            self.documents.insert(0, new_doc)
            self.show_edit_modal = False
            return rx.toast.success("Đã thêm tài liệu mới thành công!")
        else:
            updated = []
            for d in self.documents:
                if d.id == self.edit_doc_id:
                    d.title = self.edit_title
                    d.subject_code = self.edit_subject
                    d.folder_name = self.edit_folder
                    d.doc_type = self.edit_type
                    d.type_label = type_info["label"]
                    d.type_color = type_info["color"]
                    d.description = self.edit_desc
                    d.tags = list(self.edit_tags)
                    d.updated_at = time_now
                updated.append(d)
            self.documents = updated
            self.show_edit_modal = False
            return rx.toast.success("Đã cập nhật thông tin tài liệu!")

    # ── Version History Logic ──
    def open_version_modal(self, doc: LecturerDoc):
        self.active_version_doc = doc
        self.new_version_file_name = f"{doc.subject_code}_vUpdate.pdf"
        self.new_version_summary = ""
        self.show_version_modal = True

    def close_version_modal(self):
        self.show_version_modal = False

    def set_version_summary(self, value: str):
        self.new_version_summary = value

    def upload_new_version(self):
        if not self.new_version_summary.strip():
            return rx.toast.error("Vui lòng nhập tóm tắt nội dung thay đổi phiên bản!")

        doc_id = self.active_version_doc.id
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

        updated = []
        for d in self.documents:
            if d.id == doc_id:
                # Tăng version
                cur_v = float(d.current_version.replace("v", ""))
                new_v_str = f"v{cur_v + 1.0:.1f}"
                new_ver = DocVersion(
                    version=new_v_str,
                    file_name=self.new_version_file_name,
                    change_summary=self.new_version_summary,
                    uploaded_at=time_now,
                    file_size="16.2 MB",
                )
                d.current_version = new_v_str
                d.file_name = self.new_version_file_name
                d.updated_at = time_now
                d.versions.insert(0, new_ver)
                self.active_version_doc = d
            updated.append(d)

        self.documents = updated
        self.new_version_summary = ""
        self.show_version_modal = False
        return rx.toast.success("Đã xuất bản phiên bản mới thành công!")

    # ── Permission Logic ──
    def open_permission_modal(self, doc: LecturerDoc):
        self.active_perm_doc = doc
        self.new_perm_scope = "CLASS"
        self.new_perm_target = "Lớp D21CQCN01-B"
        self.new_perm_can_view = True
        self.new_perm_can_download = True
        self.new_perm_can_edit = False
        self.show_permission_modal = True

    def close_permission_modal(self):
        self.show_permission_modal = False

    def set_new_perm_scope(self, value: str):
        self.new_perm_scope = value

    def set_new_perm_target(self, value: str):
        self.new_perm_target = value

    def toggle_can_view(self, value: bool):
        self.new_perm_can_view = value

    def toggle_can_download(self, value: bool):
        self.new_perm_can_download = value

    def toggle_can_edit(self, value: bool):
        self.new_perm_can_edit = value

    def add_permission(self):
        if not self.new_perm_target.strip():
            return rx.toast.error("Vui lòng nhập đối tượng áp dụng quyền!")

        doc_id = self.active_perm_doc.id
        perm = DocPermission(
            id=f"perm_{datetime.now().timestamp()}",
            scope_type=self.new_perm_scope,
            target_name=self.new_perm_target,
            can_view=self.new_perm_can_view,
            can_download=self.new_perm_can_download,
            can_edit=self.new_perm_can_edit,
        )

        updated = []
        for d in self.documents:
            if d.id == doc_id:
                d.permissions.append(perm)
                d.permission_summary = f"Phân quyền theo {self.new_perm_scope}: {self.new_perm_target}"
                self.active_perm_doc = d
            updated.append(d)

        self.documents = updated
        return rx.toast.success("Đã bổ sung cấu hình quyền thành công!")

    def remove_permission(self, perm_id: str):
        doc_id = self.active_perm_doc.id
        updated = []
        for d in self.documents:
            if d.id == doc_id:
                d.permissions = [p for p in d.permissions if p.id != perm_id]
                if not d.permissions:
                    d.permission_summary = "Chưa thiết lập quyền"
                self.active_perm_doc = d
            updated.append(d)
        self.documents = updated
        return rx.toast.info("Đã xóa quyền truy cập.")

    # ── Delete Logic ──
    def open_delete_modal(self, doc_id: str, title: str):
        self.delete_doc_id = doc_id
        self.delete_doc_title = title
        self.show_delete_modal = True

    def close_delete_modal(self):
        self.show_delete_modal = False
        self.delete_doc_id = ""

    def confirm_delete(self):
        doc_id = self.delete_doc_id
        self.documents = [d for d in self.documents if d.id != doc_id]
        self.show_delete_modal = False
        self.delete_doc_id = ""
        return rx.toast.success("Đã xóa tài liệu khỏi hệ thống!")


# ─── UI Helper Components ────────────────────────────────────────────────────

def doc_table_row(doc: LecturerDoc) -> rx.Component:
    return rx.table.row(
        # 1. Tên tài liệu & Mã môn
        rx.table.cell(
            rx.vstack(
                rx.hstack(
                    rx.badge(doc.subject_code, color_scheme="blue", variant="surface", size="1"),
                    rx.badge(doc.type_label, color_scheme=doc.type_color, variant="surface", size="1"),
                    align="center",
                    spacing="1",
                ),
                rx.text(doc.title, size="2", weight="bold", color="slate.12", line_clamp=1),
                rx.text(f"Thư mục: {doc.folder_name}", size="1", color="slate.8"),
                spacing="1",
                align="start",
            ),
        ),
        # 2. Phiên bản
        rx.table.cell(
            rx.vstack(
                rx.badge(doc.current_version, color_scheme="indigo", variant="solid", size="2"),
                rx.text(doc.file_size, size="1", color="slate.8"),
                spacing="1",
                align="center",
            ),
        ),
        # 3. Phân quyền
        rx.table.cell(
            rx.vstack(
                rx.badge(doc.permission_summary, color_scheme="gray", variant="surface", size="1"),
                rx.text(f"Cập nhật: {doc.updated_at}", size="1", color="slate.8"),
                spacing="1",
                align="start",
            ),
        ),
        # 4. Thống kê Xem/Tải
        rx.table.cell(
            rx.hstack(
                rx.hstack(
                    rx.icon("eye", size=13, color="var(--blue-9)"),
                    rx.text(doc.views.to_string(), size="1", color="slate.10", weight="medium"),
                    align="center",
                    spacing="1",
                ),
                rx.hstack(
                    rx.icon("download", size=13, color="var(--green-9)"),
                    rx.text(doc.downloads.to_string(), size="1", color="green.11", weight="bold"),
                    align="center",
                    spacing="1",
                ),
                align="center",
                spacing="3",
            ),
        ),
        # 5. Các nút thao tác
        rx.table.cell(
            rx.hstack(
                # Nút Sửa
                rx.button(
                    rx.icon("pencil", size=13),
                    "Sửa",
                    size="1",
                    variant="surface",
                    color_scheme="blue",
                    on_click=LecturerDocState.open_edit_modal(doc),
                ),
                # Nút Version
                rx.button(
                    rx.icon("git-branch", size=13),
                    "Version",
                    size="1",
                    variant="surface",
                    color_scheme="indigo",
                    on_click=LecturerDocState.open_version_modal(doc),
                ),
                # Nút Phân quyền
                rx.button(
                    rx.icon("shield", size=13),
                    "Quyền",
                    size="1",
                    variant="surface",
                    color_scheme="teal",
                    on_click=LecturerDocState.open_permission_modal(doc),
                ),
                # Nút Xóa
                rx.button(
                    rx.icon("trash-2", size=13),
                    size="1",
                    variant="ghost",
                    color_scheme="red",
                    on_click=LecturerDocState.open_delete_modal(doc.id, doc.title),
                ),
                align="center",
                spacing="2",
            ),
        ),
    )


# ─── Modal 1: Thêm Mới / Chỉnh Sửa Tài Liệu ──────────────────────────────────

def edit_create_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("file-text", size=20, color="var(--blue-9)"),
                        bg="blue.3",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.heading(
                            rx.cond(LecturerDocState.is_create_mode, "Thêm Mới Học Liệu", "Chỉnh Sửa Thông Tin Học Liệu"),
                            size="4",
                            weight="bold",
                            color="slate.12",
                        ),
                        rx.text("Cập nhật thông tin tiêu đề, môn học, thư mục và gắn thẻ tags", size="2", color="slate.9"),
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

                # Tiêu đề
                rx.vstack(
                    rx.text("Tiêu đề tài liệu:", size="2", weight="bold", color="slate.11"),
                    rx.input(
                        placeholder="Nhập tiêu đề (VD: Giáo trình Cấu trúc dữ liệu 2026)...",
                        value=LecturerDocState.edit_title,
                        on_change=LecturerDocState.set_edit_title,
                        size="2",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),

                # Môn học & Loại tài liệu
                rx.grid(
                    rx.vstack(
                        rx.text("Môn học phụ trách:", size="2", weight="bold", color="slate.11"),
                        rx.select.root(
                            rx.select.trigger(width="100%", size="2"),
                            rx.select.content(
                                rx.select.item("IT202 - Cấu trúc dữ liệu & GT", value="IT202"),
                                rx.select.item("IT305 - Cơ sở dữ liệu", value="IT305"),
                                rx.select.item("IT101 - Nhập môn lập trình", value="IT101"),
                                rx.select.item("IT410 - Lập trình Web", value="IT410"),
                                rx.select.item("IT420 - Kiến trúc phần mềm", value="IT420"),
                            ),
                            value=LecturerDocState.edit_subject,
                            on_change=LecturerDocState.set_edit_subject,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Loại học liệu:", size="2", weight="bold", color="slate.11"),
                        rx.select.root(
                            rx.select.trigger(width="100%", size="2"),
                            rx.select.content(
                                rx.select.item("Giáo trình", value="TEXTBOOK"),
                                rx.select.item("Slide Bài giảng", value="SLIDE"),
                                rx.select.item("Đề thi & Đáp án", value="EXAM"),
                                rx.select.item("Bài tập lớn", value="EXERCISE"),
                                rx.select.item("Sách tham khảo", value="REFERENCE"),
                            ),
                            value=LecturerDocState.edit_type,
                            on_change=LecturerDocState.set_edit_type,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),

                # Thư mục lưu trữ
                rx.vstack(
                    rx.text("Thư mục lưu trữ:", size="2", weight="bold", color="slate.11"),
                    rx.input(
                        placeholder="Nhập tên thư mục (VD: Giáo trình chính thức, Slide bài giảng...)",
                        value=LecturerDocState.edit_folder,
                        on_change=LecturerDocState.set_edit_folder,
                        size="2",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),

                # Mô tả tóm tắt
                rx.vstack(
                    rx.text("Mô tả nội dung:", size="2", weight="bold", color="slate.11"),
                    rx.text_area(
                        placeholder="Mô tả ngắn gọn về tài liệu để sinh viên nắm được mục tiêu...",
                        value=LecturerDocState.edit_desc,
                        on_change=LecturerDocState.set_edit_desc,
                        size="2",
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),

                # Tags chip
                rx.vstack(
                    rx.text("Gắn nhãn (Tags):", size="2", weight="bold", color="slate.11"),
                    rx.hstack(
                        rx.input(
                            placeholder="Nhập tag mới...",
                            value=LecturerDocState.new_tag_input,
                            on_change=LecturerDocState.set_new_tag_input,
                            size="2",
                            flex="1",
                        ),
                        rx.button(
                            rx.icon("plus", size=14),
                            "Thêm tag",
                            size="2",
                            variant="surface",
                            color_scheme="blue",
                            on_click=LecturerDocState.add_edit_tag,
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.foreach(
                            LecturerDocState.edit_tags,
                            lambda t: rx.badge(
                                rx.hstack(
                                    rx.text(t, size="1"),
                                    rx.icon("x", size=12, on_click=LecturerDocState.remove_edit_tag(t)),
                                    align="center",
                                    spacing="1",
                                ),
                                color_scheme="blue",
                                variant="surface",
                                size="1",
                            ),
                        ),
                        spacing="1",
                        flex_wrap="wrap",
                    ),
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
                        rx.icon("check", size=15),
                        "Lưu tài liệu",
                        color_scheme="blue",
                        size="2",
                        variant="solid",
                        on_click=LecturerDocState.save_document,
                    ),
                    align="center",
                    spacing="2",
                    width="100%",
                    padding_top="2",
                ),

                spacing="3",
                width="100%",
            ),
            max_width="540px",
            padding="5",
        ),
        open=LecturerDocState.show_edit_modal,
        on_open_change=LecturerDocState.close_edit_modal,
    )


# ─── Modal 2: Quản Lý Lịch Sử Phiên Bản (Version History) ────────────────────

def version_row(v: DocVersion) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.badge(v.version, color_scheme="indigo", variant="solid", size="2"),
            rx.vstack(
                rx.text(v.file_name, size="2", weight="bold", color="slate.12"),
                rx.text(v.change_summary, size="1", color="slate.9"),
                rx.hstack(
                    rx.text(f"Ngày nộp: {v.uploaded_at}", size="1", color="slate.8"),
                    rx.text("•", size="1", color="slate.6"),
                    rx.text(v.file_size, size="1", color="slate.8"),
                    align="center",
                    spacing="1",
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("download", size=13),
                "Tải bản này",
                size="1",
                variant="surface",
                color_scheme="gray",
                on_click=rx.toast.info(f"Đang tải bản {v.version}: {v.file_name}"),
            ),
            align="center",
            width="100%",
        ),
        variant="surface",
        padding="3",
        width="100%",
    )


def version_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("git-branch", size=20, color="var(--indigo-9)"),
                        bg="indigo.3",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.heading("Lịch Sử Phiên Bản & Xuất Bản Mới", size="4", weight="bold", color="slate.12"),
                        rx.text(LecturerDocState.active_version_doc.title, size="2", color="indigo.10", weight="medium"),
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

                # Form nộp version mới
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("cloud-upload", size=16, color="var(--indigo-9)"),
                            rx.text("Xuất bản phiên bản tiếp theo:", size="2", weight="bold", color="indigo-11"),
                            align="center",
                            spacing="1",
                        ),
                        rx.input(
                            placeholder="Tóm tắt thay đổi (VD: Cập nhật đề cương, bổ sung lời giải bài 4...)...",
                            value=LecturerDocState.new_version_summary,
                            on_change=LecturerDocState.set_version_summary,
                            size="2",
                            width="100%",
                        ),
                        rx.button(
                            rx.icon("circle-check", size=14),
                            "Xuất bản Version mới",
                            color_scheme="indigo",
                            size="2",
                            variant="solid",
                            on_click=LecturerDocState.upload_new_version,
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    bg="var(--indigo-2)",
                    border="1px solid var(--indigo-5)",
                    padding="3",
                    width="100%",
                ),

                rx.text("Các phiên bản đã lưu trữ trước đây:", size="2", weight="bold", color="slate.11"),

                # Danh sách version cũ
                rx.vstack(
                    rx.foreach(
                        LecturerDocState.active_version_doc.versions,
                        version_row,
                    ),
                    spacing="2",
                    width="100%",
                    max_height="280px",
                    overflow_y="auto",
                ),

                rx.hstack(
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button("Đóng lại", variant="surface", color_scheme="gray", size="2"),
                    ),
                    align="center",
                    width="100%",
                    padding_top="2",
                ),

                spacing="3",
                width="100%",
            ),
            max_width="560px",
            padding="5",
        ),
        open=LecturerDocState.show_version_modal,
        on_open_change=LecturerDocState.close_version_modal,
    )


# ─── Modal 3: Phân Quyền Truy Cập (Access Control) ───────────────────────────

def perm_item_row(p: DocPermission) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.badge(p.scope_type, color_scheme="teal", variant="surface", size="1"),
            rx.vstack(
                rx.text(p.target_name, size="2", weight="bold", color="slate.12"),
                rx.hstack(
                    rx.badge(rx.cond(p.can_view, "Được xem", "Cấm xem"), color_scheme=rx.cond(p.can_view, "green", "red"), variant="surface", size="1"),
                    rx.badge(rx.cond(p.can_download, "Được tải", "Cấm tải"), color_scheme=rx.cond(p.can_download, "green", "red"), variant="surface", size="1"),
                    rx.badge(rx.cond(p.can_edit, "Được sửa", "Chỉ đọc"), color_scheme=rx.cond(p.can_edit, "amber", "gray"), variant="surface", size="1"),
                    align="center",
                    spacing="1",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("trash", size=13),
                size="1",
                variant="ghost",
                color_scheme="red",
                on_click=LecturerDocState.remove_permission(p.id),
            ),
            align="center",
            width="100%",
        ),
        variant="surface",
        padding="2",
        width="100%",
    )


def permission_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("shield-check", size=20, color="var(--teal-9)"),
                        bg="teal.3",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.heading("Phân Quyền Truy Cập Học Liệu", size="4", weight="bold", color="slate.12"),
                        rx.text(LecturerDocState.active_perm_doc.title, size="2", color="teal.10", weight="medium"),
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

                # Form gán quyền mới
                rx.card(
                    rx.vstack(
                        rx.text("Cấp quyền mới:", size="2", weight="bold", color="slate.12"),
                        rx.grid(
                            rx.vstack(
                                rx.text("Phạm vi cấp quyền:", size="1", color="slate.8"),
                                rx.select.root(
                                    rx.select.trigger(width="100%", size="2"),
                                    rx.select.content(
                                        rx.select.item("Lớp học cụ thể", value="CLASS"),
                                        rx.select.item("Toàn bộ Khoa", value="DEPARTMENT"),
                                        rx.select.item("Công khai toàn trường", value="PUBLIC"),
                                    ),
                                    value=LecturerDocState.new_perm_scope,
                                    on_change=LecturerDocState.set_new_perm_scope,
                                ),
                                spacing="1",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("Tên đối tượng áp dụng:", size="1", color="slate.8"),
                                rx.input(
                                    placeholder="VD: Lớp D21CQCN01-B...",
                                    value=LecturerDocState.new_perm_target,
                                    on_change=LecturerDocState.set_new_perm_target,
                                    size="2",
                                    width="100%",
                                ),
                                spacing="1",
                                width="100%",
                            ),
                            columns="2",
                            spacing="2",
                            width="100%",
                        ),
                        # Checkboxes quyền
                        rx.hstack(
                            rx.hstack(
                                rx.checkbox(checked=LecturerDocState.new_perm_can_view, on_change=LecturerDocState.toggle_can_view),
                                rx.text("Được xem", size="2", color="slate.10"),
                                align="center",
                                spacing="1",
                            ),
                            rx.hstack(
                                rx.checkbox(checked=LecturerDocState.new_perm_can_download, on_change=LecturerDocState.toggle_can_download),
                                rx.text("Được tải", size="2", color="slate.10"),
                                align="center",
                                spacing="1",
                            ),
                            rx.hstack(
                                rx.checkbox(checked=LecturerDocState.new_perm_can_edit, on_change=LecturerDocState.toggle_can_edit),
                                rx.text("Được chỉnh sửa", size="2", color="slate.10"),
                                align="center",
                                spacing="1",
                            ),
                            align="center",
                            spacing="4",
                            padding_y="1",
                        ),
                        rx.button(
                            rx.icon("plus", size=14),
                            "Áp dụng cấu hình quyền",
                            color_scheme="teal",
                            size="2",
                            variant="solid",
                            on_click=LecturerDocState.add_permission,
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    bg="var(--teal-2)",
                    border="1px solid var(--teal-5)",
                    padding="3",
                    width="100%",
                ),

                rx.text("Danh sách phân quyền đang có hiệu lực:", size="2", weight="bold", color="slate.11"),

                # Danh sách quyền
                rx.vstack(
                    rx.foreach(
                        LecturerDocState.active_perm_doc.permissions,
                        perm_item_row,
                    ),
                    spacing="2",
                    width="100%",
                    max_height="220px",
                    overflow_y="auto",
                ),

                rx.hstack(
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button("Xong", variant="surface", color_scheme="gray", size="2"),
                    ),
                    align="center",
                    width="100%",
                    padding_top="2",
                ),

                spacing="3",
                width="100%",
            ),
            max_width="560px",
            padding="5",
        ),
        open=LecturerDocState.show_permission_modal,
        on_open_change=LecturerDocState.close_permission_modal,
    )


# ─── Modal 4: Xác Nhận Xóa Tài Liệu ──────────────────────────────────────────

def delete_confirm_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("triangle-alert", size=24, color="var(--red-9)"),
                    rx.heading("Xác Nhận Xóa Tài Liệu", size="4", weight="bold", color="red.11"),
                    align="center",
                    spacing="2",
                ),
                rx.text(
                    f"Bạn có chắc chắn muốn xóa tài liệu '{LecturerDocState.delete_doc_title}'? Hành động này sẽ gỡ bỏ tài liệu và toàn bộ lịch sử phiên bản khỏi kho học liệu.",
                    size="2",
                    color="slate.10",
                    line_height="1.5",
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button("Hủy bỏ", variant="surface", color_scheme="gray", size="2"),
                    ),
                    rx.button(
                        rx.icon("trash-2", size=14),
                        "Xóa vĩnh viễn",
                        color_scheme="red",
                        size="2",
                        variant="solid",
                        on_click=LecturerDocState.confirm_delete,
                    ),
                    align="center",
                    spacing="2",
                    width="100%",
                    padding_top="2",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="440px",
            padding="4",
        ),
        open=LecturerDocState.show_delete_modal,
        on_open_change=LecturerDocState.close_delete_modal,
    )


# ─── Main Page ───────────────────────────────────────────────────────────────

def lecturer_documents_page() -> rx.Component:
    return lecturer_page_wrapper(
        rx.vstack(
            # ── Header Bar ──
            rx.hstack(
                rx.vstack(
                    rx.heading("Quản Lý Kho Tài Liệu Phụ Trách", size="6", weight="bold", color="slate.12"),
                    rx.text("Danh mục học liệu cá nhân và bộ môn: Thêm mới, chỉnh sửa, phân quyền và quản lý phiên bản", size="2", color="slate.9"),
                    spacing="1",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("plus", size=16),
                    "Thêm mới học liệu",
                    color_scheme="indigo",
                    size="3",
                    variant="solid",
                    on_click=LecturerDocState.open_create_modal,
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
                            rx.icon("files", size=20, color="var(--blue-9)"),
                            bg="blue.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Tổng số tài liệu", size="1", color="slate.8"),
                            rx.text(LecturerDocState.total_docs_count.to_string(), size="5", weight="bold", color="slate.12"),
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
                            rx.icon("eye", size=20, color="var(--indigo-9)"),
                            bg="indigo.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Tổng lượt xem", size="1", color="slate.8"),
                            rx.text(LecturerDocState.total_views.to_string(), size="5", weight="bold", color="indigo.11"),
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
                            rx.icon("download", size=20, color="var(--green-9)"),
                            bg="green.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Tổng lượt tải", size="1", color="slate.8"),
                            rx.text(LecturerDocState.total_downloads.to_string(), size="5", weight="bold", color="green.11"),
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
                            rx.icon("hard-drive", size=20, color="var(--purple-9)"),
                            bg="purple.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Dung lượng kho", size="1", color="slate.8"),
                            rx.text("92.8 MB", size="5", weight="bold", color="purple.11"),
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

            # ── Filter & Search Controls ──
            rx.card(
                rx.hstack(
                    rx.input(
                        rx.input.slot(rx.icon("search", size=16, color="var(--slate-8)")),
                        placeholder="Tìm kiếm tài liệu theo tiêu đề, môn học, thư mục...",
                        value=LecturerDocState.search_query,
                        on_change=LecturerDocState.set_search_query,
                        size="2",
                        flex="1",
                    ),
                    rx.select.root(
                        rx.select.trigger(width="240px", size="2"),
                        rx.select.content(
                            rx.select.item("Tất cả môn học", value="ALL"),
                            rx.select.item("IT202 - Cấu trúc dữ liệu & GT", value="IT202"),
                            rx.select.item("IT305 - Cơ sở dữ liệu", value="IT305"),
                            rx.select.item("IT101 - Nhập môn lập trình", value="IT101"),
                            rx.select.item("IT410 - Lập trình Web", value="IT410"),
                            rx.select.item("IT420 - Kiến trúc phần mềm", value="IT420"),
                        ),
                        value=LecturerDocState.selected_subject,
                        on_change=LecturerDocState.set_selected_subject,
                    ),
                    rx.select.root(
                        rx.select.trigger(width="180px", size="2"),
                        rx.select.content(
                            rx.select.item("Tất cả loại học liệu", value="ALL"),
                            rx.select.item("Giáo trình", value="TEXTBOOK"),
                            rx.select.item("Slide Bài giảng", value="SLIDE"),
                            rx.select.item("Đề thi & Đáp án", value="EXAM"),
                            rx.select.item("Bài tập lớn", value="EXERCISE"),
                            rx.select.item("Sách tham khảo", value="REFERENCE"),
                        ),
                        value=LecturerDocState.selected_type,
                        on_change=LecturerDocState.set_selected_type,
                    ),
                    spacing="3",
                    width="100%",
                ),
                variant="surface",
                padding="3",
                width="100%",
            ),

            # ── Data Table ──
            rx.card(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Thông tin tài liệu"),
                            rx.table.column_header_cell("Phiên bản"),
                            rx.table.column_header_cell("Phạm vi quyền"),
                            rx.table.column_header_cell("Lượt xem / Tải"),
                            rx.table.column_header_cell("Thao tác"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            LecturerDocState.filtered_docs,
                            doc_table_row,
                        ),
                    ),
                    width="100%",
                ),
                variant="surface",
                padding="0",
                width="100%",
            ),

            # Modals
            edit_create_modal(),
            version_modal(),
            permission_modal(),
            delete_confirm_modal(),

            spacing="4",
            width="100%",
        ),
        current_route="/lecturer/documents",
    )
