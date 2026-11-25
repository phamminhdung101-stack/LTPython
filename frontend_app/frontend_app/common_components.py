"""
DocUni - Common UI Components (Reflex Framework)
Cung cấp các component dùng chung: Navbar sinh viên, Sidebar giảng viên, KPI Card, Badge trạng thái,
Bộ chuyển đổi người dùng (User Switcher Demo ACL) và Hộp thoại cảnh báo 403 Access Denied.
"""

from typing import Any, Optional
import reflex as rx
from .data_store import GlobalDocState
from .auth import AuthState


# ─── 1. Bộ Chuyển Đổi Profile Người Dùng (Demo Phân Quyền Lớp A vs Lớp B) ────

def user_profile_switcher() -> rx.Component:
    """Hiển thị profile người dùng đăng nhập thực tế từ PostgreSQL; hỗ trợ switcher khi test."""
    return rx.cond(
        AuthState.is_logged_in & (AuthState.current_user_role != ""),
        # Hiển thị thông tin người dùng thật từ Database khi đã đăng nhập
        rx.hstack(
            rx.badge(
                AuthState.current_user_role,
                color_scheme=rx.cond(AuthState.current_user_role == "ADMIN", "red", rx.cond(AuthState.current_user_role == "LECTURER", "purple", "blue")),
                variant="solid",
                size="1",
                radius="full",
            ),
            rx.hstack(
                rx.avatar(
                    fallback=rx.cond(AuthState.current_user_role == "STUDENT", "SV", rx.cond(AuthState.current_user_role == "LECTURER", "GV", "AD")),
                    size="1",
                    radius="full",
                    color_scheme=rx.cond(AuthState.current_user_role == "STUDENT", "blue", "purple"),
                ),
                rx.text(AuthState.current_user_name, size="2", weight="bold", max_width="140px", truncate=True),
                align="center",
                spacing="2",
            ),
            align="center",
            spacing="2",
        ),
        # Fallback cho bộ kiểm thử và demo
        rx.hstack(
            rx.badge(
                GlobalDocState.current_user_role,
                color_scheme="purple",
                variant="solid",
                size="1",
                radius="full",
            ),
            rx.select.root(
                rx.select.trigger(
                    rx.hstack(
                        rx.avatar(
                            fallback=rx.cond(GlobalDocState.is_student, "SV", "GV"),
                            size="1",
                            radius="full",
                            color_scheme=rx.cond(GlobalDocState.is_student, "blue", "purple"),
                        ),
                        rx.text(GlobalDocState.current_user_name, size="2", weight="bold", max_width="140px", truncate=True),
                        align="center",
                        spacing="2",
                    ),
                    variant="surface",
                    size="2",
                ),
                rx.select.content(
                    rx.select.group(
                        rx.select.label("Sinh viên (Demo ACL Lớp A / Lớp B):"),
                        rx.select.item("👤 Lê Hoàng Nam (Lớp D21CQCN01 - Lớp A)", value="u1"),
                        rx.select.item("👤 Trần Thị Mai (Lớp D21CQCN02 - Lớp B)", value="u2"),
                    ),
                    rx.select.separator(),
                    rx.select.group(
                        rx.select.label("Giảng viên & Quản trị:"),
                        rx.select.item("🎓 TS. Nguyễn Văn An (Giảng viên)", value="u3"),
                        rx.select.item("🛡️ Quản trị viên Hệ thống (Admin)", value="u4"),
                    ),
                ),
                value=GlobalDocState.current_user_id,
                on_change=GlobalDocState.switch_user,
            ),
            align="center",
            spacing="2",
        ),
    )


# ─── 2. Hộp Thoại Cảnh Báo Từ Chối Truy Cập 403 (ACL Demo Lớp A vs Lớp B) ─────

