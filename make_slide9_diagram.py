import os
from PIL import Image, ImageDraw, ImageFont

def generate_slide9_diagram():
    w, h = 900, 1050
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("arialbd.ttf", 20)
        font_title = ImageFont.truetype("arialbd.ttf", 17)
        font_sub = ImageFont.truetype("arial.ttf", 14)
        font_tag = ImageFont.truetype("arialbd.ttf", 14)
    except:
        font_header = font_title = font_sub = font_tag = ImageFont.load_default()

    border_blue = (37, 99, 235, 255)
    border_slate = (15, 23, 42, 255)
    text_color = (15, 23, 42, 255)
    sub_color = (71, 85, 105, 255)
    arrow_color = (37, 99, 235, 255)

    draw.text((40, 30), "SƠ ĐỒ KIẾN TRÚC CÔNG NGHỆ 3 TẦNG (TECH STACK)", fill=text_color, font=font_header)
    draw.text((40, 65), "Đồng bộ thời gian thực 100% bằng Python từ giao diện đến CSDL", fill=sub_color, font=font_sub)

    layers = [
        ("TẦNG 1: FRONTEND / GIAO DIỆN NGƯỜI DÙNG", 
         "Biên dịch tự động từ Python sang React 19 + Radix Themes + Tailwind CSS.\nTrải nghiệm mượt mà, responsive trên máy tính và điện thoại.",
         (240, 249, 255, 255), (2, 132, 199, 255), "CLIENT"),

        ("KÊNH GIAO TIẾP THỜI GIAN THỰC: WEBSOCKETS", 
         "Duy trì kết nối 2 chiều liên tục giữa trình duyệt và máy chủ Python.\nĐộ trễ phản hồi cực thấp (< 50ms), tự động đồng bộ biến trạng thái (State).",
         (245, 243, 255, 255), (124, 58, 237, 255), "REALTIME"),

        ("TẦNG 2: BACKEND LOGIC & STATE MANAGER", 
         "Framework Reflex + FastAPI Event Loop xử lý hoàn toàn bằng Python.\nQuản lý State Machine kiểm duyệt, phân quyền vai trò và nhật ký hệ thống.",
         (240, 253, 244, 255), (22, 163, 74, 255), "SERVER"),

        ("TẦNG 3: CƠ SỞ DỮ LIỆU & ORM MÔ HÌNH HÓA", 
         "• Django ORM: Quản lý models, migration và quan hệ thực thể 1-N, N-N.\n• PostgreSQL: RDBMS chuẩn ACID, khóa dòng FOR UPDATE an toàn.",
         (254, 243, 199, 255), (217, 119, 6, 255), "DATABASE")
    ]

    card_w = 820
    card_h = 145
    left = 40
    top_start = 120
    gap = 75

    for i, (title, desc, bg_c, bdr_c, tag_str) in enumerate(layers):
        top = top_start + i * (card_h + gap)
        draw.rounded_rectangle([left, top, left + card_w, top + card_h], radius=14, fill=bg_c, outline=bdr_c, width=2)

        # Tag pill
        draw.rounded_rectangle([left + 25, top + 18, left + 140, top + 48], radius=8, fill=bdr_c)
        draw.text((left + 38, top + 24), tag_str, fill=(255, 255, 255, 255), font=font_tag)

        # Title & Desc
        draw.text((left + 155, top + 22), title, fill=text_color, font=font_title)
        draw.text((left + 25, top + 65), desc, fill=sub_color, font=font_sub)

        # Double arrow between layers
        if i < len(layers) - 1:
            ay1 = top + card_h + 8
            ay2 = ay1 + gap - 16
            ax = left + card_w // 2
            draw.line([(ax, ay1), (ax, ay2)], fill=arrow_color, width=3)
            # Arrow down
            draw.polygon([(ax, ay2 + 6), (ax - 6, ay2 - 2), (ax + 6, ay2 - 2)], fill=arrow_color)
            # Arrow up
            draw.polygon([(ax, ay1 - 6), (ax - 6, ay1 + 2), (ax + 6, ay1 + 2)], fill=arrow_color)

    out_file = r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_9_Kien_Truc.png"
    img.save(out_file)
    print("SUCCESS: Generated", out_file)

if __name__ == "__main__":
    generate_slide9_diagram()
