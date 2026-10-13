"""
DocUni - Trang Trợ Lý Học Tập AI (AI Learning Assistant)
Route: /student/ai-assistant
Framework: Reflex (Python Full-Stack)

Cung cấp trợ lý học tập thông minh dựa trên RAG (Retrieval-Augmented Generation)
kết hợp Semantic Search trên kho tài liệu học phần của trường.
Cho phép hỏi đáp kiến thức, tóm tắt bài giảng, trích dẫn chính xác trang tài liệu
và độ tương đồng ngữ nghĩa (Cosine Similarity %).
"""

import dataclasses
from datetime import datetime
from typing import List, Dict, Any
import reflex as rx
from .common_components import student_page_wrapper


# ─── Dataclass Models Cho State & Dynamic Rendering ──────────────────────────

@dataclasses.dataclass
class Citation:
    id: str = ""
    doc_title: str = ""
    subject_code: str = ""
    page: int = 1
    score: str = ""
    snippet: str = ""
    file_url: str = "/documents"


@dataclasses.dataclass
class ChatMessage:
    id: str = ""
    sender: str = "ai"  # "user" hoặc "ai"
    content: str = ""
    timestamp: str = ""
    mode: str = "rag"  # "rag" hoặc "explain"
    citations: List[Citation] = dataclasses.field(default_factory=list)


# ─── Mock Knowledge Base & Citations ─────────────────────────────────────────

