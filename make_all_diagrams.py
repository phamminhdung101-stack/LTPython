import os
from PIL import Image, ImageDraw, ImageFont

def get_fonts():
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 18)
        font_sub = ImageFont.truetype("arial.ttf", 14)
        font_tag = ImageFont.truetype("arialbd.ttf", 15)
        font_header = ImageFont.truetype("arialbd.ttf", 20)
    except:
        font_title = font_sub = font_tag = font_header = ImageFont.load_default()
    return font_title, font_sub, font_tag, font_header

# --- SLIDE 6 DIAGRAM ---
def generate_slide6_diagram():
    w, h = 950, 1100
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    f_title, f_sub, f_tag, f_header = get_fonts()

    # Colors
    bg_card = (248, 250, 252, 255)
    border_blue = (37, 99, 235, 255)
    border_slate = (15, 23, 42, 255)
    text_color = (15, 23, 42, 255)
    sub_color = (71, 85, 105, 255)
    arrow_color = (37, 99, 235, 255)

    # Section 1: State Machine Overview (Top)
    draw.rounded_rectangle([40, 25, 910, 280], radius=12, fill=(241, 245, 249, 255), outline=border_slate, width=2)
    draw.text((60, 40), "1. MÁY TRẠNG THÁI HỌC LIỆU (STATE MACHINE)", fill=text_color, font=f_header)

    # 3 States Boxes
    draw.rounded_rectangle([70, 95, 290, 165], radius=10, fill=(254, 243, 199, 255), outline=(217, 119, 6, 255), width=2)
    draw.text((105, 110), "PENDING", fill=(180, 83, 9, 255), font=f_title)
    draw.text((95, 138), "Chờ GV phê duyệt", fill=sub_color, font=f_sub)

    draw.rounded_rectangle([365, 95, 585, 165], radius=10, fill=(240, 253, 244, 255), outline=(22, 163, 74, 255), width=2)
    draw.text((395, 110), "APPROVED", fill=(21, 128, 61, 255), font=f_title)
    draw.text((385, 138), "Công khai kho chung", fill=sub_color, font=f_sub)

    draw.rounded_rectangle([660, 95, 880, 165], radius=10, fill=(254, 242, 242, 255), outline=(220, 38, 38, 255), width=2)
    draw.text((690, 110), "REJECTED", fill=(185, 28, 28, 255), font=f_title)
    draw.text((680, 138), "Từ chối kèm lý do", fill=sub_color, font=f_sub)

    # State transitions notes
    draw.text((70, 190), "• Duyệt (Approve): PENDING -> APPROVED (Xuất bản)", fill=text_color, font=f_sub)
    draw.text((70, 218), "• Từ chối (Reject): PENDING -> REJECTED (Lưu feedback)", fill=text_color, font=f_sub)
    draw.text((70, 246), "• Nộp lại bản sửa đổi: REJECTED / APPROVED -> PENDING (Thẩm định lại)", fill=text_color, font=f_sub)

    # Section 2: Flow Steps (Bottom)
    draw.text((40, 320), "2. LUỒNG THẨM ĐỊNH TRONG TRANSACTION AN TOÀN", fill=border_blue, font=f_header)

    steps = [
        ("BƯỚC 1: MỞ DANH SÁCH PENDING", "Giảng viên mở hàng đợi duyệt, chọn 1 tài liệu cần thẩm định"),
        ("BƯỚC 2: KHÓA DÒNG KIỂM TRA", "BEGIN; SELECT documents FOR UPDATE; kiểm tra còn PENDING"),
        ("BƯỚC 3: QUYẾT ĐỊNH THẨM ĐỊNH", "• DUYỆT: UPDATE status=APPROVED | • TỪ CHỐI: UPDATE status=REJECTED"),
        ("BƯỚC 4: GHI NHẬT KÝ HỆ THỐNG", "INSERT document_activity_logs (APPROVE / REJECT kèm lý do)"),
        ("BƯỚC 5: COMMIT GIAO DỊCH", "Lưu thay đổi nguyên tử; Rollback nếu phát sinh lỗi"),
        ("BƯỚC 6: HẬU KỲ SAU DUYỆT", "Nếu Duyệt: Đẩy job tạo AI Embedding | Nếu Từ chối: Thông báo SV")
    ]

    card_w = 870
    card_h = 75
    left = 40
    top_start = 365
    gap = 40

    for i, (stitle, ssub) in enumerate(steps):
        top = top_start + i * (card_h + gap)
        is_last = (i == len(steps) - 1)
        card_bg = (240, 253, 244, 255) if is_last else bg_card
        card_bdr = (22, 163, 74, 255) if is_last else border_blue

        draw.rounded_rectangle([left, top, left + card_w, top + card_h], radius=10, fill=card_bg, outline=card_bdr, width=2)

        # Number circle
        cx = left + 30
        cy = top + card_h // 2
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=card_bdr)
        draw.text((cx - 5, cy - 9), str(i + 1), fill=(255, 255, 255, 255), font=f_tag)

        draw.text((left + 65, top + 14), stitle, fill=text_color, font=f_title)
        draw.text((left + 65, top + 42), ssub, fill=sub_color, font=f_sub)

        # Arrow
        if i < len(steps) - 1:
            ay1 = top + card_h + 3
            ay2 = ay1 + gap - 6
            ax = left + card_w // 2
            draw.line([(ax, ay1), (ax, ay2)], fill=arrow_color, width=3)
            draw.polygon([(ax, ay2 + 3), (ax - 6, ay2 - 5), (ax + 6, ay2 - 5)], fill=arrow_color)

    out_file = r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_6_Rut_Gon.png"
    img.save(out_file)
    print("SUCCESS: Generated", out_file)

