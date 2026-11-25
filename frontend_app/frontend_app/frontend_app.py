import reflex as rx
from typing import TypedDict

class State(rx.State):
    """The app state."""
    
    search_query: str = ""

    def set_search_query(self, value: str):
        self.search_query = value

from frontend_app.common_components import student_page_wrapper, kpi_card, file_type_badge
from frontend_app.data_store import GlobalDocState
from frontend_app.auth import AuthState, login_page


class RecentApprovedDoc(TypedDict):
    id: str
    title: str
    subject_code: str
    file_name: str
    folder_path: str
    uploader_name: str
    downloads: int


def index() -> rx.Component:
    def recent_doc_item(doc: rx.Var[RecentApprovedDoc]) -> rx.Component:
        return rx.card(
            rx.hstack(
                rx.box(
                    file_type_badge(doc["file_name"]),
                    padding_top="1",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.heading(doc["title"], size="3", weight="bold", color="slate.12", line_clamp=1),
                        rx.spacer(),
                        rx.badge(doc["subject_code"], color_scheme="blue", variant="surface", size="1"),
                        align="center",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.icon("folder", size=12, color="var(--slate-8)"),
                        rx.text(doc["folder_path"], size="1", color="slate.9", truncate=True),
                        rx.text("•", size="1", color="slate.7"),
                        rx.icon("user", size=12, color="var(--slate-8)"),
                        rx.text(doc["uploader_name"], size="1", color="slate.9"),
                        rx.text("•", size="1", color="slate.7"),
                        rx.icon("download", size=12, color="var(--slate-8)"),
                        rx.text(doc["downloads"], size="1", color="slate.9"),
                        align="center",
                        spacing="2",
                        wrap="wrap",
                    ),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                rx.button(
                    rx.icon("eye", size=14),
                    "Mở",
                    size="1",
                    variant="surface",
                    color_scheme="blue",
                    on_click=GlobalDocState.open_document(doc["id"]),
                    border_radius="md",
                ),
                align="center",
                spacing="3",
                width="100%",
            ),
            padding="3.5",
            border_radius="xl",
            border="1px solid var(--slate-4)",
            background="white",
            _hover={"border_color": "var(--blue-7)", "box_shadow": "0 4px 12px rgba(0, 0, 0, 0.04)", "transform": "translateY(-1px)"},
            transition="all 0.2s ease",
            width="100%",
        )

    content = rx.vstack(
        # 1. Welcome Greeting Banner (Modern SaaS Hero)
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.avatar(
                            fallback=rx.cond(AuthState.current_user_role == "STUDENT", "SV", rx.cond(AuthState.current_user_role == "LECTURER", "GV", "AD")),
                            size="3",
                            radius="full",
                            background="rgba(255, 255, 255, 0.25)",
                            color="white",
                            border="2px solid rgba(255, 255, 255, 0.5)",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.heading(
                                    "Xin chào, ",
                                    rx.cond(AuthState.current_user_name != "", AuthState.current_user_name, "Sinh viên"),
                                    "! 👋",
                                    size="6",
                                    weight="bold",
                                    color="white",
                                    letter_spacing="-0.02em",
                                ),
                                rx.badge(
                                    rx.cond(AuthState.current_user_role != "", AuthState.current_user_role, "STUDENT"),
                                    color_scheme="indigo",
                                    variant="solid",
                                    size="1",
                                    radius="full",
                                ),
                                align="center",
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.cond(
                                    AuthState.current_user_class != "",
                                    rx.badge(
                                        rx.hstack(rx.icon("users", size=11), rx.text(AuthState.current_user_class, size="1"), align="center", spacing="1"),
                                        color_scheme="blue",
                                        variant="surface",
                                        radius="full",
                                    ),
                                    rx.fragment(),
                                ),
                                rx.cond(
                                    AuthState.current_user_department != "",
                                    rx.badge(
                                        rx.hstack(rx.icon("building", size=11), rx.text(AuthState.current_user_department, size="1"), align="center", spacing="1"),
                                        color_scheme="teal",
                                        variant="surface",
                                        radius="full",
                                    ),
                                    rx.fragment(),
                                ),
                                rx.badge(
                                    rx.hstack(rx.icon("sparkles", size=11), rx.text("AI RAG Ready", size="1"), align="center", spacing="1"),
                                    color_scheme="purple",
                                    variant="surface",
                                    radius="full",
                                ),
                                align="center",
                                spacing="2",
                                wrap="wrap",
                            ),
                            spacing="2",
                            align="start",
                        ),
                        align="center",
                        spacing="4",
                    ),
                    rx.spacer(),
                    display=rx.breakpoints(initial="block", md="flex"),
                    width="100%",
                ),
                rx.text(
                    "Chào mừng bạn đến với Cổng Học Liệu Số DocUni. Tra cứu giáo trình, bài giảng, đề thi và đối soát ngữ nghĩa AI theo thời gian thực.",
                    size="2",
                    color="rgba(255, 255, 255, 0.85)",
                    line_height="1.5",
                    margin_top="1",
                ),
                # Big Search Input inside hero banner
                rx.hstack(
                    rx.input(
                        rx.input.slot(rx.icon("search", size=18, color="var(--slate-8)")),
                        placeholder="Tìm kiếm môn học, bài giảng, đề cương (VD: Lập trình Java, SQL, Kinh tế vi mô...)...",
                        value=State.search_query,
                        on_change=State.set_search_query,
                        size="3",
                        background="white",
                        border_radius="xl",
                        flex="1",
                        box_shadow="sm",
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("arrow-right", size=16),
                            "Tìm kiếm",
                            background="linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)",
                            color="white",
                            size="3",
                            variant="solid",
                            border_radius="xl",
                            box_shadow="0 4px 12px rgba(14, 165, 233, 0.35)",
                            _hover={"transform": "translateY(-1px)"},
                        ),
                        href="/documents",
                    ),
                    align="center",
                    spacing="3",
                    width="100%",
                    margin_top="3",
                ),
                spacing="3",
                width="100%",
            ),
            background="linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #4f46e5 100%)",
            padding=rx.breakpoints(initial="5", sm="6", md="7"),
            border_radius="2xl",
            box_shadow="0 10px 30px -10px rgba(37, 99, 235, 0.35)",
            width="100%",
        ),

        # 2. Bốn Thẻ KPI Số Liệu Thực Tế Từ PostgreSQL
        rx.grid(
            kpi_card("Kho Học Liệu Môn Học", GlobalDocState.documents.length(), "book-open", "blue", "Tài liệu trực tuyến trong database", trend="Database"),
            kpi_card("Tài Liệu Đã Phê Duyệt", GlobalDocState.public_documents.length(), "circle-check", "green", "Khả dụng học tập toàn trường", trend="Đã duyệt"),
            kpi_card("Đóng Góp Của Bạn", GlobalDocState.my_contributions.length(), "cloud-upload", "indigo", "Tài liệu bạn đã nộp", trend="Cá nhân"),
            kpi_card("Lượt Tải Toàn Hệ Thống", GlobalDocState.total_downloads_count, "download", "amber", "Tổng lượt tải tích lũy", trend="Tích lũy"),
            columns=rx.breakpoints(initial="1", sm="2", lg="4"),
            spacing="4",
            width="100%",
        ),

        # 3. Two-Column Dashboard Grid
        rx.grid(
            # Cột Trái: Tài liệu học phần mới được phê duyệt
            rx.vstack(
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon("sparkles", size=18, color="var(--blue-10)"),
                                    bg="blue.3",
                                    padding="2",
                                    border_radius="lg",
                                ),
                                rx.vstack(
                                    rx.heading("Tài Liệu Mới Được Phê Duyệt", size="4", weight="bold", color="slate.12"),
                                    rx.text("Cập nhật tự động từ database PostgreSQL", size="1", color="slate.9"),
                                    spacing="0",
                                ),
                                align="center",
                                spacing="3",
                            ),
                            rx.spacer(),
                            rx.link(
                                rx.hstack(
                                    rx.text("Xem tất cả", size="2", weight="bold", color="blue.10"),
                                    rx.icon("arrow-right", size=14, color="var(--blue-10)"),
                                    align="center",
                                    spacing="1",
                                ),
                                href="/documents",
                                underline="none",
                            ),
                            align="center",
                            width="100%",
                        ),
                        rx.divider(color_scheme="gray"),
                        rx.cond(
                            GlobalDocState.recent_approved_docs.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    GlobalDocState.recent_approved_docs.to(list[RecentApprovedDoc]),
                                    recent_doc_item,
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            rx.center(
                                rx.vstack(
                                    rx.icon("file-check", size=32, color="var(--slate-7)"),
                                    rx.text("Chưa có tài liệu nào được phê duyệt.", size="2", color="slate.9"),
                                    spacing="2",
                                    align="center",
                                    padding="6",
                                ),
                                width="100%",
                            ),
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    padding="5",
                    border_radius="2xl",
                    background="white",
                    border="1px solid var(--slate-4)",
                    box_shadow="0 2px 12px rgba(0, 0, 0, 0.03)",
                    width="100%",
                ),
                width="100%",
            ),

            # Cột Phải: Lối tắt công cụ thông minh & Môn học hot
            rx.vstack(
                # Card AI Assistant nổi bật
                rx.link(
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon("sparkles", size=22, color="white"),
                                    background="rgba(255, 255, 255, 0.2)",
                                    padding="2.5",
                                    border_radius="xl",
                                ),
                                rx.badge("AI Powered", color_scheme="purple", variant="surface", size="1", radius="full"),
                                align="center",
                                spacing="2",
                            ),
                            rx.heading("Trợ Lý AI Tra Cứu Ngữ Cảnh", size="4", weight="bold", color="white"),
                            rx.text(
                                "Hỏi đáp thông minh trên giáo trình, trích dẫn chính xác số trang và độ tương đồng ngữ nghĩa bằng công nghệ RAG.",
                                size="2",
                                color="rgba(255, 255, 255, 0.85)",
                                line_height="1.5",
                            ),
                            rx.hstack(
                                rx.text("Bắt đầu trò chuyện ngay", size="2", weight="bold", color="white"),
                                rx.icon("arrow-right", size=15, color="white"),
                                align="center",
                                spacing="2",
                                margin_top="1",
                            ),
                            spacing="3",
                            align="start",
                        ),
                        padding="5",
                        border_radius="2xl",
                        background="linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                        box_shadow="0 8px 24px -6px rgba(124, 58, 237, 0.45)",
                        _hover={"transform": "translateY(-2px)", "box_shadow": "0 12px 28px -6px rgba(124, 58, 237, 0.55)"},
                        transition="all 0.2s ease",
                        width="100%",
                    ),
                    href="/student/ai-assistant",
                    underline="none",
                    width="100%",
                ),

                # Card Đóng Góp Tài Liệu
                rx.link(
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon("cloud-upload", size=22, color="white"),
                                    background="rgba(255, 255, 255, 0.2)",
                                    padding="2.5",
                                    border_radius="xl",
                                ),
                                rx.badge("Đóng góp học liệu", color_scheme="teal", variant="surface", size="1", radius="full"),
                                align="center",
                                spacing="2",
                            ),
                            rx.heading("Đóng Góp Tài Liệu Học Phần", size="4", weight="bold", color="white"),
                            rx.text(
                                "Chia sẻ bài giảng, đề thi, slide học tập cho lớp học và cộng đồng sinh viên.",
                                size="2",
                                color="rgba(255, 255, 255, 0.85)",
                                line_height="1.5",
                            ),
                            rx.hstack(
                                rx.text("Tải lên tài liệu mới", size="2", weight="bold", color="white"),
                                rx.icon("arrow-right", size=15, color="white"),
                                align="center",
                                spacing="2",
                                margin_top="1",
                            ),
                            spacing="3",
                            align="start",
                        ),
                        padding="5",
                        border_radius="2xl",
                        background="linear-gradient(135deg, #0d9488 0%, #0284c7 100%)",
                        box_shadow="0 8px 24px -6px rgba(13, 148, 136, 0.4)",
                        _hover={"transform": "translateY(-2px)", "box_shadow": "0 12px 28px -6px rgba(13, 148, 136, 0.5)"},
                        transition="all 0.2s ease",
                        width="100%",
                    ),
                    href="/student/upload",
                    underline="none",
                    width="100%",
                ),

                # Môn học hot / trọng tâm
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("tags", size=16, color="var(--blue-9)"),
                            rx.text("Môn học được quan tâm", size="2", weight="bold", color="slate.12"),
                            align="center",
                            spacing="2",
                        ),
                        rx.flex(
                            rx.link(rx.badge("💻 Lap trinh Java", color_scheme="blue", variant="surface", size="2", radius="full"), href="/documents"),
                            rx.link(rx.badge("🗄️ Co so du lieu", color_scheme="teal", variant="surface", size="2", radius="full"), href="/documents"),
                            rx.link(rx.badge("🌐 Mang may tinh", color_scheme="indigo", variant="surface", size="2", radius="full"), href="/documents"),
                            rx.link(rx.badge("📈 Kinh te vi mo", color_scheme="orange", variant="surface", size="2", radius="full"), href="/documents"),
                            rx.link(rx.badge("📑 Ke toan dai cuong", color_scheme="amber", variant="surface", size="2", radius="full"), href="/documents"),
                            spacing="2",
                            wrap="wrap",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    padding="4",
                    border_radius="xl",
                    background="white",
                    border="1px solid var(--slate-4)",
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),

            columns=rx.breakpoints(initial="1", lg="3"),
            spacing="5",
            width="100%",
        ),

        spacing="6",
        width="100%",
    )

    return rx.cond(
        AuthState.is_logged_in & (AuthState.current_user_role != ""),
        student_page_wrapper(content, active_route="/"),
        login_page(),
    )