MOCK_KB = [
    {
        "keywords": ["cây nhị phân", "cây", "bst", "tìm kiếm", "cấu trúc dữ liệu", "it202", "đồ thị"],
        "answer": (
            "Trong môn Cấu trúc dữ liệu & Giải thuật (IT202), Cây nhị phân tìm kiếm (Binary Search Tree - BST) "
            "là một cây nhị phân có đặc tính quan trọng:\n\n"
            "1. Giá trị của mọi nút trên cây con bên trái luôn NHỎ HƠN giá trị của nút gốc.\n"
            "2. Giá trị của mọi nút trên cây con bên phải luôn LỚN HƠN giá trị của nút gốc.\n"
            "3. Cả cây con bên trái và bên phải đều phải là cây nhị phân tìm kiếm.\n\n"
            "• Độ phức tạp tìm kiếm/thêm/xóa trung bình: O(log n)\n"
            "• Độ phức tạp trong trường hợp xấu nhất (cây suy biến thành danh sách liên kết): O(n)\n"
            "• Để khắc phục suy biến, giải thuật nâng cao sử dụng Cây tự cân bằng AVL hoặc Cây Đỏ-Đen (Red-Black Tree)."
        ),
        "citations": [
            Citation(
                id="c1",
                doc_title="Giáo trình Cấu trúc dữ liệu và giải thuật",
                subject_code="IT202",
                page=84,
                score="96.5%",
                snippet="Định nghĩa 4.2: Cây nhị phân tìm kiếm T là cây nhị phân hoặc rỗng, hoặc thỏa mãn: mọi khóa trên cây con trái(v) < khóa(v) < mọi khóa trên cây con phải(v). Phép duyệt trung thứ tự (In-order) trên BST sẽ cho dãy khóa có thứ tự tăng dần.",
                file_url="/documents",
            ),
            Citation(
                id="c2",
                doc_title="Slide Bài giảng Chương 4: Cây và Đồ thị",
                subject_code="IT202",
                page=28,
                score="91.8%",
                snippet="Thuật toán chèn nút mới vào BST: Bắt đầu từ gốc, so sánh giá trị cần chèn x với nút hiện tại. Nếu x < current.data thì rẽ trái, ngược lại rẽ phải cho đến khi gặp nút null.",
                file_url="/documents",
            ),
        ],
    },
    {
        "keywords": ["kinh tế vi mô", "cung cầu", "co giãn", "eco101", "độ co giãn", "giá"],
        "answer": (
            "Trong học phần Kinh tế vi mô (ECO101), Độ co giãn của cầu theo giá (Price Elasticity of Demand - Ed) "
            "đo lường mức độ phản ứng của lượng cầu khi giá hàng hóa thay đổi:\n\n"
            "• Công thức tính: Ed = (% Thay đổi của lượng cầu) / (% Thay đổi của mức giá)\n"
            "• Phương pháp trung điểm: Ed = [(Q2 - Q1) / ((Q1 + Q2)/2)] / [(P2 - P1) / ((P1 + P2)/2)]\n\n"
            "Phân loại mức độ co giãn:\n"
            "- |Ed| > 1: Cầu co giãn nhiều (hàng xa xỉ, có nhiều hàng thay thế). Khi giảm giá, tổng doanh thu TR tăng.\n"
            "- |Ed| < 1: Cầu co giãn ít (hàng thiết yếu như lương thực, điện nước). Khi tăng giá, tổng doanh thu TR tăng.\n"
            "- |Ed| = 1: Cầu co giãn đơn vị. Doanh thu cực đại tại điểm này."
        ),
        "citations": [
            Citation(
                id="c3",
                doc_title="Slide Bài giảng Chương 3: Độ co giãn và Ứng dụng",
                subject_code="ECO101",
                page=42,
                score="95.2%",
                snippet="Mối quan hệ giữa độ co giãn và Tổng doanh thu (TR = P x Q): Nếu cầu co giãn (|Ed| > 1), phần trăm tăng lượng bán lớn hơn phần trăm giảm giá => TR tăng khi doanh nghiệp hạ giá bán.",
                file_url="/documents",
            ),
        ],
    },
    {
        "keywords": ["sql", "chuẩn hóa", "cơ sở dữ liệu", "khóa ngoại", "3nf", "it305"],
        "answer": (
            "Chuẩn hóa dữ liệu trong Cơ sở dữ liệu quan hệ (IT305) là kỹ thuật tổ chức các bảng nhằm "
            "loại bỏ dư thừa dữ liệu và ngăn ngừa các dị thường khi Thêm, Sửa, Xóa:\n\n"
            "1. Dạng chuẩn 1 (1NF): Mọi thuộc tính đều mang giá trị nguyên tố (nguyên tử), không chứa danh sách hoặc mảng giá trị.\n"
            "2. Dạng chuẩn 2 (2NF): Đã đạt 1NF và mọi thuộc tính không khóa phải phụ thuộc hàm ĐẦY ĐỦ vào khóa chính (không phụ thuộc vào một phần khóa chính phức hợp).\n"
            "3. Dạng chuẩn 3 (3NF): Đã đạt 2NF và không có thuộc tính không khóa nào phụ thuộc BẮC CẦU vào khóa chính (nghĩa là X -> Y và Y -> Z với Z là thuộc tính không khóa)."
        ),
        "citations": [
            Citation(
                id="c4",
                doc_title="Script SQL & Bài tập lớn Cơ sở dữ liệu",
                subject_code="IT305",
                page=19,
                score="93.4%",
                snippet="Chương 5 - Lý thuyết thiết kế CSDL quan hệ: Định lý Heath và quy trình tách bảo toàn thông tin. Chuẩn hóa về 3NF/BCNF là tiêu chuẩn vàng cho các hệ thống OLTP nghiệp vụ thực tế.",
                file_url="/documents",
            ),
        ],
    },
    {
        "keywords": ["điều hành bay", "atc", "huấn lệnh", "cất cánh", "atc101", "hàng không"],
        "answer": (
            "Trong nghiệp vụ Điều hành bay cơ bản (ATC101), quy trình cấp huấn lệnh xuất phát và cất cánh "
            "tuân theo tiêu chuẩn chuẩn hóa ICAO:\n\n"
            "1. Giai đoạn Delivery / Ground: Cấp huấn lệnh đường dài (IFR Clearance) gồm: Điểm đến, SID (Standard Instrument Departure), mực bay ban đầu và mã Squawk transponder.\n"
            "2. Giai đoạn Pushback & Taxi: Huấn lệnh đẩy lùi khỏi cầu ống lồng và hướng dẫn lăn theo vệt sơn tim đường lăn ra đường băng chờ.\n"
            "3. Giai đoạn Tower (Đài chỉ huy): Huấn lệnh Line-up (vào đường băng chờ) và 'Cleared for Take-off' (Cất cánh) khi đường băng đảm bảo giãn cách an toàn và gió trong ngưỡng cho phép."
        ),
        "citations": [
            Citation(
                id="c5",
                doc_title="Sổ tay Quy trình & Thủ tục Kiểm soát không lưu tại sân",
                subject_code="ATC101",
                page=31,
                score="97.1%",
                snippet="ICAO Doc 4444 PANS-ATM: Mẫu thoại chuẩn cất cánh 'VN123, runway 25R, wind 240 degrees 8 knots, cleared for take-off'. Phi công bắt buộc phải đọc lại (readback) đầy đủ đường băng và lệnh cất cánh.",
                file_url="/documents",
            ),
        ],
    },
]

