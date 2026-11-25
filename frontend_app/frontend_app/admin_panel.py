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
from .auth import AuthState, login_page


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


# ─── Initial Options ──────────────────────────────────────────────────────────

ROLE_OPTIONS = ["ADMIN", "LECTURER", "STUDENT"]
DEPARTMENT_OPTIONS = ["Cong nghe thong tin", "Kinh te", "Ngoai ngu"]
STATUS_OPTIONS = ["ACTIVE", "INACTIVE"]


def get_dept_classes(dept_name: str) -> List[str]:
    dept_norm = dept_name.strip().lower()
    if "thong tin" in dept_norm or "cntt" in dept_norm or dept_norm == "d1":
        return ["CNTT-K0", "CNTT-K1", "CNTT-K2"]
    elif "kinh te" in dept_norm or "kt" in dept_norm or dept_norm == "d2":
        return ["KT-K1", "KT-K2"]
    elif "ngoai ngu" in dept_norm or "nn" in dept_norm or dept_norm == "d3":
        return ["NN-K1"]
    return []


# ─── Admin User State ─────────────────────────────────────────────────────────

class AdminUserState(rx.State):
    """Quản lý trang Quản lý người dùng từ dữ liệu PostgreSQL thực tế."""

    users: List[AdminUser] = []
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
    form_dept: str = "Cong nghe thong tin"
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

    # System & Indexing stats
    total_docs: int = 0
    total_folders: int = 0
    total_tags: int = 0
    indexing_rate: str = "0%"
    total_chunks: int = 0

    async def run_all_indexing(self):
        """Chạy lập chỉ mục lại toàn bộ tài liệu (Re-index) và cập nhật số liệu thực tế."""
        from .auth import AuthState
        auth = await self.get_state(AuthState)
        headers = {"Authorization": f"Bearer {auth.auth_token}"} if (auth and auth.auth_token) else {}
        try:
            import httpx
            r = httpx.post("http://127.0.0.1:8000/api/indexing/run/", headers=headers, timeout=30.0)
            if r.status_code == 200:
                data = r.json()
                await self.load_users()
                return rx.toast.success(f"Đã lập chỉ mục AI thành công! {data.get('message', '')}")
        except Exception:
            pass

        try:
            import asyncio
            def _do_index():
                from documents.indexing_service import index_all_documents
                return index_all_documents()
            res = await asyncio.to_thread(_do_index)
            await self.load_users()
            return rx.toast.success(f"Đã hoàn thành Indexing toàn bộ: {res.get('indexed_count')} tài liệu ({res.get('total_chunks')} chunks).")
        except Exception as e:
            return rx.toast.error(f"Lỗi: {str(e)}")

    async def load_users(self):
        """Tải danh sách người dùng thực tế và các chỉ số thống kê từ PostgreSQL."""
        from .auth import AuthState
        auth = await self.get_state(AuthState)
        headers = {"Authorization": f"Bearer {auth.auth_token}"} if (auth and auth.auth_token) else {}

        loaded_ok = False
        try:
            import httpx
            # 1. Gọi API danh sách người dùng kèm Bearer token của Quản trị viên
            resp = httpx.get("http://127.0.0.1:8000/api/users/", headers=headers, timeout=3.5)
            if resp.status_code == 200:
                res_json = resp.json()
                raw_data = res_json.get("users") or res_json.get("data") or []
                loaded = []
                for item in raw_data:
                    u_id = str(item.get("id") or item.get("user_id") or "")
                    name = item.get("full_name") or item.get("username") or ""
                    uname = item.get("username") or ""
                    email = item.get("email") or f"{uname}@docuni.edu.vn"
                    role = str(item.get("role") or item.get("role_name") or "STUDENT").upper()
                    dept = item.get("department_name") or ""
                    s_class = item.get("class_name") or ""
                    active = bool(item.get("is_active", True))
                    created = str(item.get("created_at") or "")[:10]
                    avatar = name[:2].upper() if name else uname[:2].upper()
                    loaded.append(AdminUser(
                        id=u_id,
                        full_name=name,
                        username=uname,
                        email=email,
                        role=role,
                        department=dept,
                        student_class=s_class,
                        is_active=active,
                        created_at=created,
                        avatar_fallback=avatar,
                    ))
                self.users = loaded
                loaded_ok = True

            # 2. Gọi API thống kê toàn hệ thống từ PostgreSQL
            r_stats = httpx.get("http://127.0.0.1:8000/api/dashboard/stats/", headers=headers, timeout=3.5)
            if r_stats.status_code == 200:
                s_data = r_stats.json().get("stats") or r_stats.json().get("data") or {}
                self.total_docs = int(s_data.get("total_documents", 0))
                self.total_folders = int(s_data.get("total_folders", 0))
                self.total_tags = int(s_data.get("total_tags", 0))
                idx_data = s_data.get("indexing", {})
                self.indexing_rate = f"{idx_data.get('indexing_percentage', 0)}%"
                self.total_chunks = int(idx_data.get("total_chunks", 0))
                if loaded_ok:
                    return
        except Exception:
            pass

        # 3. Fallback ORM: Thực thi trong thread riêng để không chặn asyncio loop
        try:
            import os, sys, asyncio
            def _load_data_orm():
                backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
                if backend_dir not in sys.path:
                    sys.path.insert(0, backend_dir)
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
                import django
                django.setup()
                from accounts.models import User
                from documents.models import Document, Folder, Tag
                from documents.indexing_service import get_indexing_stats

                doc_cnt = Document.objects.count()
                fold_cnt = Folder.objects.count()
                tag_cnt = Tag.objects.count()
                idx_info = get_indexing_stats()

                qs = User.objects.select_related('role', 'department', 'student_class').order_by('id')
                user_list = []
                for u in qs:
                    name = u.full_name or u.username
                    uname = u.username
                    email = getattr(u, 'email', '') or f"{uname}@docuni.edu.vn"
                    role = str(u.role.role_name if u.role else "STUDENT").upper()
                    dept = u.department.department_name if u.department else ""
                    s_class = u.student_class.class_name if u.student_class else ""
                    active = bool(getattr(u, 'is_active', True))
                    created = u.created_at.strftime('%Y-%m-%d') if getattr(u, 'created_at', None) else ""
                    avatar = name[:2].upper() if name else uname[:2].upper()
                    user_list.append(AdminUser(
                        id=str(u.id),
                        full_name=name,
                        username=uname,
                        email=email,
                        role=role,
                        department=dept,
                        student_class=s_class,
                        is_active=active,
                        created_at=created,
                        avatar_fallback=avatar,
                    ))
                return doc_cnt, fold_cnt, tag_cnt, idx_info, user_list

            doc_cnt, fold_cnt, tag_cnt, idx_info, user_list = await asyncio.to_thread(_load_data_orm)
            self.total_docs = doc_cnt
            self.total_folders = fold_cnt
            self.total_tags = tag_cnt
            self.total_chunks = int(idx_info.get("total_chunks", 0))
            self.indexing_rate = f"{idx_info.get('indexing_percentage', 0)}%"
            self.users = user_list
        except Exception:
            self.users = []

    # ── Computed vars ──
    @rx.var
    def filtered_users(self) -> List[AdminUser]:
        result = self.users
        q = self.search_query.strip().lower()
        if q:
            result = [u for u in result if q in u.full_name.lower() or q in u.username.lower() or q in u.email.lower() or q in u.student_class.lower()]
        if self.filter_role != "ALL":
            result = [u for u in result if u.role == self.filter_role]
        if self.filter_dept != "ALL":
            f_d = self.filter_dept.strip().lower()
            result = [
                u for u in result
                if u.department.strip().lower() == f_d
                or (f_d in ("cong nghe thong tin", "d1") and ("thong tin" in u.department.lower() or "cntt" in u.department.lower()))
                or (f_d in ("kinh te", "d2") and "kinh te" in u.department.lower())
                or (f_d in ("ngoai ngu", "d3") and "ngoai ngu" in u.department.lower())
            ]
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

    @rx.var
    def available_classes_for_form(self) -> List[str]:
        dept_norm = self.form_dept.strip().lower()
        if "thong tin" in dept_norm or "cntt" in dept_norm or dept_norm == "d1":
            return ["CNTT-K0", "CNTT-K1", "CNTT-K2"]
        elif "kinh te" in dept_norm or "kt" in dept_norm or dept_norm == "d2":
            return ["KT-K1", "KT-K2"]
        elif "ngoai ngu" in dept_norm or "nn" in dept_norm or dept_norm == "d3":
            return ["NN-K1"]
        return []

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

    # ── Helpers for Department & Class mapping ──
    def get_classes_for_dept(self, dept_name: str) -> List[str]:
        dept_norm = dept_name.strip().lower()
        if "thong tin" in dept_norm or "cntt" in dept_norm or dept_norm == "d1":
            return ["CNTT-K0", "CNTT-K1", "CNTT-K2"]
        elif "kinh te" in dept_norm or "kt" in dept_norm or dept_norm == "d2":
            return ["KT-K1", "KT-K2"]
        elif "ngoai ngu" in dept_norm or "nn" in dept_norm or dept_norm == "d3":
            return ["NN-K1"]
        return []

    def get_dept_id(self, dept_name: str) -> int:
        dept_norm = dept_name.strip().lower()
        if "thong tin" in dept_norm or "cntt" in dept_norm or dept_norm == "d1":
            return 1
        elif "kinh te" in dept_norm or "kt" in dept_norm or dept_norm == "d2":
            return 2
        elif "ngoai ngu" in dept_norm or "nn" in dept_norm or dept_norm == "d3":
            return 3
        return 1

    def get_class_id(self, class_name: str) -> Optional[int]:
        c_map = {
            'CNTT-K1': 1,
            'CNTT-K2': 2,
            'KT-K1': 3,
            'KT-K2': 4,
            'NN-K1': 5,
            'CNTT-K0': 6,
        }
        return c_map.get(class_name)

    # ── Create Modal ──
    def open_create_modal(self):
        self.is_create_mode = True
        self.modal_user_id = ""
        self.form_full_name = ""
        self.form_username = ""
        self.form_email = ""
        self.form_password = ""
        self.form_role = "STUDENT"
        self.form_dept = "Cong nghe thong tin"
        self.form_class = "CNTT-K1"
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
        self.form_dept = user.department or "Cong nghe thong tin"
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
        if v == "STUDENT":
            classes = self.get_classes_for_dept(self.form_dept)
            if classes and (not self.form_class or self.form_class not in classes):
                self.form_class = classes[0]
        else:
            self.form_class = ""

    def set_form_dept(self, v: str):
        self.form_dept = v
        if self.form_role == "STUDENT":
            classes = self.get_classes_for_dept(v)
            self.form_class = classes[0] if classes else ""
        else:
            self.form_class = ""

    def set_form_class(self, v: str):
        self.form_class = v

    def toggle_form_active(self, v: bool):
        self.form_active = v

    async def save_user(self):
        fname = self.form_full_name.strip()
        uname = self.form_username.strip()
        email = self.form_email.strip()
        pwd = self.form_password.strip()
        role = self.form_role
        dept = self.form_dept
        cls_name = self.form_class

        if not fname:
            self.form_error = "Họ tên không được để trống."
            return
        if not uname:
            self.form_error = "Username không được để trống."
            return
        if email and "@" not in email:
            self.form_error = "Email không đúng định dạng."
            return

        # Ràng buộc: Không cho phép sinh viên thuộc khoa này bị gán nhầm vào lớp của khoa khác
        if role == "STUDENT" and cls_name:
            valid_classes = self.get_classes_for_dept(dept)
            if valid_classes and cls_name not in valid_classes:
                self.form_error = f"Lớp '{cls_name}' không thuộc khoa '{dept}'. Vui lòng chọn lớp đúng khoa."
                return

        from .auth import AuthState
        auth = await self.get_state(AuthState)
        headers = {"Authorization": f"Bearer {auth.auth_token}"} if (auth and auth.auth_token) else {}

        dept_id = self.get_dept_id(dept)
        class_id = self.get_class_id(cls_name) if (role == "STUDENT" and cls_name) else None

        if self.is_create_mode:
            if not pwd:
                self.form_error = "Mật khẩu không được để trống khi tạo mới."
                return
            created_ok = False
            try:
                import httpx
                payload = {
                    "username": uname,
                    "full_name": fname,
                    "email": email,
                    "password": pwd,
                    "role": role,
                    "department_id": dept_id,
                    "class_id": class_id,
                }
                r = httpx.post("http://127.0.0.1:8000/api/users/", json=payload, headers=headers, timeout=4.0)
                if r.status_code == 201:
                    created_ok = True
                elif r.status_code == 400:
                    self.form_error = r.json().get("message", "Lỗi tạo tài khoản.")
                    return
            except Exception:
                pass

            if not created_ok:
                try:
                    import asyncio
                    def _create_user_orm(u, fn, em, pw, ro, did, cid, is_act):
                        from accounts.models import User, Role
                        from academics.models import Department, Class
                        if User.objects.filter(username__iexact=u).exists():
                            return False, f"Username '{u}' đã tồn tại."
                        r_obj, _ = Role.objects.get_or_create(role_name=ro.upper())
                        d_obj = Department.objects.filter(id=did).first() if did else None
                        c_obj = Class.objects.filter(id=cid).first() if cid else None
                        User.objects.create_user(
                            username=u, full_name=fn, role=r_obj, password=pw,
                            email=em, department=d_obj, student_class=c_obj, is_active=is_act
                        )
                        return True, ""
                    ok, err = await asyncio.to_thread(_create_user_orm, uname, fname, email, pwd, role, dept_id, class_id, self.form_active)
                    if not ok:
                        self.form_error = err
                        return
                except Exception as e:
                    self.form_error = f"Lỗi tạo tài khoản: {str(e)}"
                    return

            self.show_user_modal = False
            await self.load_users()
            return rx.toast.success(f"Đã thêm người dùng '{fname}' vào cơ sở dữ liệu thành công!")

        else:
            target_pk = int(self.modal_user_id) if self.modal_user_id.isdigit() else None
            updated_ok = False
            if target_pk:
                try:
                    import httpx
                    payload = {
                        "full_name": fname,
                        "email": email,
                        "role": role,
                        "department_id": dept_id,
                        "class_id": class_id,
                        "is_active": self.form_active,
                    }
                    r = httpx.patch(f"http://127.0.0.1:8000/api/users/{target_pk}/", json=payload, headers=headers, timeout=4.0)
                    if r.status_code == 200:
                        updated_ok = True
                except Exception:
                    pass

            if not updated_ok and target_pk:
                try:
                    import asyncio
                    def _update_user_orm(pk, fn, em, ro, did, cid, is_act):
                        from accounts.models import User, Role
                        from academics.models import Department, Class
                        u = User.objects.filter(id=pk).first()
                        if not u:
                            return False, "Không tìm thấy người dùng."
                        u.full_name = fn
                        u.email = em
                        r_obj = Role.objects.filter(role_name=ro.upper()).first()
                        if r_obj:
                            u.role = r_obj
                        u.department = Department.objects.filter(id=did).first() if did else None
                        u.student_class = Class.objects.filter(id=cid).first() if cid else None
                        u.is_active = is_act
                        u.save()
                        return True, ""
                    ok, err = await asyncio.to_thread(_update_user_orm, target_pk, fname, email, role, dept_id, class_id, self.form_active)
                    if not ok:
                        self.form_error = err
                        return
                except Exception as e:
                    self.form_error = f"Lỗi cập nhật: {str(e)}"
                    return

            self.show_user_modal = False
            await self.load_users()
            return rx.toast.success(f"Đã cập nhật thông tin người dùng '{fname}' vào PostgreSQL thành công!")

    # ── Toggle Account Status ──
    async def toggle_user_status(self, user_id: str):
        target_pk = int(user_id) if user_id.isdigit() else None
        from .auth import AuthState
        auth = await self.get_state(AuthState)
        headers = {"Authorization": f"Bearer {auth.auth_token}"} if (auth and auth.auth_token) else {}

        toggled = False
        if target_pk:
            try:
                import httpx
                r = httpx.patch(f"http://127.0.0.1:8000/api/users/{target_pk}/toggle-status/", headers=headers, timeout=3.0)
                if r.status_code == 200:
                    toggled = True
            except Exception:
                pass

        if not toggled and target_pk:
            try:
                import asyncio
                def _toggle_orm(pk):
                    from accounts.models import User
                    u = User.objects.filter(id=pk).first()
                    if u:
                        u.is_active = not u.is_active
                        u.save(update_fields=['is_active'])
                        return True, u.is_active, u.full_name
                    return False, False, ""
                ok, st, name = await asyncio.to_thread(_toggle_orm, target_pk)
                if ok:
                    await self.load_users()
                    msg = "Đã mở khóa" if st else "Đã khóa"
                    return rx.toast.info(f"{msg} tài khoản '{name}' thành công.")
            except Exception:
                pass

        await self.load_users()
        return rx.toast.info("Đã cập nhật trạng thái tài khoản thành công.")

    # ── Delete ──
    def open_delete_dialog(self, user_id: str, user_name: str):
        self.delete_user_id = user_id
        self.delete_user_name = user_name
        self.show_delete_dialog = True

    def cancel_delete(self):
        self.show_delete_dialog = False
        self.delete_user_id = ""

    async def confirm_delete(self):
        target_pk = int(self.delete_user_id) if self.delete_user_id.isdigit() else None
        name = self.delete_user_name
        from .auth import AuthState
        auth = await self.get_state(AuthState)
        headers = {"Authorization": f"Bearer {auth.auth_token}"} if (auth and auth.auth_token) else {}

        deleted = False
        if target_pk:
            try:
                import httpx
                r = httpx.delete(f"http://127.0.0.1:8000/api/users/{target_pk}/", headers=headers, timeout=3.0)
                if r.status_code == 200:
                    deleted = True
            except Exception:
                pass

        if not deleted and target_pk:
            try:
                import asyncio
                def _del_orm(pk):
                    from accounts.models import User
                    User.objects.filter(id=pk).delete()
                await asyncio.to_thread(_del_orm, target_pk)
            except Exception:
                pass

        self.show_delete_dialog = False
        self.delete_user_id = ""
        await self.load_users()
        return rx.toast.success(f"Đã xóa người dùng '{name}' khỏi PostgreSQL thành công!")

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
                                rx.select.item("Cong nghe thong tin", value="Cong nghe thong tin"),
                                rx.select.item("Kinh te", value="Kinh te"),
                                rx.select.item("Ngoai ngu", value="Ngoai ngu"),
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
                        rx.cond(
                            AdminUserState.form_role == "STUDENT",
                            rx.select.root(
                                rx.select.trigger(placeholder="Chọn lớp theo khoa...", width="100%", size="2"),
                                rx.select.content(
                                    rx.select.item("-- Không thuộc lớp --", value=""),
                                    rx.select.item("CNTT-K0", value="CNTT-K0"),
                                    rx.select.item("CNTT-K1", value="CNTT-K1"),
                                    rx.select.item("CNTT-K2", value="CNTT-K2"),
                                    rx.select.item("KT-K1", value="KT-K1"),
                                    rx.select.item("KT-K2", value="KT-K2"),
                                    rx.select.item("NN-K1", value="NN-K1"),
                                ),
                                value=AdminUserState.form_class,
                                on_change=AdminUserState.set_form_class,
                            ),
                            rx.text("Không áp dụng cho Giảng viên / Admin", size="2", color="slate.8", font_style="italic", padding_top="2"),
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
                rx.button(
                    rx.hstack(
                        rx.icon("log-out", size=15, color="var(--red-9)"),
                        rx.text("Đăng xuất", size="2", color="red.10"),
                        spacing="2", padding="2", align="center",
                    ),
                    variant="ghost",
                    on_click=AuthState.logout,
                    width="100%",
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
    return rx.cond(
        AuthState.is_logged_in & (AuthState.current_user_role != ""),
        admin_page_wrapper(
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
            rx.grid(
                kpi_box("Tài liệu trong kho", AdminUserState.total_docs.to_string() + " tài liệu", "file-text", "blue"),
                kpi_box("Thư mục hệ thống", AdminUserState.total_folders.to_string() + " thư mục", "folder", "indigo"),
                kpi_box("Thẻ phân loại", AdminUserState.total_tags.to_string() + " tags", "tag", "teal"),
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("sparkles", size=18, color="var(--purple-10)"),
                                bg="purple.3", padding="2", border_radius="lg",
                            ),
                            rx.vstack(
                                rx.text("AI Indexing (RAG)", size="1", color="slate.9", weight="medium"),
                                rx.heading(AdminUserState.indexing_rate, size="4", weight="bold", color="purple.11"),
                                spacing="0",
                            ),
                            rx.spacer(),
                            rx.button(
                                rx.icon("play", size=12),
                                "Re-index",
                                size="1",
                                variant="surface",
                                color_scheme="purple",
                                on_click=AdminUserState.run_all_indexing,
                            ),
                            align="center", spacing="2", width="100%",
                        ),
                        spacing="1", width="100%",
                    ),
                    variant="surface", padding="3",
                ),
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
                                rx.select.item("Cong nghe thong tin", value="Cong nghe thong tin"),
                                rx.select.item("Kinh te", value="Kinh te"),
                                rx.select.item("Ngoai ngu", value="Ngoai ngu"),
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
    ),
    login_page(),
)
