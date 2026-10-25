"""
DocUni - Common UI Components (Reflex Framework)
Cung cấp các component dùng chung: Navbar sinh viên, Sidebar giảng viên, KPI Card, Badge trạng thái và Khung trang chuẩn.
"""

import reflex as rx
from frontend_app.auth import AuthState

# 1. Navbar Sinh Viên Dùng Chung
def student_navbar(active_route: str = "") -> rx.Component:
    def nav_item(text: str, href: str, icon: str, is_active: bool = False) -> rx.Component:
        return rx.link(
            rx.hstack(
                rx.icon(icon, size=16),
                rx.text(text, size="2", weight="medium"),
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
                            rx.text("Cổng Học Tập", size="1", color="blue.10", weight="bold"),
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

                # Right action & user profile
                rx.cond(
                    AuthState.is_logged_in,
                    rx.hstack(
                        rx.cond(
                            (AuthState.current_user_role == "LECTURER") | (AuthState.current_user_role == "ADMIN"),
                            rx.link(
                                rx.button(
                                    rx.icon("user-cog", size=15),
                                    "Cổng Giảng viên",
                                    size="2",
                                    variant="surface",
                                    color_scheme="indigo",
                                ),
                                href="/lecturer/dashboard",
                            ),
                        ),
                        rx.cond(
                            AuthState.current_user_role == "ADMIN",
                            rx.link(
                                rx.button(
                                    rx.icon("shield", size=15),
                                    "Admin",
                                    size="2",
                                    variant="ghost",
                                    color_scheme="gray",
                                ),
                                href="/admin/users",
                            ),
                        ),
                        rx.hstack(
                            rx.avatar(fallback="US", size="2", radius="full", color_scheme="blue"),
                            rx.vstack(
                                rx.text(AuthState.current_user_name, size="2", weight="bold", color="slate.12"),
                                rx.badge(AuthState.current_user_role, size="1", color_scheme="blue", variant="surface"),
                                spacing="0",
                                align="start",
                            ),
                            align="center",
                            spacing="2",
                        ),
                        rx.button(
                            rx.icon("log-out", size=15),
                            "Đăng xuất",
                            size="2",
                            variant="ghost",
                            color_scheme="red",
                            on_click=AuthState.logout,
                        ),
                        align="center",
                        spacing="3",
                    ),
                    rx.hstack(
                        rx.link(
                            rx.button(
                                rx.icon("log-in", size=15),
                                "Đăng nhập",
                                size="2",
                                variant="solid",
                                color_scheme="blue",
                            ),
                            href="/login",
                        ),
                        align="center",
                    )
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


# 2. Sidebar Giảng Viên Dùng Chung
def lecturer_sidebar(current_route: str = "") -> rx.Component:
    def sidebar_item(title: str, href: str, icon: str, is_active: bool = False, badge: str = "") -> rx.Component:
        return rx.link(
            rx.hstack(
                rx.icon(icon, size=18, color=rx.cond(is_active, "var(--indigo-10)", "var(--slate-9)")),
                rx.text(title, size="2", weight=rx.cond(is_active, "bold", "medium")),
                rx.spacer(),
                rx.cond(
                    badge != "",
                    rx.badge(badge, color_scheme="indigo", variant="surface", size="1"),
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

            # Lecturer Info Card
            rx.box(
                rx.hstack(
                    rx.avatar(fallback="GV", size="2", radius="full", color_scheme="indigo"),
                    rx.vstack(
                        rx.text(AuthState.current_user_name, size="2", weight="bold", color="slate.12"),
                        rx.badge(AuthState.current_user_role, size="1", color_scheme="indigo", variant="surface"),
                        spacing="0",
                        align="start",
                    ),
                    align="center",
                    spacing="2",
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
                sidebar_item("Kiểm duyệt tài liệu", "/lecturer/approval", "clipboard-check", current_route == "/lecturer/approval", badge="Chờ duyệt"),
                spacing="2",
                width="100%",
            ),

            rx.spacer(),

            rx.divider(color_scheme="gray", margin_y="3"),

            # External / Role Switch Shortcuts
            rx.vstack(
                rx.link(
                    rx.hstack(
                        rx.icon("external-link", size=15, color="var(--slate-9)"),
                        rx.text("Xem Cổng Sinh viên", size="2", color="slate.10"),
                        align="center",
                        spacing="2",
                        padding="2",
                    ),
                    href="/",
                    underline="none",
                ),
                rx.link(
                    rx.hstack(
                        rx.icon("users-round", size=15, color="var(--slate-9)"),
                        rx.text("Cổng Quản trị Admin", size="2", color="slate.10"),
                        align="center",
                        spacing="2",
                        padding="2",
                    ),
                    href="/admin/users",
                    underline="none",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("log-out", size=15, color="var(--red-9)"),
                        rx.text("Đăng xuất", size="2", color="red.10"),
                        align="center",
                        spacing="2",
                    ),
                    variant="ghost",
                    on_click=AuthState.logout,
                    width="100%",
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


# 3. KPI Card Dùng Chung
def kpi_card(title: str, value: str, icon: str, color_scheme: str = "blue", description: str = "") -> rx.Component:
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


# 4. Status Badge Dùng Chung
def status_badge(status: str) -> rx.Component:
    return rx.match(
        status,
        ("PENDING", rx.badge(rx.hstack(rx.icon("clock", size=12), rx.text("Chờ duyệt", size="1"), align="center", spacing="1"), color_scheme="amber", variant="surface")),
        ("APPROVED", rx.badge(rx.hstack(rx.icon("circle-check", size=12), rx.text("Đã duyệt", size="1"), align="center", spacing="1"), color_scheme="green", variant="surface")),
        ("REJECTED", rx.badge(rx.hstack(rx.icon("circle-x", size=12), rx.text("Bị từ chối", size="1"), align="center", spacing="1"), color_scheme="red", variant="surface")),
        rx.badge(status, color_scheme="gray", variant="surface")
    )


# 5. Wrapper Cho Trang Sinh Viên
def student_page_wrapper(content: rx.Component, active_route: str = "") -> rx.Component:
    return rx.box(
        student_navbar(active_route=active_route),
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
                    rx.text("© 2026 DocUni - Hệ thống Quản trị & Đóng góp Tài liệu Học tập Học Viện Hàng Không", size="2", color="slate.9"),
                    rx.spacer(),
                    rx.text("Python Reflex Full-Stack Web", size="1", color="slate.8", weight="bold"),
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


# 6. Wrapper Cho Trang Giảng Viên
def lecturer_page_wrapper(content: rx.Component, current_route: str = "") -> rx.Component:
    return rx.hstack(
        lecturer_sidebar(current_route=current_route),
        rx.box(
            rx.box(
                # Top header nhỏ gọn
                rx.hstack(
                    rx.hstack(
                        rx.icon("graduation-cap", size=18, color="var(--indigo-10)"),
                        rx.text("Cổng Nghiệp Vụ Giảng Viên", size="2", weight="bold", color="indigo.11"),
                        align="center",
                        spacing="2",
                    ),
                    rx.spacer(),
                    rx.badge("Học kỳ 1 - 2026", color_scheme="indigo", variant="surface"),
                    align="center",
                    padding_x="6",
                    padding_y="3.5",
                    border_b="1px solid var(--slate-4)",
                    bg="white",
                ),
                # Main content container
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
