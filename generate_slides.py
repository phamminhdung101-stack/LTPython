import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color palette
    COLOR_PRIMARY = RGBColor(15, 23, 42)      # Slate 900 (Navy)
    COLOR_SECONDARY = RGBColor(37, 99, 235)   # Blue 600
    COLOR_ACCENT = RGBColor(79, 70, 229)      # Indigo 600
    COLOR_MUTED = RGBColor(100, 116, 139)     # Slate 500
    COLOR_BG_CARD = RGBColor(248, 250, 252)   # Slate 50
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_DARK_TEXT = RGBColor(30, 41, 59)    # Slate 800
    COLOR_LIGHT_TEXT = RGBColor(241, 245, 249)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, tag_text, title_text, is_dark=False):
        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.5), Inches(2.8), Inches(0.4))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_SECONDARY if is_dark else RGBColor(224, 231, 255)
        badge.line.fill.background()
        tf_b = badge.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = tag_text
        p_b.font.size = Pt(11)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_WHITE if is_dark else COLOR_SECONDARY
        p_b.alignment = PP_ALIGN.CENTER

        # Title
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(11.5), Inches(0.8))
        tf_t = tx_title.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE if is_dark else COLOR_PRIMARY

    def set_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # ==========================================
    # SLIDE 1: Title Task 3
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_PRIMARY
    bg1.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(11), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "HỌC VIỆN HÀNG KHÔNG VIỆT NAM — KHOA CNTT"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    p = tf1.add_paragraph()
    p.text = "TASK 3: HỆ THỐNG QUẢN LÝ PHIÊN BẢN (VERSIONING), GẮN THẺ VÀ QUY TRÌNH KIỂM DUYỆT 3 BƯỚC"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(20)

    p = tf1.add_paragraph()
    p.text = "Đồ án Học phần: Lập trình Python (DocUni Platform)"
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_before = Pt(10)

    p = tf1.add_paragraph()
    p.text = "• Sinh viên thực hiện: THÁI ANH KỲ (MSSV: 2431540124 — Lớp: 24ĐHTT03)\n• Giảng viên hướng dẫn: Bộ môn Công nghệ Thông tin\n• Nền tảng: Python Reflex Framework, Radix Themes, WebSockets"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_before = Pt(30)

    set_notes(s1, "Kính thưa quý Thầy/Cô và các bạn sinh viên. Em tên là Thái Anh Kỳ, sinh viên lớp 24ĐHTT03, mã số sinh viên 2431540124. Hôm nay, em xin đại diện nhóm báo cáo chi tiết về kết quả thiết kế và triển khai Task 3 của đề tài DocUni: 'Hệ thống Quản lý phiên bản (Versioning), Phân loại theo Thẻ (Tagging) và Quy trình kiểm duyệt học liệu số 3 bước'. Đây là phân hệ đóng vai trò cốt lõi trong việc đảm bảo chất lượng, tính toàn vẹn và vòng đời của dữ liệu học tập trước khi được công khai rộng rãi.")

    # ==========================================
    # SLIDE 2: Problem & Objectives (Task 3)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "TASK 3 • TỔNG QUAN", "ĐẶT VẤN ĐỀ THỰC TIỄN & MỤC TIÊU NGHIỆP VỤ")

    # Card Left: Thach thuc
    c2_l = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8))
    c2_l.fill.solid()
    c2_l.fill.fore_color.rgb = RGBColor(254, 242, 242)
    c2_l.line.color.rgb = RGBColor(254, 202, 202)
    tf2_l = c2_l.text_frame
    tf2_l.word_wrap = True
    p = tf2_l.paragraphs[0]
    p.text = "THỰC TRẠNG & BẤT CẬP HIỆN TẠI"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(185, 28, 28)
    p = tf2_l.add_paragraph()
    p.text = "• Mất dấu vết tài liệu: Đề thi, slide bài giảng được cập nhật qua các năm; việc ghi đè file làm mất lịch sử các thay đổi cũ.\n\n• Rác dữ liệu & Sai lệch kiến thức: Sinh viên tự do tải lên tài liệu mà không qua thẩm định dẫn đến tài liệu trùng lặp, sai đáp án hoặc vi phạm bản quyền.\n\n• Phân loại đơn chiều: Lưu trữ theo thư mục cứng nhắc gây khó khăn khi một tài liệu liên quan đến nhiều môn học khác nhau."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    # Card Right: Muc tieu
    c2_r = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8))
    c2_r.fill.solid()
    c2_r.fill.fore_color.rgb = RGBColor(240, 253, 244)
    c2_r.line.color.rgb = RGBColor(187, 247, 208)
    tf2_r = c2_r.text_frame
    tf2_r.word_wrap = True
    p = tf2_r.paragraphs[0]
    p.text = "MỤC TIÊU GIẢI QUYẾT CỦA TASK 3"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(21, 128, 61)
    p = tf2_r.add_paragraph()
    p.text = "• Semantic Versioning: Tự động đánh phiên bản (v1.0 -> v2.0 -> v2.1) lưu giữ đầy đủ bản tóm tắt thay đổi (Changelog).\n\n• Quy trình kiểm duyệt 2 chiều (Moderation): Sinh viên đóng góp -> Giảng viên thẩm định -> Duyệt công khai hoặc Từ chối kèm nhận xét cụ thể.\n\n• Gắn thẻ đa chiều (Tagging): Hệ thống nhãn chip linh hoạt, liên kết chéo các chủ đề môn học phục vụ tra cứu thông minh."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    set_notes(s2, "Thưa Thầy/Cô, trong các hệ thống chia sẻ học liệu đại học, vấn đề lớn nhất không phải là thiếu tài liệu, mà là 'rác tài liệu' và sự sai lệch kiến thức qua các năm học. Khi một tài liệu được cập nhật đề thi mới hay chỉnh sửa lỗi sai, nếu chúng ta chỉ lưu đè lên file cũ, sinh viên sẽ không biết đã thay đổi những gì. Do đó, mục tiêu của Task 3 là giải quyết triệt để 3 bài toán: Quản lý phiên bản Semantic Versioning, Kiểm duyệt 3 bước khép kín và Gắn thẻ nhãn đa chiều.")

    # ==========================================
    # SLIDE 3: DB Schema & Models
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "TASK 3 • KIẾN TRÚC DỮ LIỆU", "THIẾT KẾ CƠ SỞ DỮ LIỆU & QUAN HỆ THỰC THỂ (SCHEMA)")

    # 4 Tables Grid
    boxes = [
        ("documents (Bảng chính)", "• id (PK, UUID/Int)\n• title, faculty, subject_code\n• current_version (v1.0, v2.0)\n• status (PENDING, APPROVED, REJECTED)\n• created_at, updated_at", Inches(0.8), Inches(1.9)),
        ("document_versions (Phiên bản)", "• id (PK), document_id (FK)\n• version_number (v1.0, v2.0...)\n• file_path, file_size\n• change_summary (Changelog)\n• uploaded_by, created_at", Inches(6.8), Inches(1.9)),
        ("document_contributions (Kiểm duyệt)", "• id (PK), document_id (FK)\n• student_name, student_id\n• review_status (PENDING, APPROVED...)\n• lecturer_feedback (Lời nhận xét GV)\n• submitted_at, reviewed_at", Inches(0.8), Inches(4.5)),
        ("document_tags & tags (Gắn nhãn)", "• document_id (FK), tag_id (FK)\n• Quan hệ Nhiều - Nhiều (N-N)\n• Chuẩn hóa slug viết thường\n• Hỗ trợ lọc chéo theo chủ đề", Inches(6.8), Inches(4.5))
    ]

    for title, content, left, top in boxes:
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.7), Inches(2.3))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_BG_CARD
        box.line.color.rgb = RGBColor(226, 232, 240)
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY
        p = tf.add_paragraph()
        p.text = content
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(6)

    set_notes(s3, "Để hiện thực hóa yêu cầu trên, em đã thiết kế mô hình dữ liệu quan hệ gồm 4 thực thể cốt lõi. Trong đó, bảng documents liên kết 1-Nhiều với bảng document_versions. Nghĩa là một học liệu có thể tồn tại nhiều bản lưu trữ từ v1.0, v2.0 trở đi mà không bao giờ bị mất dữ liệu cũ. Bảng document_contributions lưu trữ độc lập trạng thái kiểm duyệt và trường lecturer_feedback, giúp sinh viên có thể đọc lại toàn bộ nhận xét của giảng viên khi bài nộp bị từ chối.")

    # ==========================================
    # SLIDE 4: Workflow & State Machine
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "TASK 3 • QUY TRÌNH NGHIỆP VỤ", "QUY TRÌNH KIỂM DUYỆT 3 BƯỚC & STATE MACHINE WORKFLOW")

    steps = [
        ("BƯỚC 1: SUBMISSION", "Sinh viên tải tài liệu lên\nkèm tags và phân loại môn.\nTrạng thái ban đầu: PENDING\n(Ẩn với kho công khai).", RGBColor(59, 130, 246)),
        ("BƯỚC 2: MODERATION", "Giảng viên nhận bài tại hàng đợi,\nxem trước (Preview) nội dung.\n• Phê duyệt -> APPROVED\n• Từ chối -> REJECTED + Feedback", RGBColor(16, 185, 129)),
        ("BƯỚC 3: RESUBMISSION", "Sinh viên đọc lời nhận xét,\nsửa đổi file và nộp lại.\nHệ thống tự nâng lên v2.0\nvà quay lại trạng thái PENDING.", RGBColor(245, 158, 11))
    ]

    for i, (stitle, sdesc, scolor) in enumerate(steps):
        s_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 4.0), Inches(2.2), Inches(3.7), Inches(4.5))
        s_box.fill.solid()
        s_box.fill.fore_color.rgb = COLOR_BG_CARD
        s_box.line.color.rgb = scolor
        s_box.line.width = Pt(2)
        tf = s_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = scolor
        p = tf.add_paragraph()
        p.text = sdesc
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(16)

    set_notes(s4, "Trên slide là sơ đồ máy trạng thái (State Machine) của quy trình kiểm duyệt học liệu. Quy trình gồm 3 bước khép kín: Bước 1 - Sinh viên tải tài liệu lên, hệ thống tự động khóa tài liệu ở trạng thái PENDING; lúc này tài liệu hoàn toàn vô hình trên kho học liệu chung để ngăn ngừa rò rỉ dữ liệu chưa chuẩn hóa. Bước 2 - Giảng viên tại Hàng đợi duyệt mở xem trước nội dung: nếu đạt yêu cầu, thầy/cô bấm Phê duyệt; nếu chưa đạt, thầy/cô bấm Từ chối và nhập lời nhận xét. Bước 3 - Sinh viên nhận thông báo tại màn hình Đóng góp của mình, đọc phản hồi, sửa đổi file và bấm 'Nộp phiên bản v2.0'.")

    # ==========================================
    # SLIDE 5: Reflex Architecture
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "TASK 3 • KIẾN TRÚC PHẦN MỀM", "KIẾN TRÚC CÔNG NGHỆ REFLEX PYTHON FULL-STACK")

    c5_l = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8))
    c5_l.fill.solid()
    c5_l.fill.fore_color.rgb = COLOR_BG_CARD
    c5_l.line.color.rgb = RGBColor(226, 232, 240)
    tf5_l = c5_l.text_frame
    tf5_l.word_wrap = True
    p = tf5_l.paragraphs[0]
    p.text = "ƯU ĐIỂM CỦA REFLEX FRAMEWORK"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf5_l.add_paragraph()
    p.text = "• 100% Thuần Python: Viết UI, State và Backend hoàn toàn bằng Python, không cần tách riêng React/NodeJS.\n\n• Biên dịch tự động: Chuyển mã Python sang React 19 + Radix UI + Tailwind CSS hiện đại.\n\n• Giao tiếp thời gian thực: WebSockets 2 chiều giữa Client và Server, độ trễ phản hồi cực thấp (< 50ms).\n\n• Phản hồi theo sự kiện (Event-driven): State tự động đồng bộ khi biến thay đổi."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    c5_r = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8))
    c5_r.fill.solid()
    c5_r.fill.fore_color.rgb = COLOR_BG_CARD
    c5_r.line.color.rgb = RGBColor(226, 232, 240)
    tf5_r = c5_r.text_frame
    tf5_r.word_wrap = True
    p = tf5_r.paragraphs[0]
    p.text = "PHÂN TÁCH MODULES TASK 3"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf5_r.add_paragraph()
    p.text = "• student_upload.py:\n  Form kéo thả rx.upload, dropdown phân cấp Khoa/Môn, quản lý nhãn chip tương tác.\n\n• student_contributions.py:\n  Dashboard theo dõi bài nộp, 4 thẻ KPI cá nhân, Tab filter trạng thái, Modal nộp bản v2.0.\n\n• lecturer_approval.py:\n  Hàng đợi kiểm duyệt Side-by-Side, Preview tài liệu, Modal từ chối kèm phản hồi."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    set_notes(s5, "Toàn bộ hệ thống được xây dựng trên nền tảng công nghệ Reflex — một framework Python Full-Stack hiện đại bậc nhất hiện nay. Điểm ưu việt của Reflex là chúng em có thể viết 100% ứng dụng bằng Python từ giao diện, State quản lý đến Backend xử lý dữ liệu mà không cần phải phân tách dự án thành 2 repo riêng biệt giữa React và Node.js. Cơ chế hoạt động của Reflex là sử dụng WebSockets để duy trì kết nối liên tục giữa trình duyệt và máy chủ Python với độ trễ dưới 50ms.")

    # ==========================================
    # SLIDE 6: UI Upload & Tagging
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "TASK 3 • GIAO DIỆN NGƯỜI DÙNG", "GIAO DIỆN ĐÓNG GÓP HỌC LIỆU & GẮN THẺ (/student/upload)")

    c6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8))
    c6.fill.solid()
    c6.fill.fore_color.rgb = COLOR_BG_CARD
    c6.line.color.rgb = RGBColor(226, 232, 240)
    tf6 = c6.text_frame
    tf6.word_wrap = True
    p = tf6.paragraphs[0]
    p.text = "CẤU TRÚC GIAO DIỆN BỐ CỤC 2 CỘT (2-COLUMN MODERN LAYOUT)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf6.add_paragraph()
    p.text = "1. Cột trái — Form nhập liệu học thuật chuyên nghiệp:\n   • Vùng kéo thả tệp (rx.upload Zone) hỗ trợ .pdf, .docx, .pptx, .zip (tối đa 50MB).\n   • Bộ 3 Dropdown phân cấp logic: Khoa viện -> Môn học -> Thư mục học phần.\n   • Thẻ nhãn tương tác (Tag Chips): Nhập tag tự do nhấn Enter hoặc nhấp chọn các tag gợi ý sẵn ('python', 'sql', 'giai-thuat').\n   • Xóa tag 1 chạm bằng icon xmark.\n\n2. Cột phải — Chuẩn mực bản quyền & Tiêu chí kiểm duyệt:\n   • Bảng hướng dẫn sinh viên tuân thủ liêm chính học thuật và bản quyền của Học viện Hàng không Việt Nam.\n   • Checklist 3 tiêu chí phê duyệt giúp sinh viên tự kiểm tra tài liệu trước khi gửi."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(12)

    set_notes(s6, "Trên màn hình là giao diện trang Tải lên học liệu (/student/upload). Chúng em đã áp dụng bố cục 2 cột bất đối xứng theo chuẩn UX hiện đại. Ở cột bên trái, sinh viên có thể kéo thả trực tiếp tệp tin vào vùng Upload Zone. Form nhập liệu yêu cầu phân cấp rõ ràng từ Khoa đến Môn học và Thư mục lưu trữ. Chức năng Gắn thẻ (Tagging) được thiết kế dạng Chip tương tác: sinh viên có thể gõ từ khóa và bấm Enter để sinh tag mới, hoặc nhấp vào các tag gợi ý sẵn. Ở cột bên phải là các tiêu chuẩn học thuật giúp sinh viên tự rà soát trước khi gửi.")

    # ==========================================
    # SLIDE 7: UI Contributions & v2.0
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "TASK 3 • GIAO DIỆN NGƯỜI DÙNG", "THEO DÕI DUYỆT & NỘP PHIÊN BẢN v2.0 (/student/contributions)")

    c7 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8))
    c7.fill.solid()
    c7.fill.fore_color.rgb = COLOR_BG_CARD
    c7.line.color.rgb = RGBColor(226, 232, 240)
    tf7 = c7.text_frame
    tf7.word_wrap = True
    p = tf7.paragraphs[0]
    p.text = "TÍNH NĂNG THEO DÕI VÒNG ĐỜI BÀI NỘP"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf7.add_paragraph()
    p.text = "• 4 Thẻ KPI cá nhân: Tổng số đóng góp, Đang chờ duyệt (vàng), Đã xuất bản (xanh lá), Bị từ chối (đỏ).\n\n• Bộ lọc Tabs nhanh: Chuyển đổi xem toàn bộ hoặc xem riêng từng trạng thái.\n\n• Phản hồi lỗi chi tiết: Với tài liệu bị từ chối, hiển thị khung Callout đỏ trích nguyên văn nhận xét của giảng viên.\n\n• Nộp phiên bản v2.0: Mở Modal chuyên biệt, tự động kế thừa thông tin tài liệu cũ, cho phép tải tệp mới và bắt buộc nhập 'Tóm tắt nội dung chỉnh sửa' (Changelog).\n\n• Chức năng thu hồi (Revoke): Cho phép sinh viên tự hủy yêu cầu duyệt nếu phát hiện đính kèm nhầm file."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(12)

    set_notes(s7, "Sau khi sinh viên gửi tài liệu, toàn bộ lịch sử sẽ được quản lý tại trang Đóng góp của tôi (/student/contributions). Tại đây có 4 thẻ KPI tóm tắt và thanh Tabs để lọc nhanh. Điểm nổi bật nhất của trang này là khả năng phản hồi tương tác 2 chiều: Khi một tài liệu bị giảng viên từ chối, thẻ bài nộp sẽ hiển thị rõ lời nhận xét của thầy cô. Sinh viên bấm vào 'Nộp phiên bản v2.0' để mở Modal tải tệp sửa đổi và nhập bản tóm tắt các điểm đã sửa. Sau khi nộp, tài liệu được tự động nâng lên v2.0 và quay lại hàng đợi duyệt.")

    # ==========================================
    # SLIDE 8: UI Approval Queue
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "TASK 3 • GIAO DIỆN NGƯỜI DÙNG", "GIAO DIỆN KIỂM DUYỆT SIDE-BY-SIDE (/lecturer/approval)")

    c8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8))
    c8.fill.solid()
    c8.fill.fore_color.rgb = COLOR_BG_CARD
    c8.line.color.rgb = RGBColor(226, 232, 240)
    tf8 = c8.text_frame
    tf8.word_wrap = True
    p = tf8.paragraphs[0]
    p.text = "THIẾT KẾ XEM TRƯỚC KÉP HIỆN ĐẠI (SPLIT-VIEW AUDIT)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf8.add_paragraph()
    p.text = "• Cột trái (Hàng đợi kiểm duyệt 400px):\n  Danh sách thẻ bài nộp PENDING, hiển thị rõ Họ tên sinh viên, MSSV, Lớp và thời gian nộp.\n  Thẻ được chọn sẽ có viền xanh nổi bật.\n\n• Cột phải (Khung chi tiết & Đọc trước):\n  Hiển thị toàn bộ metadata, nhãn tags và bản tóm tắt.\n  Khung Document Reader Preview giả lập đọc trước trang 1-2 của tài liệu ngay trên trình duyệt mà không cần tải file về.\n\n• Thao tác thẩm định 1 chạm:\n  - Nút xanh 'Phê duyệt & Xuất bản': Chuyển trạng thái sang APPROVED, công khai tài liệu vào kho học liệu.\n  - Nút đỏ 'Từ chối đóng góp': Mở Dialog nhập lý do từ chối để phản hồi trực tiếp cho sinh viên."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(12)

    set_notes(s8, "Để hỗ trợ quý thầy/cô kiểm duyệt tài liệu nhanh chóng và tiện lợi nhất, trang /lecturer/approval được thiết kế theo mô hình Side-by-Side Split View. Cột bên trái là danh sách hàng đợi các bài nộp cần xử lý. Khi bấm chọn vào một mục, cột bên phải sẽ lập tức hiển thị toàn bộ hồ sơ học liệu. Khung Document Reader Preview cho phép thầy/cô xem trực tiếp trích đoạn nội dung tài liệu mà không cần tải file về máy. Giảng viên chỉ cần 1 thao tác: Nhấp 'Phê duyệt' hoặc 'Từ chối' kèm lời nhận xét.")

    # ==========================================
    # SLIDE 9: Testing & Optimization
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "TASK 3 • KIỂM THỬ & TỐI ƯU HÓA", "KIỂM THỬ HỆ THỐNG, XỬ LÝ LỖI GÕ TĨNH & CLEAN CODE")

    c9 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8))
    c9.fill.solid()
    c9.fill.fore_color.rgb = COLOR_BG_CARD
    c9.line.color.rgb = RGBColor(226, 232, 240)
    tf9 = c9.text_frame
    tf9.word_wrap = True
    p = tf9.paragraphs[0]
    p.text = "CÁC GIẢI PHÁP TỐI ƯU HÓA MÃ NGUỒN"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf9.add_paragraph()
    p.text = "1. Xử lý gõ tĩnh với Python Dataclass (@dataclasses.dataclass):\n   Khắc phục triệt để lỗi UntypedVarError trong quá trình Reflex phân tích AST, đảm bảo an toàn kiểu dữ liệu (Type Safety) cho các model PendingDoc, DocVersion.\n\n2. Chuẩn hóa Radix UI Themes:\n   Chuyển đổi 100% thuộc tính padding/gap/margin từ chuỗi sang số nguyên chuẩn (0 - 9).\n   Chuẩn hóa tên icon sang định dạng kebab-case của Lucide Icons ('circle-check', 'triangle-alert').\n\n3. Kết quả kiểm thử biên dịch:\n   • py_compile: Không phát hiện lỗi cú pháp.\n   • reflex compile: Biên dịch thành công 100% toàn bộ 30 trang giao diện (Clean Build)."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(12)

    set_notes(s9, "Trong quá trình lập trình hệ thống với Reflex, một trong những thách thức kỹ thuật lớn nhất là cơ chế biên dịch từ Python sang React đòi hỏi tính nhất quán về kiểu dữ liệu rất cao. Để giải quyết dứt điểm vấn đề này, em đã áp dụng cấu trúc Dataclass có khai báo kiểu dữ liệu tường minh cho toàn bộ các đối tượng Version và Document. Nhờ đó, Reflex nhận diện chính xác các trường dữ liệu và không phát sinh lỗi UntypedVarError. Lệnh reflex compile đã biên dịch thành công 100% toàn bộ 30 trang web của dự án.")

    # ==========================================
    # SLIDE 10: Conclusion Task 3
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "TASK 3 • TỔNG KẾT", "TỔNG KẾT TASK 3 & TÀI LIỆU THAM KHẢO")

    c10_l = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8))
    c10_l.fill.solid()
    c10_l.fill.fore_color.rgb = RGBColor(240, 253, 244)
    c10_l.line.color.rgb = RGBColor(187, 247, 208)
    tf10_l = c10_l.text_frame
    tf10_l.word_wrap = True
    p = tf10_l.paragraphs[0]
    p.text = "KẾT QUẢ ĐẠT ĐƯỢC TASK 3"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(21, 128, 61)
    p = tf10_l.add_paragraph()
    p.text = "• Hoàn thành 100% yêu cầu về Quản lý phiên bản (Versioning), Gắn thẻ (Tagging) và Quy trình kiểm duyệt 3 bước.\n\n• Xây dựng trọn vẹn 3 trang giao diện người dùng tương tác thời gian thực qua WebSockets: /student/upload, /student/contributions, /lecturer/approval.\n\n• Hệ thống vận hành ổn định, mã nguồn sạch sẽ, không có cảnh báo biên dịch."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    c10_r = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8))
    c10_r.fill.solid()
    c10_r.fill.fore_color.rgb = COLOR_BG_CARD
    c10_r.line.color.rgb = RGBColor(226, 232, 240)
    tf10_r = c10_r.text_frame
    tf10_r.word_wrap = True
    p = tf10_r.paragraphs[0]
    p.text = "TÀI LIỆU THAM KHẢO CHÍNH"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf10_r.add_paragraph()
    p.text = "1. Reflex Documentation (v0.10.0)\n   https://reflex.dev/docs/\n\n2. Radix UI Themes Component Library\n   https://www.radix-ui.com/themes/docs\n\n3. Semantic Versioning Specification (SemVer 2.0.0)\n   https://semver.org/\n\n4. PostgreSQL Documentation: DDL Constraints\n   https://www.postgresql.org/docs/"
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    set_notes(s10, "Tổng kết lại phần Task 3, em đã hoàn thành đầy đủ tất cả các yêu cầu đề ra của bài toán: từ mô hình dữ liệu lưu trữ đa phiên bản, cơ chế gắn thẻ linh hoạt, cho đến quy trình kiểm duyệt học liệu số 3 bước với trải nghiệm người dùng hoàn chỉnh. Sau đây, em xin phép kính mời Thầy/Cô tiếp tục theo dõi phần báo cáo Task 4 do bạn Phạm Nguyễn Vân Anh trình bày về Hệ thống Lập chỉ mục, Tra cứu học liệu đa chiều và Bảng điều khiển Dashboard quản trị học viện. Em xin chân thành cảm ơn!")

    # ==========================================
    # SLIDE 11: Title Task 4
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    bg11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg11.fill.solid()
    bg11.fill.fore_color.rgb = RGBColor(30, 41, 59) # Slate 800
    bg11.line.fill.background()

    tb11 = s11.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(11), Inches(4.8))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    
    p = tf11.paragraphs[0]
    p.text = "HỌC VIỆN HÀNG KHÔNG VIỆT NAM — KHOA CNTT"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    p = tf11.add_paragraph()
    p.text = "TASK 4: HỆ THỐNG LẬP CHỈ MỤC (INDEXING), GIAO DIỆN TRA CỨU ĐA CHIỀU VÀ DASHBOARD QUẢN TRỊ"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(20)

    p = tf11.add_paragraph()
    p.text = "Đồ án Học phần: Lập trình Python (DocUni Platform)"
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_before = Pt(10)

    p = tf11.add_paragraph()
    p.text = "• Sinh viên thực hiện & Báo cáo: PHẠM NGUYỄN VÂN ANH (MSSV: 2431540123 — Lớp: 24ĐHTT03)\n• Phụ trách Kỹ thuật: THÁI ANH KỲ (MSSV: 2431540124)\n• Nền tảng: Reflex Framework, Recharts SVG, Inverted Index Search, RBAC Security"
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(226, 232, 240)
    p.space_before = Pt(30)

    set_notes(s11, "Kính thưa quý Thầy/Cô và các bạn sinh viên. Em tên là Phạm Nguyễn Vân Anh, sinh viên lớp 24ĐHTT03, mã số sinh viên 2431540123. Tiếp nối phần trình bày về kiểm duyệt và phiên bản của bạn Kỳ, em xin đại diện nhóm báo cáo chi tiết về Task 4 của đồ án DocUni: 'Hệ thống Lập chỉ mục (Indexing), Giao diện tra cứu học liệu đa chiều và Bảng điều khiển Dashboard quản trị giảng viên'. Mục tiêu của phân hệ này là giúp sinh viên tìm kiếm chính xác tài liệu chỉ trong vài mili-giây, đồng thời cung cấp cho giảng viên bức tranh tổng thể về mức độ tương tác thông qua các biểu đồ phân tích trực quan.")

    # ==========================================
    # SLIDE 12: Problem & Objectives (Task 4)
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "TASK 4 • TỔNG QUAN", "ĐẶT VẤN ĐỀ THỰC TIỄN & MỤC TIÊU NGHIỆP VỤ")

    c12_l = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8))
    c12_l.fill.solid()
    c12_l.fill.fore_color.rgb = RGBColor(254, 242, 242)
    c12_l.line.color.rgb = RGBColor(254, 202, 202)
    tf12_l = c12_l.text_frame
    tf12_l.word_wrap = True
    p = tf12_l.paragraphs[0]
    p.text = "THỰC TRẠNG & BẤT CẬP HIỆN TẠI"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(185, 28, 28)
    p = tf12_l.add_paragraph()
    p.text = "• Tra cứu chậm & Bỏ sót: Số lượng tài liệu môn học ngày càng lớn; sinh viên mất nhiều thời gian lục lọi thư mục, khó lọc theo môn học hoặc loại tài liệu mong muốn.\n\n• Thiếu số liệu đo lường mức độ quan tâm: Giảng viên và nhà trường không có dữ liệu thực tế để biết tài liệu nào được xem/tải nhiều nhất, môn nào đang thiếu đề thi ôn tập.\n\n• Quản lý phân tán: Khó kiểm soát phạm vi chia sẻ học liệu giữa các khoa và các lớp khác nhau."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    c12_r = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8))
    c12_r.fill.solid()
    c12_r.fill.fore_color.rgb = RGBColor(240, 253, 244)
    c12_r.line.color.rgb = RGBColor(187, 247, 208)
    tf12_r = c12_r.text_frame
    tf12_r.word_wrap = True
    p = tf12_r.paragraphs[0]
    p.text = "MỤC TIÊU GIẢI QUYẾT CỦA TASK 4"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(21, 128, 61)
    p = tf12_r.add_paragraph()
    p.text = "• Kho học liệu số (/documents):\n  Tìm kiếm tức thời và bộ lọc đa chiều (Khoa, Môn học, Loại tài liệu).\n\n• Trang Quản lý tài liệu giảng viên (/lecturer/documents):\n  Quản lý CRUD, phân quyền theo lớp/khoa và quản lý phiên bản tập trung.\n\n• Dashboard phân tích (/lecturer/dashboard):\n  Bộ 3 biểu đồ Recharts (Area, Bar, Donut) và các chỉ số KPI theo dõi tương tác thời gian thực."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    set_notes(s12, "Thưa Thầy/Cô, một kho tài liệu dù phong phú đến đâu nhưng nếu sinh viên không thể tìm thấy nội dung mình cần trong vòng 5 giây thì kho tài liệu đó gần như mất đi giá trị. Đồng thời, về phía người dạy, nếu không có số liệu thống kê lượt xem và lượt tải về, thầy/cô sẽ không biết được tài liệu của mình có tiếp cận được sinh viên hay không. Vì vậy, Task 4 được phát triển nhằm giải quyết trọn vẹn cả 2 góc nhìn: Đối với người học, cung cấp công cụ tìm kiếm tức thời; đối với người dạy, cung cấp Dashboard quản trị thông minh.")

    # ==========================================
    # SLIDE 13: Indexing Model & Stats Schema
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "TASK 4 • CẤU TRÚC DỮ LIỆU", "MÔ HÌNH LẬP CHỈ MỤC (INDEXING) & DỮ LIỆU THỐNG KÊ")

    c13_l = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8))
    c13_l.fill.solid()
    c13_l.fill.fore_color.rgb = COLOR_BG_CARD
    c13_l.line.color.rgb = RGBColor(226, 232, 240)
    tf13_l = c13_l.text_frame
    tf13_l.word_wrap = True
    p = tf13_l.paragraphs[0]
    p.text = "CHIẾN LƯỢC LẬP CHỈ MỤC ĐA TRƯỜNG"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf13_l.add_paragraph()
    p.text = "• Chỉ mục đa thuộc tính (Multi-field Index):\n  Lập chỉ mục trên: title, subject_code, faculty, doc_type, tags.\n\n• Chuẩn hóa từ khóa (Tokenization & Normalization):\n  Chuyển về chữ thường không dấu, loại bỏ ký tự đặc biệt.\n\n• Hỗ trợ tìm kiếm tiền tố (Prefix Search) và đối soát từ khóa linh hoạt.\n\n• Tốc độ quét cực nhanh, đáp ứng hàng ngàn tài liệu đồng thời."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    c13_r = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8))
    c13_r.fill.solid()
    c13_r.fill.fore_color.rgb = COLOR_BG_CARD
    c13_r.line.color.rgb = RGBColor(226, 232, 240)
    tf13_r = c13_r.text_frame
    tf13_r.word_wrap = True
    p = tf13_r.paragraphs[0]
    p.text = "MÔ HÌNH DỮ LIỆU THỐNG KÊ TƯƠNG TÁC"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf13_r.add_paragraph()
    p.text = "• Bảng document_stats:\n  Lưu trữ lượt xem trực tuyến (views) và lượt tải về máy (downloads).\n\n• Bảng document_permissions:\n  Phân quyền chi tiết (can_view, can_download, can_edit) gắn theo từng Khoa hoặc Lớp học cụ thể.\n\n• Bảng activity_logs:\n  Nhật ký hoạt động thời gian thực (user_id, action, doc_id, timestamp)."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    set_notes(s13, "Để đảm bảo tốc độ phản hồi tính bằng mili-giây, chúng em áp dụng chiến lược lập chỉ mục đa trường. Khi một tài liệu được phê duyệt, hệ thống sẽ tiến hành chuẩn hóa văn bản và lập chỉ mục trên tiêu đề, mã môn, tên khoa và các thẻ nhãn. Nhờ vậy, sinh viên chỉ cần gõ mã môn như 'IT101' hay gõ từ khóa 'python', hệ thống sẽ quét qua cây chỉ mục ngay lập tức. Song song với đó, hệ thống duy trì mô hình thống kê tương tác thông qua bảng document_stats và activity_logs, ghi nhận từng lượt tương tác làm cơ sở cho Dashboard.")

    # ==========================================
    # SLIDE 14: Faceted Search & Reactive Filter
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "TASK 4 • THUẬT TOÁN & HIỆU NĂNG", "KIẾN TRÚC BỘ LỌC ĐA CHIỀU & TÌM KIẾM TỨC THỜI")

    c14 = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8))
    c14.fill.solid()
    c14.fill.fore_color.rgb = COLOR_BG_CARD
    c14.line.color.rgb = RGBColor(226, 232, 240)
    tf14 = c14.text_frame
    tf14.word_wrap = True
    p = tf14.paragraphs[0]
    p.text = "LUỒNG XỬ LÝ TÌM KIẾM ĐA DIỆN (FACETED SEARCH ENGINE)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf14.add_paragraph()
    p.text = "• Lọc 3 Tầng Đồng Thời:\n  1. Tầng 1 (Keyword Search): Lọc chuỗi tức thời trên Tiêu đề, Mô tả và Thẻ Tags.\n  2. Tầng 2 (Faculty Facet): Lọc theo Khoa/Viện (CNTT, Kinh tế, Ngoại ngữ, Điều hành bay).\n  3. Tầng 3 (Type Facet): Lọc theo Loại học liệu (Giáo trình, Slide, Đề thi & Đáp án, Bài tập lớn, Sách tham khảo).\n\n• Kỹ thuật Reactive Computed Vars của Reflex (@rx.var):\n  - Không cần gọi lại API thủ công hoặc reload trang.\n  - Biến trạng thái tự động tính toán lại danh sách hiển thị khi có thay đổi.\n  - Độ trễ lọc cực thấp (< 15ms), trải nghiệm tương tác mượt mà như ứng dụng native."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(12)

    set_notes(s14, "Kiến trúc tìm kiếm của DocUni áp dụng mô hình Faceted Search — tìm kiếm theo các khía cạnh thuộc tính. Quá trình lọc diễn ra đồng thời qua 3 tầng: Tầng từ khóa, Tầng khoa viện và Tầng định dạng học liệu. Điểm đặc sắc ở đây là chúng em tận dụng cơ chế Computed Variable với cú pháp @rx.var của Reflex. Khi sinh viên bấm chuyển loại tài liệu từ 'Tất cả' sang 'Đề thi', biến trạng thái thay đổi sẽ tự động kích hoạt hàm lọc trên Server và phản hồi dữ liệu về giao diện chỉ trong vòng 15 mili-giây mà không cần reload trang.")

    # ==========================================
    # SLIDE 15: Recharts Architecture
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "TASK 4 • TRỰC QUAN HÓA DỮ LIỆU", "KIẾN TRÚC BIỂU ĐỒ RECHARTS & DASHBOARD KPIS")

    charts = [
        ("1. AREA CHART (XU HƯỚNG)", "So sánh 2 đường diện tích Lượt xem (Xanh dương) vs Lượt tải (Xanh lá) theo chu kỳ 7 ngày hoặc 30 ngày.", RGBColor(59, 130, 246)),
        ("2. BAR CHART (TOP TÀI LIỆU)", "Xếp hạng 5 môn học có lượt tải về cao nhất, phát hiện môn học được sinh viên quan tâm nhất.", RGBColor(16, 185, 129)),
        ("3. DONUT CHART (CƠ CẤU)", "Phân tích tỷ lệ % cơ cấu giữa Giáo trình, Slide, Đề thi, Bài tập, giúp cân đối nguồn tài liệu.", RGBColor(245, 158, 11))
    ]

    for i, (ctitle, cdesc, ccolor) in enumerate(charts):
        c_box = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 4.0), Inches(2.2), Inches(3.7), Inches(4.5))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = COLOR_BG_CARD
        c_box.line.color.rgb = ccolor
        c_box.line.width = Pt(2)
        tf = c_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = ccolor
        p = tf.add_paragraph()
        p.text = cdesc
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_DARK_TEXT
        p.space_before = Pt(16)
        p = tf.add_paragraph()
        p.text = "• Đồ họa vector SVG sắc nét\n• Responsive trên mọi màn hình\n• Hiệu ứng Tooltip & Animation"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_MUTED
        p.space_before = Pt(20)

    set_notes(s15, "Để xây dựng Dashboard quản trị trực quan, chúng em đã tích hợp thư viện rx.recharts của Reflex. Toàn bộ các biểu đồ được dựng trực tiếp bằng mã nguồn Python nhưng render ra client dưới dạng đồ họa vector SVG siêu nét và mượt mà. Dashboard trang bị bộ 3 biểu đồ phân tích chuyên sâu: Thứ nhất là Biểu đồ miền Area Chart so sánh trực quan giữa lượt xem và lượt tải; Thứ hai là Biểu đồ cột Bar Chart xếp hạng top 5 môn học được quan tâm nhất; Và thứ ba là Biểu đồ tròn Donut Chart phân tích tỷ trọng cơ cấu học liệu.")

    # ==========================================
    # SLIDE 16: UI Documents Catalog
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "TASK 4 • GIAO DIỆN NGƯỜI DÙNG", "GIAO DIỆN KHO HỌC LIỆU MÔN HỌC (/documents)")

    c16 = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8))
    c16.fill.solid()
    c16.fill.fore_color.rgb = COLOR_BG_CARD
    c16.line.color.rgb = RGBColor(226, 232, 240)
    tf16 = c16.text_frame
    tf16.word_wrap = True
    p = tf16.paragraphs[0]
    p.text = "THIẾT KẾ TRẢI NGHIỆM TRA CỨU HỌC LIỆU CHO SINH VIÊN"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf16.add_paragraph()
    p.text = "• Thanh tìm kiếm trung tâm & Bộ lọc Pills:\n  Ô tìm kiếm lớn có icon kính lúp, Dropdown chọn Khoa viện và hàng nút bấm chọn nhanh loại tài liệu.\n  Badge tự động đếm kết quả theo thời gian thực (VD: 'Tìm thấy 4 tài liệu').\n\n• Lưới Thẻ Học Liệu (Responsive 3-Column Card Grid):\n  - Phân màu trực quan: Giáo trình (Xanh dương), Slide (Cam), Đề thi (Đỏ), Bài tập (Tím), Tham khảo (Xanh lá).\n  - Đầy đủ thông tin: Mã môn, Tên môn, Giảng viên phụ trách, Thời gian đăng tải và số lượt tải về.\n  - Nút 'Tải về' kích hoạt download kèm Toast thông báo; Nút 'Đóng góp' điều hướng nhanh sang form nộp bài."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(12)

    set_notes(s16, "Đây là giao diện trang Kho học liệu (/documents) phục vụ sinh viên toàn trường. Phía trên là thanh công cụ tìm kiếm kết hợp bộ lọc theo Khoa và dải nút bấm loại tài liệu. Phía dưới là lưới thẻ học liệu được thiết kế dạng 3 cột responsive. Để sinh viên dễ dàng nhận diện, mỗi loại tài liệu được gắn một mã màu riêng: màu đỏ cho Đề thi, màu cam cho Slide và màu xanh cho Giáo trình. Mỗi thẻ hiển thị rõ ràng thông tin môn học, số lượt tải về và nút tải file trực tiếp kèm thông báo Toast sinh động.")

    # ==========================================
    # SLIDE 17: UI Lecturer Documents
    # ==========================================
    s17 = prs.slides.add_slide(blank_layout)
    add_header(s17, "TASK 4 • GIAO DIỆN NGƯỜI DÙNG", "GIAO DIỆN QUẢN TRỊ KHO TÀI LIỆU GIẢNG VIÊN (/lecturer/documents)")

    c17 = s17.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8))
    c17.fill.solid()
    c17.fill.fore_color.rgb = COLOR_BG_CARD
    c17.line.color.rgb = RGBColor(226, 232, 240)
    tf17 = c17.text_frame
    tf17.word_wrap = True
    p = tf17.paragraphs[0]
    p.text = "BẢNG ĐIỀU KHIỂN & HỆ THỐNG 4 MODAL QUẢN TRỊ"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf17.add_paragraph()
    p.text = "• Thống kê kho tài liệu: 4 KPI Cards hiển thị Tổng số tài liệu (5), Lượt xem (11.7k), Lượt tải (4.7k), Dung lượng kho (92.8 MB).\n\n• Hệ thống 4 Modal Dialog chuyên biệt:\n  1. Modal Thêm mới / Chỉnh sửa: Cập nhật thông tin học liệu, mã môn, khoa và nhãn tags.\n  2. Modal Lịch sử phiên bản: Quản lý các bản lưu trữ v1.0, v2.0 và form phát hành bản cập nhật mới.\n  3. Modal Phân quyền động: Cấp quyền xem/tải theo Lớp, Khoa hoặc Công khai toàn trường.\n  4. Modal Xác nhận xóa an toàn: Cảnh báo xác nhận trước khi xóa học liệu nhằm ngăn ngừa mất mát dữ liệu."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(12)

    set_notes(s17, "Đối với giảng viên, việc quản lý hàng chục tệp bài giảng đòi hỏi một công cụ quản trị chặt chẽ. Trang /lecturer/documents cung cấp bảng quản lý tài liệu tập trung với 4 thẻ thống kê và 4 hộp thoại Modal xử lý các nghiệp vụ chuyên sâu: Quản lý phiên bản cũ, Phân quyền chia sẻ theo lớp/khoa, Chỉnh sửa thông tin học liệu và Modal xóa an toàn.")

    # ==========================================
    # SLIDE 18: UI Lecturer Dashboard
    # ==========================================
    s18 = prs.slides.add_slide(blank_layout)
    add_header(s18, "TASK 4 • GIAO DIỆN NGƯỜI DÙNG", "GIAO DIỆN DASHBOARD PHÂN TÍCH GIẢNG VIÊN (/lecturer/dashboard)")

    c18 = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8))
    c18.fill.solid()
    c18.fill.fore_color.rgb = COLOR_BG_CARD
    c18.line.color.rgb = RGBColor(226, 232, 240)
    tf18 = c18.text_frame
    tf18.word_wrap = True
    p = tf18.paragraphs[0]
    p.text = "TRUNG TÂM PHÂN TÍCH DỮ LIỆU TƯƠNG TÁC THỜI GIAN THỰC"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf18.add_paragraph()
    p.text = "• 4 Thẻ KPI đầu trang:\n  Tổng tài liệu (5), Tổng lượt xem (11,720), Tổng lượt tải (4,700), Đóng góp chờ duyệt (2).\n\n• Cụm 3 Biểu đồ Recharts:\n  - Area Chart: Đường diện tích xem/tải kèm nút chuyển đổi 7 ngày / 30 ngày.\n  - Bar Chart: Xếp hạng top tài liệu được quan tâm nhiều nhất.\n  - Donut Chart: Cơ cấu % danh mục tài liệu có bảng chú thích màu sắc (Legend).\n\n• Nhật ký hoạt động (Live Activity Feed):\n  Dòng thời gian ghi nhận các sự kiện sinh viên nộp bài, tải file, duyệt bài theo từng phút."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(12)

    set_notes(s18, "Trang Dashboard giảng viên (/lecturer/dashboard) chính là trung tâm điều khiển và phân tích của hệ thống. Ngay khi truy cập, thầy/cô sẽ nắm bắt được các con số tổng quan qua 4 thẻ KPI. Điểm nhấn của trang là cụm 3 biểu đồ Recharts hoạt động mượt mà: biểu đồ Area Chart cho thấy nhịp độ học tập tăng cao vào giữa tuần; biểu đồ Bar Chart cho thấy tài liệu 'Lập trình Python' dẫn đầu với hơn 1,400 lượt tải. Mục Live Feed ghi nhận từng tương tác theo thời gian thực.")

    # ==========================================
    # SLIDE 19: Testing & RBAC Security
    # ==========================================
    s19 = prs.slides.add_slide(blank_layout)
    add_header(s19, "TASK 4 • HIỆU NĂNG & BẢO MẬT", "KIỂM THỬ HIỆU NĂNG, KHẢ NĂNG MỞ RỘNG & BẢO MẬT PHÂN QUYỀN (RBAC)")

    c19_l = s19.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8))
    c19_l.fill.solid()
    c19_l.fill.fore_color.rgb = COLOR_BG_CARD
    c19_l.line.color.rgb = RGBColor(226, 232, 240)
    tf19_l = c19_l.text_frame
    tf19_l.word_wrap = True
    p = tf19_l.paragraphs[0]
    p.text = "KIỂM THỬ HIỆU NĂNG & TỐI ƯU HÓA"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf19_l.add_paragraph()
    p.text = "• Tốc độ phản hồi tìm kiếm: < 15ms nhờ cơ chế Reactive State của Reflex.\n\n• Hiệu năng render Recharts: < 100ms, tỷ lệ khung hình đạt chuẩn 60 FPS mượt mà.\n\n• Khả năng mở rộng: Dễ dàng mở rộng kết nối với chỉ mục GIN của PostgreSQL khi kho tài liệu tăng trưởng lớn."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    c19_r = s19.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8))
    c19_r.fill.solid()
    c19_r.fill.fore_color.rgb = COLOR_BG_CARD
    c19_r.line.color.rgb = RGBColor(226, 232, 240)
    tf19_r = c19_r.text_frame
    tf19_r.word_wrap = True
    p = tf19_r.paragraphs[0]
    p.text = "MÔ HÌNH PHÂN QUYỀN BẢO MẬT RBAC"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf19_r.add_paragraph()
    p.text = "• Phân tách phân hệ rõ ràng: Phân hệ Sinh viên (student_*) và Giảng viên (lecturer_*).\n\n• Kiểm soát truy cập: Sinh viên không có quyền truy cập vào các hàm duyệt bài hoặc sửa đổi học liệu.\n\n• Phân quyền cấp dữ liệu (Row-Level Security): Tài liệu phân quyền theo lớp chỉ hiển thị cho sinh viên thuộc đúng lớp học đó."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    set_notes(s19, "Về mặt kỹ thuật và vận hành, nhóm đã tiến hành kiểm thử hiệu năng và bảo mật hệ thống một cách kỹ lưỡng. Về hiệu năng, các thao tác lọc và biểu đồ đều phản hồi tức thời dưới 15 mili-giây, không xảy ra hiện tượng giật lag giao diện. Về bảo mật, chúng em triển khai mô hình phân quyền dựa trên vai trò RBAC chặt chẽ: phân hệ của Sinh viên và Giảng viên được tách biệt hoàn toàn; sinh viên tuyệt đối không thể can thiệp vào các API duyệt bài hoặc xóa học liệu.")

    # ==========================================
    # SLIDE 20: Conclusion Task 4
    # ==========================================
    s20 = prs.slides.add_slide(blank_layout)
    add_header(s20, "TASK 4 • TỔNG KẾT", "TỔNG KẾT TASK 4 & TÀI LIỆU THAM KHẢO")

    c20_l = s20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.8))
    c20_l.fill.solid()
    c20_l.fill.fore_color.rgb = RGBColor(240, 253, 244)
    c20_l.line.color.rgb = RGBColor(187, 247, 208)
    tf20_l = c20_l.text_frame
    tf20_l.word_wrap = True
    p = tf20_l.paragraphs[0]
    p.text = "KẾT QUẢ ĐẠT ĐƯỢC TASK 4"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(21, 128, 61)
    p = tf20_l.add_paragraph()
    p.text = "• Xây dựng hoàn chỉnh Kho tra cứu học liệu số thông minh với khả năng tìm kiếm tức thời và bộ lọc đa chiều.\n\n• Hoàn thiện Bảng điều khiển Dashboard và Quản trị học liệu giảng viên với hệ thống biểu đồ Recharts trực quan, chuyên nghiệp.\n\n• Phân quyền bảo mật chặt chẽ, trải nghiệm người dùng hiện đại và hiệu năng ổn định."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    c20_r = s20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.9), Inches(5.7), Inches(4.8))
    c20_r.fill.solid()
    c20_r.fill.fore_color.rgb = COLOR_BG_CARD
    c20_r.line.color.rgb = RGBColor(226, 232, 240)
    tf20_r = c20_r.text_frame
    tf20_r.word_wrap = True
    p = tf20_r.paragraphs[0]
    p.text = "TÀI LIỆU THAM KHẢO CHÍNH"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p = tf20_r.add_paragraph()
    p.text = "1. Reflex Recharts Integration Guide\n   https://reflex.dev/docs/library/graphing/charts/\n\n2. Information Retrieval & Faceted Search Best Practices\n   Manning Publications\n\n3. Data Visualization for Web Applications with SVG & React\n   W3C Standards\n\n4. DocUni LTPython Codebase (GitHub Repository)"
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_DARK_TEXT
    p.space_before = Pt(14)

    set_notes(s20, "Kính thưa quý Thầy/Cô, tóm lại ở Task 4, nhóm đã hoàn thành xuất sắc các mục tiêu: xây dựng thành công Kho tài liệu môn học có bộ lọc đa diện tốc độ cao, hoàn thiện Dashboard phân tích trực quan với 3 biểu đồ Recharts và tích hợp đầy đủ công cụ quản trị học liệu cho giảng viên. Sự kết hợp giữa Task 3 về kiểm duyệt phiên bản và Task 4 về tra cứu, thống kê đã tạo nên một giải pháp hoàn chỉnh. Chúng em xin chân thành cảm ơn quý Thầy/Cô đã lắng nghe. Sau đây, nhóm em xin phép được thực hiện phần Live Demo trực tiếp!")

    # Save presentation
    output_path = os.path.join(os.getcwd(), "DocUni_Slide_ThuyetTrinh_Task3_Task4.pptx")
    prs.save(output_path)
    print(f"SUCCESS: Generated {len(prs.slides)} slides at {output_path}")

if __name__ == "__main__":
    create_deck()
