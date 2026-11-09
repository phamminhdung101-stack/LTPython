"""
DocUni - Trang Kho Học Liệu & Cây Thư Mục Phân Quyền (Task 2 & Task 3)
Route: /documents
Framework: Reflex (Python Full-Stack)

Tính năng chính:
- Task 2:
  + Cây thư mục đa tầng (Khoa -> Môn học -> Thư mục) cho phép duyệt và lọc trực quan.
  + Kiểm tra phân quyền ACL (Sinh viên Lớp A mở được tài liệu Lớp A, Sinh viên Lớp B bị chặn 403).
- Task 3:
  + Hiển thị nhãn phiên bản (v1.0, v2.1) và modal xem lịch sử các version cũ.
  + Gắn thẻ phân loại (Tag chips) và lọc theo tag.
  + Hiển thị tài liệu công khai sau khi Giảng viên phê duyệt.
  + Modal xem nhật ký hoạt động (Audit Activity Logs).
"""

import reflex as rx
from typing import Dict, Any
from .common_components import student_page_wrapper
from .data_store import GlobalDocState, FOLDER_TREE_DATA


# ─── 1. Component Cây Thư Mục Tương Tác (Task 2: Folder Tree) ─────────────────

def folder_tree_sidebar() -> rx.Component:
    """Sidebar hiển thị cấu trúc Cây thư mục phân cấp cha - con."""
    def folder_item(f: Dict[str, Any], subject_code: str) -> rx.Component:
        is_selected = (GlobalDocState.selected_folder == f["name"]) & (GlobalDocState.selected_subject == subject_code)
        return rx.box(
            rx.hstack(
                rx.icon("folder", size=14, color=rx.cond(is_selected, "var(--blue-10)", "var(--slate-8)")),
                rx.text(f["name"], size="1", weight=rx.cond(is_selected, "bold", "normal")),
                align="center",
                spacing="2",
                padding_y="1.5",
                padding_x="2.5",
                border_radius="md",
                bg=rx.cond(is_selected, "var(--blue-3)", "transparent"),
                color=rx.cond(is_selected, "var(--blue-11)", "var(--slate-11)"),
                _hover={"bg": "var(--slate-3)", "cursor": "pointer"},
                transition="all 0.15s ease",
            ),
            on_click=[
                GlobalDocState.select_tree_filter("SUBJECT", subject_code),
                GlobalDocState.select_tree_filter("FOLDER", f["name"]),
            ],
            width="100%",
            padding_left="3",
        )

    def subject_item(sub: Dict[str, Any]) -> rx.Component:
        is_sub_selected = GlobalDocState.selected_subject == sub["code"]
        return rx.vstack(
            rx.hstack(
                rx.icon("book-open", size=15, color=rx.cond(is_sub_selected, "var(--blue-10)", "var(--slate-9)")),
                rx.text(sub["name"], size="2", weight=rx.cond(is_sub_selected, "bold", "medium")),
                align="center",
                spacing="2",
                padding_y="2",
                padding_x="2.5",
                border_radius="md",
                bg=rx.cond(is_sub_selected, "var(--blue-2)", "transparent"),
                color=rx.cond(is_sub_selected, "var(--blue-11)", "var(--slate-12)"),
                _hover={"bg": "var(--slate-3)", "cursor": "pointer"},
                on_click=GlobalDocState.select_tree_filter("SUBJECT", sub["code"]),
                width="100%",
            ),
            # Danh sách thư mục con của môn học
            rx.vstack(
                *[folder_item(f, sub["code"]) for f in sub.get("children", [])],
                spacing="1",
                width="100%",
                padding_left="2",
            ),
            spacing="1",
            width="100%",
        )

    def faculty_group(fac: Dict[str, Any]) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.icon("building-2", size=16, color="var(--blue-9)"),
                rx.text(fac["name"], size="2", weight="bold", color="slate.12"),
                align="center",
                spacing="2",
                padding_y="2",
                border_b="1px solid var(--slate-4)",
                width="100%",
            ),
            rx.vstack(
                *[subject_item(sub) for sub in fac.get("children", [])],
                spacing="2",
                width="100%",
                padding_top="2",
            ),
            spacing="1",
            width="100%",
            margin_bottom="3",
        )

    return rx.card(
        rx.vstack(
            # Tiêu đề Cây thư mục
            rx.hstack(
                rx.icon("folder-tree", size=18, color="var(--blue-10)"),
                rx.heading("Cây Thư Mục Học Liệu", size="3", weight="bold", color="slate.12"),
                rx.spacer(),
                rx.button(
                    rx.icon("rotate-ccw", size=12),
                    "Tất cả",
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=GlobalDocState.select_tree_filter("RESET", ""),
                ),
                align="center",
                width="100%",
                padding_bottom="2",
                border_b="1px solid var(--slate-4)",
            ),
            # Danh sách phân cấp
            rx.vstack(
                *[faculty_group(fac) for fac in FOLDER_TREE_DATA],
                spacing="3",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        variant="surface",
        padding="4",
        width=["100%", "100%", "300px"],
        min_width=["100%", "100%", "300px"],
        height="fit-content",
    )


# ─── 2. Thẻ Tài Liệu (Document Card) ──────────────────────────────────────────

def document_card(doc: Dict[str, Any]) -> rx.Component:
    """Thẻ tài liệu có nhãn bảo mật ACL, nhãn phiên bản và các nút tương tác."""
    return rx.card(
        rx.vstack(
            # Header: Loại tài liệu, Phiên bản & Cờ bảo mật ACL
            rx.hstack(
                rx.badge(
                    rx.hstack(rx.icon("file-text", size=12), rx.text(doc["type_label"], size="1"), align="center", spacing="1"),
                    color_scheme="blue",
                    variant="surface",
                    radius="full",
                ),
                rx.badge(
                    rx.hstack(rx.icon("git-commit-horizontal", size=11), rx.text(doc["current_version"], size="1", weight="bold"), align="center", spacing="1"),
                    color_scheme="violet",
                    variant="solid",
                    radius="full",
                ),
                rx.spacer(),
                # Cờ phân quyền ACL
                rx.cond(
                    doc["is_public"],
                    rx.badge(rx.hstack(rx.icon("globe", size=11), rx.text("Công khai", size="1"), align="center", spacing="1"), color_scheme="green", variant="surface"),
                    rx.badge(rx.hstack(rx.icon("lock", size=11), rx.text("Nội bộ theo Lớp", size="1"), align="center", spacing="1"), color_scheme="orange", variant="surface"),
                ),
                align="center",
                width="100%",
            ),

            # Tiêu đề & Môn học
            rx.vstack(
                rx.heading(doc["title"], size="4", weight="bold", color="slate.12", line_height="1.3"),
                rx.hstack(
                    rx.badge(doc["subject_code"], color_scheme="blue", variant="soft", size="1"),
                    rx.text(doc["folder_path"], size="1", color="slate.9", truncate=True),
                    align="center",
                    spacing="2",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),

            # Mô tả tóm tắt
            rx.text(
                doc["description"],
                size="2",
                color="slate.10",
                line_clamp=2,
                line_height="1.4",
            ),

            # Tags chips
            rx.hstack(
                rx.icon("tag", size=12, color="var(--blue-9)"),
                rx.text(doc["tag_str"], size="1", color="var(--blue-11)", weight="medium"),
                align="center",
                spacing="1",
            ),

            rx.divider(color_scheme="gray", margin_y="1"),

            # Footer: Uploader, Views, Downloads & Buttons
            rx.hstack(
                rx.hstack(
                    rx.icon("user", size=12, color="var(--slate-8)"),
                    rx.text(doc["uploader_name"], size="1", color="slate.9"),
                    align="center",
                    spacing="1",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.icon("eye", size=12, color="var(--slate-8)"),
                    rx.text(doc["views"], size="1", color="slate.9"),
                    rx.icon("download", size=12, color="var(--slate-8)"),
                    rx.text(doc["downloads"], size="1", color="slate.9"),
                    align="center",
                    spacing="2",
                ),
                align="center",
                width="100%",
            ),

            # Action Buttons Row
            rx.hstack(
                rx.button(
                    rx.icon("file-text", size=14),
                    "Mở / Tải tài liệu",
                    size="2",
                    color_scheme="blue",
                    variant="solid",
                    on_click=GlobalDocState.open_document(doc["id"]),
                    flex="1",
                ),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("history", size=14),
                        size="2",
                        variant="surface",
                        color_scheme="violet",
                        on_click=GlobalDocState.open_version_modal(doc["id"]),
                    ),
                    content="Xem lịch sử các phiên bản",
                ),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("file-clock", size=14),
                        size="2",
                        variant="surface",
                        color_scheme="gray",
                        on_click=GlobalDocState.open_audit_modal(doc["id"]),
                    ),
                    content="Xem nhật ký kiểm toán (Audit Logs)",
                ),
                align="center",
                spacing="2",
                width="100%",
                margin_top="1",
            ),
            spacing="3",
            width="100%",
        ),
        variant="surface",
        padding="4",
        _hover={"box_shadow": "md", "border_color": "var(--blue-7)"},
        transition="all 0.2s ease",
    )


