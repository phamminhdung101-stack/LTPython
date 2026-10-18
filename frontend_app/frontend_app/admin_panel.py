"""
DocUni - Trang Quản Trị Admin (Admin Panel)
Routes: /admin/users, /admin/departments, /admin/subjects, /admin/classes
Framework: Reflex (Python Full-Stack)

Cung cấp giao diện quản trị đầy đủ cho Admin:
- Quản lý người dùng: CRUD, phân quyền, khóa/mở tài khoản
- Quản lý tổ chức: Khoa, Môn học, Lớp học
"""

import dataclasses
from datetime import datetime
from typing import List, Optional
import reflex as rx
from .common_components import status_badge


# ─── Dataclass Models ─────────────────────────────────────────────────────────

@dataclasses.dataclass
class AdminUser:
    id: str = ""
    full_name: str = ""
    username: str = ""
    email: str = ""
    role: str = "STUDENT"          # "ADMIN", "LECTURER", "STUDENT"
    department: str = ""
    student_class: str = ""
    is_active: bool = True
    created_at: str = ""
    avatar_fallback: str = "SV"


# ─── Mock Data (sẽ thay bằng API call) ───────────────────────────────────────

MOCK_USERS: List[AdminUser] = [
    AdminUser("u1", "Quản trị viên hệ thống", "admin", "admin@docuni.edu.vn", "ADMIN", "CNTT", "", True, "2026-01-01", "AD"),
    AdminUser("u2", "TS. Nguyễn Văn An", "gv.nguyenan", "nguyenan@docuni.edu.vn", "LECTURER", "CNTT", "", True, "2026-01-05", "NA"),
    AdminUser("u3", "ThS. Lê Thị Bình", "gv.lethib", "lethib@docuni.edu.vn", "LECTURER", "KT", "", True, "2026-01-06", "LB"),
    AdminUser("u4", "Lê Hoàng Nam", "sv.namle", "namle@vaa.edu.vn", "STUDENT", "CNTT", "D21CQCN01-B", True, "2026-09-01", "LN"),
    AdminUser("u5", "Trần Thị Mai", "sv.tranm", "tranm@vaa.edu.vn", "STUDENT", "KT", "D21CQKT01-B", True, "2026-09-01", "TM"),
    AdminUser("u6", "Phạm Minh Đức", "sv.phamd", "phamd@vaa.edu.vn", "STUDENT", "CNTT", "D22CQCN01-B", False, "2026-09-02", "PD"),
    AdminUser("u7", "Nguyễn Thị Hoa", "sv.nguyen_hoa", "nguyen_hoa@vaa.edu.vn", "STUDENT", "NN", "D21CQNN01-B", True, "2026-09-03", "NH"),
    AdminUser("u8", "ThS. Trần Quang Huy", "gv.tranhuy", "tranhuy@docuni.edu.vn", "LECTURER", "DHB", "", True, "2026-01-07", "TH"),
]

ROLE_OPTIONS = ["ADMIN", "LECTURER", "STUDENT"]
DEPARTMENT_OPTIONS = ["CNTT", "KT", "NN", "DHB"]
STATUS_OPTIONS = ["ACTIVE", "INACTIVE"]


# ─── Admin User State ─────────────────────────────────────────────────────────

