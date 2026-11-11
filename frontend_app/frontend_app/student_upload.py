"""
DocUni - Task 3.1: Trang Đóng Góp Tài Liệu (Student Upload)
Route: /student/upload
Framework: Reflex (Python Full-Stack)

State quản lý:
- Danh sách khoa, môn học, thư mục (phân cấp động)
- File được chọn upload
- Tags chip (thêm/xóa)
- Validation + Submit gửi đóng góp
- Thông báo kết quả qua rx.toast (Sonner)
"""

import reflex as rx
from typing import List
from .common_components import student_page_wrapper
from .data_store import GlobalDocState
from .storage_service import StorageService

# ─── Dữ liệu danh mục thực tế từ PostgreSQL ───

def get_real_departments():
    try:
        import httpx
        r = httpx.get("http://127.0.0.1:8000/api/departments/", timeout=2.0)
        if r.status_code == 200:
            return [{"id": str(d["id"]), "name": d["department_name"]} for d in r.json().get("departments", [])]
    except Exception:
        pass
    return [
        {"id": "1", "name": "Khoa Công nghệ thông tin"},
        {"id": "2", "name": "Khoa Kinh tế"},
        {"id": "3", "name": "Khoa Ngoại ngữ"},
    ]

def get_real_subjects():
    try:
        import httpx
        r = httpx.get("http://127.0.0.1:8000/api/subjects/", timeout=2.0)
        if r.status_code == 200:
            subs = r.json().get("subjects", [])
            mapping = {}
            for s in subs:
                dept_id = str(s.get("department_id", "1"))
                mapping.setdefault(dept_id, []).append({
                    "id": str(s.get("id")),
                    "name": f"{s.get('subject_name')}"
                })
            return mapping
    except Exception:
        pass
    return {
        "1": [{"id": "1", "name": "Cấu trúc dữ liệu & GT"}, {"id": "2", "name": "Cơ sở dữ liệu"}],
        "2": [{"id": "4", "name": "Kinh tế vi mô"}],
    }

def get_real_folders():
    return {
        "1": ["Slide bài giảng", "Bài tập thực hành", "Đề thi & Đáp án"],
        "2": ["Slide bài giảng", "Script SQL", "Đồ án"],
        "4": ["Slide bài giảng", "Bài tập kinh tế"],
    }

DOC_TYPES = [
    {"value": "SLIDE", "label": "Slide Bài giảng", "icon": "presentation"},
    {"value": "TEXTBOOK", "label": "Giáo trình / Sách", "icon": "book"},
    {"value": "EXERCISE", "label": "Bài tập thực hành", "icon": "pencil-line"},
    {"value": "EXAM", "label": "Đề thi / Đáp án", "icon": "file-check"},
    {"value": "REFERENCE", "label": "Tài liệu tham khảo", "icon": "library"},
    {"value": "OTHER", "label": "Loại khác", "icon": "file"},
]

SUGGESTED_TAGS = [
    "Python", "Java", "CSDL", "SQL", "Toán rời rạc", "Mạng máy tính",
    "Giữa kỳ", "Cuối kỳ", "Bài tập lớn", "Thực hành", "Lý thuyết", "Đề cương"
]

# ─── State ───────────────────────────────────────────────────────────────────

