import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_student_deck(filename, student_name, student_id, task_title, task_num, slides_data):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    COLOR_PRIMARY = RGBColor(15, 23, 42)      # Slate 900
    COLOR_SECONDARY = RGBColor(37, 99, 235)   # Blue 600
    COLOR_BG_CARD = RGBColor(248, 250, 252)   # Slate 50
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_DARK_TEXT = RGBColor(30, 41, 59)    # Slate 800
    COLOR_MUTED = RGBColor(100, 116, 139)     # Slate 500

    blank_layout = prs.slide_layouts[6]

    for idx, sdata in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)

        # Set Speaker Notes
        if "notes" in sdata and sdata["notes"]:
            slide.notes_slide.notes_text_frame.text = sdata["notes"]

        if idx == 0:
            # Title slide (Dark Navy)
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg.fill.solid()
            bg.fill.fore_color.rgb = COLOR_PRIMARY
            bg.line.fill.background()

            tb = slide.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.3), Inches(5.5))
            tf = tb.text_frame
            tf.word_wrap = True

            p0 = tf.paragraphs[0]
            p0.text = "HỌC VIỆN HÀNG KHÔNG VIỆT NAM — KHOA CNTT"
            p0.font.size = Pt(14)
            p0.font.bold = True
            p0.font.color.rgb = RGBColor(147, 197, 253)

            p1 = tf.add_paragraph()
            p1.text = f"TASK {task_num}: {task_title.upper()}"
            p1.font.size = Pt(26)
            p1.font.bold = True
            p1.font.color.rgb = COLOR_WHITE
            p1.space_before = Pt(16)

            p2 = tf.add_paragraph()
            p2.text = "Môn học: Lập trình Python — Bài tập lớn nhóm: Web DocUni"
            p2.font.size = Pt(18)
            p2.font.color.rgb = RGBColor(203, 213, 225)
            p2.space_before = Pt(10)

            p3 = tf.add_paragraph()
            p3.text = f"• Sinh viên thực hiện: {student_name} (MSSV: {student_id} — Lớp: 24ĐHTT03)\n• Nhóm thực hiện: Nhóm 5 (Kho học liệu môn học DocUni)\n• Công nghệ: Python Reflex Framework, Radix UI Themes, WebSockets"
            p3.font.size = Pt(15)
            p3.font.color.rgb = RGBColor(226, 232, 240)
            p3.space_before = Pt(24)

        else:
            # Content slide
            # Header Badge
            badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.6), Inches(0.38))
            badge.fill.solid()
            badge.fill.fore_color.rgb = RGBColor(224, 231, 255)
            badge.line.fill.background()
            tf_b = badge.text_frame
            tf_b.word_wrap = True
            pb = tf_b.paragraphs[0]
            pb.text = f"TASK {task_num} • SLIDE {idx + 1}/10"
            pb.font.size = Pt(11)
            pb.font.bold = True
            pb.font.color.rgb = COLOR_SECONDARY
            pb.alignment = PP_ALIGN.CENTER

            # Title
            tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.7))
            tf_t = tx_title.text_frame
            tf_t.word_wrap = True
            pt = tf_t.paragraphs[0]
            pt.text = sdata["title"].upper()
            pt.font.size = Pt(20)
            pt.font.bold = True
            pt.font.color.rgb = COLOR_PRIMARY

            # Left Card: 3-5 Bullet points
            c_left = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(6.8), Inches(5.2))
            c_left.fill.solid()
            c_left.fill.fore_color.rgb = COLOR_BG_CARD
            c_left.line.color.rgb = RGBColor(226, 232, 240)
            tf_l = c_left.text_frame
            tf_l.word_wrap = True

            pl0 = tf_l.paragraphs[0]
            pl0.text = "CÁC Ý NỘI DUNG CHÍNH (≤ 15 TỪ/Ý)"
            pl0.font.size = Pt(14)
            pl0.font.bold = True
            pl0.font.color.rgb = COLOR_PRIMARY

            for pt_txt in sdata["points"]:
                p_item = tf_l.add_paragraph()
                p_item.text = f"• {pt_txt}"
                p_item.font.size = Pt(13)
                p_item.font.color.rgb = COLOR_DARK_TEXT
                p_item.space_before = Pt(12)

            # Right Card: Illustration Suggestion & Speaker Note Preview
            c_right = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.9), Inches(1.7), Inches(4.6), Inches(5.2))
            c_right.fill.solid()
            c_right.fill.fore_color.rgb = RGBColor(241, 245, 249)
            c_right.line.color.rgb = RGBColor(203, 213, 225)
            tf_r = c_right.text_frame
            tf_r.word_wrap = True

            pr0 = tf_r.paragraphs[0]
            pr0.text = "GỢI Ý HÌNH / SƠ ĐỒ MINH HỌA"
            pr0.font.size = Pt(13)
            pr0.font.bold = True
            pr0.font.color.rgb = COLOR_SECONDARY

            pr1 = tf_r.add_paragraph()
            pr1.text = sdata.get("illustration", "Chèn ảnh minh họa giao diện hoặc sơ đồ thực tế.")
            pr1.font.size = Pt(12)
            pr1.font.color.rgb = COLOR_DARK_TEXT
            pr1.space_before = Pt(8)

            pr2 = tf_r.add_paragraph()
            pr2.text = "GHI CHÚ THUYẾT TRÌNH (SPEAKER NOTES):"
            pr2.font.size = Pt(13)
            pr2.font.bold = True
            pr2.font.color.rgb = COLOR_PRIMARY
            pr2.space_before = Pt(16)

            pr3 = tf_r.add_paragraph()
            pr3.text = sdata.get("notes", "")
            pr3.font.size = Pt(11)
            pr3.font.italic = True
            pr3.font.color.rgb = COLOR_MUTED
            pr3.space_before = Pt(6)

    output_path = os.path.join(os.getcwd(), filename)
    prs.save(output_path)
    print(f"SUCCESS: Generated {output_path}")