INITIAL_AI_MESSAGE = ChatMessage(
    id="msg_0",
    sender="ai",
    content=(
        "Chào bạn! Tôi là **DocUni AI Assistant** - Trợ lý học tập thông minh được tích hợp công nghệ "
        "**Semantic Search & RAG (Retrieval-Augmented Generation)** trên kho học liệu chính thức của học viện.\n\n"
        "Tôi có thể hỗ trợ bạn:\n"
        "• 🔍 **Tra cứu tài liệu & trích dẫn nguồn**: Tìm kiếm khái niệm kèm số trang, tài liệu học phần và % độ tương đồng.\n"
        "• 📚 **Tóm tắt nội dung bài giảng**: Rút gọn các chương giáo trình phức tạp thành các ý chính cô đọng.\n"
        "• 💡 **Giải đáp bài tập & ôn thi**: Hướng dẫn giải thuật, công thức kinh tế, quy trình kiểm soát bay...\n\n"
        "Bạn hãy chọn câu hỏi gợi ý bên cạnh hoặc gõ câu hỏi vào ô bên dưới nhé!"
    ),
    timestamp="Vừa xong",
    mode="rag",
    citations=[
        Citation(
            id="c0",
            doc_title="Kho Học Liệu DocUni Hệ Thống",
            subject_code="DocUni-RAG",
            page=1,
            score="100%",
            snippet="Chỉ mục tìm kiếm ngữ nghĩa đã sẵn sàng với 8 học phần chính: CNTT, Kinh tế, Ngoại ngữ, Điều hành bay.",
            file_url="/documents",
        )
    ],
)

QUICK_PROMPTS = [
    {
        "title": "Cây nhị phân tìm kiếm (BST)",
        "prompt": "Giải thích cấu trúc và độ phức tạp giải thuật của Cây nhị phân tìm kiếm trong môn Cấu trúc dữ liệu?",
        "subject": "IT202",
    },
    {
        "title": "Độ co giãn cung cầu",
        "prompt": "Cách tính độ co giãn của cầu theo giá và ý nghĩa đối với tổng doanh thu trong Kinh tế vi mô?",
        "subject": "ECO101",
    },
    {
        "title": "Chuẩn hóa dữ liệu 3NF",
        "prompt": "Các bước chuẩn hóa cơ sở dữ liệu quan hệ từ 1NF lên 3NF cần chú ý điều gì?",
        "subject": "IT305",
    },
    {
        "title": "Quy trình cấp lệnh cất cánh ATC",
        "prompt": "Quy trình và câu thoại ICAO chuẩn khi cấp huấn lệnh cất cánh cho máy bay tại sân bay?",
        "subject": "ATC101",
    },
]

SUBJECT_FILTERS = [
    {"label": "Tất cả học phần (Toàn trường)", "value": "ALL"},
    {"label": "IT202 - Cấu trúc dữ liệu & GT", "value": "IT202"},
    {"label": "ECO101 - Kinh tế vi mô", "value": "ECO101"},
    {"label": "IT305 - Cơ sở dữ liệu", "value": "IT305"},
    {"label": "ATC101 - Điều hành bay cơ bản", "value": "ATC101"},
    {"label": "ENG201 - Tiếng Anh hàng không", "value": "ENG201"},
]


# ─── State ───────────────────────────────────────────────────────────────────

