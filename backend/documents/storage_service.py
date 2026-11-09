"""
DocUni File Storage Service.
Quản lý lưu trữ file cục bộ sử dụng Django FileSystemStorage (media/documents/YYYY/MM/...).
Không sử dụng dịch vụ đám mây trả phí.
Bao gồm:
- Kiểm tra whitelist phần mở rộng (PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT).
- Kiểm tra MIME type và magic bytes thực tế của file.
- Giới hạn dung lượng file theo cấu hình MAX_UPLOAD_SIZE.
- Tạo object key duy nhất (documents/YYYY/MM/{uuid}_{filename}).
- Chống Path Traversal và bảo vệ an toàn hệ thống.
"""

import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousFileOperation
from rest_framework.exceptions import ValidationError


# Whitelist định dạng và MIME type tiêu chuẩn
ALLOWED_EXTENSIONS = {
    '.pdf': {
        'mime': 'application/pdf',
        'type': 'PDF',
        'magic': [b'%PDF-'],
    },
    '.docx': {
        'mime': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'type': 'DOCX',
        'magic': [b'PK\x03\x04'],
    },
    '.doc': {
        'mime': 'application/msword',
        'type': 'DOC',
        'magic': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],
    },
    '.pptx': {
        'mime': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'type': 'PPTX',
        'magic': [b'PK\x03\x04'],
    },
    '.ppt': {
        'mime': 'application/vnd.ms-powerpoint',
        'type': 'PPT',
        'magic': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],
    },
    '.xlsx': {
        'mime': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'type': 'XLSX',
        'magic': [b'PK\x03\x04'],
    },
    '.xls': {
        'mime': 'application/vnd.ms-excel',
        'type': 'XLS',
        'magic': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],
    },
    '.txt': {
        'mime': 'text/plain',
        'type': 'TXT',
        'magic': [],  # Kiểm tra text thuần không chứa null bytes
    },
}