class UploadState(rx.State):
    """Quản lý toàn bộ logic trang Đóng góp tài liệu."""

    # Form fields
    title: str = ""
    description: str = ""
    selected_dept_id: str = ""
    selected_subject_id: str = ""
    selected_folder: str = ""
    new_folder_name: str = ""
    doc_type: str = "SLIDE"
    is_public: bool = True

    # Tags
    tags: List[str] = []
    tag_input: str = ""

    # File upload
    uploaded_filename: str = ""
    uploaded_filesize: str = ""

    # UI state
    show_new_folder_input: bool = False
    is_submitting: bool = False
    submit_success: bool = False
    error_message: str = ""

    @rx.var
    def available_subjects(self) -> List[dict]:
        if not self.selected_dept_id:
            return []
        return get_real_subjects().get(self.selected_dept_id, [])

    @rx.var
    def available_folders(self) -> List[str]:
        if not self.selected_subject_id:
            return []
        return get_real_folders().get(self.selected_subject_id, ['Tài liệu chung', 'Slide bài giảng', 'Đề thi'])

    @rx.var
    def dept_options(self) -> List[dict]:
        return get_real_departments()

    @rx.var
    def is_form_valid(self) -> bool:
        return (
            len(self.title.strip()) >= 3
            and self.selected_dept_id != ""
            and self.selected_subject_id != ""
            and self.selected_folder != ""
        )

    @rx.var
    def char_count(self) -> str:
        return f"{len(self.description)}/500"

    def set_title(self, value: str):
        self.title = value
        self.error_message = ""

    def set_description(self, value: str):
        if len(value) <= 500:
            self.description = value

    def set_dept(self, value: str):
        self.selected_dept_id = value
        self.selected_subject_id = ""
        self.selected_folder = ""
        self.show_new_folder_input = False

    def set_subject(self, value: str):
        self.selected_subject_id = value
        self.selected_folder = ""
        self.show_new_folder_input = False

    def set_folder(self, value: str):
        self.selected_folder = value

    def set_doc_type(self, value: str):
        self.doc_type = value

    def toggle_public(self):
        self.is_public = not self.is_public

    def toggle_new_folder_input(self):
        self.show_new_folder_input = not self.show_new_folder_input
        if not self.show_new_folder_input:
            self.new_folder_name = ""

    def set_new_folder_name(self, value: str):
        self.new_folder_name = value

    def confirm_new_folder(self):
        name = self.new_folder_name.strip()
        if not name:
            return
        subject_id = self.selected_subject_id
        if subject_id:
            if name:
                pass
            self.selected_folder = name
        self.show_new_folder_input = False
        self.new_folder_name = ""
        return rx.toast.success(f"Đã tạo thư mục mới: {name}")

    def set_tag_input(self, value: str):
        self.tag_input = value

    def add_tag(self):
        tag = self.tag_input.strip().lower()
        if tag and tag not in self.tags and len(self.tags) < 8:
            self.tags.append(tag)
            self.tag_input = ""

    def add_suggested_tag(self, tag: str):
        if tag not in self.tags and len(self.tags) < 8:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        self.tags = [t for t in self.tags if t != tag]

    def handle_file_upload(self, files: list[rx.UploadFile]):
        if files:
            f = files[0]
            self.uploaded_filename = f.filename
            self.uploaded_filesize = "Đã chọn từ máy"
            self.error_message = ""

    def clear_file(self):
        self.uploaded_filename = ""
        self.uploaded_filesize = ""

    def quick_fill_sample(self):
        self.title = "Tài liệu Ôn tập Cây AVL và BTL Web 2026"
        self.selected_dept_id = "1"
        self.selected_subject_id = "IT410"
        self.selected_folder = "Backend Python"
        self.doc_type = "EXERCISE"
        self.description = "Tài liệu đóng góp tổng hợp lý thuyết, bài tập lớn và starter code thực hành môn Lập trình Web."
        self.tags = ["Python", "Web", "Reflex", "BTL"]
        self.uploaded_filename = "BTL_Web_Starter_DocUni.zip"
        self.uploaded_filesize = "5.4 MB"
        self.error_message = ""
        return rx.toast.info("Đã điền sẵn toàn bộ dữ liệu mẫu! Bạn chỉ cần cuộn xuống và bấm 'Gửi yêu cầu đóng góp'.")

    async def submit_contribution(self, files: list[rx.UploadFile] = None):
        file_url = ""
        file_size = self.uploaded_filesize or "4.5 MB"

        if files and len(files) > 0:
            f = files[0]
            data = await f.read()
            clean_name, file_url, size_str = StorageService.save_file(f.filename, data)
            self.uploaded_filename = clean_name
            self.uploaded_filesize = size_str
            file_size = size_str

        if not self.title.strip():
            self.error_message = "Vui lòng nhập Tiêu đề tài liệu!"
            return rx.toast.error(self.error_message)
        if not self.selected_dept_id:
            self.error_message = "Vui lòng chọn Khoa phụ trách!"
            return rx.toast.error(self.error_message)
        if not self.selected_subject_id:
            self.error_message = "Vui lòng chọn Môn học tương ứng!"
            return rx.toast.error(self.error_message)
        if not self.selected_folder:
            self.error_message = "Vui lòng chọn Thư mục lưu trữ!"
            return rx.toast.error(self.error_message)

        if not self.uploaded_filename:
            # Tạo tệp mẫu để có thể tải về
            fname = f"{self.selected_subject_id}_TaiLieu_DongGop.pdf"
            sample_content = (
                f"=== TÀI LIỆU HỌC TẬP DOCUNI ===\n"
                f"Tiêu đề: {self.title}\n"
                f"Môn học: {self.selected_subject_id}\n"
                f"Thư mục: {self.selected_folder}\n"
                f"Mô tả: {self.description}\n"
                f"Người đóng góp: Sinh viên DocUni\n"
            ).encode("utf-8")
            clean_name, file_url, size_str = StorageService.save_file(fname, sample_content)
            self.uploaded_filename = clean_name
            self.uploaded_filesize = size_str
            file_size = size_str

        fname = self.uploaded_filename
        self.is_submitting = False
        self.submit_success = True

        return [
            GlobalDocState.add_contribution(
                title=self.title,
                subject_code=self.selected_subject_id,
                folder_name=self.selected_folder,
                doc_type=self.doc_type,
                tags=list(self.tags),
                file_name=fname,
                description=self.description,
                is_public=self.is_public,
                allowed_class="",
                file_size=file_size,
                file_url=file_url,
            ),
            rx.toast.success("Tài liệu đã được gửi thành công vào hàng đợi kiểm duyệt!"),
        ]

    def reset_form(self):
        self.title = ""
        self.description = ""
        self.selected_dept_id = ""
        self.selected_subject_id = ""
        self.selected_folder = ""
        self.doc_type = "SLIDE"
        self.is_public = True
        self.tags = []
        self.tag_input = ""
        self.uploaded_filename = ""
        self.uploaded_filesize = ""
        self.show_new_folder_input = False
        self.error_message = ""
        self.submit_success = False


