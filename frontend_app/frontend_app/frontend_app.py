import reflex as rx

class State(rx.State):
    """The app state."""
    
    search_query: str = ""

    def set_search_query(self, value: str):
        self.search_query = value

from frontend_app.common_components import student_page_wrapper

def index() -> rx.Component:
    def feature_card(title: str, desc: str, icon: str, href: str, color_scheme: str = "blue", badge_text: str = "") -> rx.Component:
        return rx.link(
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon(icon, size=24, color=f"var(--{color_scheme}-10)"),
                            bg=f"var(--{color_scheme}-3)",
                            padding="3",
                            border_radius="xl",
                        ),
                        rx.spacer(),
                        rx.cond(
                            badge_text != "",
                            rx.badge(badge_text, color_scheme=color_scheme, variant="surface", size="1"),
                            rx.fragment(),
                        ),
                        align="center",
                        width="100%",
                    ),
                    rx.heading(title, size="4", weight="bold", color="slate.12"),
                    rx.text(desc, size="2", color="slate.9", line_height="1.5"),
                    rx.hstack(
                        rx.text("Truy cập ngay", size="2", weight="bold", color=f"var(--{color_scheme}-10)"),
                        rx.icon("arrow-right", size=14, color=f"var(--{color_scheme}-10)"),
                        align="center",
                        spacing="1",
                        margin_top="2",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                variant="surface",
                padding="5",
                _hover={
                    "border_color": f"var(--{color_scheme}-8)",
                    "box_shadow": "md",
                    "transform": "translateY(-2px)",
                },
                transition="all 0.2s ease",
                height="100%",
            ),
            href=href,
            underline="none",
        )

    content = rx.vstack(
        # Hero Section
        rx.center(
            rx.vstack(
                rx.badge(
                    rx.hstack(
                        rx.icon("sparkles", size=13),
                        rx.text("Cổng Học Liệu Thông Minh DocUni 2026", size="1", weight="bold"),
                        align="center",
                        spacing="1",
                    ),
                    color_scheme="blue",
                    variant="surface",
                    radius="full",
                    padding_x="3",
                    padding_y="1",
                ),
                rx.heading("Hệ Thống Quản Trị & Đóng Góp Tài Liệu Học Tập", size="8", weight="bold", color="slate.12", text_align="center"),
                rx.text(
                    "Nền tảng số hóa học liệu dành cho sinh viên và giảng viên: Tra cứu slide, bài giảng, đề thi, đóng góp tài liệu và kiểm duyệt trực tuyến.",
                    size="3",
                    color="slate.10",
                    text_align="center",
                    max_width="650px",
                ),
                # Search bar
                rx.hstack(
                    rx.input(
                        rx.input.slot(rx.icon("search", size=16, color="var(--slate-8)")),
                        placeholder="Tìm kiếm môn học, bài giảng, đề thi (VD: Cấu trúc dữ liệu, SQL, IT101...)...",
                        value=State.search_query,
                        on_change=State.set_search_query,
                        size="3",
                        width=["100%", "450px", "500px"],
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("arrow-right", size=16),
                            "Tìm kiếm",
                            color_scheme="blue",
                            size="3",
                            variant="solid",
                        ),
                        href="/documents",
                    ),
                    align="center",
                    spacing="2",
                    margin_top="3",
                ),
                align="center",
                spacing="4",
                padding_y="8",
            ),
            width="100%",
        ),

        # Section Grid: Các phân hệ chính
        rx.vstack(
            rx.hstack(
                rx.heading("Các Chức Năng Chính", size="5", weight="bold", color="slate.12"),
                rx.spacer(),
                rx.text("Chọn phân hệ bạn muốn làm việc", size="2", color="slate.9"),
                align="center",
                width="100%",
            ),
            rx.grid(
                feature_card(
                    "Đóng Góp Tài Liệu",
                    "Sinh viên tải lên slide, đề thi, bài tập thực hành theo Khoa, Môn học và thư mục lưu trữ kèm gắn thẻ tags.",
                    "upload",
                    "/student/upload",
                    color_scheme="blue",
                    badge_text="Sinh viên",
                ),
                feature_card(
                    "Theo Dõi Trạng Thái Duyệt",
                    "Theo dõi tiến độ kiểm duyệt tài liệu đã nộp, xem nhận xét từ chối của giảng viên và nộp lại phiên bản v2.0.",
                    "list-checks",
                    "/student/contributions",
                    color_scheme="indigo",
                    badge_text="Sinh viên",
                ),
                feature_card(
                    "Trợ Lý Học Tập AI (RAG)",
                    "Hỏi đáp thông minh, trích dẫn chính xác số trang giáo trình và đối soát nội dung theo thời gian thực.",
                    "sparkles",
                    "/student/ai-assistant",
                    color_scheme="violet",
                    badge_text="AI RAG",
                ),
                feature_card(
                    "Kho Tài Liệu Học Phần",
                    "Tra cứu toàn bộ tài liệu chính thức theo mã môn CNTT, Kinh tế, Ngoại ngữ, Điều hành bay...",
                    "book-open",
                    "/documents",
                    color_scheme="teal",
                    badge_text="Tra cứu",
                ),
                feature_card(
                    "Quản Lý Kho Tài Liệu",
                    "Dành cho giảng viên: Thêm mới, chỉnh sửa, phân quyền và quản lý lịch sử phiên bản học liệu phụ trách.",
                    "folder-kanban",
                    "/lecturer/documents",
                    color_scheme="purple",
                    badge_text="Giảng viên",
                ),
                feature_card(
                    "Bảng Điều Khiển Giảng Viên",
                    "Xem phân tích số liệu tương tác học liệu, biểu đồ xu hướng xem/tải và xử lý hàng đợi kiểm duyệt.",
                    "layout-dashboard",
                    "/lecturer/dashboard",
                    color_scheme="amber",
                    badge_text="Giảng viên",
                ),
                columns="2",
                spacing="4",
                width="100%",
            ),
            spacing="4",
            width="100%",
            margin_top="4",
        ),
        spacing="6",
        width="100%",
    )

    return student_page_wrapper(content, active_route="/")

