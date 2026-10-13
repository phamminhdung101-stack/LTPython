"""
DocUni - Trang Kiểm Duyệt Tài Liệu Sinh Viên Đóng Góp (Task 4.2)
Route: /lecturer/approval
Framework: Reflex (Python Full-Stack)

Cung cấp giao diện hàng đợi kiểm duyệt dành cho giảng viên:
- Bố cục xem trước kép (Side-by-Side Split View):
  - Cột trái: Hàng đợi duyệt tài liệu với bộ lọc trạng thái (Chờ duyệt, Đã duyệt, Từ chối).
  - Cột phải: Xem chi tiết thông tin sinh viên, metadata học liệu, khung đọc trước tài liệu.
- Quy trình phê duyệt / từ chối:
  - Nút "Phê duyệt": Xuất bản tài liệu vào kho học liệu chính thức.
  - Nút "Từ chối": Nhập lý do phản hồi gửi về cho sinh viên để nộp lại bản v2.0.
"""

import dataclasses
from datetime import datetime
from typing import List, Dict, Any
import reflex as rx
from .common_components import lecturer_page_wrapper, status_badge


# ─── Dataclass Models ────────────────────────────────────────────────────────

@dataclasses.dataclass
class PendingDoc:
    id: str = ""
    title: str = ""
    subject_code: str = ""
    subject_name: str = ""
    faculty: str = "CNTT"
    proposed_folder: str = ""
    doc_type: str = "SLIDE"  # "TEXTBOOK", "SLIDE", "EXAM", "EXERCISE", "REFERENCE"
    type_label: str = "Slide"
    type_color: str = "orange"
    file_name: str = ""
    file_size: str = ""
    description: str = ""
    tags: List[str] = dataclasses.field(default_factory=list)
    student_name: str = ""
    student_id: str = ""
    student_class: str = ""
    submitted_at: str = ""
    status: str = "PENDING"  # "PENDING", "APPROVED", "REJECTED"
    review_feedback: str = ""
    version: str = "v1.0"
    preview_text: str = ""


# ─── Initial Mock Data ───────────────────────────────────────────────────────

