import reflex as rx

class State(rx.State):
    """The app state."""
    
    search_query: str = ""

    def set_search_query(self, value: str):
        self.search_query = value

def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("DocUni - Hệ thống Tài liệu Sinh viên", size="9"),
            rx.text("Khám phá giáo trình, bài giảng, đề thi... (Viết bằng 100% Python/Reflex)", size="5", color="gray"),
            rx.hstack(
                rx.input(placeholder="Nhập tên môn học, mã môn...", width="300px", on_change=State.set_search_query),
                rx.button("Tìm kiếm", color_scheme="blue", variant="solid"),
            ),
            rx.link(rx.button("Truy cập Trang quản lý sinh viên", color_scheme="green", variant="outline"), href="/documents"),
            align="center",
            spacing="7",
            font_family="Inter",
        ),
        height="100vh",
    )

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
app.add_page(index, route="/")
app.add_page(document_list, route="/documents")
app.add_page(user_management, route="/admin/users")

