"""
DocUni - Trang Quản Lý Tổ Chức (Admin)
Route: /admin/organization
Framework: Reflex (Python Full-Stack)

Giao diện quản trị khoa, danh sách môn học và lớp học.
Tabs: Khoa | Môn học | Lớp học
"""

import dataclasses
from datetime import datetime
from typing import List
import reflex as rx
from .admin_panel import admin_page_wrapper
from .auth import AuthState


# ─── Dataclass Models ─────────────────────────────────────────────────────────

@dataclasses.dataclass
class Department:
    id: str = ""
    code: str = ""
    name: str = ""
    description: str = ""
    total_subjects: int = 0
    total_lecturers: int = 0
    total_students: int = 0


@dataclasses.dataclass
class Subject:
    id: str = ""
    code: str = ""
    name: str = ""
    department_code: str = ""
    department_name: str = ""
    credits: int = 3
    total_docs: int = 0


@dataclasses.dataclass
class StudentClass:
    id: str = ""
    class_name: str = ""
    department_code: str = ""
    department_name: str = ""
    year: str = ""
    total_students: int = 0


# ─── State ────────────────────────────────────────────────────────────────────

class OrgState(rx.State):
    """Quản lý trang tổ chức: Khoa, Môn học, Lớp - kết nối trực tiếp PostgreSQL via API."""

    active_tab: str = "departments"
    departments: List[Department] = []
    subjects: List[Subject] = []
    classes: List[StudentClass] = []
    is_loading: bool = False
    api_error: str = ""
    dept_search: str = ""
    subject_search: str = ""
    class_search: str = ""
    subject_dept_filter: str = "ALL"
    class_dept_filter: str = "ALL"

    # Add Department
    show_dept_modal: bool = False
    dept_form_code: str = ""
    dept_form_name: str = ""
    dept_form_desc: str = ""
    dept_form_error: str = ""

    # Add Subject
    show_subject_modal: bool = False
    subj_form_code: str = ""
    subj_form_name: str = ""
    subj_form_dept: str = "CNTT"
    subj_form_credits: str = "3"
    subj_form_error: str = ""

    # Add Class
    show_class_modal: bool = False
    class_form_name: str = ""
    class_form_dept: str = "CNTT"
    class_form_year: str = ""
    class_form_error: str = ""

    # Delete
    show_delete_dialog: bool = False
    delete_item_id: str = ""
    delete_item_name: str = ""
    delete_item_type: str = ""

    def set_active_tab(self, tab: str):
        self.active_tab = tab

    def set_dept_search(self, v: str):
        self.dept_search = v

    def set_subject_search(self, v: str):
        self.subject_search = v

    def set_class_search(self, v: str):
        self.class_search = v

    def set_subject_dept_filter(self, v: str):
        self.subject_dept_filter = v

    def set_class_dept_filter(self, v: str):
        self.class_dept_filter = v

    @rx.var
    def filtered_departments(self) -> List[Department]:
        q = self.dept_search.strip().lower()
        if not q:
            return self.departments
        return [d for d in self.departments if q in d.name.lower() or q in d.code.lower()]

    @rx.var
    def filtered_subjects(self) -> List[Subject]:
        q = self.subject_search.strip().lower()
        result = self.subjects
        if self.subject_dept_filter != "ALL":
            result = [s for s in result if s.department_code == self.subject_dept_filter]
        if q:
            result = [s for s in result if q in s.name.lower() or q in s.code.lower()]
        return result

    @rx.var
    def filtered_classes(self) -> List[StudentClass]:
        q = self.class_search.strip().lower()
        result = self.classes
        if self.class_dept_filter != "ALL":
            result = [c for c in result if c.department_code == self.class_dept_filter]
        if q:
            result = [c for c in result if q in c.class_name.lower()]
        return result

    # ── Department CRUD ──
    def open_dept_modal(self):
        self.dept_form_code = ""
        self.dept_form_name = ""
        self.dept_form_desc = ""
        self.dept_form_error = ""
        self.show_dept_modal = True

    def close_dept_modal(self):
        self.show_dept_modal = False

    def set_dept_form_code(self, v: str):
        self.dept_form_code = v

    def set_dept_form_name(self, v: str):
        self.dept_form_name = v

    def set_dept_form_desc(self, v: str):
        self.dept_form_desc = v

    async def fetch_all(self):
        """Nạp danh sách Khoa, Môn học, Lớp học thực tế từ PostgreSQL qua Django API."""
        self.is_loading = True
        self.api_error = ""
        try:
            auth = await self.get_state(AuthState)
            headers = {}
            if auth.auth_token:
                headers["Authorization"] = f"Bearer {auth.auth_token}"

            import httpx
            async with httpx.AsyncClient() as client:
                # 1. Departments
                resp_d = await client.get("http://127.0.0.1:8000/api/departments/", headers=headers, timeout=5.0)
                depts = []
                if resp_d.status_code == 200:
                    for d in resp_d.json().get("departments", []):
                        did = str(d.get("department_id", ""))
                        dname = d.get("department_name", "")
                        depts.append(
                            Department(
                                id=did,
                                code=f"K{did}",
                                name=dname,
                                description=f"Khoa {dname}",
                                total_subjects=0,
                                total_lecturers=0,
                                total_students=0,
                            )
                        )
                self.departments = depts

                # 2. Subjects
                resp_s = await client.get("http://127.0.0.1:8000/api/subjects/", headers=headers, timeout=5.0)
                subjs = []
                if resp_s.status_code == 200:
                    for s in resp_s.json().get("subjects", []):
                        sid = str(s.get("subject_id", ""))
                        sname = s.get("subject_name", "")
                        d_info = s.get("department", {})
                        d_name = d_info.get("department_name", "") if isinstance(d_info, dict) else ""
                        d_code = f"K{d_info.get('department_id', '')}" if isinstance(d_info, dict) else "CNTT"
                        subjs.append(
                            Subject(
                                id=sid,
                                code=f"MH{int(sid):02d}" if sid.isdigit() else sid,
                                name=sname,
                                department_code=d_code,
                                department_name=d_name,
                                credits=3,
                                total_documents=0,
                            )
                        )
                self.subjects = subjs

                # 3. Classes
                resp_c = await client.get("http://127.0.0.1:8000/api/classes/", headers=headers, timeout=5.0)
                clss = []
                if resp_c.status_code == 200:
                    for c in resp_c.json().get("classes", []):
                        cid = str(c.get("class_id", ""))
                        cname = c.get("class_name", "")
                        d_info = c.get("department", {})
                        d_name = d_info.get("department_name", "") if isinstance(d_info, dict) else ""
                        d_code = f"K{d_info.get('department_id', '')}" if isinstance(d_info, dict) else "CNTT"
                        clss.append(
                            StudentClass(
                                id=cid,
                                class_name=cname,
                                department_code=d_code,
                                department_name=d_name,
                                year="2026",
                                student_count=0,
                            )
                        )
                self.classes = clss
        except Exception as e:
            self.api_error = f"Không thể kết nối đến máy chủ: {str(e)}"
        finally:
            self.is_loading = False

    async def save_department(self):
        if not self.dept_form_name.strip():
            self.dept_form_error = "Tên Khoa không được để trống."
            return

        auth = await self.get_state(AuthState)
        headers = {}
        if auth.auth_token:
            headers["Authorization"] = f"Bearer {auth.auth_token}"

        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://127.0.0.1:8000/api/departments/",
                json={"department_name": self.dept_form_name.strip()},
                headers=headers,
                timeout=5.0,
            )
            if resp.status_code == 201:
                self.show_dept_modal = False
                await self.fetch_all()
                return rx.toast.success(f"Đã thêm Khoa '{self.dept_form_name}' vào PostgreSQL thành công!")
            else:
                err = resp.json().get("errors") or resp.json().get("message", "Lỗi tạo khoa.")
                self.dept_form_error = str(err)

    # ── Subject CRUD ──
    def open_subject_modal(self):
        self.subj_form_code = ""
        self.subj_form_name = ""
        self.subj_form_dept = "CNTT"
        self.subj_form_credits = "3"
        self.subj_form_error = ""
        self.show_subject_modal = True

    def close_subject_modal(self):
        self.show_subject_modal = False

    def set_subj_code(self, v: str):
        self.subj_form_code = v

    def set_subj_name(self, v: str):
        self.subj_form_name = v

    def set_subj_dept(self, v: str):
        self.subj_form_dept = v

    def set_subj_credits(self, v: str):
        self.subj_form_credits = v

    async def save_subject(self):
        if not self.subj_form_name.strip():
            self.subj_form_error = "Tên môn học không được để trống."
            return

        auth = await self.get_state(AuthState)
        headers = {}
        if auth.auth_token:
            headers["Authorization"] = f"Bearer {auth.auth_token}"

        dept_id = 1
        if self.departments:
            match = next((d for d in self.departments if d.code == self.subj_form_dept or d.id == self.subj_form_dept), None)
            if match and match.id.isdigit():
                dept_id = int(match.id)
            elif self.departments[0].id.isdigit():
                dept_id = int(self.departments[0].id)

        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://127.0.0.1:8000/api/subjects/",
                json={"subject_name": self.subj_form_name.strip(), "department_id": dept_id},
                headers=headers,
                timeout=5.0,
            )
            if resp.status_code == 201:
                self.show_subject_modal = False
                await self.fetch_all()
                return rx.toast.success(f"Đã thêm môn học '{self.subj_form_name}' vào PostgreSQL thành công!")
            else:
                err = resp.json().get("errors") or resp.json().get("message", "Lỗi tạo môn học.")
                self.subj_form_error = str(err)

    # ── Class CRUD ──
    def open_class_modal(self):
        self.class_form_name = ""
        self.class_form_dept = "CNTT"
        self.class_form_year = str(datetime.now().year)
        self.class_form_error = ""
        self.show_class_modal = True

    def close_class_modal(self):
        self.show_class_modal = False

    def set_class_name(self, v: str):
        self.class_form_name = v

    def set_class_dept(self, v: str):
        self.class_form_dept = v

    def set_class_year(self, v: str):
        self.class_form_year = v

    async def save_class(self):
        if not self.class_form_name.strip():
            self.class_form_error = "Tên lớp không được để trống."
            return

        auth = await self.get_state(AuthState)
        headers = {}
        if auth.auth_token:
            headers["Authorization"] = f"Bearer {auth.auth_token}"

        dept_id = 1
        if self.departments:
            match = next((d for d in self.departments if d.code == self.class_form_dept or d.id == self.class_form_dept), None)
            if match and match.id.isdigit():
                dept_id = int(match.id)
            elif self.departments[0].id.isdigit():
                dept_id = int(self.departments[0].id)

        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://127.0.0.1:8000/api/classes/",
                json={"class_name": self.class_form_name.strip().upper(), "department_id": dept_id, "is_locked": False},
                headers=headers,
                timeout=5.0,
            )
            if resp.status_code == 201:
                self.show_class_modal = False
                await self.fetch_all()
                return rx.toast.success(f"Đã thêm lớp '{self.class_form_name}' vào PostgreSQL thành công!")
            else:
                err = resp.json().get("errors") or resp.json().get("message", "Lỗi tạo lớp.")
                self.class_form_error = str(err)

    # ── Delete ──
    def open_delete(self, item_id: str, item_name: str, item_type: str):
        self.delete_item_id = item_id
        self.delete_item_name = item_name
        self.delete_item_type = item_type
        self.show_delete_dialog = True

    def cancel_delete(self):
        self.show_delete_dialog = False

    async def confirm_delete(self):
        name = self.delete_item_name
        auth = await self.get_state(AuthState)
        headers = {}
        if auth.auth_token:
            headers["Authorization"] = f"Bearer {auth.auth_token}"

        endpoint_map = {
            "dept": f"http://127.0.0.1:8000/api/departments/{self.delete_item_id}/",
            "subject": f"http://127.0.0.1:8000/api/subjects/{self.delete_item_id}/",
            "class": f"http://127.0.0.1:8000/api/classes/{self.delete_item_id}/",
        }
        url = endpoint_map.get(self.delete_item_type)
        if not url:
            self.show_delete_dialog = False
            return

        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.delete(url, headers=headers, timeout=5.0)
            self.show_delete_dialog = False
            if resp.status_code == 200:
                await self.fetch_all()
                return rx.toast.success(f"Đã xóa '{name}' khỏi PostgreSQL thành công!")
            else:
                msg = resp.json().get("message", "Không thể xóa mục này.")
                return rx.toast.error(msg)