# Task 3 Data (Thái Anh Kỳ)
task3_slides = [
    {
        "title": "Bìa Báo Cáo Task 3",
        "notes": "Kính thưa Thầy/Cô, em tên là Thái Anh Kỳ, MSSV 2431540124. Hôm nay em xin báo cáo Task 3 với nhiệm vụ xây dựng hệ thống quản lý phiên bản, gắn thẻ và quy trình kiểm duyệt học liệu. Đây là phân hệ nòng cốt bảo đảm chất lượng và tính toàn vẹn dữ liệu cho toàn bộ hệ thống DocUni."
    },
    {
        "title": "Đặt Vấn Đề Và Mục Tiêu Của Task 3",
        "points": [
            "Ghi đè file làm mất lịch sử các thay đổi học liệu qua các năm.",
            "Tải lên tự do dễ gây rác dữ liệu và sai lệch kiến thức đề thi.",
            "Mục tiêu: Tự động quản lý phiên bản học liệu v1.0, v2.0 có lưu vết.",
            "Mục tiêu: Thiết lập quy trình kiểm duyệt 2 chiều giữa sinh viên và giảng viên.",
            "Mục tiêu: Gắn thẻ nhãn đa chiều giúp liên kết chéo các chủ đề môn học."
        ],
        "illustration": "Bảng so sánh 2 cột: 'Bất cập hiện tại' (màu đỏ) vs 'Giải pháp DocUni Task 3' (màu xanh lá).",
        "notes": "Trong thực tế, việc sinh viên tự do tải tài liệu dễ dẫn đến tình trạng sai lệch kiến thức và mất dấu vết khi tài liệu được cập nhật. Vì vậy, mục tiêu của Task 3 là giải quyết triệt để vấn đề này bằng cơ chế quản lý phiên bản tự động và quy trình kiểm duyệt chặt chẽ. Ngoài ra, hệ thống gắn thẻ nhãn đa chiều giúp việc phân loại tài liệu trở nên khoa học và linh hoạt hơn."
    },
    {
        "title": "Thiết Kế Cơ Sở Dữ Liệu Và Quan Hệ Thực Thể",
        "points": [
            "Bảng documents liên kết 1-Nhiều với bảng document_versions lưu lịch sử sửa đổi.",
            "Bảng document_versions lưu version_number, file_path và bản tóm tắt changelog.",
            "Bảng document_contributions theo dõi trạng thái duyệt PENDING, APPROVED, REJECTED.",
            "Quan hệ Nhiều-Nhiều giữa documents và tags thông qua bảng trung gian document_tags."
        ],
        "illustration": "Sơ đồ ERD chuẩn quan hệ giữa 4 bảng: documents, document_versions, document_contributions và tags.",
        "notes": "Em đã thiết kế mô hình cơ sở dữ liệu quan hệ với 4 thực thể chính. Bảng tài liệu liên kết một-nhiều với bảng phiên bản giúp lưu trữ vĩnh viễn các bản sửa đổi cũ mà không bị ghi đè. Bảng đóng góp lưu trữ độc lập trạng thái duyệt và phản hồi của giảng viên để sinh viên tiện theo dõi."
    },
    {
        "title": "Quy Trình Kiểm Duyệt 3 Bước Và State Machine",
        "points": [
            "Bước 1: Sinh viên nộp tài liệu, hệ thống tự gán trạng thái PENDING khóa công khai.",
            "Bước 2: Giảng viên xem trước tài liệu, chọn Phê duyệt (APPROVED) hoặc Từ chối (REJECTED).",
            "Giảng viên bắt buộc nhập lý do phản hồi nếu bấm từ chối tài liệu đóng góp.",
            "Bước 3: Sinh viên đọc góp ý, sửa bài nộp lên v2.0 và quay lại PENDING."
        ],
        "illustration": "Sơ đồ Flowchart máy trạng thái biểu diễn luồng: PENDING -> APPROVED / REJECTED -> v2.0.",
        "notes": "Quy trình kiểm duyệt được chuẩn hóa thành một máy trạng thái khép kín gồm 3 bước. Tài liệu mới nộp luôn ở trạng thái PENDING và bị ẩn khỏi kho chung để đảm bảo an toàn. Khi giảng viên từ chối kèm nhận xét, sinh viên có thể nộp lại bản v2.0 kế thừa dữ liệu cũ mà không phải nhập lại từ đầu."
    },
    {
        "title": "Kiến Trúc Công Nghệ Và Tổ Chức Mã Nguồn",
        "points": [
            "Xây dựng 100% bằng Python Full-stack thông qua framework hiện đại Reflex.",
            "Tự động biên dịch mã Python sang React 19 và Radix UI chuẩn thiết kế.",
            "Giao tiếp thời gian thực Client-Server qua WebSockets với độ trễ dưới 50ms.",
            "Phân chia rõ ràng giữa State logic nghiệp vụ và hàm render giao diện người dùng."
        ],
        "illustration": "Sơ đồ kiến trúc 3 tầng: Client (React/Radix) <-> WebSocket <-> Server (FastAPI/Python State).",
        "notes": "Hệ thống được phát triển trên nền tảng Reflex, cho phép lập trình toàn bộ giao diện và backend bằng 100% Python thuần. Cơ chế WebSockets duy trì kết nối liên tục giúp giao diện cập nhật ngay lập tức khi trạng thái duyệt thay đổi. Cấu trúc mã nguồn được tổ chức theo chuẩn Clean Architecture, tách biệt rõ giữa xử lý dữ liệu và hiển thị."
    },
    {
        "title": "Cài Đặt Giao Diện Tải Lên Và Gắn Thẻ (/student/upload)",
        "points": [
            "Bố cục 2 cột hiện đại: Cột form nhập liệu và Cột quy chế học viện.",
            "Vùng kéo thả tệp rx.upload hỗ trợ các định dạng PDF, DOCX, PPTX và ZIP.",
            "Bộ ba Dropdown chọn phân cấp: Khoa viện -> Môn học -> Thư mục chuyên đề.",
            "Gắn thẻ dạng Chip tương tác: Nhập phím Enter hoặc bấm tag gợi ý sẵn."
        ],
        "illustration": "Ảnh chụp giao diện màn hình /student/upload có khoanh vùng Upload Zone và cụm Tags chip.",
        "notes": "Trang tải lên học liệu được thiết kế 2 cột chuẩn UX hiện đại. Sinh viên có thể kéo thả trực tiếp file tài liệu và chọn đúng phân cấp Khoa môn để tránh nhầm lẫn. Đặc biệt, chức năng gắn thẻ dạng Chip cho phép gõ tự do hoặc chọn nhanh các tag phổ biến như Python hay SQL."
    },
    {
        "title": "Theo Dõi Bài Nộp Và Nộp Bản v2.0 (/student/contributions)",
        "points": [
            "Trang bị 4 thẻ KPI cá nhân: Tổng đóng góp, Chờ duyệt, Đã duyệt, Bị từ chối.",
            "Thanh Tabs chuyển đổi linh hoạt giúp sinh viên lọc nhanh danh sách bài nộp.",
            "Hiển thị khung cảnh báo đỏ trích nguyên văn lời nhận xét của giảng viên.",
            "Modal nộp bản v2.0 kế thừa dữ liệu cũ và bắt buộc nhập bản tóm tắt."
        ],
        "illustration": "Ảnh chụp màn hình /student/contributions làm nổi bật Callout nhận xét từ chối và Modal nộp phiên bản v2.0.",
        "notes": "Trang đóng góp cá nhân giúp sinh viên nắm bắt trạng thái bài nộp qua 4 thẻ chỉ số và thanh lọc tab. Nếu bài nộp bị từ chối, hệ thống hiển thị rõ ràng lời phê của giảng viên để sinh viên khắc phục. Nút 'Nộp phiên bản v2.0' mở hộp thoại cho phép tải tệp mới và nhập lý do chỉnh sửa một cách thuận tiện."
    },
    {
        "title": "Cài Đặt Giao Diện Kiểm Duyệt Side-by-Side (/lecturer/approval)",
        "points": [
            "Thiết kế xem trước kép Split View: Hàng đợi bên trái và Khung chi tiết bên phải.",
            "Hiển thị đầy đủ thông tin: Họ tên sinh viên, MSSV, lớp và thời gian nộp bài.",
            "Tích hợp Document Reader Preview giả lập xem trước nội dung tài liệu trực tiếp.",
            "Thao tác 1 chạm: Phê duyệt xuất bản hoặc Từ chối kèm hộp thoại góp ý."
        ],
        "illustration": "Ảnh chụp màn hình /lecturer/approval hiển thị giao diện chia 2 cột Side-by-Side kèm nút Duyệt/Từ chối.",
        "notes": "Giao diện kiểm duyệt dành cho giảng viên sử dụng bố cục Side-by-Side chuyên nghiệp. Thầy/cô có thể chọn bài nộp ở cột bên trái và xem trước nội dung tệp ở cột bên phải mà không cần tải về máy tính. Thao tác thẩm định được tối ưu hóa chỉ với 1 cú nhấp chuột để phê duyệt hoặc từ chối kèm lời nhắc nhở."
    },
    {
        "title": "Kết Quả Triển Khai Và Liên Kết Sản Phẩm Nhóm",
        "points": [
            "Triển khai hoàn tất 3 màn hình tương tác mượt mà trên môi trường máy chủ.",
            "Biên dịch thành công 100% mã nguồn Reflex không phát sinh lỗi cảnh báo.",
            "Liên kết chặt chẽ với Task 4: Tài liệu duyệt xong tự động lên kho public.",
            "Cung cấp dữ liệu phiên bản chuẩn hóa cho trợ lý học tập AI Assistant tra cứu."
        ],
        "illustration": "Cụm ảnh chụp màn hình thực tế khi chạy trên trình duyệt kèm sơ đồ liên kết giữa Task 3 sang Task 4 và AI.",
        "notes": "Phân hệ Task 3 đã được triển khai hoàn chỉnh và biên dịch sạch sẽ trên nền tảng web. Tài liệu sau khi được giảng viên phê duyệt sẽ ngay lập tức được đẩy sang kho học liệu của Task 4 để sinh viên tra cứu. Đồng thời, dữ liệu phiên bản chuẩn này cũng là nguồn tri thức tin cậy cho tính năng AI Assistant của nhóm."
    },
    {
        "title": "Khó Khăn, Hướng Cải Thiện Và Tài Liệu Tham Khảo",
        "points": [
            "Khó khăn: Xử lý định kiểu tĩnh AST của Reflex bằng Python @dataclass.",
            "Hướng cải thiện: Bổ sung tính năng so sánh trực quan sai khác giữa hai phiên bản.",
            "Hướng cải thiện: Tự động quét phát hiện trùng lặp tài liệu bằng mã băm SHA-256.",
            "Nguồn tham khảo: Tài liệu Reflex Docs, chuẩn SemVer 2.0 và Radix Themes."
        ],
        "illustration": "Bảng tóm tắt khó khăn - giải pháp và danh sách link mã nguồn/tài liệu tham khảo chính.",
        "notes": "Khó khăn lớn nhất trong quá trình làm là việc đảm bảo tính an toàn kiểu dữ liệu trong Reflex, em đã giải quyết bằng việc sử dụng dataclass. Hướng phát triển tiếp theo là bổ sung cơ chế so sánh diff giữa hai phiên bản tài liệu. Em xin chân thành cảm ơn quý Thầy/Cô đã chú ý lắng nghe phần báo cáo của em!"
    }
]