def acl_denied_dialog() -> rx.Component:
    """Popup cảnh báo đỏ 403 hiển thị khi sinh viên lớp A/B cố mở tài liệu lớp khác."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("shield-alert", size=28, color="var(--red-10)"),
                        bg="var(--red-3)",
                        padding="3",
                        border_radius="full",
                    ),
                    rx.vstack(
                        rx.alert_dialog.title("Từ Chối Truy Cập (403 Forbidden)"),
                        rx.badge("Vi phạm chính sách bảo mật ACL", color_scheme="red", variant="surface", size="1"),
                        spacing="1",
                        align="start",
                    ),
                    align="center",
                    spacing="3",
                    margin_bottom="3",
                ),
                rx.alert_dialog.description(
                    rx.vstack(
                        rx.text(
                            "Bạn không có quyền mở hoặc tải tài liệu: ",
                            rx.text.strong(GlobalDocState.acl_denied_doc_title),
                            size="2",
                            color="slate.11",
                        ),
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Lớp được cấp quyền:", size="1", weight="bold", color="slate.10", width="150px"),
                                    rx.badge(GlobalDocState.acl_denied_target_class, color_scheme="green", variant="surface"),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.text("Lớp của bạn hiện tại:", size="1", weight="bold", color="slate.10", width="150px"),
                                    rx.badge(GlobalDocState.acl_denied_current_class, color_scheme="red", variant="surface"),
                                    spacing="2",
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            bg="slate.2",
                            padding="3",
                            border_radius="md",
                            border="1px solid var(--slate-4)",
                            width="100%",
                            margin_y="3",
                        ),
                        rx.text(
                            "💡 Mẹo Demo: Sử dụng bộ chọn profile ở góc trên bên phải để chuyển sang đúng tài khoản sinh viên được cấp quyền để mở tài liệu này.",
                            size="1",
                            color="slate.9",
                            font_style="italic",
                        ),
                        spacing="2",
                    )
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.alert_dialog.cancel(
                        rx.button("Đã hiểu & Đóng", color_scheme="gray", variant="surface", on_click=GlobalDocState.close_acl_denied),
                    ),
                    rx.button(
                        "Chuyển sang Sinh viên Lớp A (u1)",
                        color_scheme="blue",
                        on_click=[
                            GlobalDocState.switch_user("u1"),
                            GlobalDocState.close_acl_denied,
                        ],
                    ),
                    spacing="3",
                    margin_top="4",
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            max_width="520px",
            border_radius="xl",
        ),
        open=GlobalDocState.acl_denied_open,
    )


# ─── 3. Navbar Sinh Viên Dùng Chung (Modern SaaS Glassmorphism) ───────────────

def student_navbar(active_route: str = "") -> rx.Component:
    def nav_item(text: str, href: str, icon: str, is_active: bool = False, badge_count: Optional[rx.Var] = None, accent_color: str = "blue") -> rx.Component:
        return rx.link(
            rx.hstack(
                rx.icon(icon, size=16, color=rx.cond(is_active, f"var(--{accent_color}-10)", "var(--slate-9)")),
                rx.text(text, size="2", weight=rx.cond(is_active, "bold", "medium")),
                rx.cond(
                    badge_count is not None,
                    rx.badge(badge_count, color_scheme="amber", variant="solid", size="1", radius="full"),
                    rx.fragment(),
                ),
                align="center",
                spacing="2",
                padding_x="3.5",
                padding_y="2",
                border_radius="xl",
                bg=rx.cond(is_active, f"var(--{accent_color}-3)", "transparent"),
                color=rx.cond(is_active, f"var(--{accent_color}-11)", "var(--slate-11)"),
                border=rx.cond(is_active, f"1px solid var(--{accent_color}-6)", "1px solid transparent"),
                _hover={
                    "bg": f"var(--{accent_color}-2)",
                    "color": f"var(--{accent_color}-10)",
                    "border_color": f"var(--{accent_color}-4)",
                    "transform": "translateY(-1px)",
                },
                transition="all 0.18s cubic-bezier(0.4, 0, 0.2, 1)",
            ),
            href=href,
            underline="none",
        )

    return rx.box(
        rx.container(
            rx.hstack(
                # Logo với hiệu ứng gradient rực rỡ và bóng mờ hiện đại
                rx.link(
                    rx.hstack(
                        rx.box(
                            rx.icon("graduation-cap", size=22, color="white"),
                            background="linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)",
                            padding="2.5",
                            border_radius="xl",
                            box_shadow="0 4px 12px rgba(37, 99, 235, 0.3)",
                            transition="transform 0.2s ease",
                            _hover={"transform": "scale(1.05)"},
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text("DocUni", size="4", weight="bold", color="slate.12", line_height="1", letter_spacing="-0.02em"),
                                rx.badge("Edu 4.0", color_scheme="indigo", variant="surface", size="1", radius="full"),
                                align="center",
                                spacing="2",
                            ),
                            rx.text("Kho Học Liệu Số", size="1", color="blue.10", weight="bold", letter_spacing="0.04em"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    href="/",
                    underline="none",
                ),

                # Navigation Menu Links với màu sắc phân biệt sinh động
                rx.hstack(
                    nav_item("Trang chủ", "/", "home", active_route == "/", accent_color="blue"),
                    nav_item("Kho tài liệu", "/documents", "book-open", active_route == "/documents", accent_color="blue"),
                    nav_item("Đóng góp", "/student/upload", "cloud-upload", active_route == "/student/upload", accent_color="teal"),
                    nav_item("Theo dõi duyệt", "/student/contributions", "list-checks", active_route == "/student/contributions", accent_color="amber"),
                    nav_item("Trợ lý AI", "/student/ai-assistant", "sparkles", active_route == "/student/ai-assistant", accent_color="purple"),
                    spacing="2",
                    display=rx.breakpoints(initial="none", md="flex"),
                    align="center",
                ),

                rx.spacer(),

                # Right action & user profile switcher
                rx.hstack(
                    user_profile_switcher(),
                    rx.cond(
                        (AuthState.current_user_role == "LECTURER") | (AuthState.current_user_role == "ADMIN"),
                        rx.link(
                            rx.button(
                                rx.icon("user-cog", size=15),
                                "Cổng GV",
                                rx.cond(
                                    GlobalDocState.pending_count > 0,
                                    rx.badge(GlobalDocState.pending_count, color_scheme="red", variant="solid", size="1", radius="full"),
                                    rx.fragment(),
                                ),
                                size="2",
                                variant="surface",
                                color_scheme="indigo",
                                border_radius="lg",
                                box_shadow="sm",
                            ),
                            href="/lecturer/approval",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        AuthState.is_logged_in & (AuthState.current_user_role != ""),
                        rx.button(
                            rx.icon("log-out", size=15),
                            "Đăng xuất",
                            size="2",
                            variant="soft",
                            color_scheme="red",
                            border_radius="lg",
                            on_click=AuthState.logout,
                            _hover={"bg": "var(--red-3)", "transform": "translateY(-1px)"},
                            transition="all 0.15s ease",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("log-in", size=15),
                                "Đăng nhập",
                                size="2",
                                variant="solid",
                                color_scheme="blue",
                                border_radius="lg",
                            ),
                            href="/login",
                        ),
                    ),
                    align="center",
                    spacing="3",
                ),
                align="center",
                justify="between",
                height="68px",
            ),
            size="4",
        ),
        border_b="1px solid rgba(226, 232, 240, 0.8)",
        background="rgba(255, 255, 255, 0.92)",
        backdrop_filter="blur(16px)",
        position="sticky",
        top="0",
        z_index="50",
        box_shadow="0 2px 10px rgba(0, 0, 0, 0.03)",
    )


# ─── 4. Sidebar Giảng Viên Dùng Chung ────────────────────────────────────────

def lecturer_sidebar(current_route: str = "") -> rx.Component:
    def sidebar_item(title: str, href: str, icon: str, is_active: bool = False, badge_var: Optional[rx.Var] = None) -> rx.Component:
        return rx.link(
            rx.hstack(
                rx.icon(icon, size=18, color=rx.cond(is_active, "var(--indigo-10)", "var(--slate-9)")),
                rx.text(title, size="2", weight=rx.cond(is_active, "bold", "medium")),
                rx.spacer(),
                rx.cond(
                    badge_var is not None,
                    rx.badge(badge_var, color_scheme="red", variant="solid", size="1", radius="full"),
                    rx.fragment(),
                ),
                align="center",
                spacing="3",
                padding_x="3",
                padding_y="2.5",
                border_radius="lg",
                bg=rx.cond(is_active, "var(--indigo-3)", "transparent"),
                color=rx.cond(is_active, "var(--indigo-11)", "var(--slate-11)"),
                _hover={"bg": "var(--indigo-2)", "color": "var(--indigo-10)"},
                transition="all 0.15s ease",
            ),
            href=href,
            underline="none",
            width="100%",
        )

    return rx.box(
        rx.vstack(
            # Logo Portal với gradient sắc nét
            rx.link(
                rx.hstack(
                    rx.box(
                        rx.icon("shield-check", size=22, color="white"),
                        background="linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                        padding="2.5",
                        border_radius="xl",
                        box_shadow="0 4px 12px rgba(79, 70, 229, 0.35)",
                    ),
                    rx.vstack(
                        rx.text("DocUni", size="4", weight="bold", color="slate.12", line_height="1", letter_spacing="-0.02em"),
                        rx.text("Cổng Giảng Viên", size="1", color="indigo.10", weight="bold", letter_spacing="0.04em"),
                        spacing="0",
                    ),
                    align="center",
                    spacing="3",
                    padding_y="3",
                    padding_x="2",
                ),
                href="/lecturer/dashboard",
                underline="none",
                width="100%",
            ),

            rx.divider(color_scheme="gray", margin_y="1"),

            # Lecturer Profile Card
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.avatar(fallback="GV", size="2", radius="full", color_scheme="indigo"),
                        rx.vstack(
                            rx.text("TS. Nguyễn Văn An", size="2", weight="bold", color="slate.12"),
                            rx.text("Khoa CNTT • Thẩm định viên", size="1", color="slate.10"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    rx.badge(
                        rx.hstack(rx.icon("bell", size=12), rx.text("Chờ duyệt: ", GlobalDocState.pending_count, " tài liệu"), align="center", spacing="1"),
                        color_scheme="amber",
                        variant="surface",
                        size="1",
                        radius="full",
                        width="100%",
                        justify="center",
                    ),
                    spacing="2",
                    width="100%",
                ),
                padding="3.5",
                border_radius="xl",
                background="linear-gradient(135deg, rgba(238, 242, 255, 0.8) 0%, rgba(245, 243, 255, 0.8) 100%)",
                border="1px solid rgba(199, 210, 254, 0.6)",
                box_shadow="sm",
                width="100%",
                margin_bottom="3",
            ),

            # Navigation Menu Items với icon và hiệu ứng hover hiện đại
            rx.vstack(
                sidebar_item("Bảng điều khiển", "/lecturer/dashboard", "layout-dashboard", current_route == "/lecturer/dashboard"),
                sidebar_item("Kho tài liệu môn học", "/lecturer/documents", "folder-kanban", current_route == "/lecturer/documents"),
                sidebar_item("Kiểm duyệt học liệu", "/lecturer/approval", "clipboard-check", current_route == "/lecturer/approval", badge_var=GlobalDocState.pending_count),
                spacing="2",
                width="100%",
            ),

            rx.spacer(),

            rx.divider(color_scheme="gray", margin_y="3"),

            # External Shortcuts
            rx.vstack(
                rx.link(
                    rx.hstack(
                        rx.icon("external-link", size=15, color="var(--slate-9)"),
                        rx.text("Xem Cổng Sinh viên", size="2", color="slate.11", weight="medium"),
                        align="center",
                        spacing="2",
                        padding="2",
                        border_radius="md",
                        _hover={"bg": "var(--slate-3)", "color": "var(--blue-10)"},
                    ),
                    href="/documents",
                    underline="none",
                    width="100%",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("log-out", size=15, color="var(--red-9)"),
                        rx.text("Đăng xuất", size="2", color="red.10", weight="medium"),
                        align="center",
                        spacing="2",
                    ),
                    variant="soft",
                    color_scheme="red",
                    on_click=AuthState.logout,
                    width="100%",
                    border_radius="lg",
                ),
                spacing="2",
                width="100%",
            ),
            height="100%",
            padding="4",
        ),
        width="270px",
        min_width="270px",
        height="100vh",
        border_r="1px solid rgba(226, 232, 240, 0.8)",
        background="white",
        position="sticky",
        top="0",
        display=rx.breakpoints(initial="none", md="block"),
        box_shadow="2px 0 10px rgba(0, 0, 0, 0.02)",
    )


# ─── 5. KPI Card & Badge Trạng Thái ──────────────────────────────────────────

def file_type_badge(file_name: str) -> rx.Component:
    """Badge hiển thị định dạng tệp thông minh kèm icon và màu sắc đặc trưng."""
    fn_lower = file_name.lower()
    return rx.cond(
        fn_lower.contains(".pdf"),
        rx.badge(rx.hstack(rx.icon("file-text", size=12), rx.text("PDF", size="1"), align="center", spacing="1"), color_scheme="red", variant="surface", radius="full"),
        rx.cond(
            fn_lower.contains(".ppt") | fn_lower.contains(".pptx"),
            rx.badge(rx.hstack(rx.icon("presentation", size=12), rx.text("PPTX", size="1"), align="center", spacing="1"), color_scheme="orange", variant="surface", radius="full"),
            rx.cond(
                fn_lower.contains(".doc") | fn_lower.contains(".docx"),
                rx.badge(rx.hstack(rx.icon("file-type-2", size=12), rx.text("DOCX", size="1"), align="center", spacing="1"), color_scheme="blue", variant="surface", radius="full"),
                rx.cond(
                    fn_lower.contains(".xls") | fn_lower.contains(".xlsx"),
                    rx.badge(rx.hstack(rx.icon("sheet", size=12), rx.text("XLSX", size="1"), align="center", spacing="1"), color_scheme="green", variant="surface", radius="full"),
                    rx.badge(rx.hstack(rx.icon("file", size=12), rx.text("FILE", size="1"), align="center", spacing="1"), color_scheme="gray", variant="surface", radius="full"),
                ),
            ),
        ),
    )


def kpi_card(title: str, value: Any, icon: str, color_scheme: str = "blue", description: str = "", trend: str = "") -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=24, color=f"var(--{color_scheme}-10)"),
                    bg=f"var(--{color_scheme}-3)",
                    padding="3",
                    border_radius="xl",
                    box_shadow=f"0 4px 12px var(--{color_scheme}-4)",
                ),
                rx.spacer(),
                rx.cond(
                    trend != "",
                    rx.badge(trend, color_scheme=color_scheme, variant="surface", size="1", radius="full"),
                    rx.fragment(),
                ),
                align="center",
                width="100%",
            ),
            rx.vstack(
                rx.text(title, size="2", color="slate.10", weight="medium"),
                rx.heading(value, size="7", weight="bold", color="slate.12", letter_spacing="-0.02em"),
                rx.cond(
                    description != "",
                    rx.text(description, size="1", color="slate.9"),
                    rx.fragment(),
                ),
                spacing="1",
                align="start",
            ),
            spacing="3",
            width="100%",
        ),
        variant="surface",
        padding="5",
        border_radius="xl",
        border=f"1px solid var(--{color_scheme}-4)",
        box_shadow="0 1px 3px rgba(0, 0, 0, 0.05), 0 10px 20px -5px rgba(0, 0, 0, 0.02)",
        _hover={
            "transform": "translateY(-3px)",
            "box_shadow": f"0 12px 24px -5px var(--{color_scheme}-3)",
            "border_color": f"var(--{color_scheme}-7)",
        },
        transition="all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
    )


def status_badge(status: str) -> rx.Component:
    return rx.match(
        status,
        ("PENDING", rx.badge(rx.hstack(rx.icon("clock", size=12), rx.text("Chờ duyệt", size="1"), align="center", spacing="1"), color_scheme="amber", variant="surface", radius="full")),
        ("APPROVED", rx.badge(rx.hstack(rx.icon("circle-check", size=12), rx.text("Đã duyệt", size="1"), align="center", spacing="1"), color_scheme="green", variant="surface", radius="full")),
        ("REJECTED", rx.badge(rx.hstack(rx.icon("circle-x", size=12), rx.text("Bị từ chối", size="1"), align="center", spacing="1"), color_scheme="red", variant="surface", radius="full")),
        rx.badge(status, color_scheme="gray", variant="surface", radius="full")
    )


# ─── 6. Wrappers ─────────────────────────────────────────────────────────────

def student_page_wrapper(content: rx.Component, active_route: str = "") -> rx.Component:
    return rx.box(
        student_navbar(active_route=active_route),
        acl_denied_dialog(),  # Hộp thoại cảnh báo 403 ACL Demo
        rx.container(
            content,
            size="4",
            padding_y="7",
            min_height="calc(100vh - 160px)",
        ),
        # Footer
        rx.box(
            rx.container(
                rx.hstack(
                    rx.hstack(
                        rx.box(
                            rx.box(
                                width="8px",
                                height="8px",
                                border_radius="full",
                                bg="#10b981",
                                box_shadow="0 0 8px #10b981",
                            ),
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),
                        rx.text("PostgreSQL Online", size="1", color="slate.10", weight="medium"),
                        align="center",
                        spacing="2",
                    ),
                    rx.spacer(),
                    rx.text("© 2026 DocUni – Nền tảng Học liệu Số & Trợ lý AI Thông minh", size="2", color="slate.9"),
                    rx.spacer(),
                    rx.hstack(
                        rx.badge("Reflex 0.10.0", color_scheme="blue", variant="surface", size="1"),
                        rx.badge("Django REST API", color_scheme="indigo", variant="surface", size="1"),
                        rx.badge("AI Semantic RAG", color_scheme="purple", variant="surface", size="1"),
                        spacing="2",
                        display=rx.breakpoints(initial="none", md="flex"),
                    ),
                    align="center",
                    width="100%",
                ),
                size="4",
                padding_y="4",
            ),
            border_t="1px solid rgba(226, 232, 240, 0.8)",
            bg="rgba(255, 255, 255, 0.9)",
            backdrop_filter="blur(12px)",
        ),
        background="linear-gradient(180deg, #f8fafc 0%, #f1f5f9 50%, #eef2ff 100%)",
        min_height="100vh",
    )


def lecturer_page_wrapper(content: rx.Component, current_route: str = "") -> rx.Component:
    return rx.hstack(
        lecturer_sidebar(current_route=current_route),
        rx.box(
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("graduation-cap", size=18, color="var(--indigo-10)"),
                            bg="indigo.3",
                            padding="1.5",
                            border_radius="md",
                        ),
                        rx.vstack(
                            rx.text("Cổng Nghiệp Vụ Giảng Viên", size="2", weight="bold", color="indigo.11"),
                            rx.text("Phê duyệt, phân quyền & quản lý học liệu đại học", size="1", color="slate.9"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    rx.spacer(),
                    user_profile_switcher(),
                    align="center",
                    padding_x="6",
                    padding_y="3.5",
                    border_b="1px solid rgba(226, 232, 240, 0.8)",
                    bg="rgba(255, 255, 255, 0.9)",
                    backdrop_filter="blur(12px)",
                ),
                rx.box(
                    content,
                    padding="6",
                ),
                width="100%",
                min_height="100vh",
                background="linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)",
            ),
            flex="1",
            min_width="0",
        ),
        spacing="0",
        min_height="100vh",
        background="#f8fafc",
    )
