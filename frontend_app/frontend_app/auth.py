"""
DocUni - Trang Đăng nhập / Đăng ký / Đổi mật khẩu (Authentication)
Route: /login, /register
Framework: Reflex (Python Full-Stack)

Cung cấp giao diện xác thực người dùng: đăng nhập, đăng ký và đổi mật khẩu.
Tất cả form được validate phía frontend; tích hợp REST API Django backend.
"""

import re
import reflex as rx
from typing import Optional


# ─── Auth State ───────────────────────────────────────────────────────────────

class AuthState(rx.State):
    """Quản lý trạng thái đăng nhập / đăng ký."""

    # Login form
    login_username: str = ""
    login_password: str = ""
    login_error: str = ""
    login_loading: bool = False
    show_login_password: bool = False

    # Register form
    reg_full_name: str = ""
    reg_username: str = ""
    reg_email: str = ""
    reg_password: str = ""
    reg_confirm_password: str = ""
    reg_role: str = "STUDENT"
    reg_error: str = ""
    reg_loading: bool = False
    show_reg_password: bool = False

    # Session (mock – sẽ đồng bộ với Django session cookie)
    is_logged_in: bool = False
    current_user_name: str = ""
    current_user_role: str = ""

    # --- Login handlers ---
    def set_login_username(self, v: str):
        self.login_username = v
        self.login_error = ""

    def set_login_password(self, v: str):
        self.login_password = v
        self.login_error = ""

    def toggle_login_password(self):
        self.show_login_password = not self.show_login_password

    def login(self):
        if not self.login_username.strip():
            self.login_error = "Vui lòng nhập tên đăng nhập."
            return
        if not self.login_password:
            self.login_error = "Vui lòng nhập mật khẩu."
            return

        # Giả lập đăng nhập demo (frontend-only)
        # Khi kết nối backend, gọi: httpx.post("http://localhost:8000/auth/login/", ...)
        demo_accounts = {
            "admin": ("admin123", "ADMIN", "Quản trị viên"),
            "gv.nguyenan": ("gv123", "LECTURER", "TS. Nguyễn Văn An"),
            "sv.namle": ("sv123", "STUDENT", "Lê Hoàng Nam"),
        }

        if self.login_username in demo_accounts:
            pwd, role, name = demo_accounts[self.login_username]
            if self.login_password == pwd:
                self.is_logged_in = True
                self.current_user_name = name
                self.current_user_role = role
                self.login_error = ""
                return rx.redirect("/")
            else:
                self.login_error = "Mật khẩu không đúng. Vui lòng thử lại."
        else:
            self.login_error = "Tên đăng nhập không tồn tại trong hệ thống."

    def logout(self):
        self.is_logged_in = False
        self.current_user_name = ""
        self.current_user_role = ""
        self.login_username = ""
        self.login_password = ""
        return rx.redirect("/login")

    # --- Register handlers ---
    def set_reg_full_name(self, v: str):
        self.reg_full_name = v
        self.reg_error = ""

    def set_reg_username(self, v: str):
        self.reg_username = v
        self.reg_error = ""

    def set_reg_email(self, v: str):
        self.reg_email = v
        self.reg_error = ""

    def set_reg_password(self, v: str):
        self.reg_password = v
        self.reg_error = ""

    def set_reg_confirm_password(self, v: str):
        self.reg_confirm_password = v
        self.reg_error = ""

    def set_reg_role(self, v: str):
        self.reg_role = v

    def toggle_reg_password(self):
        self.show_reg_password = not self.show_reg_password

    def register(self):
        # Validation
        if not self.reg_full_name.strip():
            self.reg_error = "Họ tên không được để trống."
            return
        if len(self.reg_username.strip()) < 4:
            self.reg_error = "Tên đăng nhập phải có ít nhất 4 ký tự."
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.reg_email):
            self.reg_error = "Email không đúng định dạng (VD: name@example.com)."
            return
        if len(self.reg_password) < 6:
            self.reg_error = "Mật khẩu phải có ít nhất 6 ký tự."
            return
        if self.reg_password != self.reg_confirm_password:
            self.reg_error = "Xác nhận mật khẩu không khớp."
            return

        # Giả lập tạo tài khoản thành công (frontend-only demo)
        return rx.toast.success(
            f"Đã tạo tài khoản '{self.reg_username}' thành công! Vui lòng đăng nhập để tiếp tục."
        )


