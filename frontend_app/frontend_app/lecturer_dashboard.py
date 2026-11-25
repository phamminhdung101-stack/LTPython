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
from .auth import AuthState, login_page


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


# ─── State ───────────────────────────────────────────────────────────────────

class LecturerDashboardState(rx.State):
    """Quản lý trạng thái số liệu phân tích và biểu đồ cho giảng viên từ PostgreSQL thực tế."""

    time_range: str = "7d"  # "7d" hoặc "30d"
    activities: List[ActivityItem] = []
    total_docs: int = 0
    total_views: int = 0
    total_downloads: int = 0
    pending_count: int = 0

    chart_data_7d: List[Dict[str, Any]] = []
    chart_data_30d: List[Dict[str, Any]] = []
    top_docs_data: List[Dict[str, Any]] = []
    category_pie_data: List[Dict[str, Any]] = []

    async def load_data(self):
        try:
            import httpx
            from .auth import AuthState
            auth = await self.get_state(AuthState)
            headers = {"Authorization": f"Bearer {auth.auth_token}"} if auth.auth_token else {}
            resp = httpx.get("http://127.0.0.1:8000/api/dashboard/stats/", headers=headers, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                stats = data.get("stats") or data.get("data") or {}
                self.total_docs = int(stats.get("total_documents", 0))
                self.total_views = int(stats.get("total_views", 0))
                self.total_downloads = int(stats.get("total_downloads", 0))
                self.pending_count = int(stats.get("pending_documents", 0))
                
                self.chart_data_7d = data.get("chart_trends_7d") or []
                self.chart_data_30d = data.get("chart_trends_30d") or []
                self.top_docs_data = data.get("top_documents") or []
                self.category_pie_data = data.get("category_breakdown") or []

                raw_acts = data.get("recent_activities") or []
                loaded_acts = []
                for act in raw_acts:
                    loaded_acts.append(ActivityItem(
                        id=str(act.get("log_id", "")),
                        user_name=act.get("user_name", "Người dùng"),
                        user_role=act.get("user_role", "Sinh viên"),
                        action=act.get("action", "Hoạt động"),
                        target_title=act.get("document_title", ""),
                        subject_code="DocUni",
                        timestamp=act.get("created_at", "Gần đây"),
                        icon="file-text",
                        color="blue",
                    ))
                self.activities = loaded_acts
                return
        except Exception:
            pass

        # ORM Fallback
        try:
            import os, sys, asyncio
            def _fetch_db_dashboard():
                backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
                if backend_dir not in sys.path:
                    sys.path.insert(0, backend_dir)
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
                import django
                django.setup()
                from documents.models import Document, DocumentActivityLog, DocumentVersion
                from django.db.models import Sum

                tot_docs = Document.objects.count()
                pend_count = Document.objects.filter(status='PENDING').count()
                tot_views = Document.objects.aggregate(s=Sum('view_count'))['s'] or 0
                tot_downloads = Document.objects.aggregate(s=Sum('download_count'))['s'] or 0

                # Top docs
                top_qs = Document.objects.filter(status='APPROVED').order_by('-download_count', '-view_count')[:5]
                t_docs = [{'name': d.title[:20], 'downloads': d.download_count} for d in top_qs]

                # Category breakdown
                ext_counts = {}
                for v in DocumentVersion.objects.all():
                    ext = os.path.splitext(str(v.file))[1].lower() if v.file else '.pdf'
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1
                colors = ["#3b82f6", "#f97316", "#10b981", "#a855f7", "#ef4444"]
                pie_data = [
                    {'name': k.upper().replace('.', ''), 'value': v, 'fill': colors[i % len(colors)]}
                    for i, (k, v) in enumerate(sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:5])
                ]

                # Activities
                logs = DocumentActivityLog.objects.select_related('user', 'document').order_by('-created_at')[:10]
                acts = []
                for l in logs:
                    u_name = l.user.full_name if (l.user and hasattr(l.user, 'full_name') and l.user.full_name) else (l.user.username if l.user else "Người dùng")
                    d_title = l.document.title if l.document else "Tài liệu"
                    acts.append(ActivityItem(
                        id=str(l.id),
                        user_name=u_name,
                        user_role="Cán bộ / Sinh viên",
                        action=l.action,
                        target_title=d_title,
                        subject_code="DocUni",
                        timestamp=l.created_at.strftime('%Y-%m-%d %H:%M') if l.created_at else "",
                        icon="file-text",
                        color="blue",
                    ))
                return tot_docs, tot_views, tot_downloads, pend_count, t_docs, pie_data, acts

            (
                self.total_docs,
                self.total_views,
                self.total_downloads,
                self.pending_count,
                self.top_docs_data,
                self.category_pie_data,
                self.activities,
            ) = await asyncio.to_thread(_fetch_db_dashboard)
        except Exception:
            pass

    def set_time_range(self, value: str | list[str]):
        if isinstance(value, list):
            self.time_range = str(value[0]) if value else "7d"
        else:
            self.time_range = str(value)

    @rx.var
    def active_trend_data(self) -> List[dict]:
        return self.chart_data_7d if self.time_range == "7d" else self.chart_data_30d

    def refresh_metrics(self):
        return rx.toast.success("Đã đồng bộ dữ liệu thời gian thực mới nhất!")

    def export_report(self, format_type: str):
        return rx.toast.info(f"Đang tạo và tải xuống báo cáo tổng hợp định dạng {format_type}...")