# ─── UI Helpers ───────────────────────────────────────────────────────────────

def section_header(title: str, icon: str, btn_label: str, btn_onclick) -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.icon(icon, size=20, color="var(--red-10)"),
            rx.heading(title, size="5", weight="bold", color="slate.12"),
            align="center", spacing="2",
        ),
        rx.spacer(),
        rx.button(
            rx.icon("plus", size=15),
            btn_label,
            color_scheme="red",
            size="2",
            variant="solid",
            on_click=btn_onclick,
        ),
        align="center", width="100%",
    )


def search_bar(placeholder: str, value: str, on_change) -> rx.Component:
    return rx.input(
        rx.input.slot(rx.icon("search", size=15, color="var(--slate-8)")),
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        size="2",
        width="100%",
        max_width="400px",
    )


def dept_card(dept: Department) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text(dept.code, size="3", weight="bold", color="white"),
                    bg="red.9", padding_x="3", padding_y="2",
                    border_radius="lg",
                ),
                rx.vstack(
                    rx.text(dept.name, size="3", weight="bold", color="slate.12"),
                    rx.text(dept.description, size="1", color="slate.8", line_clamp=1),
                    spacing="0",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("trash-2", size=13),
                    size="1", variant="ghost", color_scheme="red",
                    on_click=OrgState.open_delete(dept.id, dept.name, "dept"),
                ),
                align="start", width="100%",
            ),
            rx.hstack(
                rx.hstack(
                    rx.icon("book-open", size=13, color="var(--blue-9)"),
                    rx.text(dept.total_subjects.to_string(), " môn", size="1", color="slate.9"),
                    align="center", spacing="1",
                ),
                rx.hstack(
                    rx.icon("graduation-cap", size=13, color="var(--indigo-9)"),
                    rx.text(dept.total_lecturers.to_string(), " GV", size="1", color="slate.9"),
                    align="center", spacing="1",
                ),
                rx.hstack(
                    rx.icon("users", size=13, color="var(--green-9)"),
                    rx.text(dept.total_students.to_string(), " SV", size="1", color="slate.9"),
                    align="center", spacing="1",
                ),
                spacing="4",
            ),
            spacing="3", width="100%",
        ),
        variant="surface", padding="4",
        _hover={"border_color": "var(--red-8)", "box_shadow": "sm"},
        transition="all 0.15s",
    )