class AdminUserState(rx.State):
    """Quản lý trang Quản lý người dùng."""

    users: List[AdminUser] = MOCK_USERS
    search_query: str = ""
    filter_role: str = "ALL"
    filter_dept: str = "ALL"
    filter_status: str = "ALL"

    # Modal: Create / Edit
    show_user_modal: bool = False
    is_create_mode: bool = True
    modal_user_id: str = ""
    form_full_name: str = ""
    form_username: str = ""
    form_email: str = ""
    form_password: str = ""
    form_role: str = "STUDENT"
    form_dept: str = "CNTT"
    form_class: str = ""
    form_active: bool = True
    form_error: str = ""

    # Modal: Delete confirm
    show_delete_dialog: bool = False
    delete_user_id: str = ""
    delete_user_name: str = ""

    # Modal: View detail
    show_detail_modal: bool = False
    detail_user: AdminUser = AdminUser()

    # ── Computed vars ──
    @rx.var
    def filtered_users(self) -> List[AdminUser]:
        result = self.users
        q = self.search_query.strip().lower()
        if q:
            result = [u for u in result if q in u.full_name.lower() or q in u.username.lower() or q in u.email.lower()]
        if self.filter_role != "ALL":
            result = [u for u in result if u.role == self.filter_role]
        if self.filter_dept != "ALL":
            result = [u for u in result if u.department == self.filter_dept]
        if self.filter_status == "ACTIVE":
            result = [u for u in result if u.is_active]
        elif self.filter_status == "INACTIVE":
            result = [u for u in result if not u.is_active]
        return result

    @rx.var
    def total_users(self) -> int:
        return len(self.users)

    @rx.var
    def active_users(self) -> int:
        return sum(1 for u in self.users if u.is_active)

    @rx.var
    def admin_count(self) -> int:
        return sum(1 for u in self.users if u.role == "ADMIN")

    @rx.var
    def lecturer_count(self) -> int:
        return sum(1 for u in self.users if u.role == "LECTURER")

    @rx.var
    def student_count(self) -> int:
        return sum(1 for u in self.users if u.role == "STUDENT")

    # ── Search & Filter ──
    def set_search_query(self, v: str):
        self.search_query = v

    def set_filter_role(self, v: str):
        self.filter_role = v

    def set_filter_dept(self, v: str):
        self.filter_dept = v

    def set_filter_status(self, v: str):
        self.filter_status = v

    def reset_filters(self):
        self.search_query = ""
        self.filter_role = "ALL"
        self.filter_dept = "ALL"
        self.filter_status = "ALL"

    # ── Create Modal ──
    def open_create_modal(self):
        self.is_create_mode = True
        self.modal_user_id = ""
        self.form_full_name = ""
        self.form_username = ""
        self.form_email = ""
        self.form_password = ""
        self.form_role = "STUDENT"
        self.form_dept = "CNTT"
        self.form_class = ""
        self.form_active = True
        self.form_error = ""
        self.show_user_modal = True

    # ── Edit Modal ──
    def open_edit_modal(self, user: AdminUser):
        self.is_create_mode = False
        self.modal_user_id = user.id
        self.form_full_name = user.full_name
        self.form_username = user.username
        self.form_email = user.email
        self.form_password = ""
        self.form_role = user.role
        self.form_dept = user.department
        self.form_class = user.student_class
        self.form_active = user.is_active
        self.form_error = ""
        self.show_user_modal = True

    def close_user_modal(self):
        self.show_user_modal = False
        self.form_error = ""

    # Form setters
    def set_form_full_name(self, v: str):
        self.form_full_name = v
        self.form_error = ""

    def set_form_username(self, v: str):
        self.form_username = v
        self.form_error = ""

    def set_form_email(self, v: str):
        self.form_email = v
        self.form_error = ""

    def set_form_password(self, v: str):
        self.form_password = v

    def set_form_role(self, v: str):
        self.form_role = v

    def set_form_dept(self, v: str):
        self.form_dept = v

    def set_form_class(self, v: str):
        self.form_class = v

    def toggle_form_active(self, v: bool):
        self.form_active = v

    def save_user(self):
        # Basic validation
        if not self.form_full_name.strip():
            self.form_error = "Họ tên không được để trống."
            return
        if not self.form_username.strip():
            self.form_error = "Username không được để trống."
            return
        if self.form_email and "@" not in self.form_email:
            self.form_error = "Email không đúng định dạng."
            return

        if self.is_create_mode:
            if not self.form_password:
                self.form_error = "Mật khẩu không được để trống khi tạo mới."
                return
            # Check duplicate username
            existing = [u for u in self.users if u.username == self.form_username.strip()]
            if existing:
                self.form_error = f"Username '{self.form_username}' đã tồn tại."
                return
            new_user = AdminUser(
                id=f"u{len(self.users) + 1}",
                full_name=self.form_full_name.strip(),
                username=self.form_username.strip(),
                email=self.form_email.strip(),
                role=self.form_role,
                department=self.form_dept,
                student_class=self.form_class,
                is_active=self.form_active,
                created_at=datetime.now().strftime("%Y-%m-%d"),
                avatar_fallback=self.form_full_name.strip()[:2].upper(),
            )
            self.users.insert(0, new_user)
            self.show_user_modal = False
            return rx.toast.success(f"Đã thêm người dùng '{self.form_full_name}' thành công!")
        else:
            updated = []
            for u in self.users:
                if u.id == self.modal_user_id:
                    u.full_name = self.form_full_name.strip()
                    u.email = self.form_email.strip()
                    u.role = self.form_role
                    u.department = self.form_dept
                    u.student_class = self.form_class
                    u.is_active = self.form_active
                    u.avatar_fallback = self.form_full_name.strip()[:2].upper()
                updated.append(u)
            self.users = updated
            self.show_user_modal = False
            return rx.toast.success(f"Đã cập nhật thông tin người dùng '{self.form_full_name}' thành công!")

    # ── Toggle Account Status ──
    def toggle_user_status(self, user_id: str):
        updated = []
        action = ""
        for u in self.users:
            if u.id == user_id:
                u.is_active = not u.is_active
                action = "Đã mở khóa" if u.is_active else "Đã khóa"
                name = u.full_name
            updated.append(u)
        self.users = updated
        return rx.toast.info(f"{action} tài khoản '{name}' thành công.")

    # ── Delete ──
    def open_delete_dialog(self, user_id: str, user_name: str):
        self.delete_user_id = user_id
        self.delete_user_name = user_name
        self.show_delete_dialog = True

    def cancel_delete(self):
        self.show_delete_dialog = False
        self.delete_user_id = ""

    def confirm_delete(self):
        name = self.delete_user_name
        self.users = [u for u in self.users if u.id != self.delete_user_id]
        self.show_delete_dialog = False
        self.delete_user_id = ""
        return rx.toast.success(f"Đã xóa người dùng '{name}' thành công!")

    # ── View Detail ──
    def open_detail(self, user: AdminUser):
        self.detail_user = user
        self.show_detail_modal = True

    def close_detail(self):
        self.show_detail_modal = False


