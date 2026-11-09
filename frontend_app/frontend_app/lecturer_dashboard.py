"""
DocUni - Trang Dashboard Giảng Viên (Task 4.4)
Route: /lecturer/dashboard
Framework: Reflex (Python Full-Stack)

Cung cấp bảng điều khiển trung tâm dành cho giảng viên:
- Thống kê 4 thẻ KPI: Tổng tài liệu, Lượt xem tích lũy, Lượt tải về, Hàng đợi chờ duyệt.
- Biểu đồ Reflex Recharts:
  - Area Chart: Xu hướng lượt xem và tải về qua các mốc thời gian.
  - Bar Chart: Top 5 học liệu được tải và quan tâm nhiều nhất.
  - Pie Chart: Cơ cấu phân bổ các loại tài liệu trong kho.
- Nhật ký hoạt động tương tác gần đây (Recent Activities).
- Phím tắt hành động nhanh (Quick Actions).
"""

import dataclasses
from typing import List, Dict, Any
import reflex as rx
from .common_components import lecturer_page_wrapper


# ─── Dataclass Models ────────────────────────────────────────────────────────

@dataclasses.dataclass
class ActivityItem:
    id: str = ""
    user_name: str = ""
    user_role: str = "Sinh viên"
    action: str = "Đã tải xuống"
    target_title: str = ""
    subject_code: str = ""
    timestamp: str = ""
    icon: str = "download"
    color: str = "blue"


# ─── Initial Mock Chart Data ─────────────────────────────────────────────────

CHART_DATA_7D = [
    {"date": "Thứ 2", "views": 420, "downloads": 150},
    {"date": "Thứ 3", "views": 680, "downloads": 240},
    {"date": "Thứ 4", "views": 850, "downloads": 310},
    {"date": "Thứ 5", "views": 1100, "downloads": 480},
    {"date": "Thứ 6", "views": 980, "downloads": 420},
    {"date": "Thứ 7", "views": 750, "downloads": 290},
    {"date": "Chủ nhật", "views": 610, "downloads": 210},
]

CHART_DATA_30D = [
    {"date": "Tuần 1", "views": 2400, "downloads": 950},
    {"date": "Tuần 2", "views": 3100, "downloads": 1280},
    {"date": "Tuần 3", "views": 3800, "downloads": 1540},
    {"date": "Tuần 4", "views": 2420, "downloads": 930},
]

TOP_DOCS_DATA = [
    {"name": "IT101 Đề thi", "downloads": 1650},
    {"name": "IT202 CTDL", "downloads": 1240},
    {"name": "IT305 Slide", "downloads": 890},
    {"name": "IT410 BTL", "downloads": 540},
    {"name": "IT420 Sách", "downloads": 380},
]

CATEGORY_PIE_DATA = [
    {"name": "Giáo trình", "value": 35, "fill": "#3b82f6"},
    {"name": "Slide Bài giảng", "value": 28, "fill": "#f97316"},
    {"name": "Đề thi & Đáp án", "value": 20, "fill": "#ef4444"},
    {"name": "Bài tập lớn", "value": 17, "fill": "#a855f7"},
]

MOCK_ACTIVITIES = [
    ActivityItem("a1", "Lê Hoàng Nam", "Sinh viên", "Đã nộp bài đóng góp mới", "Slide Tóm tắt Chương 5: Cây AVL", "IT202", "10 phút trước", "upload", "indigo"),
    ActivityItem("a2", "Trần Thị Mai", "Sinh viên", "Đã nộp bài đóng góp mới", "50 câu trắc nghiệm Kinh tế vi mô", "ECO101", "25 phút trước", "upload", "indigo"),
    ActivityItem("a3", "Nguyễn Văn Hùng", "Sinh viên", "Đã tải xuống tài liệu", "Giáo trình CTDL và Giải thuật 2026", "IT202", "1 giờ trước", "download", "green"),
    ActivityItem("a4", "Phạm Minh Đức", "Sinh viên", "Đã tải xuống tài liệu", "Slide Cơ sở dữ liệu nâng cao", "IT305", "2 giờ trước", "download", "green"),
    ActivityItem("a5", "TS. Nguyễn Văn An", "Giảng viên", "Đã phê duyệt tài liệu", "Sổ tay Từ vựng Hàng không ICAO", "ENG201", "Hôm qua", "circle-check", "purple"),
]