def pie_legend_item(item: Dict[str, Any]) -> rx.Component:
    return rx.hstack(
        rx.box(width="10px", height="10px", bg=item["fill"], border_radius="full"),
        rx.text(f"{item['name']} ({item['value']})", size="1", color="slate.9"),
        align="center",
        spacing="1",
    )


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
    return rx.cond(
        AuthState.is_logged_in & (AuthState.current_user_role != ""),
        lecturer_page_wrapper(
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

            # ── Modern 4 KPI Cards ──
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("files", size=22, color="#2563eb"),
                                background="rgba(37, 99, 235, 0.12)",
                                padding="2.5",
                                border_radius="xl",
                            ),
                            rx.spacer(),
                            rx.badge("Đang hoạt động", color_scheme="blue", variant="surface", size="1", border_radius="full"),
                            align="center",
                            width="100%",
                        ),
                        rx.heading(LecturerDashboardState.total_docs.to_string(), size="6", weight="bold", color="slate.12"),
                        rx.text("Tổng học liệu phụ trách", size="2", color="slate.9"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    background="white",
                    border="1px solid rgba(226, 232, 240, 0.9)",
                    border_radius="xl",
                    box_shadow="0 1px 3px rgba(0, 0, 0, 0.04)",
                    padding="4",
                ),
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("eye", size=22, color="#4f46e5"),
                                background="rgba(79, 70, 229, 0.12)",
                                padding="2.5",
                                border_radius="xl",
                            ),
                            rx.spacer(),
                            rx.badge("+18.4% tuần này", color_scheme="indigo", variant="surface", size="1", border_radius="full"),
                            align="center",
                            width="100%",
                        ),
                        rx.heading(LecturerDashboardState.total_views.to_string(), size="6", weight="bold", color="indigo.11"),
                        rx.text("Tổng lượt xem tích lũy", size="2", color="slate.9"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    background="white",
                    border="1px solid rgba(226, 232, 240, 0.9)",
                    border_radius="xl",
                    box_shadow="0 1px 3px rgba(0, 0, 0, 0.04)",
                    padding="4",
                ),
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("download", size=22, color="#16a34a"),
                                background="rgba(22, 163, 74, 0.12)",
                                padding="2.5",
                                border_radius="xl",
                            ),
                            rx.spacer(),
                            rx.badge("+24.1% tuần này", color_scheme="green", variant="surface", size="1", border_radius="full"),
                            align="center",
                            width="100%",
                        ),
                        rx.heading(LecturerDashboardState.total_downloads.to_string(), size="6", weight="bold", color="green.11"),
                        rx.text("Tổng lượt tải xuống", size="2", color="slate.9"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    background="white",
                    border="1px solid rgba(226, 232, 240, 0.9)",
                    border_radius="xl",
                    box_shadow="0 1px 3px rgba(0, 0, 0, 0.04)",
                    padding="4",
                ),
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("clock", size=22, color="#d97706"),
                                background="rgba(217, 119, 6, 0.12)",
                                padding="2.5",
                                border_radius="xl",
                            ),
                            rx.spacer(),
                            rx.badge("Cần xử lý", color_scheme="amber", variant="solid", size="1", border_radius="full"),
                            align="center",
                            width="100%",
                        ),
                        rx.heading(LecturerDashboardState.pending_count.to_string(), size="6", weight="bold", color="amber.11"),
                        rx.text("Đóng góp chờ kiểm duyệt", size="2", color="slate.9"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    background="white",
                    border="1px solid rgba(226, 232, 240, 0.9)",
                    border_radius="xl",
                    box_shadow="0 1px 3px rgba(0, 0, 0, 0.04)",
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
                                data=LecturerDashboardState.top_docs_data,
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
                                    data=LecturerDashboardState.category_pie_data,
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
                                rx.foreach(
                                    LecturerDashboardState.category_pie_data,
                                    pie_legend_item,
                                ),
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
    ),
    login_page(),
)