class AIAssistantState(rx.State):
    """Quản lý hội thoại chatbot học tập, truy vấn RAG và modal trích dẫn."""

    chat_history: List[ChatMessage] = [INITIAL_AI_MESSAGE]
    input_text: str = ""
    is_searching: bool = False
    search_mode: str = "rag"  # "rag" hoặc "explain"
    subject_filter: str = "ALL"

    # Citation inspection modal
    show_citation_modal: bool = False
    active_citation: Citation = Citation()

    def set_input_text(self, value: str):
        self.input_text = value

    def set_search_mode(self, mode: str | list[str]):
        if isinstance(mode, list):
            self.search_mode = str(mode[0]) if mode else "rag"
        else:
            self.search_mode = str(mode)

    def set_subject_filter(self, subject: str):
        self.subject_filter = subject

    def clear_chat(self):
        self.chat_history = [INITIAL_AI_MESSAGE]
        self.input_text = ""
        return rx.toast.info("Đã xóa lịch sử hội thoại.")

    def open_citation_modal(self, citation: Citation):
        self.active_citation = citation
        self.show_citation_modal = True

    def close_citation_modal(self):
        self.show_citation_modal = False
        self.active_citation = Citation()

    def ask_quick_prompt(self, prompt: str):
        self.input_text = prompt
        return self.send_message()

    def send_message(self):
        text = self.input_text.strip()
        if not text:
            return rx.toast.error("Vui lòng nhập câu hỏi trước khi gửi!")

        time_now = datetime.now().strftime("%H:%M")
        msg_id = f"msg_{len(self.chat_history) + 1}"

        # 1. Thêm tin nhắn của User
        user_msg = ChatMessage(
            id=msg_id,
            sender="user",
            content=text,
            timestamp=time_now,
            mode=self.search_mode,
            citations=[],
        )
        self.chat_history.append(user_msg)
        self.input_text = ""

        # 2. Xử lý câu trả lời AI (Tìm kiếm trong KB hoặc sinh câu trả lời theo ngữ cảnh)
        q_lower = text.lower()
        matched = None
        for item in MOCK_KB:
            if any(k in q_lower for k in item["keywords"]):
                matched = item
                break

        if matched:
            ai_content = matched["answer"]
            citations = matched["citations"] if self.search_mode == "rag" else []
        else:
            # Phản hồi tổng quát thông minh
            citations = [
                Citation(
                    id=f"gen_cite_{len(self.chat_history)}",
                    doc_title="Kho Giáo trình Tổng hợp DocUni",
                    subject_code=self.subject_filter if self.subject_filter != "ALL" else "IT/ECO",
                    page=12,
                    score="88.6%",
                    snippet=f"Trích xuất liên quan đến truy vấn '{text[:40]}...': Hệ thống DocUni đã đối soát ngữ nghĩa từ các tài liệu tham khảo chính thức và đề thi môn học.",
                    file_url="/documents",
                )
            ] if self.search_mode == "rag" else []

            ai_content = (
                f"Dựa trên cơ sở dữ liệu học phần và các tài liệu liên quan đến chủ đề **'{text}'**:\n\n"
                f"1. **Tổng quan khái niệm**: Yêu cầu này liên quan trực tiếp đến nội dung giảng dạy trong chương trình đào tạo của học viện.\n"
                f"2. **Các điểm cốt lõi cần ghi nhớ**:\n"
                f"   • Đọc kỹ phần lý thuyết nền tảng trong giáo trình chính thức trước khi giải bài tập trắc nghiệm.\n"
                f"   • Chú ý các điều kiện ràng buộc biên và các trường hợp ngoại lệ thường xuất hiện trong đề thi các năm trước.\n"
                f"   • Tham khảo các bài giải mẫu và slide bài giảng được giảng viên phê duyệt trên hệ thống DocUni.\n\n"
                f"💡 *Gợi ý*: Bạn có thể xem các trích dẫn tài liệu cụ thể bên dưới để mở file học liệu nghiên cứu sâu hơn!"
            )

        ai_msg = ChatMessage(
            id=f"msg_{len(self.chat_history) + 1}",
            sender="ai",
            content=ai_content,
            timestamp=time_now,
            mode=self.search_mode,
            citations=citations,
        )
        self.chat_history.append(ai_msg)