# ─── UI Helpers ───────────────────────────────────────────────────────────────

def role_badge(role: str) -> rx.Component:
    return rx.match(
        role,
        ("ADMIN", rx.badge(rx.icon("shield", size=11), "Admin", color_scheme="red", variant="solid", size="1")),
        ("LECTURER", rx.badge(rx.icon("graduation-cap", size=11), "Giảng viên", color_scheme="indigo", variant="surface", size="1")),
        ("STUDENT", rx.badge(rx.icon("user", size=11), "Sinh viên", color_scheme="blue", variant="surface", size="1")),
        rx.badge(role, color_scheme="gray", variant="surface", size="1"),
    )


def status_badge_bool(is_active: bool) -> rx.Component:
    return rx.cond(
        is_active,
        rx.badge(rx.icon("circle-check", size=11), "Hoạt động", color_scheme="green", variant="surface", size="1"),
        rx.badge(rx.icon("circle-x", size=11), "Đã khóa", color_scheme="red", variant="surface", size="1"),
    )


def kpi_box(title: str, value: str, icon: str, color: str = "blue") -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=22, color=f"var(--{color}-10)"),
                bg=f"var(--{color}-3)",
                padding="3",
                border_radius="xl",
            ),
            rx.vstack(
                rx.text(title, size="1", color="slate.9", weight="medium"),
                rx.heading(value, size="6", weight="bold", color="slate.12"),
                spacing="0",
            ),
            align="center",
            spacing="3",
        ),
        variant="surface",
        size="2",
    )


def user_table_row(user: AdminUser) -> rx.Component:
    return rx.table.row(
        # Avatar + tên
        rx.table.cell(
            rx.hstack(
                rx.avatar(fallback=user.avatar_fallback, size="2", radius="full", color_scheme="blue"),
                rx.vstack(
                    rx.text(user.full_name, size="2", weight="bold", color="slate.12"),
                    rx.text(user.username, size="1", color="slate.8"),
                    spacing="0",
                ),
                align="center",
                spacing="2",
            ),
        ),
        # Email
        rx.table.cell(rx.text(user.email, size="2", color="slate.10")),
        # Role
        rx.table.cell(role_badge(user.role)),
        # Khoa
        rx.table.cell(
            rx.cond(
                user.department != "",
                rx.badge(user.department, color_scheme="gray", variant="surface", size="1"),
                rx.text("—", color="slate.7", size="2"),
            )
        ),
        # Lớp
        rx.table.cell(
            rx.cond(
                user.student_class != "",
                rx.text(user.student_class, size="1", color="slate.9"),
                rx.text("—", color="slate.7", size="2"),
            )
        ),
        # Trạng thái
        rx.table.cell(status_badge_bool(user.is_active)),
        # Ngày tạo
        rx.table.cell(rx.text(user.created_at, size="1", color="slate.8")),
        # Thao tác
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=13),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    on_click=AdminUserState.open_detail(user),
                ),
                rx.button(
                    rx.icon("pencil", size=13),
                    size="1",
                    variant="surface",
                    color_scheme="blue",
                    on_click=AdminUserState.open_edit_modal(user),
                ),
                rx.button(
                    rx.cond(user.is_active, rx.icon("lock", size=13), rx.icon("lock-open", size=13)),
                    size="1",
                    variant="surface",
                    color_scheme=rx.cond(user.is_active, "amber", "green"),
                    on_click=AdminUserState.toggle_user_status(user.id),
                ),
                rx.button(
                    rx.icon("trash-2", size=13),
                    size="1",
                    variant="ghost",
                    color_scheme="red",
                    on_click=AdminUserState.open_delete_dialog(user.id, user.full_name),
                ),
                align="center",
                spacing="1",
            ),
        ),
    )


