"""
DocUni - Trang Kho Học Liệu & Tài Liệu Môn Học
Route: /documents
Framework: Reflex (Python Full-Stack)

Cung cấp giao diện tra cứu tài liệu học thuật theo môn học, khoa, loại tài liệu
với thanh tìm kiếm, bộ lọc trực quan và lưới thẻ tài liệu sinh động.
"""

import reflex as rx
from typing import List
from .common_components import student_page_wrapper

# ─── Mock Data Học Liệu ──────────────────────────────────────────────────────

MOCK_DOCUMENTS = [
    {
        "id": "1",
        "title": "Giáo trình Cấu trúc dữ liệu và giải thuật",
        "subject_code": "IT202",
        "subject_name": "Cấu trúc dữ liệu & giải thuật",
        "faculty": "CNTT",
        "faculty_name": "Khoa Công nghệ thông tin",
        "doc_type": "TEXTBOOK",
        "type_label": "Giáo trình",
        "type_color": "blue",
        "icon": "book",
        "desc": "Tài liệu học phần chính thức dành cho sinh viên CNTT, bao gồm lý thuyết hàng đợi, ngăn xếp, cây và đồ thị.",
        "uploader": "TS. Nguyễn Văn An",
        "uploader_role": "Giảng viên",
        "downloads": 1240,
        "views": 3150,
        "time": "Hôm qua",
        "filename": "GiaoTrinh_CTDL_GT.pdf",
    },
    {
        "id": "2",
        "title": "Slide Bài giảng Chương 1 - 5: Kinh tế vi mô",
        "subject_code": "ECO101",
        "subject_name": "Kinh tế vi mô",
        "faculty": "KT",
        "faculty_name": "Khoa Kinh tế",
        "doc_type": "SLIDE",
        "type_label": "Slide Bài giảng",
        "type_color": "orange",
        "icon": "presentation",
        "desc": "Tổng hợp toàn bộ slide bài giảng trên lớp kèm các ví dụ thực tiễn về cung cầu, độ co giãn và hành vi người tiêu dùng.",
        "uploader": "ThS. Lê Thị Bình",
        "uploader_role": "Giảng viên",
        "downloads": 856,
        "views": 1940,
        "time": "3 ngày trước",
        "filename": "KTVM_Slide_C1_C5.pptx",
    },
    {
        "id": "3",
        "title": "Bộ Đề thi cuối kỳ Nhập môn lập trình có đáp án",
        "subject_code": "IT101",
        "subject_name": "Nhập môn lập trình",
        "faculty": "CNTT",
        "faculty_name": "Khoa Công nghệ thông tin",
        "doc_type": "EXAM",
        "type_label": "Đề thi & Đáp án",
        "type_color": "red",
        "icon": "file-check",
        "desc": "Tổng hợp 4 mã đề thi các năm 2023-2025 có lời giải chi tiết và mã nguồn mẫu bằng ngôn ngữ Python.",
        "uploader": "CLB Tin học VAA",
        "uploader_role": "Sinh viên",
        "downloads": 2130,
        "views": 4820,
        "time": "1 tuần trước",
        "filename": "IT101_DeThi_DapAn_TongHop.pdf",
    },
    {
        "id": "4",
        "title": "Tóm tắt công thức & Bài tập ôn thi Kinh tế vĩ mô",
        "subject_code": "ECO202",
        "subject_name": "Kinh tế vĩ mô",
        "faculty": "KT",
        "faculty_name": "Khoa Kinh tế",
        "doc_type": "REFERENCE",
        "type_label": "Tham khảo",
        "type_color": "green",
        "icon": "library",
        "desc": "Bản tổng hợp các mô hình IS-LM, AS-AD và công thức tính toán GDP, lạm phát, thất nghiệp thi giữa kỳ & cuối kỳ.",
        "uploader": "Nhóm SV K65 Kinh tế",
        "uploader_role": "Sinh viên",
        "downloads": 1420,
        "views": 2780,
        "time": "2 tuần trước",
        "filename": "KTVM_TomTat_CongThuc.pdf",
    },
    {
        "id": "5",
        "title": "Script SQL & Bài tập lớn Cơ sở dữ liệu Quản lý bán hàng",
        "subject_code": "IT305",
        "subject_name": "Cơ sở dữ liệu",
        "faculty": "CNTT",
        "faculty_name": "Khoa Công nghệ thông tin",
        "doc_type": "EXERCISE",
        "type_label": "Bài tập lớn",
        "type_color": "violet",
        "icon": "pencil-line",
        "desc": "Bộ mã nguồn tạo bảng, ràng buộc khóa ngoại, stored procedures và 20 truy vấn SQL nâng cao minh họa.",
        "uploader": "TS. Nguyễn Văn An",
        "uploader_role": "Giảng viên",
        "downloads": 978,
        "views": 1850,
        "time": "2 tuần trước",
        "filename": "CSDL_BanHang_Script.sql",
    },
    {
        "id": "6",
        "title": "Tài liệu Từ vựng Tiếng Anh Chuyên ngành Hàng không",
        "subject_code": "ENG201",
        "subject_name": "Tiếng Anh chuyên ngành",
        "faculty": "NN",
        "faculty_name": "Khoa Ngoại ngữ",
        "doc_type": "TEXTBOOK",
        "type_label": "Giáo trình",
        "type_color": "blue",
        "icon": "book",
        "desc": "Sổ tay thuật ngữ ICAO, từ vựng kỹ thuật buồng lái và giao tiếp không lưu chuẩn quốc tế.",
        "uploader": "Khoa Ngoại ngữ VAA",
        "uploader_role": "Khoa",
        "downloads": 1640,
        "views": 3410,
        "time": "1 tháng trước",
        "filename": "Aviation_English_Vocabulary.pdf",
    },
    {
        "id": "7",
        "title": "Sổ tay Quy trình & Thủ tục Kiểm soát không lưu tại sân",
        "subject_code": "ATC101",
        "subject_name": "Điều hành bay cơ bản",
        "faculty": "DHB",
        "faculty_name": "Khoa Điều hành bay",
        "doc_type": "REFERENCE",
        "type_label": "Tham khảo",
        "type_color": "green",
        "icon": "library",
        "desc": "Tài liệu mô phỏng quy trình cấp huấn lệnh lăn, cất cánh, hạ cánh và xử lý tình huống khẩn cấp tại đài kiểm soát.",
        "uploader": "ThS. Trần Quang Huy",
        "uploader_role": "Giảng viên",
        "downloads": 745,
        "views": 1520,
        "time": "1 tháng trước",
        "filename": "SoTay_ATC_SanBay.pdf",
    },
    {
        "id": "8",
        "title": "Slide Bài giảng Lập trình Web Full-Stack với Python",
        "subject_code": "IT410",
        "subject_name": "Lập trình Web",
        "faculty": "CNTT",
        "faculty_name": "Khoa Công nghệ thông tin",
        "doc_type": "SLIDE",
        "type_label": "Slide Bài giảng",
        "type_color": "orange",
        "icon": "presentation",
        "desc": "Kiến trúc web hiện đại, REST API, kiến trúc Client-Server và xây dựng frontend tương tác cao.",
        "uploader": "TS. Nguyễn Văn An",
        "uploader_role": "Giảng viên",
        "downloads": 1120,
        "views": 2690,
        "time": "Tháng trước",
        "filename": "Web_FullStack_Python_Slide.pptx",
    },
]