# ─── 3. Modal Xem Chi Tiết Tài Liệu (Khi được phép truy cập) ─────────────────

def document_detail_modal() -> rx.Component:
    """Modal chi tiết tài liệu khi vượt qua kiểm tra ACL thành công."""
    doc = GlobalDocState.active_doc
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Modal Header
                rx.hstack(
                    rx.badge(doc.get("type_label", "Tài liệu"), color_scheme="blue", variant="surface"),
                    rx.badge(doc.get("current_version", "v1.0"), color_scheme="violet", variant="solid"),
                    rx.cond(
                        doc.get("is_public", True),
                        rx.badge("Công khai", color_scheme="green", variant="surface"),
                        rx.badge("Nội bộ theo Lớp", color_scheme="orange", variant="surface"),
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(rx.icon("x", size=16), variant="ghost", color_scheme="gray", on_click=GlobalDocState.close_detail_modal),
                    ),
                    align="center",
                    width="100%",
                ),

                rx.heading(doc.get("title", ""), size="5", weight="bold", color="slate.12"),
                rx.text(doc.get("folder_path", ""), size="2", color="slate.9"),

                rx.divider(color_scheme="gray"),

                # Metadata Cards
                rx.grid(
                    rx.box(rx.text("Người đóng góp:", size="1", color="slate.9"), rx.text(doc.get("uploader_name", ""), size="2", weight="bold")),
                    rx.box(rx.text("Môn học:", size="1", color="slate.9"), rx.text(doc.get("subject_name", ""), size="2", weight="bold")),
                    rx.box(rx.text("Tên tệp:", size="1", color="slate.9"), rx.text(doc.get("file_name", ""), size="2", weight="bold")),
                    rx.box(rx.text("Dung lượng:", size="1", color="slate.9"), rx.text(doc.get("file_size", ""), size="2", weight="bold")),
                    columns="2",
                    spacing="3",
                    width="100%",
                    bg="slate.2",
                    padding="3",
                    border_radius="lg",
                ),

                # Khung Đọc Trước Nội Dung (Document Preview)
                rx.vstack(
                    rx.hstack(
                        rx.icon("eye", size=16, color="var(--blue-9)"),
                        rx.text("Bản Đọc Trước Nội Dung (Preview)", size="2", weight="bold", color="slate.12"),
                        align="center",
                        spacing="2",
                    ),
                    rx.scroll_area(
                        rx.code_block(
                            doc.get("preview_text", "Đang tải bản xem trước..."),
                            language="markdown",
                            wrap_long_lines=True,
                        ),
                        type="always",
                        scrollbars="vertical",
                        style={"max_height": "200px"},
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),

                # Action buttons
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        "Đóng",
                        variant="surface",
                        color_scheme="gray",
                        on_click=GlobalDocState.close_detail_modal,
                    ),
                    rx.button(
                        rx.icon("download", size=15),
                        "Tải Tệp Về Máy",
                        color_scheme="blue",
                        on_click=GlobalDocState.download_active_doc,
                    ),
                    spacing="3",
                    width="100%",
                    margin_top="3",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="650px",
            border_radius="xl",
        ),
        open=GlobalDocState.detail_modal_open,
    )