app = rx.App(
    html_custom_attrs={"data-theme": "light", "translate": "no", "lang": "vi"},
    style={
        "[data-sonner-toaster]": {"display": "none !important"},
        ".connection-toast": {"display": "none !important"},
    },
    app_wraps={(5, "Overlay"): lambda stateful: rx.fragment()},
)
# ─── Auth State & Pages ────────────────────────────────────────────────────────
from frontend_app.auth import login_page, register_page, AuthState

app.add_page(index, route="/", title="Trang chủ - DocUni", on_load=AuthState.redirect_root)

# ─── Student pages ─────────────────────────────────────────────────────────────
from frontend_app.student_documents import student_documents_page
from frontend_app.data_store import GlobalDocState
from frontend_app.student_upload import student_upload_page
from frontend_app.student_contributions import student_contributions_page, ContributionState
from frontend_app.student_ai import student_ai_page

app.add_page(student_documents_page, route="/documents", title="Kho tài liệu môn học - DocUni", on_load=[AuthState.check_auth, GlobalDocState.load_documents])
app.add_page(student_upload_page, route="/student/upload", title="Đóng góp tài liệu - DocUni", on_load=AuthState.check_auth)
app.add_page(student_contributions_page, route="/student/contributions", title="Tài liệu đóng góp của tôi - DocUni", on_load=[AuthState.check_auth, ContributionState.load_contributions])
app.add_page(student_ai_page, route="/student/ai-assistant", title="Trợ lý học tập AI - DocUni", on_load=AuthState.check_auth)

