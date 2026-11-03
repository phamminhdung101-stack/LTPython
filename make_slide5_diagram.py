import os
from PIL import Image, ImageDraw, ImageFont

def generate_slide5_diagram():
    # Width x Height
    w, h = 900, 1100
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Colors
    bg_node = (248, 250, 252, 255)       # Slate 50
    border_blue = (37, 99, 235, 255)     # Blue 600
    border_slate = (15, 23, 42, 255)     # Black / Dark Navy
    text_color = (15, 23, 42, 255)       # Slate 900
    subtext_color = (71, 85, 105, 255)   # Slate 600
    arrow_color = (37, 99, 235, 255)
    commit_bg = (240, 253, 244, 255)     # Green 50
    commit_border = (22, 163, 74, 255)   # Green 600

    # Try font or default
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 15)
        font_tag = ImageFont.truetype("arialbd.ttf", 16)
    except:
        font_title = font_sub = font_tag = ImageFont.load_default()

    steps = [
        ("BƯỚC 1: KIỂM TRA QUYỀN", "Chủ sở hữu tài liệu hoặc có quyền can_edit", False),
        ("BƯỚC 2: LƯU FILE LÊN STORAGE", "Lưu trữ tệp vật lý an toàn vào ổ đĩa / Cloud", False),
        ("BƯỚC 3: KHÓA DÒNG TÀI LIỆU", "BEGIN; SELECT documents FOR UPDATE (Chống ghi đè)", False),
        ("BƯỚC 4: TẠO PHIÊN BẢN MỚI", "version_number = MAX + 1; INSERT document_versions", False),
        ("BƯỚC 5: CHUYỂN VỀ PENDING", "status = PENDING; xóa approved_by & approved_at", False),
        ("BƯỚC 6: GHI NHẬT KÝ HỆ THỐNG", "INSERT document_activity_logs (Hành động UPDATE)", False),
        ("BƯỚC 7: COMMIT GIAO DỊCH", "Hoàn tất Transaction; Xóa embedding cũ chờ duyệt lại", True)
    ]

    card_w = 680
    card_h = 95
    left = (w - card_w) // 2
    top_start = 50
    gap = 45

    for i, (title, sub, is_commit) in enumerate(steps):
        top = top_start + i * (card_h + gap)
        
        # Draw Card
        box_bg = commit_bg if is_commit else bg_node
        box_border = commit_border if is_commit else border_blue
        draw.rounded_rectangle([left, top, left + card_w, top + card_h], radius=14, fill=box_bg, outline=box_border, width=2)

        # Draw Number Tag circle
        circle_r = 18
        cx = left + 35
        cy = top + card_h // 2
        draw.ellipse([cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r], fill=box_border)
        num_str = str(i + 1)
        draw.text((cx - 5, cy - 10), num_str, fill=(255, 255, 255, 255), font=font_tag)

        # Draw Texts
        draw.text((left + 75, top + 18), title, fill=text_color, font=font_title)
        draw.text((left + 75, top + 52), sub, fill=subtext_color, font=font_sub)

        # Draw Down Arrow if not last
        if i < len(steps) - 1:
            arrow_x = w // 2
            arrow_y1 = top + card_h + 4
            arrow_y2 = arrow_y1 + gap - 8
            draw.line([(arrow_x, arrow_y1), (arrow_x, arrow_y2)], fill=arrow_color, width=3)
            # Arrow head
            draw.polygon([
                (arrow_x, arrow_y2 + 4),
                (arrow_x - 7, arrow_y2 - 6),
                (arrow_x + 7, arrow_y2 - 6)
            ], fill=arrow_color)

    out_file = r"d:\THAI_ANH_KY_WORKSPACE\Projects\LTPython\So_do_Slide_5_Rut_Gon.png"
    img.save(out_file)
    print("SUCCESS: Generated", out_file)

if __name__ == "__main__":
    generate_slide5_diagram()