# ─── 4. Modal Lịch Sử Phiên Bản (Task 3: Versioning) ──────────────────────────

def version_history_modal() -> rx.Component:
    """Modal xem toàn bộ lịch sử các version v1.0, v2.0 của tài liệu."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("git-branch", size=22, color="var(--violet-10)"),
                        bg="var(--violet-3)",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.dialog.title("Lịch Sử Các Phiên Bản Tài Liệu"),
                        rx.text(GlobalDocState.active_version_title, size="2", color="slate.10", truncate=True, max_width="450px"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(rx.icon("x", size=16), variant="ghost", color_scheme="gray", on_click=GlobalDocState.close_version_modal),
                    ),
                    align="center",
                    width="100%",
                ),

                rx.divider(color_scheme="gray"),

                # Danh sách các version
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Phiên bản"),
                            rx.table.column_header_cell("Tệp đính kèm"),
                            rx.table.column_header_cell("Tóm tắt thay đổi (Change Summary)"),
                            rx.table.column_header_cell("Ngày cập nhật"),
                            rx.table.column_header_cell("Thao tác"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            GlobalDocState.active_version_list,
                            lambda v: rx.table.row(
                                rx.table.cell(rx.badge(v["version"], color_scheme="violet", variant="solid")),
                                rx.table.cell(v["file_name"]),
                                rx.table.cell(v["change_summary"]),
                                rx.table.cell(v["uploaded_at"]),
                                rx.table.cell(
                                    rx.button(
                                        rx.icon("download", size=13),
                                        "Tải",
                                        size="1",
                                        variant="surface",
                                        color_scheme="blue",
                                        on_click=GlobalDocState.download_version_file(v["file_name"]),
                                    )
                                ),
                            ),
                        )
                    ),
                    width="100%",
                ),

                rx.hstack(
                    rx.spacer(),
                    rx.button("Đóng", color_scheme="gray", variant="surface", on_click=GlobalDocState.close_version_modal),
                    spacing="2",
                    width="100%",
                    margin_top="3",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="750px",
            border_radius="xl",
        ),
        open=GlobalDocState.version_modal_open,
    )


# ─── 5. Modal Nhật Ký Hoạt Động (Task 3: Audit Activity Logs) ─────────────────

def audit_log_modal() -> rx.Component:
    """Modal kiểm toán hệ thống ghi lại vết mọi thao tác trên tài liệu."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("file-clock", size=22, color="var(--indigo-10)"),
                        bg="var(--indigo-3)",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.dialog.title("Nhật Ký Hoạt Động & Kiểm Toán (Audit Trail)"),
                        rx.text(GlobalDocState.active_audit_title, size="2", color="slate.10", truncate=True, max_width="450px"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(rx.icon("x", size=16), variant="ghost", color_scheme="gray", on_click=GlobalDocState.close_audit_modal),
                    ),
                    align="center",
                    width="100%",
                ),

                rx.divider(color_scheme="gray"),

                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Hành động"),
                            rx.table.column_header_cell("Người thực hiện"),
                            rx.table.column_header_cell("Nội dung chi tiết"),
                            rx.table.column_header_cell("Thời điểm"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            GlobalDocState.active_audit_list,
                            lambda l: rx.table.row(
                                rx.table.cell(
                                    rx.badge(l["action"], color_scheme="blue", variant="surface")
                                ),
                                rx.table.cell(l["user_name"]),
                                rx.table.cell(l["description"]),
                                rx.table.cell(l["timestamp"]),
                            ),
                        )
                    ),
                    width="100%",
                ),

                rx.hstack(
                    rx.spacer(),
                    rx.button("Đóng", color_scheme="gray", variant="surface", on_click=GlobalDocState.close_audit_modal),
                    spacing="2",
                    width="100%",
                    margin_top="3",
                ),
                spacing="3",
                width="100%",
            ),
            max_width="750px",
            border_radius="xl",
        ),
        open=GlobalDocState.audit_modal_open,
    )