# --- SLIDE 7 DIAGRAM ---
def generate_slide7_diagram():
    w, h = 950, 1050
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    f_title, f_sub, f_tag, f_header = get_fonts()

    # Colors
    bg_card = (248, 250, 252, 255)
    border_blue = (37, 99, 235, 255)
    border_green = (22, 163, 74, 255)
    border_red = (220, 38, 38, 255)
    text_color = (15, 23, 42, 255)
    sub_color = (71, 85, 105, 255)

    # Title header
    draw.text((40, 30), "QUY TRÌNH GẮN VÀ GỠ THẺ TAG (HÌNH 8 RÚT GỌN)", fill=text_color, font=f_header)
    draw.text((40, 65), "Toàn bộ quy trình được đóng gói trong một Database Transaction", fill=sub_color, font=f_sub)

    # Branch 1: Gắn Tag (Trái)
    draw.rounded_rectangle([40, 110, 470, 980], radius=14, fill=(240, 253, 244, 255), outline=border_green, width=2)
    draw.text((70, 130), "NHÁNH 1: GẮN THẺ (ADD TAG)", fill=(21, 128, 61, 255), font=f_header)

    steps_add = [
        ("1. CHUẨN HÓA TÊN TAG", "Chuyển chữ thường, cắt khoảng trắng\nVí dụ: 'Python Cơ Bản' -> 'python-co-ban'"),
        ("2. KIỂM TRA TỒN TẠI", "SELECT * FROM tags WHERE name = ...\nNếu chưa có: INSERT tags mới"),
        ("3. NỐI TÀI LIỆU - TAG", "INSERT INTO document_tags\n(document_id, tag_id)"),
        ("4. GHI NHẬT KÝ ADD_TAG", "INSERT activity_logs: action='ADD_TAG'\nkèm tên thẻ được gắn"),
        ("5. COMMIT GIAO DỊCH", "Lưu thay đổi; Nếu trùng tag thì\nràng buộc UNIQUE bảo vệ an toàn")
    ]

    for i, (stitle, ssub) in enumerate(steps_add):
        top = 185 + i * 155
        draw.rounded_rectangle([60, top, 450, top + 115], radius=10, fill=bg_card, outline=border_green, width=2)
        draw.text((80, top + 15), stitle, fill=text_color, font=f_title)
        draw.text((80, top + 48), ssub, fill=sub_color, font=f_sub)
        if i < len(steps_add) - 1:
            draw.line([(255, top + 117), (255, top + 152)], fill=border_green, width=3)
            draw.polygon([(255, top + 155), (249, top + 147), (261, top + 147)], fill=border_green)

    # Branch 2: Gỡ Tag (Phải)
    draw.rounded_rectangle([490, 110, 910, 980], radius=14, fill=(254, 242, 242, 255), outline=border_red, width=2)
    draw.text((520, 130), "NHÁNH 2: GỠ THẺ (REMOVE TAG)", fill=(185, 28, 28, 255), font=f_header)

    steps_remove = [
        ("1. XÁC ĐỊNH LIÊN KẾT", "Tìm cặp (document_id, tag_id)\ncần gỡ khỏi tài liệu"),
        ("2. XÓA BẢNG TRUNG GIAN", "DELETE FROM document_tags\nChỉ xóa liên kết, KHÔNG xóa bảng tags"),
        ("3. GIỮ NGUYÊN TAG GỐC", "Tag gốc vẫn được bảo toàn để các\ntài liệu khác trong kho tiếp tục dùng"),
        ("4. GHI NHẬT KÝ REMOVE_TAG", "INSERT activity_logs: action='REMOVE_TAG'\nkèm tên thẻ bị gỡ"),
        ("5. COMMIT GIAO DỊCH", "Hoàn tất Transaction;\nKhôi phục (ROLLBACK) nếu gặp lỗi")
    ]

    for i, (stitle, ssub) in enumerate(steps_remove):
        top = 185 + i * 155
        draw.rounded_rectangle([510, top, 890, top + 115], radius=10, fill=bg_card, outline=border_red, width=2)
        draw.text((530, top + 15), stitle, fill=text_color, font=f_title)
        draw.text((530, top + 48), ssub, fill=sub_color, font=f_sub)
        if i < len(steps_remove) - 1:
            draw.line([(700, top + 117), (700, top + 152)], fill=border_red, width=3)
            draw.polygon([(700, top + 155), (694, top + 147), (706, top + 147)], fill=border_red)

    out_file = r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_7_Rut_Gon.png"
    img.save(out_file)
    print("SUCCESS: Generated", out_file)