MOCK_PENDING_DOCS = [
    PendingDoc(
        id="pdoc_1",
        title="Slide Tóm tắt Chương 5: Cây nhị phân và Cây AVL",
        subject_code="IT202",
        subject_name="Cấu trúc dữ liệu & GT",
        faculty="CNTT",
        proposed_folder="Slide Bài giảng",
        doc_type="SLIDE",
        type_label="Slide Bài giảng",
        type_color="orange",
        file_name="IT202_Slide_CayNhiPhan_AVL.pptx",
        file_size="6.8 MB",
        description="Em tổng hợp các thao tác xoay đơn LL, RR và xoay kép LR, RL trên cây AVL kèm mã giả thuật toán để các bạn dễ ôn thi.",
        tags=["ctdl", "cay-avl", "slide", "it202"],
        student_name="Lê Hoàng Nam",
        student_id="2151010045",
        student_class="D21CQCN01-B",
        submitted_at="2026-10-13 08:30",
        status="PENDING",
        review_feedback="",
        version="v1.0",
        preview_text=(
            "=== CHƯƠNG 5: CÂY NHỊ PHÂN TỰ CÂN BẰNG AVL ===\n\n"
            "1. Định nghĩa Cây AVL:\n"
            "Cây AVL là cây nhị phân tìm kiếm mà tại mỗi nút, chênh lệch chiều cao giữa cây con trái và cây con phải (hệ số cân bằng BF) không vượt quá 1:\n"
            "   BF(v) = height(left) - height(right) ∈ {-1, 0, 1}\n\n"
            "2. Các phép xoay cân bằng cơ bản:\n"
            "• Phép xoay đơn LL: Mất cân bằng lệch trái-trái do chèn nút vào cây con trái của nút con trái. Thực hiện xoay phải tại gốc mất cân bằng.\n"
            "• Phép xoay đơn RR: Mất cân bằng lệch phải-phải. Thực hiện xoay trái tại gốc mất cân bằng.\n"
            "• Phép xoay kép LR: Mất cân bằng lệch trái-phải. Thực hiện xoay trái tại con trái, sau đó xoay phải tại gốc.\n"
            "• Phép xoay kép RL: Mất cân bằng lệch phải-trái. Thực hiện xoay phải tại con phải, sau đó xoay trái tại gốc.\n\n"
            "3. Độ phức tạp:\n"
            "Thao tác tìm kiếm, chèn, xóa trên cây AVL luôn được đảm bảo ở mức tối ưu O(log n)."
        ),
    ),
    PendingDoc(
        id="pdoc_2",
        title="Bộ 50 câu trắc nghiệm Ôn thi Kinh tế vi mô có giải thích",
        subject_code="ECO101",
        subject_name="Kinh tế vi mô",
        faculty="KT",
        proposed_folder="Đề thi & Đáp án",
        doc_type="EXAM",
        type_label="Đề thi & Đáp án",
        type_color="red",
        file_name="TracNghiem_KTVM_50Cau_GiaiThich.pdf",
        file_size="3.4 MB",
        description="Tổng hợp câu hỏi trắc nghiệm về độ co giãn, thặng dư tiêu dùng, cân bằng thị trường có giải thích chi tiết đáp án.",
        tags=["ktvm", "trac-nghiem", "eco101"],
        student_name="Trần Thị Mai",
        student_id="2152010112",
        student_class="D21CQKT02-B",
        submitted_at="2026-10-12 17:15",
        status="PENDING",
        review_feedback="",
        version="v1.0",
        preview_text=(
            "=== 50 CÂU TRẮC NGHIỆM KINH TẾ VI MÔ ÔN THI CUỐI KỲ ===\n\n"
            "Câu 1: Khi giá hàng hóa X tăng 10% làm lượng cầu hàng hóa Y tăng 15%, hệ số co giãn chéo Exy là:\n"
            "A. -1.5\n"
            "B. +1.5 (Đáp án đúng)\n"
            "C. +0.67\n"
            "D. -0.67\n"
            "=> Giải thích: Exy = %ΔQy / %ΔPx = 15% / 10% = +1.5 > 0 => X và Y là hai hàng hóa thay thế cho nhau.\n\n"
            "Câu 2: Đường giới hạn khả năng sản xuất (PPF) dịch chuyển ra phía ngoài khi:\n"
            "A. Tỷ lệ thất nghiệp trong nền kinh tế tăng cao\n"
            "B. Nền kinh tế xảy ra lạm phát mạnh\n"
            "C. Có sự cải tiến công nghệ hoặc tăng nguồn lực sản xuất (Đáp án đúng)\n"
            "D. Chính phủ áp đặt mức giá trần đối với lương thực"
        ),
    ),
    PendingDoc(
        id="pdoc_3",
        title="Bài tập lớn & Script SQL Quản lý chuỗi cửa hàng tiện lợi",
        subject_code="IT305",
        subject_name="Cơ sở dữ liệu",
        faculty="CNTT",
        proposed_folder="Bài tập & Đồ án",
        doc_type="EXERCISE",
        type_label="Bài tập lớn",
        type_color="purple",
        file_name="BTL_SQL_QLCuaHangTienLoi.sql",
        file_size="1.9 MB",
        description="Mã nguồn SQL tạo bảng, khóa chính, khóa ngoại và 15 stored procedures nghiệp vụ quản lý kho.",
        tags=["csdl", "sql", "btl"],
        student_name="Nguyễn Văn Hùng",
        student_id="2151010088",
        student_class="D21CQCN02-B",
        submitted_at="2026-10-11 10:40",
        status="REJECTED",
        review_feedback="Mã nguồn SQL chưa có lệnh tạo Index cho các bảng có hơn 100k bản ghi. Vui lòng bổ sung lược đồ quan hệ và kịch bản test trước khi nộp lại.",
        version="v1.0",
        preview_text=(
            "-- DATABASE SCHEMA: HE THONG QUAN LY CHUOI CUA HANG TIEN LOI\n"
            "-- TAC GIA: NGUYEN VAN HUNG - D21CQCN02-B\n\n"
            "CREATE TABLE Categories (\n"
            "    CategoryID INT PRIMARY KEY IDENTITY(1,1),\n"
            "    CategoryName NVARCHAR(100) NOT NULL,\n"
            "    Description NVARCHAR(255)\n"
            ");\n\n"
            "CREATE TABLE Products (\n"
            "    ProductID INT PRIMARY KEY IDENTITY(1,1),\n"
            "    ProductName NVARCHAR(150) NOT NULL,\n"
            "    CategoryID INT FOREIGN KEY REFERENCES Categories(CategoryID),\n"
            "    UnitPrice DECIMAL(18,2) NOT NULL,\n"
            "    UnitsInStock INT DEFAULT 0\n"
            ");"
        ),
    ),
    PendingDoc(
        id="pdoc_4",
        title="Sổ tay Từ vựng Chuyên ngành Tiếng Anh Hàng không ICAO",
        subject_code="ENG201",
        subject_name="Tiếng Anh chuyên ngành",
        faculty="NN",
        proposed_folder="Sách tham khảo",
        doc_type="REFERENCE",
        type_label="Tham khảo",
        type_color="green",
        file_name="Aviation_English_Vocabulary_ICAO.pdf",
        file_size="5.2 MB",
        description="Sổ tay tra cứu 300 thuật ngữ thoại buồng lái và kiểm soát không lưu chuẩn hóa ICAO.",
        tags=["tieng-anh", "hang-khong", "icao"],
        student_name="Phạm Minh Đức",
        student_id="2253010023",
        student_class="D22CQNN01-B",
        submitted_at="2026-10-10 14:00",
        status="APPROVED",
        review_feedback="Tài liệu chất lượng cao, định dạng rõ ràng, phù hợp làm tài liệu học phần tham khảo bổ trợ.",
        version="v1.0",
        preview_text=(
            "=== SỔ TAY THUẬT NGỮ THOẠI HÀNG KHÔNG CHUẨN ICAO ===\n\n"
            "1. ROGER: Đã nhận đầy đủ toàn bộ thông tin vừa phát.\n"
            "2. WILCO: Đã hiểu và sẽ tuân thủ thực hiện huấn lệnh (Will Comply).\n"
            "3. SAY AGAIN: Đề nghị nhắc lại toàn bộ hoặc một phần thông điệp.\n"
            "4. HOLD POSITION: Dừng lại ngay tại vị trí hiện tại trên đường lăn.\n"
            "5. EXPEDITE: Yêu cầu thực hiện thao tác nhanh hơn bình thường để đảm bảo giãn cách an toàn."
        ),
    ),
]