FACULTIES = [
    {"value": "ALL", "label": "Tất cả các Khoa"},
    {"value": "CNTT", "label": "Khoa Công nghệ thông tin"},
    {"value": "KT", "label": "Khoa Kinh tế"},
    {"value": "NN", "label": "Khoa Ngoại ngữ"},
    {"value": "DHB", "label": "Khoa Điều hành bay"},
]

DOC_TYPES_FILTER = [
    {"value": "ALL", "label": "Tất cả học liệu"},
    {"value": "TEXTBOOK", "label": "Giáo trình"},
    {"value": "SLIDE", "label": "Slide Bài giảng"},
    {"value": "EXAM", "label": "Đề thi & Đáp án"},
    {"value": "EXERCISE", "label": "Bài tập"},
    {"value": "REFERENCE", "label": "Tham khảo"},
]

# ─── State ───────────────────────────────────────────────────────────────────

class DocListState(rx.State):
    """Quản lý tìm kiếm, lọc và tương tác với kho tài liệu học phần."""

    search_query: str = ""
    selected_faculty: str = "ALL"
    selected_type: str = "ALL"
    all_documents: List[dict] = MOCK_DOCUMENTS

    def set_search_query(self, value: str):
        self.search_query = value

    def set_faculty(self, value: str):
        self.selected_faculty = value

    def set_type(self, value: str):
        self.selected_type = value

    def reset_filters(self):
        self.search_query = ""
        self.selected_faculty = "ALL"
        self.selected_type = "ALL"

    @rx.var
    def filtered_documents(self) -> List[dict]:
        query = self.search_query.strip().lower()
        faculty = self.selected_faculty
        doc_type = self.selected_type

        results = self.all_documents

        if faculty != "ALL":
            results = [d for d in results if d["faculty"] == faculty]

        if doc_type != "ALL":
            results = [d for d in results if d["doc_type"] == doc_type]

        if query:
            results = [
                d for d in results
                if query in d["title"].lower()
                or query in d["subject_code"].lower()
                or query in d["subject_name"].lower()
                or query in d["desc"].lower()
            ]

        return results

    @rx.var
    def result_count(self) -> int:
        return len(self.filtered_documents)

    def download_doc(self, title: str):
        return rx.toast.success(f"Bắt đầu tải xuống: {title}")