# ─── State ───────────────────────────────────────────────────────────────────

class LecturerDashboardState(rx.State):
    """Quản lý trạng thái số liệu phân tích và biểu đồ cho giảng viên."""

    time_range: str = "7d"  # "7d" hoặc "30d"
    activities: List[ActivityItem] = MOCK_ACTIVITIES

    def set_time_range(self, value: str | list[str]):
        if isinstance(value, list):
            self.time_range = str(value[0]) if value else "7d"
        else:
            self.time_range = str(value)

    @rx.var
    def active_trend_data(self) -> List[dict]:
        return CHART_DATA_7D if self.time_range == "7d" else CHART_DATA_30D

    def refresh_metrics(self):
        return rx.toast.success("Đã đồng bộ dữ liệu thời gian thực mới nhất!")

    def export_report(self, format_type: str):
        return rx.toast.info(f"Đang tạo và tải xuống báo cáo tổng hợp định dạng {format_type}...")


# ─── UI Helper Components ────────────────────────────────────────────────────

def activity_row(act: ActivityItem) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(act.icon, size=15, color=f"var(--{act.color}-9)"),
            bg=f"var(--{act.color}-3)",
            padding="2",
            border_radius="lg",
        ),
        rx.vstack(
            rx.hstack(
                rx.text(act.user_name, size="2", weight="bold", color="slate.12"),
                rx.badge(act.subject_code, color_scheme="blue", variant="surface", size="1"),
                align="center",
                spacing="2",
            ),
            rx.text(f"{act.action}: {act.target_title}", size="1", color="slate.10", line_clamp=1),
            rx.text(act.timestamp, size="1", color="slate.8"),
            spacing="0",
            align="start",
            flex="1",
        ),
        align="center",
        spacing="3",
        padding_y="2",
        border_bottom="1px solid var(--slate-3)",
        width="100%",
    )


# ─── Main Page ───────────────────────────────────────────────────────────────