# ─── UI Helper Components ────────────────────────────────────────────────────

def form_label(text: str, required: bool = True) -> rx.Component:
    return rx.hstack(
        rx.text(text, size="2", weight="bold", color="slate.12"),
        rx.cond(required, rx.text("*", color="red.9", size="2"), rx.fragment()),
        spacing="1",
        margin_bottom="2",
    )


def section_card(title: str, icon: str, *children, **props) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=18, color="var(--blue-10)"),
                rx.text(title, size="3", weight="bold", color="slate.12"),
                align="center",
                spacing="2",
                margin_bottom="4",
            ),
            *children,
            spacing="4",
            width="100%",
        ),
        variant="surface",
        padding="5",
        **props,
    )


def tag_chip(tag: str) -> rx.Component:
    return rx.hstack(
        rx.text(tag, size="1", weight="medium"),
        rx.icon(
            "x",
            size=12,
            cursor="pointer",
            on_click=UploadState.remove_tag(tag),
            color="var(--blue-9)",
        ),
        bg="var(--blue-3)",
        color="var(--blue-11)",
        border="1px solid var(--blue-5)",
        border_radius="full",
        padding_x="2.5",
        padding_y="1",
        align="center",
        spacing="2",
    )


def upload_zone() -> rx.Component:
    return rx.vstack(
        rx.upload(
            rx.box(
                rx.vstack(
                    rx.icon("cloud-upload", size=36, color="var(--blue-8)"),
                    rx.text("Kéo & thả tệp vào đây hoặc", size="2", weight="bold", color="slate.11"),
                    rx.button(
                        rx.icon("folder-open", size=15),
                        "Chọn tệp từ máy tính",
                        size="2",
                        variant="surface",
                        color_scheme="blue",
                    ),
                    rx.text("Hỗ trợ: PDF, DOCX, PPTX, XLSX, ZIP (≤ 50 MB)", size="1", color="slate.8"),
                    spacing="2",
                    align="center",
                ),
                border="2px dashed var(--blue-6)",
                border_radius="xl",
                padding="8",
                bg="var(--blue-1)",
                _hover={"border_color": "var(--blue-8)", "bg": "var(--blue-2)"},
                transition="all 0.2s ease",
                width="100%",
                cursor="pointer",
            ),
            id="doc_upload",
            accept={
                "application/pdf": [".pdf"],
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                "application/zip": [".zip"],
            },
            multiple=False,
            width="100%",
        ),
        # Danh sách tệp người dùng chọn từ máy tính
        rx.foreach(
            rx.selected_files("doc_upload"),
            lambda f: rx.card(
                rx.hstack(
                    rx.icon("file-check", size=18, color="var(--green-10)"),
                    rx.vstack(
                        rx.text(f, size="2", weight="bold", color="green.12"),
                        rx.text("Tệp đã sẵn sàng tải lên cùng biểu mẫu", size="1", color="green.10"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.badge("Đã chọn từ máy", color_scheme="green", variant="solid", size="1"),
                    align="center",
                    spacing="2",
                    width="100%",
                ),
                variant="surface",
                padding="3",
                bg="var(--green-2)",
                border="1px solid var(--green-6)",
                width="100%",
            ),
        ),
        # Nếu có tệp mẫu được chọn sẵn
        rx.cond(
            UploadState.uploaded_filename != "",
            rx.card(
                rx.hstack(
                    rx.icon("file-check", size=18, color="var(--blue-10)"),
                    rx.vstack(
                        rx.text(UploadState.uploaded_filename, size="2", weight="bold", color="slate.12"),
                        rx.text("Tệp đính kèm tự động từ dữ liệu mẫu", size="1", color="blue.10"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.badge("Tệp mẫu", color_scheme="blue", variant="surface", size="1"),
                    align="center",
                    spacing="2",
                    width="100%",
                ),
                variant="surface",
                padding="3",
                bg="var(--blue-2)",
                border="1px solid var(--blue-6)",
                width="100%",
            ),
            rx.fragment(),
        ),
        spacing="3",
        width="100%",
    )


def folder_selector() -> rx.Component:
    return rx.vstack(
        rx.select.root(
            rx.select.trigger(placeholder="-- Chọn thư mục --", width="100%"),
            rx.select.content(
                rx.foreach(
                    UploadState.available_folders,
                    lambda folder: rx.select.item(folder, value=folder),
                ),
            ),
            value=UploadState.selected_folder,
            on_change=UploadState.set_folder,
            width="100%",
            disabled=UploadState.selected_subject_id == "",
        ),
        rx.cond(
            UploadState.show_new_folder_input,
            rx.hstack(
                rx.input(
                    placeholder="Nhập tên thư mục mới...",
                    value=UploadState.new_folder_name,
                    on_change=UploadState.set_new_folder_name,
                    size="2",
                    flex="1",
                ),
                rx.button(
                    rx.icon("check", size=14), "Tạo",
                    size="2", color_scheme="green", variant="solid",
                    on_click=UploadState.confirm_new_folder,
                ),
                rx.button(
                    rx.icon("x", size=14),
                    size="2", variant="ghost", color_scheme="gray",
                    on_click=UploadState.toggle_new_folder_input,
                ),
                spacing="2",
                width="100%",
            ),
            rx.link(
                rx.hstack(
                    rx.icon("folder-plus", size=14),
                    rx.text("Tạo thư mục mới", size="2"),
                    align="center",
                    spacing="1",
                ),
                color="blue.10",
                cursor="pointer",
                on_click=UploadState.toggle_new_folder_input,
                underline="hover",
            ),
        ),
        spacing="3",
        width="100%",
    )


def success_state() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.icon("circle-check", size=64, color="var(--green-10)"),
                rx.heading("Gửi tài liệu thành công!", size="6", color="slate.12"),
                rx.text(
                    "Tài liệu của bạn đã được gửi và đang chờ kiểm duyệt từ giảng viên. "
                    "Bạn có thể theo dõi trạng thái tại trang 'Theo dõi duyệt'.",
                    size="3", color="slate.10", text_align="center", max_width="480px",
                ),
                rx.hstack(
                    rx.button(
                        rx.icon("plus", size=15),
                        "Đóng góp tiếp",
                        size="3",
                        color_scheme="blue",
                        variant="solid",
                        on_click=UploadState.reset_form,
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("list-checks", size=15),
                            "Theo dõi tài liệu",
                            size="3",
                            variant="surface",
                            color_scheme="gray",
                        ),
                        href="/student/contributions",
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("check-check", size=15),
                            "Chuyển sang Giảng viên duyệt ngay (Demo)",
                            size="3",
                            variant="solid",
                            color_scheme="green",
                        ),
                        href="/lecturer/approval",
                    ),
                    spacing="3",
                ),
                spacing="5",
                align="center",
                padding="8",
            ),
            variant="surface",
            max_width="520px",
        ),
        height="60vh",
    )