# ─── UI Helper Components ────────────────────────────────────────────────────

def citation_chip(cite: Citation) -> rx.Component:
    """Card hiển thị nguồn trích dẫn đính kèm dưới câu trả lời của AI."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("file-text", size=14, color="var(--blue-9)"),
                    rx.text(cite.doc_title, size="1", weight="bold", color="slate.12"),
                    align="center",
                    spacing="1",
                    flex="1",
                ),
                rx.badge(
                    cite.score,
                    color_scheme="green",
                    variant="surface",
                    size="1",
                ),
                align="center",
                width="100%",
            ),
            rx.text(
                cite.snippet,
                size="1",
                color="slate.9",
                line_height="1.4",
            ),
            rx.hstack(
                rx.badge(f"Môn: {cite.subject_code}", color_scheme="gray", variant="surface", size="1"),
                rx.badge(f"Trang {cite.page.to_string()}", color_scheme="indigo", variant="surface", size="1"),
                rx.spacer(),
                rx.button(
                    rx.hstack(
                        rx.icon("external-link", size=12),
                        rx.text("Xem đối soát", size="1"),
                        align="center",
                        spacing="1",
                    ),
                    size="1",
                    variant="ghost",
                    color_scheme="blue",
                    on_click=AIAssistantState.open_citation_modal(cite),
                ),
                align="center",
                width="100%",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        variant="surface",
        padding="3",
        border_radius="lg",
        bg="var(--slate-2)",
        _hover={"bg": "var(--blue-2)", "border_color": "var(--blue-7)"},
        transition="all 0.15s ease",
        width="100%",
    )


def chat_message(msg: ChatMessage) -> rx.Component:
    """Hiển thị một bong bóng tin nhắn (User hoặc AI)."""
    return rx.cond(
        msg.sender == "user",
        # Tin nhắn của User
        rx.hstack(
            rx.spacer(),
            rx.box(
                rx.vstack(
                    rx.text(msg.content, size="2", color="white", line_height="1.5"),
                    rx.hstack(
                        rx.spacer(),
                        rx.text(msg.timestamp, size="1", color="blue.3"),
                        align="center",
                        width="100%",
                    ),
                    spacing="1",
                    align="start",
                ),
                bg="blue.9",
                padding_x="4",
                padding_y="3",
                border_radius="xl",
                border_bottom_right_radius="none",
                max_width=["85%", "75%", "65%"],
                box_shadow="sm",
            ),
            rx.avatar(fallback="SV", size="2", radius="full", color_scheme="blue"),
            spacing="3",
            align="start",
            width="100%",
            padding_y="2",
        ),
        # Tin nhắn của AI
        rx.hstack(
            rx.box(
                rx.icon("sparkles", size=20, color="white"),
                bg="linear-gradient(135deg, var(--blue-9), var(--indigo-9))",
                padding="2",
                border_radius="xl",
                box_shadow="sm",
            ),
            rx.box(
                rx.vstack(
                    # Header tin nhắn AI
                    rx.hstack(
                        rx.text("DocUni AI", size="2", weight="bold", color="slate.12"),
                        rx.cond(
                            msg.mode == "rag",
                            rx.badge("Semantic RAG", color_scheme="green", variant="surface", size="1"),
                            rx.badge("Giải thích khái niệm", color_scheme="purple", variant="surface", size="1"),
                        ),
                        rx.spacer(),
                        rx.text(msg.timestamp, size="1", color="slate.8"),
                        align="center",
                        spacing="2",
                        width="100%",
                    ),

                    # Nội dung text AI (Format Markdown)
                    rx.box(
                        rx.markdown(msg.content),
                        width="100%",
                        color="slate.11",
                        font_size="14px",
                        line_height="1.6",
                    ),

                    # Citations Box (nếu có nguồn trích dẫn)
                    rx.cond(
                        msg.citations.length() > 0,
                        rx.vstack(
                            rx.divider(color_scheme="gray"),
                            rx.hstack(
                                rx.icon("bookmark", size=13, color="var(--green-9)"),
                                rx.text("Nguồn Trích Dẫn Học Liệu Đối Soát (Semantic Sources):", size="1", weight="bold", color="green.11"),
                                align="center",
                                spacing="1",
                            ),
                            rx.grid(
                                rx.foreach(
                                    msg.citations,
                                    citation_chip,
                                ),
                                columns="1",
                                spacing="2",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                            padding_top="2",
                        ),
                        rx.fragment(),
                    ),

                    spacing="3",
                    align="start",
                    width="100%",
                ),
                bg="var(--slate-1)",
                border="1px solid var(--slate-4)",
                padding="4",
                border_radius="xl",
                border_top_left_radius="none",
                max_width=["90%", "85%", "80%"],
                box_shadow="sm",
            ),
            rx.spacer(),
            spacing="3",
            align="start",
            width="100%",
            padding_y="2",
        ),
    )


def quick_prompt_card(item: Dict[str, Any]) -> rx.Component:
    """Card gợi ý câu hỏi mẫu ở thanh bên."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(item["subject"], color_scheme="blue", variant="surface", size="1"),
                rx.spacer(),
                rx.icon("sparkles", size=12, color="var(--blue-9)"),
                align="center",
                width="100%",
            ),
            rx.heading(item["title"], size="2", weight="bold", color="slate.12"),
            rx.text(item["prompt"], size="1", color="slate.9", line_height="1.4"),
            rx.hstack(
                rx.text("Bấm để hỏi", size="1", color="blue.10", weight="bold"),
                rx.icon("arrow-right", size=12, color="var(--blue-10)"),
                align="center",
                spacing="1",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        variant="surface",
        padding="3",
        _hover={
            "border_color": "var(--blue-8)",
            "bg": "var(--blue-2)",
            "cursor": "pointer",
        },
        transition="all 0.15s ease",
        on_click=AIAssistantState.ask_quick_prompt(item["prompt"]),
        width="100%",
    )