def lecturer_dashboard_page() -> rx.Component:
    return lecturer_page_wrapper(
        rx.vstack(
            # ── Top Header & Actions ──
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Bảng Điều Khiển Tổng Quan Giảng Viên", size="6", weight="bold", color="slate.12"),
                        rx.badge("Live Analytics", color_scheme="green", variant="surface", size="1"),
                        align="center",
                        spacing="2",
                    ),
                    rx.text(
                        "Theo dõi hiệu suất học liệu, phân tích xu hướng học tập của sinh viên và xử lý yêu cầu kiểm duyệt",
                        size="2",
                        color="slate.9",
                    ),
                    spacing="1",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        rx.icon("refresh-cw", size=14),
                        "Làm mới",
                        variant="surface",
                        color_scheme="gray",
                        size="2",
                        on_click=LecturerDashboardState.refresh_metrics,
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("clipboard-check", size=14),
                            "Kiểm duyệt (2)",
                            color_scheme="amber",
                            variant="solid",
                            size="2",
                        ),
                        href="/lecturer/approval",
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("plus", size=14),
                            "Thêm học liệu",
                            color_scheme="indigo",
                            variant="solid",
                            size="2",
                        ),
                        href="/lecturer/documents",
                    ),
                    align="center",
                    spacing="2",
                ),
                align="center",
                width="100%",
            ),

            rx.divider(color_scheme="gray"),

            # ── 4 KPI Cards ──
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("files", size=22, color="var(--blue-9)"),
                                bg="blue.3",
                                padding="2.5",
                                border_radius="xl",
                            ),
                            rx.spacer(),
                            rx.badge("+1 môn mới", color_scheme="blue", variant="surface", size="1"),
                            align="center",
                            width="100%",
                        ),
                        rx.heading("5", size="6", weight="bold", color="slate.12"),
                        rx.text("Tổng học liệu phụ trách", size="2", color="slate.9"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    padding="4",
                ),
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("eye", size=22, color="var(--indigo-9)"),
                                bg="indigo.3",
                                padding="2.5",
                                border_radius="xl",
                            ),
                            rx.spacer(),
                            rx.badge("+18.4% tuần này", color_scheme="indigo", variant="surface", size="1"),
                            align="center",
                            width="100%",
                        ),
                        rx.heading("11,720", size="6", weight="bold", color="indigo.11"),
                        rx.text("Tổng lượt xem tích lũy", size="2", color="slate.9"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    padding="4",
                ),
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("download", size=22, color="var(--green-9)"),
                                bg="green.3",
                                padding="2.5",
                                border_radius="xl",
                            ),
                            rx.spacer(),
                            rx.badge("+24.1% tuần này", color_scheme="green", variant="surface", size="1"),
                            align="center",
                            width="100%",
                        ),
                        rx.heading("4,700", size="6", weight="bold", color="green.11"),
                        rx.text("Tổng lượt tải xuống", size="2", color="slate.9"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    padding="4",
                ),
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("clock", size=22, color="var(--amber-9)"),
                                bg="amber.3",
                                padding="2.5",
                                border_radius="xl",
                            ),
                            rx.spacer(),
                            rx.badge("Cần xử lý", color_scheme="amber", variant="solid", size="1"),
                            align="center",
                            width="100%",
                        ),
                        rx.heading("2", size="6", weight="bold", color="amber.11"),
                        rx.text("Đóng góp chờ kiểm duyệt", size="2", color="slate.9"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    padding="4",
                ),
                columns="4",
                spacing="3",
                width="100%",
            ),

            # ── Main Charts Grid ──
            rx.grid(
                # ── Left Column (2/3 width): Area Chart & Bar Chart ──
                rx.vstack(
                    # Chart 1: Area Chart xu hướng xem và tải
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.vstack(
                                    rx.heading("Xu Hướng Tương Tác Học Liệu", size="4", weight="bold", color="slate.12"),
                                    rx.text("So sánh giữa lượt xem trực tuyến và lượt tải xuống tệp", size="1", color="slate.8"),
                                    spacing="0",
                                ),
                                rx.spacer(),
                                rx.segmented_control.root(
                                    rx.segmented_control.item("7 ngày qua", value="7d"),
                                    rx.segmented_control.item("30 ngày qua", value="30d"),
                                    value=LecturerDashboardState.time_range,
                                    on_change=LecturerDashboardState.set_time_range,
                                    size="1",
                                ),
                                align="center",
                                width="100%",
                            ),
                            rx.hstack(
                                rx.hstack(
                                    rx.box(width="12px", height="12px", bg="#3b82f6", border_radius="sm"),
                                    rx.text("Lượt xem bài giảng", size="1", color="slate.10", weight="medium"),
                                    align="center",
                                    spacing="1",
                                ),
                                rx.hstack(
                                    rx.box(width="12px", height="12px", bg="#10b981", border_radius="sm"),
                                    rx.text("Lượt tải xuống", size="1", color="slate.10", weight="medium"),
                                    align="center",
                                    spacing="1",
                                ),
                                spacing="4",
                                padding_y="1",
                            ),
                            # Recharts Area Chart
                            rx.recharts.area_chart(
                                rx.recharts.area(
                                    data_key="views",
                                    stroke="#3b82f6",
                                    fill="#93c5fd",
                                    fill_opacity=0.4,
                                    stroke_width=2,
                                    name="Lượt xem",
                                ),
                                rx.recharts.area(
                                    data_key="downloads",
                                    stroke="#10b981",
                                    fill="#a7f3d0",
                                    fill_opacity=0.5,
                                    stroke_width=2,
                                    name="Lượt tải",
                                ),
                                rx.recharts.x_axis(data_key="date", stroke="#94a3b8"),
                                rx.recharts.y_axis(stroke="#94a3b8"),
                                rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#e2e8f0"),
                                rx.recharts.graphing_tooltip(),
                                data=LecturerDashboardState.active_trend_data,
                                width="100%",
                                height=280,
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        variant="surface",
                        padding="4",
                        width="100%",
                    ),

                    # Chart 2: Bar Chart Top tài liệu tải nhiều nhất
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.vstack(
                                    rx.heading("Top 5 Tài Liệu Được Tải Nhiều Nhất", size="4", weight="bold", color="slate.12"),
                                    rx.text("Xếp hạng theo tổng số lượt tải xuống thành công", size="1", color="slate.8"),
                                    spacing="0",
                                ),
                                rx.spacer(),
                                rx.button(
                                    rx.icon("file-spreadsheet", size=13),
                                    "Xuất Excel",
                                    size="1",
                                    variant="surface",
                                    color_scheme="green",
                                    on_click=LecturerDashboardState.export_report("Excel"),
                                ),
                                align="center",
                                width="100%",
                            ),
                            rx.recharts.bar_chart(
                                rx.recharts.bar(
                                    data_key="downloads",
                                    fill="#6366f1",
                                    radius=[4, 4, 0, 0],
                                    name="Lượt tải",
                                ),
                                rx.recharts.x_axis(data_key="name", stroke="#94a3b8"),
                                rx.recharts.y_axis(stroke="#94a3b8"),
                                rx.recharts.cartesian_grid(stroke_dasharray="3 3", stroke="#e2e8f0"),
                                rx.recharts.graphing_tooltip(),
                                data=TOP_DOCS_DATA,
                                width="100%",
                                height=220,
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        variant="surface",
                        padding="4",
                        width="100%",
                    ),

                    spacing="4",
                    width="100%",
                ),

                # ── Right Column (1/3 width): Pie Chart & Activities Feed ──
                rx.vstack(
                    # Chart 3: Pie Chart cơ cấu tài liệu
                    rx.card(
                        rx.vstack(
                            rx.heading("Cơ Cấu Loại Học Liệu", size="4", weight="bold", color="slate.12"),
                            rx.text("Tỷ lệ phân bổ theo danh mục tài liệu", size="1", color="slate.8"),
                            rx.recharts.pie_chart(
                                rx.recharts.pie(
                                    data=CATEGORY_PIE_DATA,
                                    data_key="value",
                                    name_key="name",
                                    cx="50%",
                                    cy="50%",
                                    outer_radius=75,
                                    inner_radius=40,
                                    label=True,
                                ),
                                rx.recharts.graphing_tooltip(),
                                width="100%",
                                height=200,
                            ),
                            # Chú thích màu sắc
                            rx.grid(
                                *[
                                    rx.hstack(
                                        rx.box(width="10px", height="10px", bg=item["fill"], border_radius="full"),
                                        rx.text(f"{item['name']} ({item['value']}%)", size="1", color="slate.9"),
                                        align="center",
                                        spacing="1",
                                    )
                                    for item in CATEGORY_PIE_DATA
                                ],
                                columns="2",
                                spacing="2",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        variant="surface",
                        padding="4",
                        width="100%",
                    ),

                    # Feed: Hoạt động gần đây
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.heading("Hoạt Động Gần Đây", size="4", weight="bold", color="slate.12"),
                                rx.spacer(),
                                rx.badge("Thời gian thực", color_scheme="blue", variant="surface", size="1"),
                                align="center",
                                width="100%",
                            ),
                            rx.text("Nhật ký tương tác học liệu của sinh viên và giảng viên", size="1", color="slate.8"),
                            rx.vstack(
                                rx.foreach(
                                    LecturerDashboardState.activities,
                                    activity_row,
                                ),
                                spacing="1",
                                width="100%",
                                max_height="320px",
                                overflow_y="auto",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        variant="surface",
                        padding="4",
                        width="100%",
                    ),

                    spacing="4",
                    width="100%",
                ),

                columns="2",
                spacing="4",
                width="100%",
            ),

            spacing="4",
            width="100%",
        ),
        current_route="/lecturer/dashboard",
    )