# ─── Lecturer pages ────────────────────────────────────────────────────────────
from frontend_app.lecturer_documents import lecturer_documents_page, LecturerDocState
from frontend_app.lecturer_approval import lecturer_approval_page, LecturerApprovalState
from frontend_app.lecturer_dashboard import lecturer_dashboard_page, LecturerDashboardState

app.add_page(lecturer_documents_page, route="/lecturer/documents", title="Quản lý kho tài liệu - DocUni Giảng viên", on_load=[AuthState.check_lecturer_auth, LecturerDocState.load_documents])
app.add_page(lecturer_approval_page, route="/lecturer/approval", title="Kiểm duyệt tài liệu sinh viên - DocUni Giảng viên", on_load=[AuthState.check_lecturer_auth, LecturerApprovalState.load_items])
app.add_page(lecturer_dashboard_page, route="/lecturer/dashboard", title="Bảng điều khiển Giảng viên - DocUni", on_load=[AuthState.check_lecturer_auth, LecturerDashboardState.load_data])

# ─── Admin pages ───────────────────────────────────────────────────────────────
from frontend_app.admin_panel import admin_users_page, AdminUserState
from frontend_app.admin_organization import admin_organization_page, OrgState

app.add_page(admin_users_page, route="/admin/users", title="Quản trị người dùng - DocUni Admin", on_load=[AuthState.check_admin_auth, AdminUserState.load_users])
app.add_page(admin_organization_page, route="/admin/organization", title="Quản lý tổ chức - DocUni Admin", on_load=[AuthState.check_admin_auth, OrgState.load_data])

# ─── Auth pages ────────────────────────────────────────────────────────────────
app.add_page(login_page, route="/login", title="Đăng nhập - DocUni")
app.add_page(register_page, route="/register", title="Đăng ký tài khoản - DocUni")