# ─── UI Helper Components ────────────────────────────────────────────────────

def doc_card(doc: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            # Top row: Type badge & icon
            rx.hstack(
                rx.badge(
                    rx.hstack(
                        rx.icon("file-text", size=12),
                        rx.text(doc["type_label"], size="1", weight="bold"),
                        align="center",
                        spacing="1",
                    ),
                    color_scheme=doc["type_color"],
                    variant="surface",
                    size="1",
                ),
                rx.spacer(),
                rx.badge(doc["subject_code"], color_scheme="gray", variant="surface", size="1"),
                align="center",
                width="100%",
            ),

            # Title
            rx.heading(
                doc["title"],
                size="3",
                weight="bold",
                color="slate.12",
                line_height="1.4",
                max_width="100%",
            ),

            # Description
            rx.text(
                doc["desc"],
                size="2",
                color="slate.9",
                line_height="1.5",
                max_width="100%",
            ),

            # Metadata info
            rx.hstack(
                rx.hstack(
                    rx.icon("book-open", size=13, color="var(--slate-8)"),
                    rx.text(doc["subject_name"], size="1", color="slate.9", weight="medium"),
                    align="center",
                    spacing="1",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.icon("download", size=13, color="var(--green-9)"),
                    rx.text(doc["downloads"].to_string(), size="1", color="green.11", weight="bold"),
                    align="center",
                    spacing="1",
                ),
                align="center",
                width="100%",
                padding_y="1",
            ),

            rx.divider(color_scheme="gray"),

            # Bottom row: Uploader + Download button
            rx.hstack(
                rx.hstack(
                    rx.avatar(fallback="TL", size="1", radius="full", color_scheme="blue"),
                    rx.vstack(
                        rx.text(doc["uploader"], size="1", weight="bold", color="slate.11"),
                        rx.text(doc["time"], size="1", color="slate.8"),
                        spacing="0",
                    ),
                    align="center",
                    spacing="2",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("download", size=14),
                    "Tải về",
                    size="2",
                    color_scheme="blue",
                    variant="solid",
                    on_click=DocListState.download_doc(doc["title"]),
                ),
                align="center",
                width="100%",
            ),

            spacing="3",
            align="start",
            width="100%",
        ),
        variant="surface",
        padding="4",
        _hover={
            "border_color": "var(--blue-8)",
            "box_shadow": "md",
            "transform": "translateY(-2px)",
        },
        transition="all 0.2s ease",
        height="100%",
    )