def user_form_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.box(
                        rx.icon("user-cog", size=20, color="var(--blue-9)"),
                        bg="blue.3",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.heading(
                            rx.cond(AdminUserState.is_create_mode, "Thêm người dùng mới", "Chỉnh sửa thông tin"),
                            size="4", weight="bold", color="slate.12",
                        ),
                        rx.text("Điền đầy đủ thông tin bắt buộc (*)", size="2", color="slate.9"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(rx.icon("x", size=16), variant="ghost", color_scheme="gray", size="1"),
                    ),
                    align="center", width="100%",
                ),
                rx.divider(color_scheme="gray"),

                # Error
                rx.cond(
                    AdminUserState.form_error != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle-alert", size=14)),
                        rx.callout.text(AdminUserState.form_error),
                        color="red", variant="surface", size="1", width="100%",
                    ),
                    rx.fragment(),
                ),

                # Họ tên & Username
                rx.grid(
                    rx.vstack(
                        rx.text("Họ và tên *", size="2", weight="bold", color="slate.11"),
                        rx.input(
                            placeholder="Nguyễn Văn A...",
                            value=AdminUserState.form_full_name,
                            on_change=AdminUserState.set_form_full_name,
                            size="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Username *", size="2", weight="bold", color="slate.11"),
                        rx.input(
                            placeholder="sv.nguyena...",
                            value=AdminUserState.form_username,
                            on_change=AdminUserState.set_form_username,
                            size="2", width="100%",
                            disabled=~AdminUserState.is_create_mode,
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),

                # Email & Password
                rx.grid(
                    rx.vstack(
                        rx.text("Email", size="2", weight="bold", color="slate.11"),
                        rx.input(
                            placeholder="sv@vaa.edu.vn...",
                            value=AdminUserState.form_email,
                            on_change=AdminUserState.set_form_email,
                            type="email", size="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            rx.cond(AdminUserState.is_create_mode, "Mật khẩu *", "Mật khẩu mới (bỏ trống = giữ cũ)"),
                            size="2", weight="bold", color="slate.11",
                        ),
                        rx.input(
                            placeholder="Nhập mật khẩu...",
                            value=AdminUserState.form_password,
                            on_change=AdminUserState.set_form_password,
                            type="password", size="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),

                # Role & Khoa
                rx.grid(
                    rx.vstack(
                        rx.text("Vai trò *", size="2", weight="bold", color="slate.11"),
                        rx.select.root(
                            rx.select.trigger(width="100%", size="2"),
                            rx.select.content(
                                rx.select.item("Sinh viên", value="STUDENT"),
                                rx.select.item("Giảng viên", value="LECTURER"),
                                rx.select.item("Quản trị viên", value="ADMIN"),
                            ),
                            value=AdminUserState.form_role,
                            on_change=AdminUserState.set_form_role,
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Khoa / Ngành", size="2", weight="bold", color="slate.11"),
                        rx.select.root(
                            rx.select.trigger(width="100%", size="2"),
                            rx.select.content(
                                rx.select.item("Khoa CNTT", value="CNTT"),
                                rx.select.item("Khoa Kinh tế", value="KT"),
                                rx.select.item("Khoa Ngoại ngữ", value="NN"),
                                rx.select.item("Khoa Điều hành bay", value="DHB"),
                            ),
                            value=AdminUserState.form_dept,
                            on_change=AdminUserState.set_form_dept,
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),

                # Lớp & Trạng thái
                rx.grid(
                    rx.vstack(
                        rx.text("Lớp (Sinh viên)", size="2", weight="bold", color="slate.11"),
                        rx.input(
                            placeholder="D21CQCN01-B (tuỳ chọn)",
                            value=AdminUserState.form_class,
                            on_change=AdminUserState.set_form_class,
                            size="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Trạng thái tài khoản", size="2", weight="bold", color="slate.11"),
                        rx.hstack(
                            rx.switch(
                                checked=AdminUserState.form_active,
                                on_change=AdminUserState.toggle_form_active,
                                color_scheme="green",
                            ),
                            rx.text(
                                rx.cond(AdminUserState.form_active, "Hoạt động", "Đã khóa"),
                                size="2", color="slate.10",
                            ),
                            align="center", spacing="2", padding_top="2",
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),

                # Actions
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Hủy", variant="ghost", color_scheme="gray", size="2",
                                  on_click=AdminUserState.close_user_modal),
                    ),
                    rx.button(
                        rx.cond(
                            AdminUserState.is_create_mode,
                            rx.hstack(rx.icon("user-plus", size=15), rx.text("Tạo người dùng"), align="center", spacing="1"),
                            rx.hstack(rx.icon("save", size=15), rx.text("Lưu thay đổi"), align="center", spacing="1"),
                        ),
                        color_scheme="blue",
                        size="2",
                        on_click=AdminUserState.save_user,
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    margin_top="2",
                ),

                spacing="4", width="100%",
            ),
            max_width="600px",
            padding="5",
        ),
        open=AdminUserState.show_user_modal,
        on_open_change=AdminUserState.close_user_modal,
    )


def delete_confirm_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(
                rx.hstack(
                    rx.icon("triangle-alert", size=20, color="var(--red-10)"),
                    rx.text("Xác nhận xóa người dùng"),
                    align="center", spacing="2",
                ),
            ),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text(
                        "Bạn có chắc chắn muốn xóa vĩnh viễn tài khoản của người dùng:",
                        size="2", color="slate.10",
                    ),
                    rx.text(AdminUserState.delete_user_name, size="3", weight="bold", color="red.11"),
                    rx.callout.root(
                        rx.callout.icon(rx.icon("info", size=14)),
                        rx.callout.text("Hành động này không thể hoàn tác. Tất cả dữ liệu liên quan của người dùng sẽ bị xóa."),
                        color="amber", variant="surface", size="1",
                    ),
                    spacing="2",
                ),
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Hủy bỏ", variant="ghost", color_scheme="gray",
                              on_click=AdminUserState.cancel_delete),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        rx.icon("trash-2", size=15),
                        "Xóa vĩnh viễn",
                        color_scheme="red",
                        variant="solid",
                        on_click=AdminUserState.confirm_delete,
                    ),
                ),
                spacing="3", justify="end", margin_top="4",
            ),
        ),
        open=AdminUserState.show_delete_dialog,
    )


