"""
DocUni - Common UI Components (Reflex Framework)
Cung cấp các component dùng chung: Navbar sinh viên, Sidebar giảng viên, KPI Card, Badge trạng thái,
Bộ chuyển đổi người dùng (User Switcher Demo ACL) và Hộp thoại cảnh báo 403 Access Denied.
"""

from typing import Any, Optional
import reflex as rx
from .data_store import GlobalDocState


# ─── 1. Bộ Chuyển Đổi Profile Người Dùng (Demo Phân Quyền Lớp A vs Lớp B) ────

def user_profile_switcher() -> rx.Component:
    """Dropdown chuyển đổi tài khoản trực tiếp trên Navbar để demo kịch bản giảng viên."""
    return rx.hstack(
        # Hiển thị Tag lớp hiện tại
        rx.cond(
            GlobalDocState.current_user_class != "",
            rx.badge(
                GlobalDocState.current_user_class,
                color_scheme="blue",
                variant="solid",
                size="1",
                radius="full",
            ),
            rx.badge(
                GlobalDocState.current_user_role,
                color_scheme="purple",
                variant="solid",
                size="1",
                radius="full",
            ),
        ),
        # Selector chọn người dùng
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


# ─── 3. Navbar Sinh Viên Dùng Chung ──────────────────────────────────────────

def student_navbar(active_route: str = "") -> rx.Component:
    def nav_item(text: str, href: str, icon: str, is_active: bool = False, badge_count: Optional[rx.Var] = None) -> rx.Component:
        return rx.link(
            rx.hstack(
                rx.icon(icon, size=16),
                rx.text(text, size="2", weight="medium"),
                rx.cond(
                    badge_count is not None,
                    rx.badge(badge_count, color_scheme="amber", variant="solid", size="1", radius="full"),
                    rx.fragment(),
                ),
                align="center",
                spacing="2",
                padding_x="3",
                padding_y="2",
                border_radius="md",
                bg=rx.cond(is_active, "var(--blue-3)", "transparent"),
                color=rx.cond(is_active, "var(--blue-11)", "var(--slate-11)"),
                _hover={"bg": "var(--blue-2)", "color": "var(--blue-10)"},
                transition="all 0.15s ease",
            ),
            href=href,
            underline="none",
        )

    return rx.box(
        rx.container(
            rx.hstack(
                # Logo
                rx.link(
                    rx.hstack(
                        rx.box(
                            rx.icon("graduation-cap", size=20, color="white"),
                            bg="blue.9",
                            padding="2",
                            border_radius="lg",
                            box_shadow="sm",
                        ),
                        rx.vstack(
                            rx.text("DocUni", size="4", weight="bold", color="slate.12", line_height="1"),
                            rx.text("Kho Học Liệu Số", size="1", color="blue.10", weight="bold"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    href="/",
                    underline="none",
                ),

                # Navigation Menu Links
                rx.hstack(
                    nav_item("Trang chủ", "/", "home", active_route == "/"),
                    nav_item("Kho tài liệu", "/documents", "book-open", active_route == "/documents"),
                    nav_item("Đóng góp tài liệu", "/student/upload", "upload", active_route == "/student/upload"),
                    nav_item("Theo dõi duyệt", "/student/contributions", "list-checks", active_route == "/student/contributions"),
                    nav_item("Trợ lý AI", "/student/ai-assistant", "sparkles", active_route == "/student/ai-assistant"),
                    spacing="1",
                    display=["none", "none", "flex"],
                ),

                rx.spacer(),

                # Right action & user profile switcher
                rx.hstack(
                    user_profile_switcher(),
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
                        ),
                        href="/lecturer/approval",
                    ),
                    align="center",
                    spacing="3",
                ),
                align="center",
                justify="between",
                height="64px",
            ),
            size="4",
        ),
        border_b="1px solid var(--slate-4)",
        bg="white",
        position="sticky",
        top="0",
        z_index="50",
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
            # Logo Portal
            rx.link(
                rx.hstack(
                    rx.box(
                        rx.icon("shield-check", size=22, color="white"),
                        bg="indigo.9",
                        padding="2",
                        border_radius="lg",
                        box_shadow="sm",
                    ),
                    rx.vstack(
                        rx.text("DocUni", size="4", weight="bold", color="slate.12", line_height="1"),
                        rx.text("Lecturer Portal", size="1", color="indigo.10", weight="bold", letter_spacing="0.05em"),
                        spacing="0",
                    ),
                    align="center",
                    spacing="2",
                    padding_y="3",
                    padding_x="2",
                ),
                href="/lecturer/dashboard",
                underline="none",
                width="100%",
            ),

            rx.divider(color_scheme="gray", margin_y="2"),

            # Lecturer Profile Card
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.avatar(fallback="GV", size="2", radius="full", color_scheme="indigo"),
                        rx.vstack(
                            rx.text("TS. Nguyễn Văn An", size="2", weight="bold", color="slate.12"),
                            rx.text("Khoa CNTT - Kiểm duyệt viên", size="1", color="slate.10"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    rx.badge(
                        rx.hstack(rx.icon("bell", size=12), rx.text("Chờ duyệt: ", GlobalDocState.pending_count, " tài liệu"), align="center", spacing="1"),
                        color_scheme="amber",
                        variant="surface",
                        size="1",
                        width="100%",
                        justify="center",
                    ),
                    spacing="2",
                    width="100%",
                ),
                padding="3",
                border_radius="lg",
                bg="slate.2",
                border="1px solid var(--slate-4)",
                width="100%",
                margin_bottom="3",
            ),

            # Navigation Menu Items
            rx.vstack(
                sidebar_item("Bảng điều khiển", "/lecturer/dashboard", "layout-dashboard", current_route == "/lecturer/dashboard"),
                sidebar_item("Kho tài liệu của tôi", "/lecturer/documents", "folder-kanban", current_route == "/lecturer/documents"),
                sidebar_item("Kiểm duyệt tài liệu", "/lecturer/approval", "clipboard-check", current_route == "/lecturer/approval", badge_var=GlobalDocState.pending_count),
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
                        rx.text("Xem Cổng Sinh viên", size="2", color="slate.10"),
                        align="center",
                        spacing="2",
                        padding="2",
                    ),
                    href="/documents",
                    underline="none",
                ),
                spacing="1",
                width="100%",
            ),
            height="100%",
            padding="4",
        ),
        width="260px",
        min_width="260px",
        height="100vh",
        border_r="1px solid var(--slate-4)",
        bg="white",
        position="sticky",
        top="0",
        display=["none", "none", "block"],
    )


