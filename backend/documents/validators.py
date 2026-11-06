"""
DocUni - Module Kiểm tra Định dạng & Dung lượng File (File Validator)
Phần 2:
- Whitelist đuôi file: .pdf, .docx, .pptx, .xlsx, .zip
- Dung lượng tối đa: 50MB
- Tính mã băm SHA-256 kiểm tra toàn vẹn dữ liệu
"""

import os
import hashlib
from typing import Tuple, Dict, Any, Optional
from django.conf import settings

# 50MB chuẩn theo đề bài
DEFAULT_MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 52,428,800 bytes

ALLOWED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.zip': 'application/zip',
}

# Hỗ trợ thêm các MIME type phụ phụ thuộc vào hệ điều hành / browser
MIME_ALIASES = {
    'application/x-zip-compressed': '.zip',
    'application/octet-stream': None,  # Cho phép nếu đuôi file hợp lệ
}


def get_max_upload_size() -> int:
    return getattr(settings, 'MAX_UPLOAD_SIZE', DEFAULT_MAX_UPLOAD_SIZE)


def calculate_sha256(file_obj) -> str:
    """
    Tính mã băm SHA-256 của file bằng cách đọc theo chunk để không gây tràn RAM.
    Tự động reset con trỏ file (seek 0) trước và sau khi đọc.
    """
    sha256 = hashlib.sha256()
    try:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)

        if hasattr(file_obj, 'chunks'):
            for chunk in file_obj.chunks():
                sha256.update(chunk)
        elif hasattr(file_obj, 'read'):
            while True:
                chunk = file_obj.read(65536)
                if not chunk:
                    break
                sha256.update(chunk)
        elif isinstance(file_obj, (bytes, bytearray)):
            sha256.update(file_obj)

        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
    except Exception:
        pass
    return sha256.hexdigest()


def validate_file_upload(file_obj, filename: Optional[str] = None) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Kiểm tra file upload:
    - Kiểm tra có file hay không
    - Kiểm tra đuôi file (.pdf, .docx, .pptx, .xlsx, .zip)
    - Kiểm tra dung lượng (<= 50MB)
    - Tính toán SHA-256 và xác định Content-Type

    Trả về: (is_valid, error_message, metadata_dict)
    """
    if not file_obj:
        return False, "Vui lòng chọn file tài liệu cần tải lên.", {}

    # Lấy tên file
    name = filename or getattr(file_obj, 'name', '') or 'unknown_file'
    _, ext = os.path.splitext(name)
    ext_lower = ext.lower()

    # 1. Kiểm tra phần mở rộng
    if ext_lower not in ALLOWED_EXTENSIONS:
        allowed_str = ', '.join(ALLOWED_EXTENSIONS.keys())
        return False, f"Định dạng file '{ext}' không được hỗ trợ. Chỉ chấp nhận các định dạng: {allowed_str}.", {}

    # 2. Kiểm tra dung lượng file
    file_size = getattr(file_obj, 'size', None)
    if file_size is None:
        if hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell'):
            file_obj.seek(0, os.SEEK_END)
            file_size = file_obj.tell()
            file_obj.seek(0)
        elif isinstance(file_obj, (bytes, bytearray)):
            file_size = len(file_obj)
        else:
            file_size = 0

    max_size = get_max_upload_size()
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        curr_mb = round(file_size / (1024 * 1024), 2)
        return False, f"Dung lượng file ({curr_mb} MB) vượt quá giới hạn tối đa cho phép ({max_mb:.0f} MB).", {}

    if file_size == 0:
        return False, "File rỗng (0 bytes). Vui lòng chọn một file hợp lệ.", {}

    # 3. Xác định Content-Type chuẩn
    content_type = getattr(file_obj, 'content_type', None) or ALLOWED_EXTENSIONS.get(ext_lower, 'application/octet-stream')

    # 4. Tính toán checksum SHA-256
    checksum = calculate_sha256(file_obj)

    metadata = {
        'filename': name,
        'extension': ext_lower,
        'file_size': file_size,
        'content_type': content_type,
        'checksum_sha256': checksum,
    }
    return True, None, metadata