def detail_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.avatar(
                        fallback=AdminUserState.detail_user.avatar_fallback,
                        size="4", radius="full", color_scheme="blue",
                    ),
                    rx.vstack(
                        rx.heading(AdminUserState.detail_user.full_name, size="5", weight="bold", color="slate.12"),
                        rx.hstack(
                            role_badge(AdminUserState.detail_user.role),
                            status_badge_bool(AdminUserState.detail_user.is_active),
                            spacing="2",
                        ),
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(rx.icon("x", size=16), variant="ghost", color_scheme="gray", size="1"),
                    ),
                    align="start", width="100%",
                ),
                rx.divider(color_scheme="gray"),
                rx.grid(
                    *[
                        rx.vstack(
                            rx.text(label, size="1", color="slate.8", weight="medium"),
                            rx.text(value, size="2", color="slate.12", weight="bold"),
                            spacing="0",
                        )
                        for label, value in [
                            ("Username", AdminUserState.detail_user.username),
                            ("Email", AdminUserState.detail_user.email),
                            ("Khoa / Ngành", AdminUserState.detail_user.department),
                            ("Lớp", AdminUserState.detail_user.student_class),
                            ("Ngày tạo", AdminUserState.detail_user.created_at),
                        ]
                    ],
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                rx.flex(
                    rx.button(
                        rx.icon("pencil", size=15),
                        "Chỉnh sửa",
                        color_scheme="blue",
                        size="2",
                        on_click=AdminUserState.open_edit_modal(AdminUserState.detail_user),
                    ),
                    rx.dialog.close(
                        rx.button("Đóng", variant="ghost", color_scheme="gray", size="2",
                                  on_click=AdminUserState.close_detail),
                    ),
                    spacing="2",
                    justify="end",
                    margin_top="4",
                ),
                spacing="4", width="100%",
            ),
            max_width="480px", padding="5",
        ),
        open=AdminUserState.show_detail_modal,
        on_open_change=AdminUserState.close_detail,
    )