def subject_row(subj: Subject) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.badge(subj.code, color_scheme="blue", variant="surface", size="1")),
        rx.table.cell(rx.text(subj.name, size="2", weight="medium", color="slate.12")),
        rx.table.cell(rx.badge(subj.department_code, color_scheme="gray", variant="surface", size="1")),
        rx.table.cell(rx.text(subj.department_name, size="2", color="slate.9")),
        rx.table.cell(rx.badge(subj.credits.to_string() + " TC", color_scheme="green", variant="surface", size="1")),
        rx.table.cell(
            rx.hstack(
                rx.icon("files", size=13, color="var(--blue-9)"),
                rx.text(subj.total_docs.to_string(), " TL", size="1", color="slate.9"),
                align="center", spacing="1",
            )
        ),
        rx.table.cell(
            rx.button(
                rx.icon("trash-2", size=13),
                size="1", variant="ghost", color_scheme="red",
                on_click=OrgState.open_delete(subj.id, subj.name, "subject"),
            ),
        ),
    )


def class_row(cls: StudentClass) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.badge(cls.class_name, color_scheme="indigo", variant="surface", size="1")),
        rx.table.cell(rx.badge(cls.department_code, color_scheme="gray", variant="surface", size="1")),
        rx.table.cell(rx.text(cls.department_name, size="2", color="slate.9")),
        rx.table.cell(rx.badge(cls.year, color_scheme="amber", variant="surface", size="1")),
        rx.table.cell(
            rx.hstack(
                rx.icon("users", size=13, color="var(--green-9)"),
                rx.text(cls.total_students.to_string(), " SV", size="1", color="slate.9"),
                align="center", spacing="1",
            )
        ),
        rx.table.cell(
            rx.button(
                rx.icon("trash-2", size=13),
                size="1", variant="ghost", color_scheme="red",
                on_click=OrgState.open_delete(cls.id, cls.class_name, "class"),
            ),
        ),
    )


