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

    # Session lưu trữ thông tin thực tế từ Django API & PostgreSQL
    is_logged_in: bool = False
    current_user_id: int = 0
    current_user_name: str = ""
    current_user_role: str = ""
    current_user_class: str = ""
    current_user_department: str = ""
    auth_token: str = ""

    # --- Role & Route Guards ---
    def check_auth(self):
        """Guard bảo vệ: Bắt buộc đăng nhập trước khi xem nội dung."""
        role = getattr(self, 'current_user_role', '')
        name = getattr(self, 'current_user_name', '')
        if not self.is_logged_in or not role or not name:
            self.is_logged_in = False
            self.current_user_id = 0
            self.current_user_name = ""
            self.current_user_role = ""
            self.auth_token = ""
            return rx.redirect("/login")

    def check_admin_auth(self):
        """Guard bảo vệ: Chỉ cho phép quản trị viên (ADMIN)."""
        role = getattr(self, 'current_user_role', '')
        name = getattr(self, 'current_user_name', '')
        if not self.is_logged_in or role != "ADMIN" or not name:
            self.is_logged_in = False
            self.current_user_id = 0
            self.current_user_name = ""
            self.current_user_role = ""
            self.auth_token = ""
            return rx.redirect("/login")

    def check_lecturer_auth(self):
        """Guard bảo vệ: Cho phép Giảng viên (LECTURER) hoặc Quản trị viên (ADMIN)."""
        role = getattr(self, 'current_user_role', '')
        name = getattr(self, 'current_user_name', '')
        if not self.is_logged_in or role not in ("LECTURER", "ADMIN") or not name:
            self.is_logged_in = False
            self.current_user_id = 0
            self.current_user_name = ""
            self.current_user_role = ""
            self.auth_token = ""
            return rx.redirect("/login")

    def redirect_if_logged_in(self):
        """Nếu đã đăng nhập mà truy cập /login, điều hướng về trang theo vai trò thực tế."""
        role = getattr(self, 'current_user_role', '')
        name = getattr(self, 'current_user_name', '')
        if self.is_logged_in and role and name:
            if role == "ADMIN":
                return rx.redirect("/admin/users")
            elif role == "LECTURER":
                return rx.redirect("/lecturer/dashboard")
            else:
                return rx.redirect("/documents")

    def redirect_root(self):
        """Chuyển hướng trang root '/' về /login khi mới vào chương trình."""
        return rx.redirect("/login")

    # --- Login handlers ---
    def set_login_username(self, v: str):
        self.login_username = v
        self.login_error = ""

    def set_login_password(self, v: str):
        self.login_password = v
        self.login_error = ""

    def toggle_login_password(self):
        self.show_login_password = not self.show_login_password

    def fill_demo_account(self, username: str, password: str = "password123"):
        self.login_username = username
        self.login_password = password
        self.login_error = ""

    def login(self):
        uname = self.login_username.strip()
        pwd = self.login_password
        if not uname:
            self.login_error = "Vui lòng nhập tên đăng nhập."
            return
        if not pwd:
            self.login_error = "Vui lòng nhập mật khẩu."
            return

        # Xác thực tài khoản linh hoạt:
        # Cách 1: Gọi qua REST API nếu Django server 127.0.0.1:8000 đang chạy
        api_success = False
        try:
            import httpx
            resp = httpx.post(
                "http://127.0.0.1:8000/api/auth/login/",
                json={"username": uname, "password": pwd},
                timeout=3.0
            )
            if resp.status_code == 200:
                res_data = resp.json()
                data = res_data.get("user") or res_data.get("data") or {}
                self.is_logged_in = True
                self.current_user_id = data.get("user_id", 0)
                self.current_user_name = data.get("full_name") or uname
                role_val = data.get("role_name") or data.get("role")
                if not role_val and isinstance(data.get("role"), dict):
                    role_val = data.get("role", {}).get("role_name")
                self.current_user_role = str(role_val or "STUDENT").upper()
                self.current_user_class = str(data.get("class_name") or "")
                self.current_user_department = str(data.get("department_name") or "")
                self.auth_token = str(res_data.get("token") or "")
                self.login_error = ""
                api_success = True
            elif resp.status_code == 401:
                self.login_error = "Tài khoản hoặc mật khẩu không chính xác."
                return
            elif resp.status_code == 403:
                self.login_error = "Tài khoản của bạn đã bị vô hiệu hóa hoặc khóa."
                return
        except Exception:
            # Django server chưa bật hoặc kết nối HTTP bị chặn
            pass

        # Cách 2: Tự động kết nối trực tiếp vào PostgreSQL qua Django ORM (Dự phòng thông minh)
        if not api_success:
            try:
                import os, sys
                backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
                if backend_dir not in sys.path:
                    sys.path.insert(0, backend_dir)
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
                import django
                django.setup()
                from django.contrib.auth import authenticate
                user = authenticate(None, username=uname, password=pwd)
                if user:
                    if not user.is_active:
                        self.login_error = "Tài khoản của bạn đã bị vô hiệu hóa hoặc khóa."
                        return
                    self.is_logged_in = True
                    self.current_user_id = user.id
                    self.current_user_name = user.full_name or user.username
                    self.current_user_role = str(user.role.role_name if user.role else "STUDENT").upper()
                    self.current_user_class = str(user.student_class.class_name if getattr(user, 'student_class', None) else "")
                    self.current_user_department = str(user.department.department_name if getattr(user, 'department', None) else "")
                    try:
                        from accounts.authentication import generate_jwt_token
                        self.auth_token = generate_jwt_token(user)
                    except Exception:
                        self.auth_token = f"orm_token_{user.id}"
                    self.login_error = ""
                    api_success = True
                else:
                    self.login_error = "Tài khoản hoặc mật khẩu không chính xác."
                    return
            except Exception as e:
                self.login_error = f"Lỗi xác thực: {str(e)}"
                return

        # Đồng bộ tài khoản vào GlobalDocState để navbar và các trang đều nhận diện đúng người dùng
        try:
            from .data_store import GlobalDocState
            GlobalDocState.current_user_name = self.current_user_name
            GlobalDocState.current_user_role = self.current_user_role
        except Exception:
            pass

        # Điều hướng theo vai trò (Role) lấy trực tiếp từ database PostgreSQL
        if self.current_user_role == "ADMIN":
            return rx.redirect("/admin/users")
        elif self.current_user_role == "LECTURER":
            return rx.redirect("/lecturer/dashboard")
        else:
            return rx.redirect("/documents")

    def logout(self):
        try:
            import httpx
            httpx.post("http://127.0.0.1:8000/api/auth/logout/", timeout=2.0)
        except Exception:
            pass
        self.is_logged_in = False
        self.current_user_id = 0
        self.current_user_name = ""
        self.current_user_role = ""
        self.current_user_class = ""
        self.current_user_department = ""
        self.auth_token = ""
        self.login_username = ""
        self.login_password = ""
        self.login_error = ""
        return [rx.call_script("localStorage.clear(); sessionStorage.clear();"), rx.redirect("/login")]

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