# ─── Admin Sidebar ────────────────────────────────────────────────────────────

def admin_sidebar(current_route: str = "") -> rx.Component:
    def item(title: str, href: str, icon: str, active: bool = False) -> rx.Component:
        return rx.link(
            rx.hstack(
                rx.icon(icon, size=18, color=rx.cond(active, "var(--red-10)", "var(--slate-9)")),
                rx.text(title, size="2", weight=rx.cond(active, "bold", "medium")),
                spacing="3", padding_x="3", padding_y="2.5", border_radius="lg",
                bg=rx.cond(active, "var(--red-3)", "transparent"),
                color=rx.cond(active, "var(--red-11)", "var(--slate-11)"),
                _hover={"bg": "var(--red-2)", "color": "var(--red-10)"},
                transition="all 0.15s ease", align="center",
            ),
            href=href, underline="none", width="100%",
        )

    return rx.box(
        rx.vstack(
            # Logo
            rx.link(
                rx.hstack(
                    rx.box(
                        rx.icon("shield-check", size=22, color="white"),
                        bg="red.9", padding="2", border_radius="lg",
                    ),
                    rx.vstack(
                        rx.text("DocUni", size="4", weight="bold", color="slate.12", line_height="1"),
                        rx.text("Admin Panel", size="1", color="red.10", weight="bold"),
                        spacing="0",
                    ),
                    align="center", spacing="2", padding_y="3", padding_x="2",
                ),
                href="/admin/users", underline="none", width="100%",
            ),

            rx.divider(color_scheme="gray", margin_y="2"),

            # Menu items
            rx.vstack(
                item("Quản lý người dùng", "/admin/users", "users", current_route == "/admin/users"),
                item("Quản lý tổ chức", "/admin/organization", "building", current_route == "/admin/organization"),
                spacing="1", width="100%",
            ),

            rx.spacer(),
            rx.divider(color_scheme="gray", margin_y="2"),

            rx.vstack(
                rx.link(
                    rx.hstack(
                        rx.icon("external-link", size=15, color="var(--slate-8)"),
                        rx.text("Cổng Sinh viên", size="2", color="slate.9"),
                        spacing="2", padding="2", align="center",
                    ),
                    href="/", underline="none",
                ),
                rx.link(
                    rx.hstack(
                        rx.icon("graduation-cap", size=15, color="var(--slate-8)"),
                        rx.text("Cổng Giảng viên", size="2", color="slate.9"),
                        spacing="2", padding="2", align="center",
                    ),
                    href="/lecturer/dashboard", underline="none",
                ),
                spacing="1", width="100%",
            ),

            height="100%", padding="4",
        ),
        width="260px", min_width="260px", height="100vh",
        border_r="1px solid var(--slate-4)", bg="white",
        position="sticky", top="0",
    )


def admin_page_wrapper(content: rx.Component, current_route: str = "") -> rx.Component:
    return rx.hstack(
        admin_sidebar(current_route=current_route),
        rx.box(
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.icon("shield-check", size=18, color="var(--red-10)"),
                        rx.text("Bảng Quản Trị Hệ Thống", size="2", weight="bold", color="red.11"),
                        align="center", spacing="2",
                    ),
                    rx.spacer(),
                    rx.badge("Admin Portal", color_scheme="red", variant="surface"),
                    align="center",
                    padding_x="6", padding_y="3.5",
                    border_b="1px solid var(--slate-4)", bg="white",
                ),
                rx.box(content, padding="6"),
                width="100%", min_height="100vh", bg="slate.1",
            ),
            flex="1", min_width="0",
        ),
        spacing="0", min_height="100vh",
    )


# ─── Main User Management Page ────────────────────────────────────────────────