# ─── 5. KPI Card & Badge Trạng Thái ──────────────────────────────────────────

def kpi_card(title: str, value: Any, icon: str, color_scheme: str = "blue", description: str = "") -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=22, color=f"var(--{color_scheme}-10)"),
                bg=f"var(--{color_scheme}-3)",
                padding="3",
                border_radius="xl",
            ),
            rx.vstack(
                rx.text(title, size="1", color="slate.10", weight="medium"),
                rx.heading(value, size="6", weight="bold", color="slate.12"),
                rx.cond(
                    description != "",
                    rx.text(description, size="1", color="slate.9"),
                    rx.fragment(),
                ),
                spacing="1",
            ),
            align="center",
            spacing="3",
        ),
        variant="surface",
        size="2",
    )


def status_badge(status: str) -> rx.Component:
    return rx.match(
        status,
        ("PENDING", rx.badge(rx.hstack(rx.icon("clock", size=12), rx.text("Chờ duyệt", size="1"), align="center", spacing="1"), color_scheme="amber", variant="surface")),
        ("APPROVED", rx.badge(rx.hstack(rx.icon("circle-check", size=12), rx.text("Đã duyệt", size="1"), align="center", spacing="1"), color_scheme="green", variant="surface")),
        ("REJECTED", rx.badge(rx.hstack(rx.icon("circle-x", size=12), rx.text("Bị từ chối", size="1"), align="center", spacing="1"), color_scheme="red", variant="surface")),
        rx.badge(status, color_scheme="gray", variant="surface")
    )


# ─── 6. Wrappers ─────────────────────────────────────────────────────────────

def student_page_wrapper(content: rx.Component, active_route: str = "") -> rx.Component:
    return rx.box(
        student_navbar(active_route=active_route),
        acl_denied_dialog(),  # Hộp thoại cảnh báo 403 ACL Demo
        rx.container(
            content,
            size="4",
            padding_y="6",
            min_height="calc(100vh - 140px)",
        ),
        # Footer
        rx.box(
            rx.container(
                rx.hstack(
                    rx.text("© 2026 DocUni - Hệ thống Quản trị & Đóng góp Học liệu Số (Nhóm 3)", size="2", color="slate.9"),
                    rx.spacer(),
                    rx.text("Python Reflex Framework", size="1", color="slate.8", weight="bold"),
                    align="center",
                ),
                size="4",
                padding_y="4",
            ),
            border_t="1px solid var(--slate-4)",
            bg="white",
        ),
        bg="slate.1",
        min_height="100vh",
    )


def lecturer_page_wrapper(content: rx.Component, current_route: str = "") -> rx.Component:
    return rx.hstack(
        lecturer_sidebar(current_route=current_route),
        rx.box(
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.icon("graduation-cap", size=18, color="var(--indigo-10)"),
                        rx.text("Cổng Nghiệp Vụ Giảng Viên - Phê Duyệt & Phân Quyền Học Liệu", size="2", weight="bold", color="indigo.11"),
                        align="center",
                        spacing="2",
                    ),
                    rx.spacer(),
                    user_profile_switcher(),
                    align="center",
                    padding_x="6",
                    padding_y="3.5",
                    border_b="1px solid var(--slate-4)",
                    bg="white",
                ),
                rx.box(
                    content,
                    padding="6",
                ),
                width="100%",
                min_height="100vh",
                bg="slate.1",
            ),
            flex="1",
            min_width="0",
        ),
        spacing="0",
        min_height="100vh",
        bg="slate.1",
    )