# ─── UI Helper Components ─────────────────────────────────────────────────────

def auth_input(placeholder: str, value: str, on_change, type_: str = "text",
               icon: str = "user", size: str = "3") -> rx.Component:
    """Input với icon slot dùng chung cho form auth."""
    return rx.input(
        rx.input.slot(rx.icon(icon, size=16, color="var(--slate-8)")),
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        type=type_,
        size=size,
        width="100%",
    )


def error_callout(message: str) -> rx.Component:
    return rx.callout.root(
        rx.callout.icon(rx.icon("circle-alert", size=15)),
        rx.callout.text(message),
        color="red",
        variant="surface",
        width="100%",
        size="2",
    )


# ─── Trang Đăng Nhập ─────────────────────────────────────────────────────────

def login_page() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                # Logo
                rx.center(
                    rx.vstack(
                        rx.box(
                            rx.icon("graduation-cap", size=32, color="white"),
                            bg="blue.9",
                            padding="3",
                            border_radius="xl",
                            box_shadow="md",
                        ),
                        rx.vstack(
                            rx.heading("DocUni", size="7", weight="bold", color="slate.12"),
                            rx.text("Cổng Học Liệu Thông Minh", size="2", color="blue.10", weight="bold"),
                            spacing="0",
                            align="center",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    width="100%",
                    padding_y="4",
                ),

                rx.divider(color_scheme="gray"),

                rx.vstack(
                    rx.heading("Đăng nhập", size="5", weight="bold", color="slate.12"),
                    rx.text("Nhập thông tin tài khoản của bạn để truy cập hệ thống", size="2", color="slate.9"),
                    spacing="1",
                    align="center",
                    width="100%",
                ),

                # Error message
                rx.cond(
                    AuthState.login_error != "",
                    error_callout(AuthState.login_error),
                    rx.fragment(),
                ),

                # Demo accounts info
                rx.callout.root(
                    rx.callout.icon(rx.icon("info", size=14)),
                    rx.callout.text(
                        rx.vstack(
                            rx.text("Tài khoản demo:", size="1", weight="bold"),
                            rx.text("admin / admin123 (Quản trị viên)", size="1"),
                            rx.text("gv.nguyenan / gv123 (Giảng viên)", size="1"),
                            rx.text("sv.namle / sv123 (Sinh viên)", size="1"),
                            spacing="0",
                        )
                    ),
                    color="blue",
                    variant="surface",
                    size="1",
                    width="100%",
                ),

                # Form fields
                rx.vstack(
                    rx.vstack(
                        rx.text("Tên đăng nhập", size="2", weight="bold", color="slate.11"),
                        auth_input(
                            "Nhập username...",
                            AuthState.login_username,
                            AuthState.set_login_username,
                            icon="user",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Mật khẩu", size="2", weight="bold", color="slate.11"),
                        rx.input(
                            rx.input.slot(rx.icon("lock", size=16, color="var(--slate-8)")),
                            placeholder="Nhập mật khẩu...",
                            value=AuthState.login_password,
                            on_change=AuthState.set_login_password,
                            type="password",
                            size="3",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),

                # Login button
                rx.button(
                    rx.icon("log-in", size=16),
                    "Đăng nhập",
                    size="3",
                    width="100%",
                    color_scheme="blue",
                    variant="solid",
                    loading=AuthState.login_loading,
                    on_click=AuthState.login,
                ),

                # Link register
                rx.hstack(
                    rx.text("Chưa có tài khoản?", size="2", color="slate.9"),
                    rx.link("Đăng ký ngay", href="/register", size="2", color="blue.10", weight="bold"),
                    justify="center",
                    spacing="1",
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),
            size="4",
            padding="6",
            max_width="440px",
            width="100%",
            box_shadow="xl",
        ),
        bg="slate.1",
        min_height="100vh",
        padding="4",
    )


# ─── Trang Đăng Ký ───────────────────────────────────────────────────────────

def register_page() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                # Logo
                rx.center(
                    rx.hstack(
                        rx.box(
                            rx.icon("graduation-cap", size=24, color="white"),
                            bg="blue.9",
                            padding="2",
                            border_radius="xl",
                        ),
                        rx.vstack(
                            rx.heading("DocUni", size="5", weight="bold", color="slate.12", line_height="1"),
                            rx.text("Cổng Học Liệu", size="1", color="blue.10", weight="bold"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    padding_y="3",
                    width="100%",
                ),

                rx.divider(color_scheme="gray"),

                rx.vstack(
                    rx.heading("Tạo tài khoản mới", size="5", weight="bold", color="slate.12"),
                    rx.text("Điền đầy đủ thông tin để đăng ký tài khoản học viên", size="2", color="slate.9"),
                    spacing="1",
                    align="center",
                    width="100%",
                ),

                # Error banner
                rx.cond(
                    AuthState.reg_error != "",
                    error_callout(AuthState.reg_error),
                    rx.fragment(),
                ),

                # Register form
                rx.vstack(
                    rx.grid(
                        rx.vstack(
                            rx.text("Họ và tên *", size="2", weight="bold", color="slate.11"),
                            auth_input(
                                "Nguyễn Văn A...",
                                AuthState.reg_full_name,
                                AuthState.set_reg_full_name,
                                icon="user",
                                size="2",
                            ),
                            spacing="1", width="100%",
                        ),
                        rx.vstack(
                            rx.text("Username *", size="2", weight="bold", color="slate.11"),
                            auth_input(
                                "VD: sv.nguyena...",
                                AuthState.reg_username,
                                AuthState.set_reg_username,
                                icon="at-sign",
                                size="2",
                            ),
                            spacing="1", width="100%",
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Email *", size="2", weight="bold", color="slate.11"),
                        auth_input(
                            "sv@vaa.edu.vn...",
                            AuthState.reg_email,
                            AuthState.set_reg_email,
                            icon="mail",
                            size="2",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Vai trò", size="2", weight="bold", color="slate.11"),
                        rx.select.root(
                            rx.select.trigger(width="100%", size="2"),
                            rx.select.content(
                                rx.select.item("Sinh viên", value="STUDENT"),
                                rx.select.item("Giảng viên", value="LECTURER"),
                            ),
                            value=AuthState.reg_role,
                            on_change=AuthState.set_reg_role,
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Mật khẩu *", size="2", weight="bold", color="slate.11"),
                            rx.input(
                                rx.input.slot(rx.icon("lock", size=14, color="var(--slate-8)")),
                                placeholder="Tối thiểu 6 ký tự...",
                                value=AuthState.reg_password,
                                on_change=AuthState.set_reg_password,
                                type="password",
                                size="2",
                                width="100%",
                            ),
                            spacing="1", width="100%",
                        ),
                        rx.vstack(
                            rx.text("Xác nhận mật khẩu *", size="2", weight="bold", color="slate.11"),
                            rx.input(
                                rx.input.slot(rx.icon("shield-check", size=14, color="var(--slate-8)")),
                                placeholder="Nhập lại mật khẩu...",
                                value=AuthState.reg_confirm_password,
                                on_change=AuthState.set_reg_confirm_password,
                                type="password",
                                size="2",
                                width="100%",
                            ),
                            spacing="1", width="100%",
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),

                # Submit
                rx.button(
                    rx.icon("user-plus", size=16),
                    "Tạo tài khoản",
                    size="3",
                    width="100%",
                    color_scheme="blue",
                    variant="solid",
                    loading=AuthState.reg_loading,
                    on_click=AuthState.register,
                ),

                # Link to login
                rx.hstack(
                    rx.text("Đã có tài khoản?", size="2", color="slate.9"),
                    rx.link("Đăng nhập", href="/login", size="2", color="blue.10", weight="bold"),
                    justify="center",
                    spacing="1",
                    width="100%",
                ),

                spacing="4",
                width="100%",
            ),
            size="4",
            padding="6",
            max_width="560px",
            width="100%",
            box_shadow="xl",
        ),
        bg="slate.1",
        min_height="100vh",
        padding="4",
    )