def add_dept_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("building", size=20, color="var(--red-10)"),
                    rx.heading("Thêm Khoa mới", size="4", weight="bold", color="slate.12"),
                    rx.spacer(),
                    rx.dialog.close(rx.button(rx.icon("x", size=15), variant="ghost", color_scheme="gray", size="1")),
                    align="center", width="100%",
                ),
                rx.divider(color_scheme="gray"),
                rx.cond(
                    OrgState.dept_form_error != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle-alert", size=14)),
                        rx.callout.text(OrgState.dept_form_error),
                        color="red", variant="surface", size="1",
                    ),
                    rx.fragment(),
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Mã Khoa *", size="2", weight="bold", color="slate.11"),
                        rx.input(placeholder="VD: CNTT, KT...", value=OrgState.dept_form_code,
                                 on_change=OrgState.set_dept_form_code, size="2", width="100%"),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Tên Khoa *", size="2", weight="bold", color="slate.11"),
                        rx.input(placeholder="VD: Khoa Công nghệ thông tin...", value=OrgState.dept_form_name,
                                 on_change=OrgState.set_dept_form_name, size="2", width="100%"),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),
                rx.vstack(
                    rx.text("Mô tả", size="2", weight="bold", color="slate.11"),
                    rx.text_area(placeholder="Mô tả ngắn về chức năng và đào tạo của Khoa...",
                                 value=OrgState.dept_form_desc, on_change=OrgState.set_dept_form_desc,
                                 size="2", width="100%", rows="2"),
                    spacing="1", width="100%",
                ),
                rx.flex(
                    rx.dialog.close(rx.button("Hủy", variant="ghost", color_scheme="gray", size="2")),
                    rx.button(rx.icon("plus", size=15), "Tạo Khoa", color_scheme="red", size="2",
                              on_click=OrgState.save_department),
                    spacing="2", justify="end",
                ),
                spacing="4", width="100%",
            ),
            max_width="480px", padding="5",
        ),
        open=OrgState.show_dept_modal,
        on_open_change=OrgState.close_dept_modal,
    )