def document_list() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Danh sách tài liệu", size="7"),
            rx.text("Lọc theo môn học, khóa..."),
            rx.hstack(
                rx.card(
                    rx.vstack(
                        rx.heading("Giáo trình CNTT", size="4"),
                        rx.text("Giáo trình môn Cấu trúc dữ liệu và giải thuật."),
                        rx.button("Tải xuống"),
                    )
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("Đề thi cuối kỳ", size="4"),
                        rx.text("Đề thi môn Nhập môn lập trình 2023."),
                        rx.button("Tải xuống"),
                    )
                )
            ),
            rx.link(rx.button("Quay lại", color_scheme="gray"), href="/"),
            spacing="5"
        )
    )

def user_management() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Quản lý người dùng", size="7"),
            rx.text("Quản trị viên có thể thêm, sửa, xóa, khóa người dùng."),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Tên"),
                        rx.table.column_header_cell("Email"),
                        rx.table.column_header_cell("Vai trò"),
                    )
                ),
                rx.table.body(
                    rx.table.row(
                        rx.table.row_header_cell("Admin"),
                        rx.table.cell("admin@docuni.com"),
                        rx.table.cell("ADMIN"),
                    ),
                    rx.table.row(
                        rx.table.row_header_cell("Sinh viên A"),
                        rx.table.cell("sva@docuni.com"),
                        rx.table.cell("STUDENT"),
                    ),
                ),
            ),
            rx.link(rx.button("Quay lại", color_scheme="gray"), href="/"),
            spacing="5"
        )
    )

app = rx.App(
    theme=rx.theme(appearance="light", accent_color="blue", radius="large")
)
app.add_page(index, route="/", title="Trang chủ - DocUni")
from frontend_app.student_documents import student_documents_page
app.add_page(student_documents_page, route="/documents", title="Kho tài liệu môn học - DocUni")
app.add_page(user_management, route="/admin/users", title="Quản trị người dùng - DocUni")

# ─── Phase 2: Module Đóng Góp Tài Liệu, Theo Dõi Duyệt & Trợ Lý AI (Task 3.1, 3.2, 3.3) ───
from frontend_app.student_upload import student_upload_page
from frontend_app.student_contributions import student_contributions_page
from frontend_app.student_ai import student_ai_page

app.add_page(student_upload_page, route="/student/upload", title="Đóng góp tài liệu - DocUni")
app.add_page(student_contributions_page, route="/student/contributions", title="Tài liệu đóng góp của tôi - DocUni")
app.add_page(student_ai_page, route="/student/ai-assistant", title="Trợ lý học tập AI - DocUni")

# ─── Phase 3: Module Giảng Viên - Quản Lý Kho Tài Liệu, Kiểm Duyệt & Dashboard (Task 4.1, 4.2, 4.4) ───
from frontend_app.lecturer_documents import lecturer_documents_page
from frontend_app.lecturer_approval import lecturer_approval_page
from frontend_app.lecturer_dashboard import lecturer_dashboard_page

app.add_page(lecturer_documents_page, route="/lecturer/documents", title="Quản lý kho tài liệu - DocUni Giảng viên")
app.add_page(lecturer_approval_page, route="/lecturer/approval", title="Kiểm duyệt tài liệu sinh viên - DocUni Giảng viên")
app.add_page(lecturer_dashboard_page, route="/lecturer/dashboard", title="Bảng điều khiển Giảng viên - DocUni")