def citation_modal() -> rx.Component:
    """Dialog xem chi tiết đoạn trích dẫn nguyên văn đối soát."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Modal Header
                rx.hstack(
                    rx.box(
                        rx.icon("book-open-check", size=20, color="var(--green-9)"),
                        bg="green.3",
                        padding="2",
                        border_radius="lg",
                    ),
                    rx.vstack(
                        rx.heading("Chi Tiết Trích Dẫn Học Liệu Đối Soát", size="4", weight="bold", color="slate.12"),
                        rx.text("Thông tin trích lục nguyên văn từ tài liệu nguồn", size="2", color="slate.9"),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            rx.icon("x", size=16),
                            variant="ghost",
                            color_scheme="gray",
                            size="1",
                        ),
                    ),
                    align="center",
                    width="100%",
                ),

                rx.divider(color_scheme="gray"),

                # Document metadata
                rx.grid(
                    rx.vstack(
                        rx.text("Tài liệu:", size="1", color="slate.8"),
                        rx.text(AIAssistantState.active_citation.doc_title, size="2", weight="bold", color="slate.12"),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("Mã học phần:", size="1", color="slate.8"),
                        rx.badge(AIAssistantState.active_citation.subject_code, color_scheme="blue", variant="surface", size="2"),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("Vị trí trang:", size="1", color="slate.8"),
                        rx.badge(f"Trang {AIAssistantState.active_citation.page.to_string()}", color_scheme="indigo", variant="surface", size="2"),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("Độ tương đồng Cosine:", size="1", color="slate.8"),
                        rx.badge(
                            AIAssistantState.active_citation.score,
                            color_scheme="green",
                            variant="solid",
                            size="2",
                        ),
                        spacing="0",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),

                # Verbatim text snippet box
                rx.vstack(
                    rx.hstack(
                        rx.icon("quote", size=14, color="var(--blue-9)"),
                        rx.text("Đoạn trích dẫn nguyên văn từ hệ thống RAG:", size="1", weight="bold", color="slate.11"),
                        align="center",
                        spacing="1",
                    ),
                    rx.box(
                        rx.text(
                            AIAssistantState.active_citation.snippet,
                            size="2",
                            color="slate.11",
                            line_height="1.6",
                            font_style="italic",
                        ),
                        bg="var(--slate-3)",
                        border="1px solid var(--slate-5)",
                        padding="4",
                        border_radius="lg",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),

                # Footer Actions
                rx.hstack(
                    rx.link(
                        rx.button(
                            rx.icon("external-link", size=14),
                            "Mở xem kho tài liệu môn học",
                            color_scheme="blue",
                            size="2",
                            variant="solid",
                        ),
                        href="/documents",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.button(
                            "Đóng lại",
                            color_scheme="gray",
                            variant="surface",
                            size="2",
                        ),
                    ),
                    align="center",
                    width="100%",
                    padding_top="2",
                ),

                spacing="4",
                width="100%",
            ),
            max_width="560px",
            padding="5",
        ),
        open=AIAssistantState.show_citation_modal,
        on_open_change=AIAssistantState.close_citation_modal,
    )


# ─── Main Page ───────────────────────────────────────────────────────────────

def student_ai_page() -> rx.Component:
    return student_page_wrapper(
        rx.vstack(
            # ── Page Header ──
            rx.hstack(
                rx.hstack(
                    rx.box(
                        rx.icon("bot", size=28, color="white"),
                        bg="linear-gradient(135deg, var(--blue-9), var(--indigo-9))",
                        padding="3",
                        border_radius="xl",
                        box_shadow="sm",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Trợ Lý Học Tập Thông Minh DocUni AI", size="7", weight="bold", color="slate.12"),
                            rx.badge("RAG v2.5", color_scheme="green", variant="surface", size="1"),
                            align="center",
                            spacing="2",
                        ),
                        rx.text(
                            "Hỏi đáp ngữ nghĩa, trích dẫn tài liệu học phần và đối soát nội dung theo thời gian thực",
                            size="3",
                            color="slate.9",
                        ),
                        spacing="1",
                    ),
                    align="center",
                    spacing="3",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("trash-2", size=14),
                    "Xóa đoạn chat",
                    color_scheme="gray",
                    variant="surface",
                    size="2",
                    on_click=AIAssistantState.clear_chat,
                ),
                align="center",
                width="100%",
            ),

            rx.divider(color_scheme="gray"),

            # ── Main 2-Column Chat Layout ──
            rx.hstack(
                # ── Left Column: Controls & Quick Prompts (320px) ──
                rx.vstack(
                    # 1. Chế độ truy vấn (Search Mode Card)
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("sliders-horizontal", size=14, color="var(--blue-9)"),
                                rx.text("Chế độ truy vấn AI:", size="2", weight="bold", color="slate.12"),
                                align="center",
                                spacing="2",
                            ),
                            rx.segmented_control.root(
                                rx.segmented_control.item("🔍 RAG Trích dẫn", value="rag"),
                                rx.segmented_control.item("💬 Giải thích", value="explain"),
                                value=AIAssistantState.search_mode,
                                on_change=AIAssistantState.set_search_mode,
                                size="2",
                                width="100%",
                            ),
                            rx.text(
                                rx.cond(
                                    AIAssistantState.search_mode == "rag",
                                    "Chế độ RAG: Trả lời kèm trích dẫn số trang, tên tài liệu và điểm tương đồng.",
                                    "Chế độ Giải thích: Tập trung diễn giải khái niệm ngắn gọn, dễ hiểu.",
                                ),
                                size="1",
                                color="slate.8",
                                line_height="1.4",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        variant="surface",
                        padding="3",
                        width="100%",
                    ),

                    # 2. Bộ lọc môn học (Subject Scope Card)
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("filter", size=14, color="var(--indigo-9)"),
                                rx.text("Phạm vi tài liệu đối soát:", size="2", weight="bold", color="slate.12"),
                                align="center",
                                spacing="2",
                            ),
                            rx.select.root(
                                rx.select.trigger(width="100%", size="2"),
                                rx.select.content(
                                    rx.foreach(
                                        SUBJECT_FILTERS,
                                        lambda s: rx.select.item(s["label"], value=s["value"]),
                                    ),
                                ),
                                value=AIAssistantState.subject_filter,
                                on_change=AIAssistantState.set_subject_filter,
                            ),
                            rx.text("Lọc nguồn tài liệu để AI trích dẫn chính xác theo môn bạn đang học.", size="1", color="slate.8"),
                            spacing="2",
                            width="100%",
                        ),
                        variant="surface",
                        padding="3",
                        width="100%",
                    ),

                    # 3. Quick Prompts List
                    rx.vstack(
                        rx.hstack(
                            rx.icon("zap", size=14, color="var(--amber-9)"),
                            rx.text("Câu hỏi mẫu thường gặp:", size="2", weight="bold", color="slate.12"),
                            align="center",
                            spacing="2",
                        ),
                        rx.vstack(
                            *[quick_prompt_card(qp) for qp in QUICK_PROMPTS],
                            spacing="2",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),

                    # 4. Info badge
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("shield-check", size=14, color="var(--green-9)"),
                                rx.text("DocUni Knowledge Base", size="1", weight="bold", color="green.11"),
                                align="center",
                                spacing="1",
                            ),
                            rx.text("Chỉ mục 8 học phần chuẩn hóa • Độ tương đồng Cosine > 88% • Cập nhật 2026", size="1", color="slate.8"),
                            spacing="1",
                        ),
                        bg="var(--green-2)",
                        border="1px solid var(--green-5)",
                        padding="3",
                        width="100%",
                    ),

                    spacing="3",
                    width=["100%", "100%", "320px"],
                    align="start",
                ),

                # ── Right Column: Interactive Chat Box (Flex 1) ──
                rx.card(
                    rx.vstack(
                        # Chat Box Header
                        rx.hstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon("bot", size=16, color="var(--blue-9)"),
                                    bg="blue.3",
                                    padding="2",
                                    border_radius="lg",
                                ),
                                rx.vstack(
                                    rx.text("Cửa Sổ Hội Thoại Học Tập", size="2", weight="bold", color="slate.12"),
                                    rx.text("Sẵn sàng trả lời các câu hỏi về giáo trình, bài tập và đề thi", size="1", color="slate.8"),
                                    spacing="0",
                                ),
                                align="center",
                                spacing="2",
                            ),
                            rx.spacer(),
                            rx.badge("Online", color_scheme="green", variant="surface", size="1"),
                            align="center",
                            width="100%",
                            padding_bottom="2",
                            border_bottom="1px solid var(--slate-4)",
                        ),

                        # Chat Messages Scroll Area
                        rx.box(
                            rx.vstack(
                                rx.foreach(
                                    AIAssistantState.chat_history,
                                    chat_message,
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            height="520px",
                            overflow_y="auto",
                            padding_y="3",
                            padding_x="1",
                            width="100%",
                        ),

                        # Chat Input Form Area
                        rx.vstack(
                            rx.hstack(
                                rx.input(
                                    rx.input.slot(rx.icon("message-square", size=16, color="var(--slate-8)")),
                                    placeholder="Nhập câu hỏi của bạn (VD: Giải thích thuật toán BFS, Công thức GDP...)...",
                                    value=AIAssistantState.input_text,
                                    on_change=AIAssistantState.set_input_text,
                                    size="3",
                                    flex="1",
                                ),
                                rx.button(
                                    rx.icon("send", size=16),
                                    "Gửi",
                                    color_scheme="blue",
                                    size="3",
                                    variant="solid",
                                    on_click=AIAssistantState.send_message,
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.hstack(
                                rx.icon("info", size=12, color="var(--slate-7)"),
                                rx.text(
                                    "Gợi ý: Nhấn nút 'Gửi' hoặc chọn câu hỏi mẫu bên trái để nhận câu trả lời kèm trích dẫn tài liệu.",
                                    size="1",
                                    color="slate.8",
                                ),
                                align="center",
                                spacing="1",
                            ),
                            spacing="1",
                            width="100%",
                            padding_top="2",
                            border_top="1px solid var(--slate-4)",
                        ),

                        spacing="3",
                        width="100%",
                    ),
                    variant="surface",
                    padding="4",
                    flex="1",
                    height="100%",
                ),

                spacing="4",
                align="start",
                width="100%",
            ),

            # Citation Modal
            citation_modal(),

            spacing="5",
            width="100%",
        ),
        active_route="/student/ai-assistant",
    )