def add_subject_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("book-open", size=20, color="var(--blue-10)"),
                    rx.heading("Thêm Môn học mới", size="4", weight="bold", color="slate.12"),
                    rx.spacer(),
                    rx.dialog.close(rx.button(rx.icon("x", size=15), variant="ghost", color_scheme="gray", size="1")),
                    align="center", width="100%",
                ),
                rx.divider(color_scheme="gray"),
                rx.cond(
                    OrgState.subj_form_error != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle-alert", size=14)),
                        rx.callout.text(OrgState.subj_form_error),
                        color="red", variant="surface", size="1",
                    ),
                    rx.fragment(),
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Mã môn *", size="2", weight="bold", color="slate.11"),
                        rx.input(placeholder="VD: IT101, ECO202...", value=OrgState.subj_form_code,
                                 on_change=OrgState.set_subj_code, size="2", width="100%"),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Số tín chỉ", size="2", weight="bold", color="slate.11"),
                        rx.select.root(
                            rx.select.trigger(width="100%", size="2"),
                            rx.select.content(
                                rx.select.item("2 tín chỉ", value="2"),
                                rx.select.item("3 tín chỉ", value="3"),
                                rx.select.item("4 tín chỉ", value="4"),
                                rx.select.item("5 tín chỉ", value="5"),
                            ),
                            value=OrgState.subj_form_credits,
                            on_change=OrgState.set_subj_credits,
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),
                rx.vstack(
                    rx.text("Tên môn học *", size="2", weight="bold", color="slate.11"),
                    rx.input(placeholder="VD: Cấu trúc dữ liệu & Giải thuật...", value=OrgState.subj_form_name,
                             on_change=OrgState.set_subj_name, size="2", width="100%"),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Khoa phụ trách *", size="2", weight="bold", color="slate.11"),
                    rx.select.root(
                        rx.select.trigger(width="100%", size="2"),
                        rx.select.content(
                            rx.select.item("Khoa CNTT", value="CNTT"),
                            rx.select.item("Khoa Kinh tế", value="KT"),
                            rx.select.item("Khoa Ngoại ngữ", value="NN"),
                            rx.select.item("Khoa Điều hành bay", value="DHB"),
                        ),
                        value=OrgState.subj_form_dept,
                        on_change=OrgState.set_subj_dept,
                    ),
                    spacing="1", width="100%",
                ),
                rx.flex(
                    rx.dialog.close(rx.button("Hủy", variant="ghost", color_scheme="gray", size="2")),
                    rx.button(rx.icon("plus", size=15), "Thêm Môn học", color_scheme="blue", size="2",
                              on_click=OrgState.save_subject),
                    spacing="2", justify="end",
                ),
                spacing="4", width="100%",
            ),
            max_width="480px", padding="5",
        ),
        open=OrgState.show_subject_modal,
        on_open_change=OrgState.close_subject_modal,
    )