# ─── 6. Trang Chính /documents ────────────────────────────────────────────────

def student_documents_page() -> rx.Component:
    content = rx.vstack(
        # Modals
        document_detail_modal(),
        version_history_modal(),
        audit_log_modal(),

        # Banner thông tin kịch bản Demo Task 2 & 3
        rx.card(
            rx.hstack(
                rx.icon("info", size=20, color="var(--blue-10)"),
                rx.vstack(
                    rx.text.strong("Kịch bản Demo Phân quyền ACL (Task 2):", size="2", color="slate.12"),
                    rx.text(
                        "• Đang chọn tài khoản: ",
                        rx.badge(GlobalDocState.current_user_name, color_scheme="blue", size="1"),
                        " thuộc ",
                        rx.badge(rx.cond(GlobalDocState.current_user_class != "", GlobalDocState.current_user_class, GlobalDocState.current_user_role), color_scheme="purple", size="1"),
                        " — Sử dụng bộ chọn profile ở góc trên bên phải để hoán đổi giữa Sinh viên Lớp A và Lớp B để kiểm chứng phân quyền.",
                        size="2",
                        color="slate.11",
                    ),
                    spacing="1",
                ),
                align="center",
                spacing="3",
                width="100%",
            ),
            bg="var(--blue-2)",
            border="1px solid var(--blue-5)",
            padding="3.5",
            margin_bottom="4",
            width="100%",
        ),

        # Thanh Tìm kiếm & Lọc Tag
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.input(
                        rx.input.slot(rx.icon("search", size=16, color="var(--slate-8)")),
                        placeholder="Tìm kiếm tài liệu theo tiêu đề, môn học, mã môn (IT101, CSDL...)...",
                        value=GlobalDocState.search_query,
                        on_change=GlobalDocState.set_search_query,
                        size="3",
                        flex="1",
                    ),
                    rx.button(
                        rx.icon("x", size=15),
                        "Xóa bộ lọc",
                        variant="surface",
                        color_scheme="gray",
                        on_click=GlobalDocState.select_tree_filter("RESET", ""),
                    ),
                    align="center",
                    spacing="3",
                    width="100%",
                ),
                # Tag Bar
                rx.hstack(
                    rx.text("Tags gợi ý:", size="1", weight="bold", color="slate.10"),
                    *[
                        rx.badge(
                            f"#{t}",
                            color_scheme=rx.cond(GlobalDocState.selected_tag == t, "blue", "gray"),
                            variant=rx.cond(GlobalDocState.selected_tag == t, "solid", "surface"),
                            cursor="pointer",
                            on_click=GlobalDocState.filter_by_tag(t),
                        )
                        for t in ["ctdl", "python", "web", "reflex", "csdl", "sql", "lab", "btl", "lop-a", "lop-b"]
                    ],
                    wrap="wrap",
                    align="center",
                    spacing="2",
                ),
                spacing="3",
                width="100%",
            ),
            padding="4",
            width="100%",
        ),

        # Layout 2 cột: Cây thư mục bên trái (Task 2) + Lưới tài liệu bên phải
        rx.hstack(
            folder_tree_sidebar(),
            rx.vstack(
                # Thanh thống kê kết quả lọc
                rx.hstack(
                    rx.heading("Tài Liệu Học Phần Khả Dụng", size="4", weight="bold", color="slate.12"),
                    rx.badge(rx.text(GlobalDocState.public_documents.length(), " tài liệu"), color_scheme="blue", variant="surface"),
                    rx.spacer(),
                    rx.cond(
                        GlobalDocState.selected_subject != "ALL",
                        rx.badge(f"Môn: {GlobalDocState.selected_subject}", color_scheme="violet", variant="soft"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        GlobalDocState.selected_folder != "ALL",
                        rx.badge(f"Thư mục: {GlobalDocState.selected_folder}", color_scheme="indigo", variant="soft"),
                        rx.fragment(),
                    ),
                    align="center",
                    width="100%",
                ),

                # Lưới tài liệu
                rx.cond(
                    GlobalDocState.public_documents.length() > 0,
                    rx.grid(
                        rx.foreach(
                            GlobalDocState.public_documents,
                            document_card,
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon("folder-open", size=48, color="var(--slate-8)"),
                            rx.text("Không có tài liệu nào phù hợp với thư mục hoặc bộ lọc hiện tại.", size="3", color="slate.9"),
                            rx.button("Đặt lại bộ lọc", on_click=GlobalDocState.select_tree_filter("RESET", ""), color_scheme="blue", variant="surface"),
                            align="center",
                            spacing="3",
                            padding_y="12",
                        ),
                        width="100%",
                    ),
                ),
                spacing="4",
                flex="1",
                min_width="0",
            ),
            align="start",
            spacing="5",
            width="100%",
        ),
        spacing="5",
        width="100%",
    )

    return student_page_wrapper(content, active_route="/documents")