# ─── State ───────────────────────────────────────────────────────────────────

class LecturerApprovalState(rx.State):
    """Quản lý hàng đợi và thao tác phê duyệt tài liệu sinh viên đóng góp."""

    items: List[PendingDoc] = MOCK_PENDING_DOCS
    selected_id: str = "pdoc_1"
    filter_status: str = "PENDING"  # "ALL", "PENDING", "APPROVED", "REJECTED"
    search_query: str = ""

    # Reject Dialog State
    show_reject_dialog: bool = False
    reject_reason_input: str = ""

    def set_search_query(self, value: str):
        self.search_query = value

    def set_filter_status(self, value: str | list[str]):
        if isinstance(value, list):
            self.filter_status = str(value[0]) if value else "ALL"
        else:
            self.filter_status = str(value)

    def set_reject_reason(self, value: str):
        self.reject_reason_input = value

    def select_item(self, item_id: str):
        self.selected_id = item_id

    @rx.var
    def filtered_items(self) -> List[PendingDoc]:
        query = self.search_query.strip().lower()
        docs = self.items

        if self.filter_status != "ALL":
            docs = [d for d in docs if d.status == self.filter_status]

        if query:
            docs = [
                d for d in docs
                if query in d.title.lower()
                or query in d.student_name.lower()
                or query in d.student_id.lower()
                or query in d.subject_code.lower()
            ]
        return docs

    @rx.var
    def active_item(self) -> PendingDoc:
        for d in self.items:
            if d.id == self.selected_id:
                return d
        return self.items[0] if self.items else PendingDoc()

    # Thống kê KPI
    @rx.var
    def pending_count(self) -> int:
        return len([d for d in self.items if d.status == "PENDING"])

    @rx.var
    def approved_count(self) -> int:
        return len([d for d in self.items if d.status == "APPROVED"])

    @rx.var
    def rejected_count(self) -> int:
        return len([d for d in self.items if d.status == "REJECTED"])

    @rx.var
    def total_count(self) -> int:
        return len(self.items)

    @rx.var
    def approval_rate(self) -> str:
        total = len(self.items)
        if total == 0:
            return "0%"
        approved = len([d for d in self.items if d.status == "APPROVED"])
        return f"{int((approved / total) * 100)}%"

    # Thao tác Phê duyệt
    def approve_doc(self, item_id: str):
        updated = []
        for d in self.items:
            if d.id == item_id:
                d.status = "APPROVED"
                d.review_feedback = "Tài liệu đạt chuẩn chất lượng, đã được giảng viên phê duyệt đưa vào kho học liệu."
            updated.append(d)
        self.items = updated
        return rx.toast.success("Đã phê duyệt tài liệu! Học liệu đã được công khai trên kho.")

    # Thao tác Từ chối
    def open_reject_dialog(self, item_id: str):
        self.selected_id = item_id
        self.reject_reason_input = ""
        self.show_reject_dialog = True

    def close_reject_dialog(self):
        self.show_reject_dialog = False
        self.reject_reason_input = ""

    def confirm_reject(self):
        reason = self.reject_reason_input.strip()
        if not reason:
            return rx.toast.error("Vui lòng nhập lý do từ chối để phản hồi cho sinh viên!")

        doc_id = self.selected_id
        updated = []
        for d in self.items:
            if d.id == doc_id:
                d.status = "REJECTED"
                d.review_feedback = reason
            updated.append(d)
        self.items = updated
        self.show_reject_dialog = False
        self.reject_reason_input = ""
        return rx.toast.warning("Đã từ chối tài liệu và gửi phản hồi nhận xét cho sinh viên!")