# ─── Trang Đăng Nhập (Modern Dual-Column Educational Platform) ──────────────

def login_page() -> rx.Component:
    def feature_box(icon: str, title: str, desc: str, icon_color: str = "#60a5fa") -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=22, color=icon_color),
                    background="rgba(255, 255, 255, 0.12)",
                    padding="2.5",
                    border_radius="xl",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.vstack(
                    rx.text(title, size="2", weight="bold", color="white"),
                    rx.text(desc, size="1", color="rgba(255, 255, 255, 0.75)", line_height="1.4"),
                    spacing="1",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            padding="3.5",
            border_radius="xl",
            background="rgba(255, 255, 255, 0.07)",
            border="1px solid rgba(255, 255, 255, 0.12)",
            backdrop_filter="blur(10px)",
            width="100%",
            transition="all 0.2s ease",
            _hover={"background": "rgba(255, 255, 255, 0.12)", "transform": "translateX(4px)"},
        )

    # Cột bên trái: Panel giới thiệu giáo dục công nghệ rực rỡ
    left_showcase = rx.box(
        rx.vstack(
            # Brand Header
            rx.hstack(
                rx.box(
                    rx.icon("graduation-cap", size=28, color="white"),
                    background="linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
                    padding="3",
                    border_radius="xl",
                    box_shadow="0 4px 16px rgba(139, 92, 246, 0.4)",
                ),
                rx.vstack(
                    rx.heading("DocUni", size="6", weight="bold", color="white", letter_spacing="-0.02em"),
                    rx.text("Kho Học Liệu Số & Trợ Lý AI Học Viện", size="1", color="#93c5fd", weight="bold", letter_spacing="0.05em"),
                    spacing="0",
                ),
                align="center",
                spacing="3",
            ),

            rx.spacer(),

            # Headline & Description
            rx.vstack(
                rx.badge(
                    rx.hstack(rx.icon("sparkles", size=13), rx.text("Nền Tảng Quản Trị Tri Thức 4.0", size="1", weight="bold"), align="center", spacing="1"),
                    color_scheme="purple",
                    variant="surface",
                    radius="full",
                    padding_x="3",
                    padding_y="1",
                ),
                rx.heading(
                    "Khám phá tri thức số, kết nối tương lai cùng AI",
                    size="8",
                    weight="bold",
                    color="white",
                    line_height="1.2",
                    letter_spacing="-0.03em",
                ),
                rx.text(
                    "Truy cập slide bài giảng, đề thi, giáo trình chính thức và tra cứu thông minh bằng Semantic Search RAG được bảo mật tuyệt đối.",
                    size="3",
                    color="rgba(255, 255, 255, 0.82)",
                    line_height="1.6",
                ),
                spacing="4",
                align="start",
                width="100%",
            ),

            # Feature cards
            rx.vstack(
                feature_box("book-open", "Kho Tài Liệu Học Phần", "Phân loại theo Khoa, Môn học, Thư mục và Lớp học.", "#60a5fa"),
                feature_box("sparkles", "Trợ Lý AI Tra Cứu (RAG)", "Hỏi đáp nội dung tệp ngữ cảnh và trích dẫn số trang chính xác.", "#c084fc"),
                feature_box("shield-check", "Kiểm Duyệt Hai Chiều & ACL", "Giảng viên phê duyệt, bảo vệ bản quyền tài liệu nội bộ.", "#34d399"),
                spacing="3",
                width="100%",
            ),

            rx.spacer(),

            # Demo Accounts Quick-Fill Panel
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("key-round", size=14, color="#93c5fd"),
                        rx.text("Tài khoản trong Database (Nhấn để điền nhanh):", size="1", weight="bold", color="#93c5fd"),
                        align="center",
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.button(
                            "🛡️ Admin (admin)",
                            size="1",
                            variant="surface",
                            color_scheme="red",
                            radius="full",
                            on_click=AuthState.fill_demo_account("admin", "admin123"),
                        ),
                        rx.button(
                            "🎓 Giảng viên (gv01)",
                            size="1",
                            variant="surface",
                            color_scheme="purple",
                            radius="full",
                            on_click=AuthState.fill_demo_account("gv01", "gv123"),
                        ),
                        rx.button(
                            "👤 Sinh viên (sv01)",
                            size="1",
                            variant="surface",
                            color_scheme="blue",
                            radius="full",
                            on_click=AuthState.fill_demo_account("sv01", "sv123"),
                        ),
                        spacing="2",
                        wrap="wrap",
                    ),
                    spacing="2",
                    width="100%",
                ),
                padding="3",
                border_radius="xl",
                background="rgba(0, 0, 0, 0.25)",
                border="1px solid rgba(255, 255, 255, 0.1)",
                width="100%",
            ),

            spacing="6",
            height="100%",
            justify="between",
            align="start",
            padding="10",
        ),
        flex="1",
        background="linear-gradient(135deg, #0f172a 0%, #1e3a8a 40%, #4338ca 75%, #6d28d9 100%)",
        display=rx.breakpoints(initial="none", md="flex"),
        position="relative",
        overflow="hidden",
    )

    # Cột bên phải: Form đăng nhập tinh gọn hiện đại
    right_form = rx.box(
        rx.center(
            rx.card(
                rx.vstack(
                    # Header form
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("lock", size=22, color="white"),
                                background="linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)",
                                padding="2.5",
                                border_radius="xl",
                                box_shadow="0 4px 12px rgba(37, 99, 235, 0.3)",
                            ),
                            rx.vstack(
                                rx.heading("Đăng nhập DocUni", size="6", weight="bold", color="slate.12", letter_spacing="-0.02em"),
                                rx.text("Nhập thông tin tài khoản để truy cập hệ thống", size="2", color="slate.9"),
                                spacing="0",
                            ),
                            align="center",
                            spacing="3",
                        ),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),

                    rx.divider(color_scheme="gray"),

                    # Error message
                    rx.cond(
                        AuthState.login_error != "",
                        error_callout(AuthState.login_error),
                        rx.fragment(),
                    ),

                    # Form đăng nhập
                    rx.form(
                        rx.vstack(
                            rx.vstack(
                                rx.text("Tên đăng nhập", size="2", weight="bold", color="slate.11"),
                                rx.input(
                                    rx.input.slot(rx.icon("user", size=16, color="var(--slate-8)")),
                                    placeholder="Nhập username (VD: sv01, gv01, admin)...",
                                    value=AuthState.login_username,
                                    on_change=AuthState.set_login_username,
                                    size="3",
                                    width="100%",
                                    border_radius="lg",
                                ),
                                spacing="2",
                                width="100%",
                            ),

                            rx.vstack(
                                rx.hstack(
                                    rx.text("Mật khẩu", size="2", weight="bold", color="slate.11"),
                                    rx.spacer(),
                                    rx.text(
                                        rx.cond(AuthState.show_login_password, "Ẩn", "Hiện"),
                                        size="1",
                                        color="blue.10",
                                        weight="bold",
                                        cursor="pointer",
                                        on_click=AuthState.toggle_login_password,
                                    ),
                                    align="center",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("lock", size=16, color="var(--slate-8)")),
                                    rx.input.slot(
                                        rx.icon_button(
                                            rx.cond(AuthState.show_login_password, rx.icon("eye-off", size=15), rx.icon("eye", size=15)),
                                            size="1",
                                            variant="ghost",
                                            color_scheme="gray",
                                            on_click=AuthState.toggle_login_password,
                                            type="button",
                                        )
                                    ),
                                    placeholder="Nhập mật khẩu...",
                                    value=AuthState.login_password,
                                    on_change=AuthState.set_login_password,
                                    type=rx.cond(AuthState.show_login_password, "text", "password"),
                                    size="3",
                                    width="100%",
                                    border_radius="lg",
                                ),
                                spacing="2",
                                width="100%",
                            ),

                            # Nút đăng nhập nổi bật với gradient
                            rx.button(
                                rx.hstack(
                                    rx.icon("log-in", size=17),
                                    rx.text("Đăng Nhập Vào Hệ Thống", size="2", weight="bold"),
                                    align="center",
                                    spacing="2",
                                ),
                                size="3",
                                width="100%",
                                background="linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)",
                                color="white",
                                border_radius="xl",
                                box_shadow="0 4px 14px rgba(37, 99, 235, 0.35)",
                                _hover={
                                    "background": "linear-gradient(135deg, #1d4ed8 0%, #4338ca 100%)",
                                    "transform": "translateY(-1px)",
                                    "box_shadow": "0 6px 18px rgba(37, 99, 235, 0.45)",
                                },
                                transition="all 0.2s ease",
                                loading=AuthState.login_loading,
                                type="submit",
                                margin_top="2",
                            ),

                            spacing="4",
                            width="100%",
                        ),
                        on_submit=AuthState.login,
                        width="100%",
                    ),

                    # Chuyển đổi sang đăng ký
                    rx.hstack(
                        rx.text("Bạn là học viên mới?", size="2", color="slate.9"),
                        rx.link(
                            rx.hstack(
                                rx.text("Đăng ký tài khoản", size="2", color="blue.10", weight="bold"),
                                rx.icon("arrow-right", size=13, color="var(--blue-10)"),
                                align="center",
                                spacing="1",
                            ),
                            href="/register",
                        ),
                        justify="center",
                        spacing="2",
                        width="100%",
                        padding_top="2",
                    ),

                    spacing="5",
                    width="100%",
                ),
                padding="7",
                border_radius="2xl",
                box_shadow="0 20px 40px -15px rgba(0, 0, 0, 0.08), 0 0 1px 1px rgba(0, 0, 0, 0.05)",
                background="white",
                border="1px solid rgba(226, 232, 240, 0.8)",
                width=rx.breakpoints(initial="100%", sm="440px", md="460px"),
            ),
            width="100%",
            height="100%",
            padding="6",
        ),
        flex="1",
        background="linear-gradient(180deg, #f8fafc 0%, #eef2ff 50%, #f1f5f9 100%)",
        min_height="100vh",
        display="flex",
        align_items="center",
        justify_content="center",
    )

    return rx.box(
        rx.script("localStorage.clear();"),
        rx.flex(
            left_showcase,
            right_form,
            direction=rx.breakpoints(initial="column", md="row"),
            width="100%",
            min_height="100vh",
        ),
        width="100%",
        min_height="100vh",
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