def add_class_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("users", size=20, color="var(--indigo-10)"),
                    rx.heading("Thêm Lớp học mới", size="4", weight="bold", color="slate.12"),
                    rx.spacer(),
                    rx.dialog.close(rx.button(rx.icon("x", size=15), variant="ghost", color_scheme="gray", size="1")),
                    align="center", width="100%",
                ),
                rx.divider(color_scheme="gray"),
                rx.cond(
                    OrgState.class_form_error != "",
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle-alert", size=14)),
                        rx.callout.text(OrgState.class_form_error),
                        color="red", variant="surface", size="1",
                    ),
                    rx.fragment(),
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Tên lớp *", size="2", weight="bold", color="slate.11"),
                        rx.input(placeholder="VD: D22CQCN01-B...", value=OrgState.class_form_name,
                                 on_change=OrgState.set_class_name, size="2", width="100%"),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Năm nhập học", size="2", weight="bold", color="slate.11"),
                        rx.input(placeholder="VD: 2022...", value=OrgState.class_form_year,
                                 on_change=OrgState.set_class_year, size="2", width="100%"),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),
                rx.vstack(
                    rx.text("Khoa trực thuộc *", size="2", weight="bold", color="slate.11"),
                    rx.select.root(
                        rx.select.trigger(width="100%", size="2"),
                        rx.select.content(
                            rx.select.item("Khoa CNTT", value="CNTT"),
                            rx.select.item("Khoa Kinh tế", value="KT"),
                            rx.select.item("Khoa Ngoại ngữ", value="NN"),
                            rx.select.item("Khoa Điều hành bay", value="DHB"),
                        ),
                        value=OrgState.class_form_dept,
                        on_change=OrgState.set_class_dept,
                    ),
                    spacing="1", width="100%",
                ),
                rx.flex(
                    rx.dialog.close(rx.button("Hủy", variant="ghost", color_scheme="gray", size="2")),
                    rx.button(rx.icon("plus", size=15), "Thêm Lớp học", color_scheme="indigo", size="2",
                              on_click=OrgState.save_class),
                    spacing="2", justify="end",
                ),
                spacing="4", width="100%",
            ),
            max_width="480px", padding="5",
        ),
        open=OrgState.show_class_modal,
        on_open_change=OrgState.close_class_modal,
    )


def org_delete_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Xác nhận xóa"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text("Bạn có chắc muốn xóa:", size="2"),
                    rx.text(OrgState.delete_item_name, size="3", weight="bold", color="red.11"),
                    rx.callout.root(
                        rx.callout.icon(rx.icon("triangle-alert", size=13)),
                        rx.callout.text("Hành động này không thể hoàn tác!"),
                        color="amber", variant="surface", size="1",
                    ),
                    spacing="2",
                )
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Hủy", variant="ghost", color_scheme="gray", on_click=OrgState.cancel_delete),
                ),
                rx.alert_dialog.action(
                    rx.button(rx.icon("trash-2", size=14), "Xóa", color_scheme="red",
                              on_click=OrgState.confirm_delete),
                ),
                spacing="3", justify="end", margin_top="3",
            ),
        ),
        open=OrgState.show_delete_dialog,
    )


# ─── Main Page ────────────────────────────────────────────────────────────────