# --- SLIDE 8 DIAGRAM ---
def generate_slide8_diagram():
    w, h = 950, 1050
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    f_title, f_sub, f_tag, f_header = get_fonts()

    # Colors
    bg_card = (248, 250, 252, 255)
    border_blue = (37, 99, 235, 255)
    border_slate = (15, 23, 42, 255)
    text_color = (15, 23, 42, 255)
    sub_color = (71, 85, 105, 255)

    # Title header
    draw.text((40, 25), "QUY TRÌNH GHI NHẬT KÝ & CÔNG NGHỆ (HÌNH 15)", fill=text_color, font=f_header)
    draw.text((40, 60), "Tách bạch 2 luồng: Đồng bộ dữ liệu & Bất đồng bộ tần suất cao", fill=sub_color, font=f_sub)

    # Left Column: Synchronous (DB changes)
    draw.rounded_rectangle([40, 100, 470, 780], radius=12, fill=(240, 253, 244, 255), outline=(22, 163, 74, 255), width=2)
    draw.text((60, 120), "LUỒNG 1: THAY ĐỔI DỮ LIỆU", fill=(21, 128, 61, 255), font=f_title)
    draw.text((60, 148), "CREATE, UPDATE, DELETE, APPROVE, TAG...", fill=sub_color, font=f_sub)

    steps_sync = [
        ("BEGIN TRANSACTION", "Khởi tạo giao dịch trong PostgreSQL"),
        ("THỰC HIỆN ĐỔI DỮ LIỆU", "Ghi/Sửa tài liệu, phiên bản hoặc tag"),
        ("INSERT ACTIVITY LOG", "Ghi log trong cùng transaction"),
        ("KIỂM TRA THÀNH CÔNG?", "Cả thao tác dữ liệu và log đều OK?"),
        ("COMMIT HOẶC ROLLBACK", "• Có -> COMMIT an toàn\n• Không -> ROLLBACK toàn bộ, không có log lẻ")
    ]

    for i, (stitle, ssub) in enumerate(steps_sync):
        top = 185 + i * 115
        draw.rounded_rectangle([60, top, 450, top + 85], radius=8, fill=bg_card, outline=(22, 163, 74, 255), width=1)
        draw.text((80, top + 15), stitle, fill=text_color, font=f_title)
        draw.text((80, top + 42), ssub, fill=sub_color, font=f_sub)
        if i < len(steps_sync) - 1:
            draw.line([(255, top + 87), (255, top + 113)], fill=(22, 163, 74, 255), width=2)

    # Right Column: Asynchronous Queue (View/Download)
    draw.rounded_rectangle([490, 100, 910, 780], radius=12, fill=(238, 242, 255, 255), outline=border_blue, width=2)
    draw.text((510, 120), "LUỒNG 2: XEM & TẢI (ĐỊNH HƯỚNG)", fill=border_blue, font=f_title)
    draw.text((510, 148), "VIEW, DOWNLOAD (Tần suất truy cập cao)", fill=sub_color, font=f_sub)

    steps_async = [
        ("PHÁT SINH SỰ KIỆN", "Người dùng mở xem hoặc tải file"),
        ("ĐẨY VÀO HÀNG ĐỢI (QUEUE)", "Đẩy nhanh vào Redis/Queue, trả kết quả tức thì"),
        ("WORKER GOM NHÓM", "Background worker khử trùng lặp đếm"),
        ("GHI BATCH LOG THEO LÔ", "Ghi theo đợt lớn vào DB, giảm tải I/O"),
        ("CẬP NHẬT BỘ ĐẾM", "Tăng trường views/downloads trong documents")
    ]

    for i, (stitle, ssub) in enumerate(steps_async):
        top = 185 + i * 115
        draw.rounded_rectangle([510, top, 890, top + 85], radius=8, fill=bg_card, outline=border_blue, width=1)
        draw.text((530, top + 15), stitle, fill=text_color, font=f_title)
        draw.text((530, top + 42), ssub, fill=sub_color, font=f_sub)
        if i < len(steps_async) - 1:
            draw.line([(700, top + 87), (700, top + 113)], fill=border_blue, width=2)

    # Bottom Technology Banner (3 Boxes)
    draw.rounded_rectangle([40, 810, 910, 1010], radius=12, fill=bg_card, outline=border_slate, width=2)
    draw.text((60, 825), "3 TRỤ CỘT CÔNG NGHỆ CHÍNH CỦA HỆ THỐNG", fill=text_color, font=f_title)

    techs = [
        ("POSTGRESQL", "RDBMS mạnh mẽ, hỗ trợ Transaction ACID, khóa FOR UPDATE và chỉ mục tìm kiếm"),
        ("DJANGO ORM", "Mô hình hóa dữ liệu hướng đối tượng, quản lý Migration và Transaction nguyên tử"),
        ("REFLEX (PYTHON)", "Full-stack Framework hiện đại, đồng bộ State thời gian thực qua WebSockets")
    ]

    for i, (tname, tdesc) in enumerate(techs):
        bx = 60 + i * 280
        draw.rounded_rectangle([bx, 860, bx + 265, 985], radius=8, fill=(255, 255, 255, 255), outline=border_blue, width=2)
        draw.text((bx + 15, 875), tname, fill=border_blue, font=f_title)
        draw.text((bx + 15, 905), tdesc[:40] + "\n" + tdesc[40:80] + "\n" + tdesc[80:], fill=sub_color, font=f_sub)

    out_file = r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_8_Rut_Gon.png"
    img.save(out_file)
    print("SUCCESS: Generated", out_file)

if __name__ == "__main__":
    generate_slide6_diagram()
    generate_slide7_diagram()
    generate_slide8_diagram()