# ─── UI Helper Components ────────────────────────────────────────────────────

def queue_item_card(doc: PendingDoc) -> rx.Component:
    """Thẻ yêu cầu kiểm duyệt trong cột bên trái."""
    is_active = LecturerApprovalState.selected_id == doc.id

    return rx.card(
        rx.vstack(
            # Top row: Subject code + Status badge
            rx.hstack(
                rx.badge(doc.subject_code, color_scheme="blue", variant="surface", size="1"),
                rx.badge(doc.type_label, color_scheme=doc.type_color, variant="surface", size="1"),
                rx.spacer(),
                status_badge(doc.status),
                align="center",
                width="100%",
            ),

            # Document Title
            rx.text(doc.title, size="2", weight="bold", color="slate.12", line_clamp=2),

            # Student info
            rx.hstack(
                rx.avatar(fallback=doc.student_name[:2], size="1", radius="full", color_scheme="indigo"),
                rx.vstack(
                    rx.text(doc.student_name, size="1", weight="bold", color="slate.11"),
                    rx.text(f"MSSV: {doc.student_id} • {doc.student_class}", size="1", color="slate.8"),
                    spacing="0",
                ),
                align="center",
                spacing="2",
            ),

            # Timestamp & File size
            rx.hstack(
                rx.icon("clock", size=12, color="var(--slate-7)"),
                rx.text(doc.submitted_at, size="1", color="slate.8"),
                rx.spacer(),
                rx.text(doc.file_size, size="1", color="slate.8"),
                align="center",
                width="100%",
            ),

            spacing="2",
            align="start",
            width="100%",
        ),
        variant=rx.cond(is_active, "classic", "surface"),
        border=rx.cond(is_active, "2px solid var(--indigo-8)", "1px solid var(--slate-4)"),
        bg=rx.cond(is_active, "var(--indigo-2)", "white"),
        padding="3",
        _hover={"cursor": "pointer", "border_color": "var(--indigo-7)"},
        transition="all 0.15s ease",
        on_click=LecturerApprovalState.select_item(doc.id),
        width="100%",
    )