def empty_search_state() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("folder-open", size=48, color="var(--slate-6)"),
            rx.heading("Không tìm thấy tài liệu phù hợp", size="4", color="slate.10"),
            rx.text(
                "Thử tìm bằng từ khóa khác hoặc xóa bộ lọc để xem toàn bộ danh mục tài liệu.",
                size="2",
                color="slate.8",
                text_align="center",
                max_width="450px",
            ),
            rx.button(
                rx.icon("refresh-cw", size=14),
                "Đặt lại bộ lọc",
                size="2",
                variant="surface",
                color_scheme="blue",
                on_click=DocListState.reset_filters,
            ),
            spacing="3",
            align="center",
        ),
        padding_y="16",
        width="100%",
    )


# ─── Main Page ───────────────────────────────────────────────────────────────

def document_list_page() -> rx.Component:
    return student_page_wrapper(
        rx.vstack(
            # ── Page Header ──
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("library", size=28, color="white"),
                        bg="teal.9",
                        padding="3",
                        border_radius="xl",
                    ),
                    rx.vstack(
                        rx.heading("Kho Học Liệu & Tài Liệu Môn Học", size="7", weight="bold", color="slate.12"),
                        rx.text("Tra cứu slide bài giảng, giáo trình chính thức, đề thi và bài tập được phân loại chuẩn hóa", size="3", color="slate.9"),
                        spacing="1",
                    ),
                    align="center",
                    spacing="3",
                ),
                rx.spacer(),
                rx.link(
                    rx.button(
                        rx.icon("upload", size=16),
                        "Đóng góp tài liệu",
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

            # ── Search & Filter Controls Card ──
            rx.card(
                rx.vstack(
                    # Row 1: Search bar + Select Khoa
                    rx.hstack(
                        rx.input(
                            rx.input.slot(rx.icon("search", size=16, color="var(--slate-8)")),
                            placeholder="Tìm theo tên bài giảng, mã môn (IT101, ECO101...), chủ đề...",
                            value=DocListState.search_query,
                            on_change=DocListState.set_search_query,
                            size="3",
                            flex="1",
                        ),
                        rx.select.root(
                            rx.select.trigger(width=["100%", "260px", "280px"], size="3"),
                            rx.select.content(
                                rx.foreach(
                                    FACULTIES,
                                    lambda f: rx.select.item(f["label"], value=f["value"]),
                                ),
                            ),
                            value=DocListState.selected_faculty,
                            on_change=DocListState.set_faculty,
                        ),
                        spacing="3",
                        width="100%",
                    ),

                    # Row 2: Pills loại tài liệu + Số lượng kết quả
                    rx.hstack(
                        rx.text("Loại học liệu:", size="2", color="slate.9", weight="medium"),
                        rx.hstack(
                            *[
                                rx.button(
                                    t["label"],
                                    size="2",
                                    radius="full",
                                    variant=rx.cond(DocListState.selected_type == t["value"], "solid", "surface"),
                                    color_scheme=rx.cond(DocListState.selected_type == t["value"], "blue", "gray"),
                                    on_click=DocListState.set_type(t["value"]),
                                )
                                for t in DOC_TYPES_FILTER
                            ],
                            spacing="2",
                            flex_wrap="wrap",
                        ),
                        rx.spacer(),
                        rx.badge(
                            rx.hstack(
                                rx.icon("files", size=12),
                                rx.text(DocListState.result_count.to_string(), " tài liệu", size="1", weight="bold"),
                                align="center",
                                spacing="1",
                            ),
                            color_scheme="blue",
                            variant="surface",
                            size="2",
                        ),
                        align="center",
                        width="100%",
                    ),

                    spacing="3",
                    width="100%",
                ),
                variant="surface",
                padding="4",
                width="100%",
            ),

            # ── Document Grid ──
            rx.cond(
                DocListState.filtered_documents.length() > 0,
                rx.grid(
                    rx.foreach(
                        DocListState.filtered_documents,
                        doc_card,
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                empty_search_state(),
            ),

            spacing="5",
            width="100%",
        ),
        active_route="/documents",
    )

student_documents_page = document_list_page