class LocalDocumentStorageService:
    """
    Dịch vụ lưu trữ file cục bộ dựa trên Django FileSystemStorage
    """

    def __init__(self):
        self.media_root = Path(settings.MEDIA_ROOT).resolve()
        # Đảm bảo thư mục media gốc tồn tại
        self.media_root.mkdir(parents=True, exist_ok=True)
        self.storage = FileSystemStorage(location=str(self.media_root), base_url=settings.MEDIA_URL)

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Làm sạch tên file ban đầu, chống Path Traversal và ký tự đặc biệt.
        """
        base = os.path.basename(filename).strip()
        # Loại bỏ các ký tự nguy hiểm, giữ lại chữ, số, dấu gạch nối, gạch dưới và dấu chấm
        cleaned = re.sub(r'[^a-zA-Z0-9_\u00C0-\u024F\u1EA0-\u1EF9.-]', '_', base)
        # Giảm các dấu gạch dưới liên tiếp
        cleaned = re.sub(r'_+', '_', cleaned).strip('_')
        return cleaned or f"document_{uuid.uuid4().hex[:8]}"

    @classmethod
    def validate_file(cls, uploaded_file) -> Tuple[str, str, str]:
        """
        Kiểm tra tính hợp lệ của file:
        - Phần mở rộng trong danh sách cho phép (PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT)
        - Dung lượng file <= MAX_UPLOAD_SIZE
        - Magic bytes và nội dung nhị phân thực tế
        
        Trả về tuple: (ext, mime_type, file_type)
        """
        if not uploaded_file:
            raise ValidationError('Vui lòng chọn tệp tài liệu để tải lên.')

        original_name = uploaded_file.name or ''
        ext = os.path.splitext(original_name)[1].lower()

        # 1. Kiểm tra phần mở rộng
        if ext not in ALLOWED_EXTENSIONS:
            allowed_list = ', '.join(sorted(ALLOWED_EXTENSIONS.keys()))
            raise ValidationError(
                f'Định dạng tệp "{ext}" không được hỗ trợ. Các định dạng cho phép: {allowed_list}.'
            )

        # 2. Kiểm tra dung lượng file
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 50 * 1024 * 1024)
        if uploaded_file.size > max_size:
            max_mb = max_size // (1024 * 1024)
            raise ValidationError(
                f'Dung lượng tệp ({uploaded_file.size / (1024 * 1024):.2f} MB) vượt quá giới hạn cho phép (tối đa {max_mb} MB).'
            )

        if uploaded_file.size == 0:
            raise ValidationError('Tệp tải lên không được rỗng (0 bytes).')

        spec = ALLOWED_EXTENSIONS[ext]
        expected_mime = spec['mime']
        file_type = spec['type']

        # 3. Kiểm tra Magic Bytes / Nội dung thực tế
        header = uploaded_file.read(2048)
        uploaded_file.seek(0)

        magics = spec.get('magic', [])
        if magics:
            match = any(header.startswith(m) for m in magics)
            if not match:
                raise ValidationError(
                    f'Nội dung tệp không khớp với định dạng mở rộng "{ext}" hoặc tệp đã bị hỏng.'
                )
        elif ext == '.txt':
            # Kiểm tra text không chứa null bytes
            if b'\x00' in header:
                raise ValidationError('Tệp văn bản .txt chứa ký tự nhị phân không hợp lệ.')
            try:
                header.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    header.decode('latin-1')
                except Exception:
                    raise ValidationError('Tệp văn bản không thể giải mã ký tự hợp lệ.')

        return ext, expected_mime, file_type

    def save_document_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Lưu file vào thư mục media/documents/YYYY/MM/{uuid}_{name}.
        Trả về metadata của file đã lưu.
        """
        ext, mime_type, file_type = self.validate_file(uploaded_file)
        clean_name = self.sanitize_filename(uploaded_file.name)

        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')

        # Tạo object key duy nhất
        unique_id = uuid.uuid4().hex[:12]
        stored_file_name = f"{unique_id}_{clean_name}"
        # object_key là đường dẫn tương đối trong media/
        object_key = f"documents/{year}/{month}/{stored_file_name}".replace('\\', '/')

        # Lưu file vật lý bằng FileSystemStorage
        saved_name = self.storage.save(object_key, uploaded_file)
        file_size = uploaded_file.size

        return {
            'file_name': stored_file_name,
            'original_file_name': uploaded_file.name,
            'file_type': file_type,
            'file_size': file_size,
            'mime_type': mime_type,
            'object_key': saved_name.replace('\\', '/'),
            'storage_provider': 'LOCAL',
            'upload_date': now.isoformat(),
        }

    def get_absolute_path(self, object_key: str) -> Optional[Path]:
        """
        Xác định đường dẫn tuyệt đối an toàn của file trong media/.
        Chống Path Traversal triệt để.
        """
        if not object_key:
            return None

        # Chống path traversal
        clean_key = object_key.strip().replace('\\', '/')
        if '..' in clean_key or clean_key.startswith('/'):
            raise SuspiciousFileOperation('Phát hiện đường dẫn không an toàn (Path Traversal).')

        try:
            full_path = Path(self.storage.path(clean_key)).resolve()
        except Exception:
            raise SuspiciousFileOperation('Đường dẫn tệp không hợp lệ.')

        # Xác minh đường dẫn nằm trọn trong MEDIA_ROOT
        try:
            full_path.relative_to(self.media_root)
        except ValueError:
            raise SuspiciousFileOperation('Truy cập file ngoài phạm vi thư mục media bị từ chối.')

        return full_path

    def delete_document_file(self, object_key: str) -> bool:
        """
        Xóa file vật lý khỏi media/.
        Xử lý an toàn nếu file không tồn tại.
        """
        if not object_key:
            return False

        try:
            abs_path = self.get_absolute_path(object_key)
            if abs_path and abs_path.exists() and abs_path.is_file():
                self.storage.delete(object_key)
                return True
        except Exception:
            pass

        return False