# ─── Main Page ───────────────────────────────────────────────────────────────

def student_upload_page() -> rx.Component:
    return student_page_wrapper(
        rx.cond(
            UploadState.submit_success,
            success_state(),
            rx.vstack(
                # ── Page Header ──
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("upload", size=28, color="white"),
                            bg="blue.9",
                            padding="3",
                            border_radius="xl",
                        ),
                        rx.vstack(
                            rx.heading("Đóng góp Tài liệu", size="7", weight="bold", color="slate.12"),
                            rx.text("Chia sẻ tài liệu học tập để giúp đỡ cộng đồng sinh viên", size="3", color="slate.9"),
                            spacing="1",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    rx.divider(color_scheme="gray", margin_y="4"),
                    width="100%",
                ),

                # ── Banner Điền Nhanh Dữ Liệu Mẫu (Để Demo Task 3) ──
                rx.card(
                    rx.hstack(
                        rx.icon("sparkles", size=22, color="var(--violet-10)"),
                        rx.vstack(
                            rx.text.strong("Kiểm thử nhanh Task 3 (Gửi duyệt tài liệu):", size="2", color="slate.12"),
                            rx.text("Bấm nút 'Điền mẫu nhanh' để tự động điền tiêu đề, môn học, thư mục và tệp đính kèm trong 1 click!", size="2", color="slate.10"),
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("wand-sparkles", size=15),
                            "⚡ Điền mẫu nhanh",
                            color_scheme="violet",
                            variant="solid",
                            size="2",
                            on_click=UploadState.quick_fill_sample,
                        ),
                        align="center",
                        spacing="3",
                        width="100%",
                    ),
                    bg="var(--violet-2)",
                    border="1px solid var(--violet-5)",
                    padding="3.5",
                    margin_bottom="3",
                    width="100%",
                ),

                # ── Error Banner ──
                rx.cond(
                    UploadState.error_message != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle-alert", size=16)),
                        rx.callout.text(UploadState.error_message),
                        color="red",
                        variant="surface",
                        width="100%",
                    ),
                    rx.fragment(),
                ),

                # ── 2-column layout ──
                rx.grid(
                    # LEFT: Form chính
                    rx.vstack(
                        # 1. Upload file
                        section_card(
                            "Tải tệp tài liệu lên",
                            "file-up",
                            upload_zone(),
                        ),

                        # 2. Thông tin tài liệu
                        section_card(
                            "Thông tin tài liệu",
                            "file-text",
                            # Title
                            rx.vstack(
                                form_label("Tiêu đề tài liệu", required=True),
                                rx.input(
                                    placeholder="VD: Slide Chương 3 - Hàng đợi và Ngăn xếp...",
                                    value=UploadState.title,
                                    on_change=UploadState.set_title,
                                    size="3",
                                    width="100%",
                                ),
                                spacing="1", width="100%",
                            ),
                            # Description
                            rx.vstack(
                                rx.hstack(
                                    form_label("Mô tả nội dung", required=False),
                                    rx.spacer(),
                                    rx.text(UploadState.char_count, size="1", color="slate.8"),
                                    width="100%",
                                ),
                                rx.text_area(
                                    placeholder="Mô tả ngắn gọn nội dung tài liệu, phù hợp với chủ đề nào, tuần mấy...",
                                    value=UploadState.description,
                                    on_change=UploadState.set_description,
                                    resize="vertical",
                                    rows="3",
                                    width="100%",
                                ),
                                spacing="1", width="100%",
                            ),
                            # Doc type
                            rx.vstack(
                                form_label("Loại tài liệu", required=True),
                                rx.grid(
                                    rx.foreach(
                                        DOC_TYPES,
                                        lambda dt: rx.box(
                                            rx.hstack(
                                                rx.icon(dt["icon"], size=14),
                                                rx.text(dt["label"], size="1", weight="medium"),
                                                align="center",
                                                spacing="2",
                                            ),
                                            on_click=UploadState.set_doc_type(dt["value"]),
                                            border=rx.cond(
                                                UploadState.doc_type == dt["value"],
                                                "2px solid var(--blue-8)",
                                                "1px solid var(--slate-5)"
                                            ),
                                            border_radius="lg",
                                            padding="2.5",
                                            bg=rx.cond(
                                                UploadState.doc_type == dt["value"],
                                                "var(--blue-3)",
                                                "white"
                                            ),
                                            cursor="pointer",
                                            _hover={"border_color": "var(--blue-6)"},
                                            transition="all 0.15s",
                                        ),
                                    ),
                                    columns="3",
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="2", width="100%",
                            ),
                        ),

                        # 3. Phân loại
                        section_card(
                            "Phân loại & Thư mục lưu trữ",
                            "folder-tree",
                            # Dept
                            rx.vstack(
                                form_label("Khoa / Ngành", required=True),
                                rx.select.root(
                                    rx.select.trigger(placeholder="-- Chọn Khoa --", width="100%"),
                                    rx.select.content(
                                        rx.foreach(
                                            UploadState.dept_options,
                                            lambda d: rx.select.item(d["name"], value=d["id"]),
                                        ),
                                    ),
                                    value=UploadState.selected_dept_id,
                                    on_change=UploadState.set_dept,
                                    width="100%",
                                ),
                                spacing="1", width="100%",
                            ),
                            # Subject
                            rx.vstack(
                                form_label("Môn học", required=True),
                                rx.select.root(
                                    rx.select.trigger(placeholder="-- Chọn Môn học --", width="100%"),
                                    rx.select.content(
                                        rx.foreach(
                                            UploadState.available_subjects,
                                            lambda s: rx.select.item(s["name"], value=s["id"]),
                                        ),
                                    ),
                                    value=UploadState.selected_subject_id,
                                    on_change=UploadState.set_subject,
                                    disabled=UploadState.selected_dept_id == "",
                                    width="100%",
                                ),
                                rx.cond(
                                    UploadState.selected_dept_id == "",
                                    rx.text("Vui lòng chọn Khoa trước", size="1", color="slate.8"),
                                    rx.fragment(),
                                ),
                                spacing="1", width="100%",
                            ),
                            # Folder
                            rx.vstack(
                                form_label("Thư mục lưu trữ", required=True),
                                folder_selector(),
                                spacing="1", width="100%",
                            ),
                        ),

                        # 4. Tags
                        section_card(
                            "Nhãn & Từ khóa (Tags)",
                            "tag",
                            rx.vstack(
                                # Input add tag
                                rx.hstack(
                                    rx.input(
                                        placeholder="Nhập từ khóa và nhấn Enter...",
                                        value=UploadState.tag_input,
                                        on_change=UploadState.set_tag_input,
                                        on_key_down=lambda key: rx.cond(
                                            key == "Enter",
                                            UploadState.add_tag(),
                                            rx.noop(),
                                        ),
                                        size="2",
                                        flex="1",
                                    ),
                                    rx.button(
                                        rx.icon("plus", size=14),
                                        "Thêm",
                                        size="2",
                                        variant="surface",
                                        color_scheme="blue",
                                        on_click=UploadState.add_tag,
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                # Selected tags
                                rx.cond(
                                    UploadState.tags.length() > 0,
                                    rx.flex(
                                        rx.foreach(UploadState.tags, tag_chip),
                                        flex_wrap="wrap",
                                        gap="2",
                                        width="100%",
                                    ),
                                    rx.fragment(),
                                ),
                                # Suggested tags
                                rx.vstack(
                                    rx.text("Gợi ý từ khóa phổ biến:", size="1", color="slate.9", weight="medium"),
                                    rx.flex(
                                        *[
                                            rx.badge(
                                                f"+ {t}",
                                                variant="surface",
                                                color_scheme="blue",
                                                size="2",
                                                cursor="pointer",
                                                _hover={"color_scheme": "indigo", "cursor": "pointer"},
                                                on_click=UploadState.add_suggested_tag(t),
                                            )
                                            for t in SUGGESTED_TAGS[:8]
                                        ],
                                        flex_wrap="wrap",
                                        gap="2",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                        ),

                        # 5. Visibility + Submit
                        section_card(
                            "Cài đặt quyền truy cập",
                            "lock",
                            rx.hstack(
                                rx.icon(
                                    rx.cond(UploadState.is_public, "globe", "lock"),
                                    size=20,
                                    color=rx.cond(UploadState.is_public, "var(--green-10)", "var(--amber-10)"),
                                ),
                                rx.vstack(
                                    rx.text(
                                        rx.cond(UploadState.is_public, "Công khai cho tất cả sinh viên", "Chỉ sinh viên được phân quyền"),
                                        size="2", weight="bold", color="slate.12",
                                    ),
                                    rx.text(
                                        rx.cond(UploadState.is_public, "Mọi sinh viên trong hệ thống có thể xem và tải.", "Chỉ sinh viên trong lớp/khoa được phép truy cập."),
                                        size="1", color="slate.9",
                                    ),
                                    spacing="0",
                                ),
                                rx.spacer(),
                                rx.switch(
                                    checked=UploadState.is_public,
                                    on_change=UploadState.toggle_public,
                                    color_scheme="green",
                                ),
                                align="center",
                                spacing="3",
                                width="100%",
                            ),
                        ),

                        # Submit button
                        rx.button(
                            rx.cond(
                                UploadState.is_submitting,
                                rx.spinner(size="3"),
                                rx.icon("send", size=18),
                            ),
                            rx.cond(
                                UploadState.is_submitting,
                                "Đang gửi...",
                                "Gửi yêu cầu đóng góp (Nộp vào hàng đợi duyệt)",
                            ),
                            size="4",
                            width="100%",
                            color_scheme="blue",
                            variant="solid",
                            loading=UploadState.is_submitting,
                            on_click=UploadState.submit_contribution(rx.upload_files(upload_id="doc_upload")),
                        ),

                        spacing="4",
                        width="100%",
                    ),

                    # RIGHT: Hướng dẫn
                    rx.vstack(
                        # Checklist quy định
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("info", size=18, color="var(--blue-10)"),
                                    rx.text("Quy định đóng góp tài liệu", size="3", weight="bold", color="slate.12"),
                                    align="center",
                                    spacing="2",
                                ),
                                rx.vstack(
                                    *[
                                        rx.hstack(
                                            rx.icon("circle-check", size=15, color="var(--green-9)"),
                                            rx.text(t, size="2", color="slate.11"),
                                            align="center",
                                            spacing="2",
                                        )
                                        for t in [
                                            "Tài liệu phải đúng môn học được chọn",
                                            "Tiêu đề rõ ràng, phản ánh đúng nội dung",
                                            "Không chứa nội dung bản quyền trái phép",
                                            "File phải rõ ràng, chất lượng tốt",
                                            "Kích thước tệp ≤ 50 MB",
                                            "Hỗ trợ định dạng: PDF, DOCX, PPTX, XLSX, ZIP",
                                        ]
                                    ],
                                    spacing="2",
                                ),
                                spacing="4",
                            ),
                            variant="surface",
                            padding="5",
                        ),

                        # Tiêu chí kiểm duyệt
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("shield-check", size=18, color="var(--indigo-10)"),
                                    rx.text("Tiêu chí kiểm duyệt", size="3", weight="bold", color="slate.12"),
                                    align="center",
                                    spacing="2",
                                ),
                                rx.grid(
                                    *[
                                        rx.box(
                                            rx.vstack(
                                                rx.icon(item[0], size=20, color=item[2]),
                                                rx.text(item[1], size="1", weight="bold", color="slate.12", text_align="center"),
                                                rx.text(item[3], size="1", color="slate.9", text_align="center"),
                                                spacing="1",
                                                align="center",
                                            ),
                                            bg="var(--slate-2)",
                                            border_radius="lg",
                                            padding="3",
                                        )
                                        for item in [
                                            ("file-search", "Nội dung", "var(--blue-9)", "Phù hợp và học thuật"),
                                            ("copyright", "Bản quyền", "var(--amber-9)", "Hợp pháp"),
                                            ("award", "Chất lượng", "var(--green-9)", "Rõ ràng, đầy đủ"),
                                            ("tag", "Phân loại", "var(--purple-9)", "Đúng môn, đúng loại"),
                                        ]
                                    ],
                                    columns="2",
                                    spacing="3",
                                    width="100%",
                                ),
                                spacing="4",
                            ),
                            variant="surface",
                            padding="5",
                        ),

                        # Trạng thái quy trình
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("milestone", size=18, color="var(--violet-10)"),
                                    rx.text("Quy trình duyệt tài liệu", size="3", weight="bold", color="slate.12"),
                                    align="center",
                                    spacing="2",
                                ),
                                *[
                                    rx.hstack(
                                        rx.box(
                                            rx.text(str(n), size="1", weight="bold", color="white"),
                                            bg=f"var(--{c}-9)",
                                            width="24px",
                                            height="24px",
                                            border_radius="full",
                                            display="flex",
                                            align_items="center",
                                            justify_content="center",
                                            flex_shrink="0",
                                        ),
                                        rx.vstack(
                                            rx.text(title, size="2", weight="bold", color="slate.12"),
                                            rx.text(desc, size="1", color="slate.9"),
                                            spacing="0",
                                        ),
                                        align="start",
                                        spacing="3",
                                    )
                                    for n, c, title, desc in [
                                        (1, "blue", "Nộp tài liệu", "Điền thông tin và upload tệp"),
                                        (2, "amber", "Chờ kiểm duyệt", "Giảng viên xem xét trong 1-3 ngày"),
                                        (3, "green", "Được duyệt", "Tài liệu xuất hiện trong kho học liệu"),
                                    ]
                                ],
                                spacing="3",
                            ),
                            variant="surface",
                            padding="5",
                        ),

                        spacing="4",
                        width="100%",
                    ),

                    columns="5fr 3fr",
                    spacing="6",
                    width="100%",
                ),

                spacing="5",
                width="100%",
            ),
        ),
        active_route="/student/upload",
    )