def reject_reason_modal() -> rx.Component:
    """Dialog nhập lý do phản hồi khi từ chối bài đóng góp."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("circle-x", size=20, color="var(--red-9)"),
                        bg="red.3",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.heading("Từ Chối & Phản Hồi Chỉnh Sửa", size="4", weight="bold", color="red.11"),
                        rx.text("Gửi lý do nhận xét chi tiết để sinh viên hoàn thiện lại tài liệu", size="2", color="slate.9"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(rx.icon("x", size=16), variant="ghost", color_scheme="gray", size="1"),
                    ),
                    align="center",
                    width="100%",
                ),

                rx.divider(color_scheme="gray"),

                rx.vstack(
                    rx.text("Lý do từ chối / Hướng dẫn chỉnh sửa:", size="2", weight="bold", color="slate.11"),
                    rx.text_area(
                        placeholder="VD: Tài liệu chưa có đáp án câu 4; Cần định dạng lại trang bìa; Đính kèm thêm slide tóm tắt...",
                        value=LecturerApprovalState.reject_reason_input,
                        on_change=LecturerApprovalState.set_reject_reason,
                        size="3",
                        rows="4",
                        width="100%",
                    ),
                    rx.text("Nhận xét này sẽ hiển thị trực tiếp tại trang 'Theo dõi trạng thái duyệt' của sinh viên.", size="1", color="slate.8"),
                    spacing="2",
                    width="100%",
                ),

                # Actions
                rx.hstack(
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button("Hủy bỏ", variant="surface", color_scheme="gray", size="2"),
                    ),
                    rx.button(
                        rx.icon("send", size=14),
                        "Gửi phản hồi từ chối",
                        color_scheme="red",
                        size="2",
                        variant="solid",
                        on_click=LecturerApprovalState.confirm_reject,
                    ),
                    align="center",
                    spacing="2",
                    width="100%",
                    padding_top="2",
                ),

                spacing="4",
                width="100%",
            ),
            max_width="500px",
            padding="5",
        ),
        open=LecturerApprovalState.show_reject_dialog,
        on_open_change=LecturerApprovalState.close_reject_dialog,
    )


# ─── Main Page ───────────────────────────────────────────────────────────────

def lecturer_approval_page() -> rx.Component:
    active = LecturerApprovalState.active_item

    return lecturer_page_wrapper(
        rx.vstack(
            # ── Header Bar ──
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Kiểm Duyệt Học Liệu Đóng Góp Từ Sinh Viên", size="6", weight="bold", color="slate.12"),
                        rx.badge(
                            rx.hstack(
                                rx.icon("clock", size=12),
                                rx.text(LecturerApprovalState.pending_count.to_string(), " chờ duyệt", size="1", weight="bold"),
                                align="center",
                                spacing="1",
                            ),
                            color_scheme="amber",
                            variant="surface",
                            size="2",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    rx.text("Đánh giá nội dung, phê duyệt xuất bản vào kho tài liệu hoặc gửi phản hồi nhận xét cho sinh viên", size="2", color="slate.9"),
                    spacing="1",
                ),
                align="center",
                width="100%",
            ),

            rx.divider(color_scheme="gray"),

            # ── KPI Cards ──
            rx.grid(
                rx.card(
                    rx.hstack(
                        rx.box(
                            rx.icon("clock", size=20, color="var(--amber-9)"),
                            bg="amber.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Chờ kiểm duyệt", size="1", color="slate.8"),
                            rx.text(LecturerApprovalState.pending_count.to_string(), size="5", weight="bold", color="amber.11"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    padding="3",
                ),
                rx.card(
                    rx.hstack(
                        rx.box(
                            rx.icon("circle-check", size=20, color="var(--green-9)"),
                            bg="green.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Đã phê duyệt", size="1", color="slate.8"),
                            rx.text(LecturerApprovalState.approved_count.to_string(), size="5", weight="bold", color="green.11"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    padding="3",
                ),
                rx.card(
                    rx.hstack(
                        rx.box(
                            rx.icon("circle-x", size=20, color="var(--red-9)"),
                            bg="red.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Đã từ chối", size="1", color="slate.8"),
                            rx.text(LecturerApprovalState.rejected_count.to_string(), size="5", weight="bold", color="red.11"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    padding="3",
                ),
                rx.card(
                    rx.hstack(
                        rx.box(
                            rx.icon("check-check", size=20, color="var(--indigo-9)"),
                            bg="indigo.3",
                            padding="2.5",
                            border_radius="lg",
                        ),
                        rx.vstack(
                            rx.text("Tỷ lệ duyệt", size="1", color="slate.8"),
                            rx.text(LecturerApprovalState.approval_rate, size="5", weight="bold", color="indigo.11"),
                            spacing="0",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    padding="3",
                ),
                columns="4",
                spacing="3",
                width="100%",
            ),

            # ── Main Side-by-Side Split View ──
            rx.hstack(
                # ── Left Column: Hàng Đợi Kiểm Duyệt (400px) ──
                rx.vstack(
                    # Search & Tabs
                    rx.card(
                        rx.vstack(
                            rx.input(
                                rx.input.slot(rx.icon("search", size=15, color="var(--slate-8)")),
                                placeholder="Tìm theo tên bài, tên sinh viên, MSSV...",
                                value=LecturerApprovalState.search_query,
                                on_change=LecturerApprovalState.set_search_query,
                                size="2",
                                width="100%",
                            ),
                            rx.segmented_control.root(
                                rx.segmented_control.item("Chờ duyệt", value="PENDING"),
                                rx.segmented_control.item("Đã duyệt", value="APPROVED"),
                                rx.segmented_control.item("Từ chối", value="REJECTED"),
                                rx.segmented_control.item("Tất cả", value="ALL"),
                                value=LecturerApprovalState.filter_status,
                                on_change=LecturerApprovalState.set_filter_status,
                                size="1",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        variant="surface",
                        padding="3",
                        width="100%",
                    ),

                    # Danh sách thẻ hàng đợi cuộn mượt mà
                    rx.box(
                        rx.vstack(
                            rx.foreach(
                                LecturerApprovalState.filtered_items,
                                queue_item_card,
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        max_height="620px",
                        overflow_y="auto",
                        width="100%",
                    ),

                    spacing="3",
                    width=["100%", "100%", "400px"],
                    align="start",
                ),

                # ── Right Column: Khung Xem Chi Tiết & Duyệt (Flex 1) ──
                rx.card(
                    rx.vstack(
                        # 1. Header chi tiết: Sinh viên + Trạng thái
                        rx.hstack(
                            rx.hstack(
                                rx.avatar(fallback=active.student_name[:2], size="3", radius="full", color_scheme="indigo"),
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(active.student_name, size="3", weight="bold", color="slate.12"),
                                        rx.badge(active.student_class, color_scheme="indigo", variant="surface", size="1"),
                                        align="center",
                                        spacing="2",
                                    ),
                                    rx.text(f"Mã sinh viên: {active.student_id} • Khoa: {active.faculty} • Nộp: {active.submitted_at}", size="1", color="slate.9"),
                                    spacing="0",
                                ),
                                align="center",
                                spacing="3",
                            ),
                            rx.spacer(),
                            status_badge(active.status),
                            align="center",
                            width="100%",
                            padding_bottom="3",
                            border_bottom="1px solid var(--slate-4)",
                        ),

                        # 2. Metadata tài liệu đóng góp
                        rx.grid(
                            rx.vstack(
                                rx.text("Tên tài liệu:", size="1", color="slate.8"),
                                rx.text(active.title, size="2", weight="bold", color="slate.12"),
                                spacing="0",
                            ),
                            rx.vstack(
                                rx.text("Môn học:", size="1", color="slate.8"),
                                rx.hstack(
                                    rx.badge(active.subject_code, color_scheme="blue", variant="surface", size="1"),
                                    rx.text(active.subject_name, size="1", color="slate.10", weight="medium"),
                                    align="center",
                                    spacing="1",
                                ),
                                spacing="0",
                            ),
                            rx.vstack(
                                rx.text("Thư mục đề xuất:", size="1", color="slate.8"),
                                rx.badge(active.proposed_folder, color_scheme="gray", variant="surface", size="1"),
                                spacing="0",
                            ),
                            rx.vstack(
                                rx.text("Loại học liệu & Tệp:", size="1", color="slate.8"),
                                rx.hstack(
                                    rx.badge(active.type_label, color_scheme=active.type_color, variant="surface", size="1"),
                                    rx.text(f"{active.file_name} ({active.file_size})", size="1", color="slate.10"),
                                    align="center",
                                    spacing="1",
                                ),
                                spacing="0",
                            ),
                            columns="2",
                            spacing="3",
                            width="100%",
                            padding_y="2",
                        ),

                        # 3. Mô tả của sinh viên
                        rx.vstack(
                            rx.text("Ghi chú của sinh viên:", size="1", weight="bold", color="slate.11"),
                            rx.box(
                                rx.text(active.description, size="2", color="slate.11", line_height="1.5"),
                                bg="var(--slate-2)",
                                padding="3",
                                border_radius="md",
                                border="1px solid var(--slate-4)",
                                width="100%",
                            ),
                            spacing="1",
                            width="100%",
                        ),

                        # 4. Tags
                        rx.hstack(
                            rx.text("Tags:", size="1", weight="bold", color="slate.11"),
                            rx.foreach(
                                active.tags,
                                lambda t: rx.badge(t, color_scheme="blue", variant="surface", size="1"),
                            ),
                            align="center",
                            spacing="2",
                        ),

                        # 5. Khung Preview giả lập tài liệu
                        rx.vstack(
                            rx.hstack(
                                rx.icon("file-text", size=15, color="var(--indigo-9)"),
                                rx.text("Bản Xem Trước Tài Liệu (Document Reader Preview):", size="2", weight="bold", color="indigo.11"),
                                rx.spacer(),
                                rx.badge("Trang 1 / 15", color_scheme="gray", variant="surface", size="1"),
                                align="center",
                                width="100%",
                            ),
                            rx.box(
                                rx.text(
                                    active.preview_text,
                                    size="2",
                                    color="slate.12",
                                    font_family="monospace",
                                    white_space="pre-wrap",
                                    line_height="1.6",
                                ),
                                bg="var(--slate-1)",
                                border="1px solid var(--slate-5)",
                                border_radius="lg",
                                padding="4",
                                max_height="240px",
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                            padding_y="2",
                        ),

                        # 6. Nhận xét phản hồi nếu đã có
                        rx.cond(
                            active.review_feedback != "",
                            rx.card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("message-square", size=14, color="var(--indigo-9)"),
                                        rx.text("Ý kiến nhận xét của giảng viên:", size="1", weight="bold", color="indigo.11"),
                                        align="center",
                                        spacing="1",
                                    ),
                                    rx.text(active.review_feedback, size="2", color="slate.11"),
                                    spacing="1",
                                    width="100%",
                                ),
                                bg="var(--indigo-2)",
                                border="1px solid var(--indigo-5)",
                                padding="3",
                                width="100%",
                            ),
                            rx.fragment(),
                        ),

                        # 7. Thanh thao tác (Action Bar)
                        rx.hstack(
                            rx.cond(
                                active.status == "PENDING",
                                rx.hstack(
                                    rx.button(
                                        rx.icon("circle-check", size=15),
                                        "Phê duyệt & Xuất bản",
                                        color_scheme="green",
                                        size="3",
                                        variant="solid",
                                        on_click=LecturerApprovalState.approve_doc(active.id),
                                    ),
                                    rx.button(
                                        rx.icon("circle-x", size=15),
                                        "Từ chối đóng góp",
                                        color_scheme="red",
                                        size="3",
                                        variant="surface",
                                        on_click=LecturerApprovalState.open_reject_dialog(active.id),
                                    ),
                                    spacing="3",
                                ),
                                rx.badge(
                                    rx.hstack(
                                        rx.icon("info", size=13),
                                        rx.text(f"Hồ sơ này đã ở trạng thái {active.status}", size="1", weight="bold"),
                                        align="center",
                                        spacing="1",
                                    ),
                                    color_scheme=rx.cond(active.status == "APPROVED", "green", "red"),
                                    variant="surface",
                                    size="2",
                                    padding="2",
                                ),
                            ),
                            rx.spacer(),
                            rx.button(
                                rx.icon("download", size=14),
                                "Tải tệp gốc về máy",
                                color_scheme="gray",
                                size="2",
                                variant="surface",
                                on_click=rx.toast.info(f"Đang tải tệp: {active.file_name}"),
                            ),
                            align="center",
                            width="100%",
                            padding_top="3",
                            border_top="1px solid var(--slate-4)",
                        ),

                        spacing="3",
                        width="100%",
                    ),
                    variant="surface",
                    padding="5",
                    flex="1",
                ),

                spacing="4",
                align="start",
                width="100%",
            ),

            # Reject Dialog
            reject_reason_modal(),

            spacing="4",
            width="100%",
        ),
        current_route="/lecturer/approval",
    )