def admin_organization_page() -> rx.Component:
    return admin_page_wrapper(
        rx.vstack(
            # Header
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("building", size=28, color="white"),
                        bg="red.9", padding="3", border_radius="xl",
                    ),
                    rx.vstack(
                        rx.heading("Quản lý Tổ chức", size="7", weight="bold", color="slate.12"),
                        rx.text("Quản lý Khoa, Môn học và Lớp học trong toàn bộ hệ thống", size="3", color="slate.9"),
                        spacing="1",
                    ),
                    align="center", spacing="3",
                ),
                align="center", width="100%",
            ),

            rx.divider(color_scheme="gray"),

            # Tabs
            rx.hstack(
                *[
                    rx.button(
                        rx.icon(icon, size=16),
                        label,
                        size="2",
                        radius="full",
                        variant=rx.cond(OrgState.active_tab == tab_val, "solid", "surface"),
                        color_scheme=rx.cond(OrgState.active_tab == tab_val, "red", "gray"),
                        on_click=OrgState.set_active_tab(tab_val),
                    )
                    for label, tab_val, icon in [
                        ("Khoa / Ngành", "departments", "building"),
                        ("Môn học", "subjects", "book-open"),
                        ("Lớp học", "classes", "users"),
                    ]
                ],
                spacing="2",
            ),

            # ── Tab: Khoa ──
            rx.cond(
                OrgState.active_tab == "departments",
                rx.vstack(
                    rx.hstack(
                        section_header("Danh sách Khoa / Ngành", "building", "+ Thêm Khoa", OrgState.open_dept_modal),
                        width="100%",
                    ),
                    search_bar("Tìm kiếm theo tên hoặc mã Khoa...", OrgState.dept_search, OrgState.set_dept_search),
                    rx.grid(
                        rx.foreach(OrgState.filtered_departments, dept_card),
                        columns="2", spacing="4", width="100%",
                    ),
                    spacing="4", width="100%",
                ),
                rx.fragment(),
            ),

            # ── Tab: Môn học ──
            rx.cond(
                OrgState.active_tab == "subjects",
                rx.vstack(
                    section_header("Danh sách Môn học", "book-open", "+ Thêm Môn học", OrgState.open_subject_modal),
                    rx.hstack(
                        search_bar("Tìm kiếm môn học...", OrgState.subject_search, OrgState.set_subject_search),
                        rx.select.root(
                            rx.select.trigger(placeholder="Lọc theo Khoa", size="2", width="200px"),
                            rx.select.content(
                                rx.select.item("Tất cả Khoa", value="ALL"),
                                rx.select.item("Khoa CNTT", value="CNTT"),
                                rx.select.item("Khoa Kinh tế", value="KT"),
                                rx.select.item("Khoa Ngoại ngữ", value="NN"),
                                rx.select.item("Khoa Điều hành bay", value="DHB"),
                            ),
                            value=OrgState.subject_dept_filter,
                            on_change=OrgState.set_subject_dept_filter,
                        ),
                        spacing="3", align="center",
                    ),
                    rx.card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(*[
                                    rx.table.column_header_cell(rx.text(t, size="1", weight="bold", color="slate.9"))
                                    for t in ["Mã môn", "Tên môn học", "Khoa", "Tên Khoa", "Tín chỉ", "Tài liệu", "Xóa"]
                                ]),
                            ),
                            rx.table.body(rx.foreach(OrgState.filtered_subjects, subject_row)),
                            width="100%", variant="surface", size="2",
                        ),
                        variant="surface", padding="4", width="100%",
                    ),
                    spacing="4", width="100%",
                ),
                rx.fragment(),
            ),

            # ── Tab: Lớp học ──
            rx.cond(
                OrgState.active_tab == "classes",
                rx.vstack(
                    section_header("Danh sách Lớp học", "users", "+ Thêm Lớp học", OrgState.open_class_modal),
                    rx.hstack(
                        search_bar("Tìm kiếm lớp học...", OrgState.class_search, OrgState.set_class_search),
                        rx.select.root(
                            rx.select.trigger(placeholder="Lọc theo Khoa", size="2", width="200px"),
                            rx.select.content(
                                rx.select.item("Tất cả Khoa", value="ALL"),
                                rx.select.item("Khoa CNTT", value="CNTT"),
                                rx.select.item("Khoa Kinh tế", value="KT"),
                                rx.select.item("Khoa Ngoại ngữ", value="NN"),
                                rx.select.item("Khoa Điều hành bay", value="DHB"),
                            ),
                            value=OrgState.class_dept_filter,
                            on_change=OrgState.set_class_dept_filter,
                        ),
                        spacing="3", align="center",
                    ),
                    rx.card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(*[
                                    rx.table.column_header_cell(rx.text(t, size="1", weight="bold", color="slate.9"))
                                    for t in ["Tên lớp", "Khoa", "Tên Khoa", "Năm nhập học", "Sĩ số", "Xóa"]
                                ]),
                            ),
                            rx.table.body(rx.foreach(OrgState.filtered_classes, class_row)),
                            width="100%", variant="surface", size="2",
                        ),
                        variant="surface", padding="4", width="100%",
                    ),
                    spacing="4", width="100%",
                ),
                rx.fragment(),
            ),

            # Modals
            add_dept_modal(),
            add_subject_modal(),
            add_class_modal(),
            org_delete_dialog(),

            spacing="5", width="100%",
        ),
        current_route="/admin/organization",
    )