def admin_users_page() -> rx.Component:
    return admin_page_wrapper(
        rx.vstack(
            # ── Header ──
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("users", size=28, color="white"),
                        bg="red.9", padding="3", border_radius="xl",
                    ),
                    rx.vstack(
                        rx.heading("Quản lý Người dùng", size="7", weight="bold", color="slate.12"),
                        rx.text("Thêm, sửa, xóa và phân quyền tài khoản trong hệ thống", size="3", color="slate.9"),
                        spacing="1",
                    ),
                    align="center", spacing="3",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("user-plus", size=16),
                    "Thêm người dùng",
                    color_scheme="red",
                    size="3",
                    variant="solid",
                    on_click=AdminUserState.open_create_modal,
                ),
                align="center", width="100%",
            ),

            rx.divider(color_scheme="gray"),

            # ── KPI Cards ──
            rx.grid(
                kpi_box("Tổng người dùng", AdminUserState.total_users.to_string(), "users", "blue"),
                kpi_box("Đang hoạt động", AdminUserState.active_users.to_string(), "circle-check", "green"),
                kpi_box("Quản trị viên", AdminUserState.admin_count.to_string(), "shield", "red"),
                kpi_box("Giảng viên", AdminUserState.lecturer_count.to_string(), "graduation-cap", "indigo"),
                columns="4", spacing="4", width="100%",
            ),

            # ── Filters ──
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.input(
                            rx.input.slot(rx.icon("search", size=16, color="var(--slate-8)")),
                            placeholder="Tìm kiếm theo tên, username, email...",
                            value=AdminUserState.search_query,
                            on_change=AdminUserState.set_search_query,
                            size="3", flex="1",
                        ),
                        rx.select.root(
                            rx.select.trigger(placeholder="Vai trò", size="3", width="160px"),
                            rx.select.content(
                                rx.select.item("Tất cả vai trò", value="ALL"),
                                rx.select.item("Admin", value="ADMIN"),
                                rx.select.item("Giảng viên", value="LECTURER"),
                                rx.select.item("Sinh viên", value="STUDENT"),
                            ),
                            value=AdminUserState.filter_role,
                            on_change=AdminUserState.set_filter_role,
                        ),
                        rx.select.root(
                            rx.select.trigger(placeholder="Khoa", size="3", width="180px"),
                            rx.select.content(
                                rx.select.item("Tất cả Khoa", value="ALL"),
                                rx.select.item("Khoa CNTT", value="CNTT"),
                                rx.select.item("Khoa Kinh tế", value="KT"),
                                rx.select.item("Khoa Ngoại ngữ", value="NN"),
                                rx.select.item("Khoa Điều hành bay", value="DHB"),
                            ),
                            value=AdminUserState.filter_dept,
                            on_change=AdminUserState.set_filter_dept,
                        ),
                        rx.select.root(
                            rx.select.trigger(placeholder="Trạng thái", size="3", width="160px"),
                            rx.select.content(
                                rx.select.item("Tất cả trạng thái", value="ALL"),
                                rx.select.item("Hoạt động", value="ACTIVE"),
                                rx.select.item("Đã khóa", value="INACTIVE"),
                            ),
                            value=AdminUserState.filter_status,
                            on_change=AdminUserState.set_filter_status,
                        ),
                        rx.button(
                            rx.icon("refresh-cw", size=14),
                            "Đặt lại",
                            size="3", variant="surface", color_scheme="gray",
                            on_click=AdminUserState.reset_filters,
                        ),
                        spacing="3", align="center", width="100%",
                    ),
                    width="100%",
                ),
                variant="surface", padding="4", width="100%",
            ),

            # ── User Table ──
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            AdminUserState.filtered_users.length().to_string(),
                            " người dùng",
                            size="2", color="slate.9", weight="medium",
                        ),
                        rx.spacer(),
                        align="center", width="100%",
                    ),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                *[
                                    rx.table.column_header_cell(
                                        rx.text(t, size="1", weight="bold", color="slate.10"),
                                    )
                                    for t in ["Người dùng", "Email", "Vai trò", "Khoa", "Lớp/Khóa", "Trạng thái", "Ngày tạo", "Thao tác"]
                                ],
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                AdminUserState.filtered_users,
                                user_table_row,
                            ),
                        ),
                        width="100%",
                        variant="surface",
                        size="2",
                    ),
                    spacing="3", width="100%",
                ),
                variant="surface", padding="4", width="100%",
            ),

            # ── Dialogs ──
            user_form_modal(),
            delete_confirm_dialog(),
            detail_modal(),

            spacing="5", width="100%",
        ),
        current_route="/admin/users",
    )