# Task 4 Data (Phạm Nguyễn Vân Anh)
task4_slides = [
    {
        "title": "Bìa Báo Cáo Task 4",
        "notes": "Kính thưa Thầy/Cô, em tên là Phạm Nguyễn Vân Anh, MSSV 2431540123. Em xin đại diện nhóm báo cáo Task 4 với đề tài Lập chỉ mục, Tra cứu học liệu đa chiều và Dashboard quản trị. Đây là phân hệ trực tiếp phục vụ nhu cầu tìm kiếm của sinh viên và cung cấp số liệu thống kê trực quan cho giảng viên."
    },
    {
        "title": "Đặt Vấn Đề Và Mục Tiêu Của Task 4",
        "points": [
            "Số lượng tài liệu lớn khiến việc tìm kiếm thủ công mất nhiều thời gian.",
            "Nhà trường thiếu công cụ đo lường mức độ tương tác học liệu của sinh viên.",
            "Mục tiêu: Xây dựng kho học liệu /documents tìm kiếm đa chiều tức thời.",
            "Mục tiêu: Xây dựng Dashboard phân tích trực quan qua hệ thống biểu đồ Recharts.",
            "Mục tiêu: Cung cấp trang quản trị giúp giảng viên quản lý kho tài liệu bộ môn."
        ],
        "illustration": "Bảng so sánh 2 bài toán: 'Khó khăn tra cứu/thống kê' đối chiếu với '3 Mục tiêu kỹ thuật của Task 4'.",
        "notes": "Khi số lượng tài liệu tăng lên, việc sinh viên tìm kiếm thủ công rất tốn thời gian và dễ bỏ sót tài liệu quan trọng. Đồng thời, giảng viên cũng thiếu công cụ nắm bắt tài liệu nào đang được quan tâm nhất. Task 4 được xây dựng nhằm giải quyết cả hai bài toán: tối ưu trải nghiệm tìm kiếm cho người học và cung cấp bảng điều khiển phân tích cho người dạy."
    },
    {
        "title": "Mô Hình Lập Chỉ Mục Và Dữ Liệu Thống Kê",
        "points": [
            "Lập chỉ mục đa trường trên tiêu đề, mã môn học, khoa viện và nhãn tags.",
            "Chuẩn hóa chuỗi tìm kiếm không phân biệt chữ hoa thường và hỗ trợ tìm mờ.",
            "Bảng document_stats lưu trữ số lượt xem trực tuyến và số lượt tải về.",
            "Bảng document_permissions phân quyền truy cập theo từng Lớp học hoặc Khoa viện."
        ],
        "illustration": "Sơ đồ cấu trúc cây Inverted Index và mô hình quan hệ giữa bảng tài liệu với bảng thống kê tương tác.",
        "notes": "Để đảm bảo tốc độ phản hồi tính bằng mili-giây, em đã triển khai mô hình lập chỉ mục đa trường trên tiêu đề, mã môn và các thẻ nhãn. Song song đó, hệ thống duy trì bảng thống kê tương tác để tự động ghi nhận số lượt xem và lượt tải về. Bảng phân quyền giúp kiểm soát chính xác tài liệu nào được công khai hay giới hạn theo từng lớp học."
    },
    {
        "title": "Kiến Trúc Bộ Lọc Đa Chiều Và Tìm Kiếm Tức Thời",
        "points": [
            "Hệ thống tìm kiếm kết hợp 3 tầng lọc: Từ khóa, Khoa viện và Loại học liệu.",
            "Tầng từ khóa hỗ trợ quét tức thời trên tiêu đề và mô tả tài liệu.",
            "Áp dụng kỹ thuật Reactive Computed Vars @rx.var độc quyền của Reflex.",
            "Tự động tính toán lại kết quả lọc với độ trễ dưới 15ms không reload."
        ],
        "illustration": "Sơ đồ khối biểu diễn luồng dữ liệu 3 tầng lọc: Input -> Computed Var Filter -> Render Cards.",
        "notes": "Cơ chế tìm kiếm áp dụng mô hình Faceted Search với 3 tầng lọc đồng thời: từ khóa, khoa viện và định dạng tài liệu. Nhờ cơ chế Computed Vars của Reflex, khi người dùng gõ phím hoặc chọn danh mục, danh sách tài liệu sẽ tự động tính toán lại ngay trên server. Quá trình lọc phản hồi tức thời dưới 15 mili-giây mà không cần tải lại trang web."
    },
    {
        "title": "Kiến Trúc Trực Quan Hóa Dữ Liệu Dashboard",
        "points": [
            "Tích hợp thư viện đồ họa rx.recharts dựng trực tiếp từ mã nguồn Python.",
            "Render dưới dạng đồ họa vector SVG sắc nét và tự động co giãn responsive.",
            "Area Chart biểu diễn xu hướng lượt xem và tải theo 7 hoặc 30 ngày.",
            "Bar Chart xếp hạng Top 5 tài liệu môn học có lượt tải cao nhất.",
            "Donut Chart phân tích tỷ trọng cơ cấu phần trăm các loại tài liệu trong kho."
        ],
        "illustration": "Hình minh họa 3 loại biểu đồ (Area, Bar, Donut) với bảng màu chuẩn công nghệ (Blue, Green, Amber).",
        "notes": "Dashboard quản trị được tích hợp thư viện Reflex Recharts, cho phép sinh biểu đồ trực tiếp từ Python dưới dạng vector SVG sắc nét. Hệ thống trang bị 3 biểu đồ chính: biểu đồ miền so sánh xu hướng xem và tải, biểu đồ cột xếp hạng tài liệu được quan tâm nhất, và biểu đồ tròn phân tích cơ cấu học liệu. Tất cả biểu đồ đều hỗ trợ rê chuột xem thông số chi tiết."
    },
    {
        "title": "Cài Đặt Giao Diện Kho Học Liệu Môn Học (/documents)",
        "points": [
            "Thanh tìm kiếm trung tâm lớn kèm Dropdown chọn Khoa và bộ nút lọc Pills.",
            "Huy hiệu Badge tự động đếm và hiển thị số lượng tài liệu tìm thấy.",
            "Lưới thẻ học liệu 3 cột hiển thị đầy đủ môn học, giảng viên và lượt tải.",
            "Phân màu thẻ trực quan: Đỏ cho Đề thi, Cam cho Slide, Xanh cho Giáo trình."
        ],
        "illustration": "Ảnh chụp màn hình trang /documents làm nổi bật thanh tìm kiếm, dải nút lọc Pills và lưới thẻ tài liệu.",
        "notes": "Trang kho học liệu phục vụ sinh viên với thanh tìm kiếm trực quan và dải nút bấm phân loại dạng viên thuốc tiện lợi. Phía dưới là lưới thẻ tài liệu 3 cột có mã màu riêng biệt cho từng định dạng giúp dễ dàng nhận biết. Mỗi thẻ học liệu đều hiển thị rõ số lượt tải về và tích hợp nút tải nhanh kèm thông báo tức thời."
    },
    {
        "title": "Cài Đặt Giao Diện Quản Trị Tài Liệu Giảng Viên (/lecturer/documents)",
        "points": [
            "Cung cấp bảng quản trị dữ liệu tập trung các tài liệu giảng viên phụ trách.",
            "4 Thẻ KPI trên cùng: Tổng tài liệu, Lượt xem, Lượt tải và Dung lượng kho.",
            "Tích hợp 4 Modal chuyên biệt: Sửa metadata, Xem version, Phân quyền và Xóa an toàn.",
            "Modal phân quyền cho phép chia sẻ linh hoạt theo Lớp hoặc Công khai toàn trường."
        ],
        "illustration": "Ảnh chụp màn hình /lecturer/documents hiển thị bảng dữ liệu cùng các icon thao tác kích hoạt 4 Modal.",
        "notes": "Trang quản trị tài liệu giúp giảng viên dễ dàng kiểm soát các học liệu mình phụ trách qua bảng danh sách trực quan. Bốn thẻ KPI đầu trang cung cấp số liệu nhanh về dung lượng và tương tác học liệu. Đặc biệt, hệ thống trang bị 4 hộp thoại Modal giúp giảng viên chỉnh sửa thông tin, xem lại lịch sử phiên bản và phân quyền chia sẻ an toàn."
    },
    {
        "title": "Cài Đặt Dashboard Phân Tích Và Báo Cáo (/lecturer/dashboard)",
        "points": [
            "Hàng thẻ chỉ số KPI tổng quan đo lường tương tác học liệu toàn hệ thống.",
            "Biểu đồ Area Chart tích hợp nút bấm chuyển đổi chu kỳ 7 ngày và 30 ngày.",
            "Biểu đồ Bar Chart trực quan hóa số lượng tải về của các môn học tiêu biểu.",
            "Nhật ký hoạt động Live Feed cập nhật từng phút các hành động của sinh viên."
        ],
        "illustration": "Ảnh chụp màn hình /lecturer/dashboard với đầy đủ cụm 3 biểu đồ Recharts và mục Activity Feed.",
        "notes": "Dashboard giảng viên là trung tâm điều khiển và giám sát toàn diện mức độ sử dụng học liệu. Giảng viên có thể chuyển đổi chu kỳ xem 7 ngày hoặc 30 ngày trên biểu đồ Area Chart để theo dõi nhịp độ học tập. Mục nhật ký hoạt động thời gian thực phía dưới giúp giảng viên biết chính xác sinh viên nào vừa tải tài liệu hay nộp bài mới."
    },
    {
        "title": "Kết Quả Triển Khai Và Liên Kết Sản Phẩm Nhóm",
        "points": [
            "Tìm kiếm và bộ lọc phản hồi cực nhanh dưới 15ms mang lại trải nghiệm mượt mà.",
            "Dashboard và biểu đồ Recharts render chuẩn xác đạt tốc độ 60 khung hình/giây.",
            "Liên kết trực tiếp với Task 3: Hiển thị ngay các tài liệu vừa được phê duyệt.",
            "Triển khai phân quyền RBAC bảo vệ an toàn các chức năng quản trị giảng viên."
        ],
        "illustration": "Cụm ảnh chụp màn hình kiểm thử tốc độ lọc trang /documents và khả năng hiển thị responsive trên thiết bị di động.",
        "notes": "Hệ thống Task 4 đã được chạy thử nghiệm thành công với hiệu năng ấn tượng: thao tác lọc phản hồi dưới 15 mili-giây và biểu đồ hiển thị mượt mà. Phân hệ liên kết đồng bộ với Task 3, đảm bảo tài liệu duyệt xong sẽ xuất hiện ngay trên kho tra cứu. Đồng thời, cơ chế bảo mật RBAC giúp bảo vệ an toàn cho các trang quản trị của giảng viên."
    },
    {
        "title": "Khó Khăn, Hướng Cải Thiện Và Tài Liệu Tham Khảo",
        "points": [
            "Khó khăn: Định dạng dữ liệu reactive cho biểu đồ SVG Recharts trong Reflex.",
            "Hướng cải thiện: Tích hợp chỉ mục GIN của PostgreSQL khi kho tài liệu mở rộng.",
            "Hướng cải thiện: Bổ sung tính năng xuất báo cáo thống kê định dạng Excel và PDF.",
            "Nguồn tham khảo: Tài liệu Reflex Recharts, giáo trình Information Retrieval và Recharts.org."
        ],
        "illustration": "Bảng thống kê các mốc cải tiến tương lai kèm danh mục tài liệu tham khảo học thuật chính thức.",
        "notes": "Khó khăn chính của Task 4 là việc ánh xạ cấu trúc dữ liệu từ Python sang định dạng SVG của Recharts sao cho mượt mà nhất. Khi quy mô trường học mở rộng, nhóm sẽ nâng cấp lên chỉ mục chuyên sâu của PostgreSQL và thêm tính năng xuất file báo cáo. Em xin chân thành cảm ơn quý Thầy/Cô đã lắng nghe phần báo cáo của em!"
    }
]

if __name__ == "__main__":
    build_student_deck(
        "2431540124_ThaiAnhKy.pptx",
        "Thái Anh Kỳ",
        "2431540124",
        "Quản lý phiên bản, gắn thẻ và quy trình kiểm duyệt học liệu",
        "3",
        task3_slides
    )

    build_student_deck(
        "2431540123_PhamNguyenVanAnh.pptx",
        "Phạm Nguyễn Vân Anh",
        "2431540123",
        "Lập chỉ mục, giao diện tra cứu học liệu đa chiều và Dashboard quản trị",
        "4",
        task4_slides
    )
