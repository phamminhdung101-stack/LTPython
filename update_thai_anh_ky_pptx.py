import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_complete_thai_anh_ky_deck():
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

    # Data for 10 slides
    slides = [
        # Slide 1: Bìa
        {
            "is_cover": True,
            "title": "TASK 3: VERSIONING, TAG, DUYỆT TÀI LIỆU PUBLIC VÀ LỊCH SỬ CHỈNH SỬA",
            "notes": "Kính thưa Thầy/Cô, em tên là Thái Anh Kỳ, MSSV 2431540124. Hôm nay em xin báo cáo Task 3 với nhiệm vụ xây dựng hệ thống quản lý phiên bản, gắn thẻ và quy trình kiểm duyệt học liệu. Đây là phân hệ nòng cốt bảo đảm chất lượng và tính toàn vẹn dữ liệu cho toàn bộ hệ thống DocUni."
        },
        # Slide 2: Đặt vấn đề và mục tiêu
        {
            "badge": "TASK 3 • SLIDE 2/10",
            "title": "NHỮNG VẤN ĐỀ VÀ MỤC TIÊU CỦA PHẦN VIỆC",
            "points": [
                "Tài liệu bị sửa đè, không biết đâu là bản mới nhất.",
                "Tài liệu sinh viên đóng góp có thể sai nhưng không ai kiểm tra.",
                "Không truy vết được ai đã sửa gì, vào lúc nào.",
                "Mục tiêu: Lưu mọi phiên bản của tài liệu, không ghi đè bản cũ.",
                "Mục tiêu: Giảng viên kiểm duyệt trước khi tài liệu được công khai."
            ],
            "img_path": None,
            "notes": "Trong thực tế, việc sinh viên tự do tải tài liệu dễ dẫn đến tình trạng sai lệch kiến thức và mất dấu vết khi tài liệu được cập nhật. Vì vậy, mục tiêu của Task 3 là giải quyết triệt để vấn đề này bằng cơ chế quản lý phiên bản tự động và quy trình kiểm duyệt chặt chẽ."
        },
        # Slide 3: Phân tích yêu cầu và vai trò
        {
            "badge": "TASK 3 • SLIDE 3/10",
            "title": "PHÂN TÍCH YÊU CẦU VÀ VAI TRÒ (USE CASE)",
            "points": [
                "SINH VIÊN: NỘP TÀI LIỆU, NỘP PHIÊN BẢN MỚI, XÓA TÀI LIỆU CỦA MÌNH.",
                "GIẢNG VIÊN: NỘP VÀ DUYỆT BÀI, GẮN GỠ TAG, XÓA TÀI LIỆU CỦA MÌNH.",
                "QUẢN TRỊ VIÊN: XÓA TÀI LIỆU, XEM NHẬT KÝ, DUYỆT HOẶC TỪ CHỐI.",
                "MỌI THAO TÁC THAY ĐỔI DỮ LIỆU ĐỀU TỰ ĐỘNG GHI NHẬT KÝ."
            ],
            "img_path": None,
            "notes": "Hệ thống phân định rõ ba vai trò: Sinh viên, Giảng viên và Quản trị viên với các quyền hạn cụ thể. Trong đó, mọi thao tác có tính chất làm thay đổi dữ liệu đều kích hoạt việc tự động ghi nhận nhật ký hệ thống để truy vết sau này."
        },
        # Slide 4: Thiết kế cơ sở dữ liệu
        {
            "badge": "TASK 3 • SLIDE 4/10",
            "title": "THIẾT KẾ CƠ SỞ DỮ LIỆU (ERD)",
            "points": [
                "NĂM BẢNG CHÍNH: TÀI LIỆU, PHIÊN BẢN, TAG, LIÊN KẾT TAG, NHẬT KÝ.",
                "MỘT TÀI LIỆU CÓ NHIỀU PHIÊN BẢN; SỐ PHIÊN BẢN KHÔNG ĐƯỢC TRÙNG.",
                "TAG LIÊN KẾT NHIỀU-NHIỀU VỚI TÀI LIỆU QUA BẢNG TRUNG GIAN.",
                "NHẬT KÝ GHI 10 LOẠI HÀNH ĐỘNG, VẪN GIỮ LẠI KHI NGƯỜI DÙNG BỊ XÓA.",
                "QUY TẮC NGHIỆP VỤ ĐẶT NGAY TRONG CSDL BẰNG UNIQUE VÀ CHECK."
            ],
            "img_path": None,
            "notes": "Em đã thiết kế mô hình cơ sở dữ liệu quan hệ gồm 5 thực thể chính. Bảng tài liệu liên kết một-nhiều với bảng phiên bản giúp lưu trữ toàn bộ các bản sửa đổi. Bảng nhật ký ghi nhận chi tiết 10 loại hành động và sử dụng các ràng buộc toàn vẹn ngay ở tầng CSDL."
        },
        # Slide 5: Quản lý phiên bản (Hình 3 rút gọn)
        {
            "badge": "TASK 3 • SLIDE 5/10",
            "title": "QUẢN LÝ PHIÊN BẢN HỌC LIỆU (VERSIONING)",
            "points": [
                "Mỗi lần cập nhật tạo phiên bản mới, không ghi đè bản cũ.",
                "Số phiên bản = số lớn nhất hiện có + 1, tính sau khi khóa tài liệu.",
                "Mỗi phiên bản lưu người cập nhật, file và tóm tắt thay đổi.",
                "Sau mỗi phiên bản mới, tài liệu quay về trạng thái chờ duyệt."
            ],
            "img_path": r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_5_Rut_Gon.png",
            "notes": "Thưa Thầy/Cô, khi cập nhật tài liệu, hệ thống khóa dòng trong cơ sở dữ liệu để tính số phiên bản kế tiếp an toàn, tránh xung đột. Toàn bộ thông tin thay đổi và nhật ký được lưu trong cùng một giao dịch; nếu có lỗi sẽ rollback toàn bộ và dọn dẹp file mồ côi. Sau khi có bản mới, tài liệu tự động chuyển về trạng thái chờ duyệt và vô hiệu hóa embedding cũ cho đến khi được duyệt lại."
        },
        # Slide 6: Duyệt tài liệu (Hình 5 + Hình 6 rút gọn)
        {
            "badge": "TASK 3 • SLIDE 6/10",
            "title": "QUY TRÌNH KIỂM DUYỆT HỌC LIỆU",
            "points": [
                "Ba trạng thái vòng đời học liệu: Chờ duyệt, Đã duyệt, Bị từ chối.",
                "Giảng viên mở hàng chờ, duyệt hoặc từ chối kèm lý do cụ thể.",
                "Khóa dòng và kiểm tra lại trạng thái, tránh hai người xử lý trùng.",
                "Quyết định phê duyệt và nhật ký ghi trong cùng một giao dịch."
            ],
            "img_path": r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_6_Rut_Gon.png",
            "notes": "Quy trình kiểm duyệt được thiết kế với ba trạng thái rõ ràng do Giảng viên trực tiếp thẩm định. Hệ thống khóa dòng và kiểm tra lại trạng thái trước khi xác nhận để tránh trường hợp hai người cùng xử lý một tài liệu. Thầy/Cô lưu ý rằng duyệt bài và công khai ra toàn trường là hai bước riêng biệt; nếu từ chối, lý do sẽ được lưu trong nhật ký."
        },
        # Slide 7: Tag (Hình 8 rút gọn)
        {
            "badge": "TASK 3 • SLIDE 7/10",
            "title": "QUẢN LÝ THẺ PHÂN LOẠI (TAGGING)",
            "points": [
                "Tag viết thường, duy nhất toàn hệ thống: java, bai-tap, python.",
                "Gắn tag: Tự tạo tag nếu chưa có, rồi nối với tài liệu học phần.",
                "Gỡ tag chỉ xóa liên kết, tag gốc vẫn dùng cho tài liệu khác.",
                "Mỗi lần gắn hoặc gỡ thẻ đều tự động ghi nhật ký hệ thống."
            ],
            "img_path": r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_7_Rut_Gon.png",
            "notes": "Hệ thống thẻ nhãn được chuẩn hóa tự động về chữ thường không dấu để tránh phân mảnh dữ liệu. Thao tác gắn và gỡ thẻ nằm trong một giao dịch với ràng buộc UNIQUE, nếu hai người tạo cùng tag thì CSDL sẽ chặn lại. Việc gỡ thẻ khỏi tài liệu chỉ xóa liên kết trung gian chứ không xóa thẻ khỏi kho dùng chung."
        },
        # Slide 8: Nhật ký và công nghệ (Hình 15)
        {
            "badge": "TASK 3 • SLIDE 8/10",
            "title": "NHẬT KÝ HỆ THỐNG VÀ CÔNG NGHỆ",
            "points": [
                "Hành động thay đổi dữ liệu: Ghi nhật ký trong cùng giao dịch.",
                "Lỗi thì rollback toàn bộ, không để lại nhật ký lẻ trên hệ thống.",
                "Hành vi xem và tải tài liệu: Đẩy vào hàng đợi, ghi theo lô.",
                "Bộ ba công nghệ cốt lõi: PostgreSQL, Django ORM và Reflex."
            ],
            "img_path": r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_8_Rut_Gon.png",
            "notes": "Mọi thao tác thay đổi dữ liệu đều được ghi nhật ký đồng thời trong cùng giao dịch; nếu lỗi sẽ rollback hoàn toàn. Đối với các hành vi tần suất cao như xem và tải, hệ thống định hướng đưa vào hàng đợi để worker gom nhóm ghi theo lô. Hệ thống sử dụng PostgreSQL đảm bảo chuẩn ACID và Reflex Python cho trải nghiệm thời gian thực."
        },
        # Slide 9: Kết quả / Demo
        {
            "badge": "TASK 3 • SLIDE 9/10",
            "title": "KẾT QUẢ TRIỂN KHAI VÀ LIÊN KẾT HỆ THỐNG",
            "points": [
                "Hoàn thành trọn vẹn 3 giao diện: Tải lên, Đóng góp và Kiểm duyệt.",
                "Biên dịch sạch sẽ 100% bằng Reflex Python, phản hồi dưới 50ms.",
                "Tài liệu sau khi duyệt lập tức xuất hiện trên kho tra cứu Task 4.",
                "Dữ liệu phiên bản chuẩn hóa cung cấp nguồn tri thức cho AI Assistant."
            ],
            "img_path": None,
            "notes": "Phân hệ Task 3 đã được triển khai hoàn chỉnh và biên dịch sạch sẽ trên nền tảng web. Tài liệu sau khi được giảng viên phê duyệt sẽ ngay lập tức được đẩy sang kho học liệu của Task 4 để sinh viên tra cứu. Đồng thời, dữ liệu phiên bản chuẩn này cũng là nguồn tri thức tin cậy cho tính năng AI Assistant của nhóm."
        },
        # Slide 10: Khó khăn và hướng cải thiện
        {
            "badge": "TASK 3 • SLIDE 10/10",
            "title": "KHÓ KHĂN, HƯỚNG CẢI THIỆN VÀ TÀI LIỆU THAM KHẢO",
            "points": [
                "Khó khăn: Đảm bảo an toàn kiểu dữ liệu AST trong quá trình biên dịch Reflex.",
                "Hướng cải thiện: Xóa mềm bằng cột deleted_at để giữ nguyên nhật ký hệ thống.",
                "Lý do: Khóa ngoại nhật ký đang ON DELETE CASCADE, xóa cứng sẽ mất lịch sử.",
                "Nguồn tham khảo: Tài liệu PostgreSQL, chuẩn SemVer 2.0 và Reflex Docs."
            ],
            "img_path": None,
            "notes": "Khó khăn lớn nhất là đảm bảo an toàn kiểu dữ liệu trong Reflex, em đã giải quyết bằng dataclass. Về hướng cải thiện, em đề xuất thêm cột deleted_at để xóa mềm, bởi vì hiện tại khóa ngoại nhật ký đang đặt CASCADE nên xóa cứng sẽ làm mất lịch sử truy vết. Em xin chân thành cảm ơn Thầy và các bạn đã chú ý theo dõi!"
        }
    ]

    for idx, sdata in enumerate(slides):
        slide = prs.slides.add_slide(blank_layout)

        # Notes
        if sdata.get("notes"):
            slide.notes_slide.notes_text_frame.text = sdata["notes"]

        if sdata.get("is_cover"):
            # Cover slide
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg.fill.solid()
            bg.fill.fore_color.rgb = COLOR_PRIMARY
            bg.line.fill.background()

            tb = slide.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(5.0))
            tf = tb.text_frame
            tf.word_wrap = True

            p0 = tf.paragraphs[0]
            p0.text = "HỌC VIỆN HÀNG KHÔNG VIỆT NAM — LẬP TRÌNH PYTHON"
            p0.font.size = Pt(14)
            p0.font.bold = True
            p0.font.color.rgb = RGBColor(147, 197, 253)

            p1 = tf.add_paragraph()
            p1.text = sdata["title"]
            p1.font.size = Pt(26)
            p1.font.bold = True
            p1.font.color.rgb = COLOR_WHITE
            p1.space_before = Pt(18)

            p2 = tf.add_paragraph()
            p2.text = "Giáo viên hướng dẫn: NGUYỄN THANH HIẾU — 0100100087202 - 24 ĐHTT02"
            p2.font.size = Pt(16)
            p2.font.color.rgb = RGBColor(203, 213, 225)
            p2.space_before = Pt(14)

            p3 = tf.add_paragraph()
            p3.text = "• Họ và tên: THÁI ANH KỲ\n• MSSV: 2431540124 — Lớp: 24ĐHTT03 — Nhóm 3\n• Ngày báo cáo: 16/10/2026"
            p3.font.size = Pt(15)
            p3.font.color.rgb = RGBColor(226, 232, 240)
            p3.space_before = Pt(24)

        else:
            # Header Badge
            badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.6), Inches(0.38))
            badge.fill.solid()
            badge.fill.fore_color.rgb = RGBColor(224, 231, 255)
            badge.line.fill.background()
            tf_b = badge.text_frame
            tf_b.word_wrap = True
            pb = tf_b.paragraphs[0]
            pb.text = sdata.get("badge", f"SLIDE {idx + 1}/10")
            pb.font.size = Pt(11)
            pb.font.bold = True
            pb.font.color.rgb = COLOR_SECONDARY
            pb.alignment = PP_ALIGN.CENTER

            # Title
            tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.7))
            tf_t = tx_title.text_frame
            tf_t.word_wrap = True
            pt = tf_t.paragraphs[0]
            pt.text = sdata["title"]
            pt.font.size = Pt(22)
            pt.font.bold = True
            pt.font.color.rgb = COLOR_PRIMARY

            has_img = sdata.get("img_path") and os.path.exists(sdata["img_path"])
            left_w = Inches(5.8) if has_img else Inches(11.7)

            # Left Card: Bullet points
            c_left = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), left_w, Inches(5.2))
            c_left.fill.solid()
            c_left.fill.fore_color.rgb = COLOR_BG_CARD
            c_left.line.color.rgb = RGBColor(226, 232, 240)
            tf_l = c_left.text_frame
            tf_l.word_wrap = True

            pl0 = tf_l.paragraphs[0]
            pl0.text = "NỘI DUNG CHÍNH (ĐÚNG QUY ƯỚC ≤ 15 TỪ/Ý)"
            pl0.font.size = Pt(14)
            pl0.font.bold = True
            pl0.font.color.rgb = COLOR_PRIMARY

            for pt_txt in sdata["points"]:
                p_item = tf_l.add_paragraph()
                p_item.text = f"• {pt_txt}"
                p_item.font.size = Pt(13)
                p_item.font.color.rgb = COLOR_DARK_TEXT
                p_item.space_before = Pt(12)

            # Right Side: Insert Diagram Image if present
            if has_img:
                img_path = sdata["img_path"]
                # Place image on the right
                img_left = Inches(7.0)
                img_top = Inches(1.7)
                img_width = Inches(5.5)
                # Keep aspect ratio
                slide.shapes.add_picture(img_path, img_left, img_top, width=img_width)

    out_file = r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\2431540124_ThaiAnhKy.pptx"
    prs.save(out_file)
    print("SUCCESS: Updated", out_file)

if __name__ == "__main__":
    build_complete_thai_anh_ky_deck()
