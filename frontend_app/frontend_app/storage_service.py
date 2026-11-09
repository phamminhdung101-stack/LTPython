"""
DocUni - Storage Service Module
Hỗ trợ lưu trữ tài liệu đa nền tảng cho cả môi trường Local lẫn Deploy Web (Render, Railway, Fly.io...):
- Khi chạy Deploy Web: Dùng Cloudinary để file không bị mất khi container khởi động lại.
- Khi chạy Local: Tự động lưu trữ vào thư mục uploaded_files/ phục vụ offline không cần internet.
- Độc lập: Sử dụng REST API chuẩn hoặc SDK Cloudinary, tự động đọc biến môi trường từ .env.
"""

import os
import re
import time
import json
import hashlib
from typing import Tuple, Optional
import reflex as rx

# Tự động nạp biến môi trường từ .env nếu có
try:
    from dotenv import load_dotenv
    # Nạp từ thư mục hiện tại hoặc thư mục cha
    load_dotenv()
    root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    if os.path.exists(root_env):
        load_dotenv(root_env)
except Exception:
    pass


def format_file_size(size_bytes: int) -> str:
    """Định dạng kích thước file sang KB, MB dễ đọc."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def sanitize_filename(filename: str) -> str:
    """Loại bỏ ký tự đặc biệt nguy hiểm khỏi tên file."""
    base = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9._\-() ]', '_', base)
    return clean or "document.bin"


def get_local_upload_dir() -> str:
    """Lấy đường dẫn thư mục lưu trữ cục bộ."""
    upload_dir = str(rx.get_upload_dir())
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


class StorageService:
    """Service điều phối việc lưu trữ file tài liệu."""

    @classmethod
    def get_cloudinary_credentials(cls) -> Optional[Tuple[str, str, str]]:
        """Lấy bộ 3 thông tin Cloudinary từ biến môi trường hoặc CLOUDINARY_URL."""
        c_name = os.getenv("CLOUDINARY_CLOUD_NAME") or os.getenv("CLOUD_NAME")
        c_key = os.getenv("CLOUDINARY_API_KEY") or os.getenv("API_KEY")
        c_secret = os.getenv("CLOUDINARY_API_SECRET") or os.getenv("API_SECRET")

        if c_name and c_key and c_secret:
            return c_name.strip(), c_key.strip(), c_secret.strip()

        # Parse từ CLOUDINARY_URL dạng: cloudinary://<api_key>:<api_secret>@<cloud_name>
        c_url = os.getenv("CLOUDINARY_URL")
        if c_url and "cloudinary://" in c_url:
            try:
                raw = c_url.split("cloudinary://")[1]
                auth_part, cloud_name = raw.split("@")
                api_key, api_secret = auth_part.split(":")
                return cloud_name.strip(), api_key.strip(), api_secret.strip()
            except Exception:
                pass

        return None

    @classmethod
    def is_cloudinary_configured(cls) -> bool:
        """Kiểm tra xem hệ thống đã sẵn sàng dùng Cloudinary chưa (yêu cầu bật USE_CLOUDINARY=true)."""
        use_cloud = os.getenv("USE_CLOUDINARY", "false").strip().lower() in ("true", "1", "yes")
        return use_cloud and (cls.get_cloudinary_credentials() is not None)

    @classmethod
    def save_file_locally(cls, filename: str, data: bytes) -> Tuple[str, str, str]:
        """Lưu file vào thư mục uploaded_files cục bộ."""
        clean_name = sanitize_filename(filename)
        upload_dir = get_local_upload_dir()
        file_path = os.path.join(upload_dir, clean_name)

        with open(file_path, "wb") as f:
            f.write(data)

        size_str = format_file_size(len(data))
        file_url = f"/_upload/{clean_name}"
        return clean_name, file_url, size_str

    @classmethod
    def save_file_cloudinary_rest(cls, filename: str, data: bytes) -> Optional[Tuple[str, str, str]]:
        """
        Upload trực tiếp lên Cloudinary REST API bằng thư viện tiêu chuẩn urllib (Không phụ thuộc SDK ngoài).
        Endpoint: https://api.cloudinary.com/v1_1/<cloud_name>/raw/upload
        """
        creds = cls.get_cloudinary_credentials()
        if not creds:
            return None

        cloud_name, api_key, api_secret = creds
        clean_name = sanitize_filename(filename)
        public_id = f"docuni/{int(time.time())}_{clean_name}"

        timestamp = str(int(time.time()))
        # Cloudinary Signature: sắp xếp tham số theo alphabet + api_secret rồi băm SHA1
        to_sign = f"public_id={public_id}&timestamp={timestamp}{api_secret}"
        signature = hashlib.sha1(to_sign.encode("utf-8")).hexdigest()

        upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/raw/upload"

        # Tạo multipart/form-data thủ công bằng urllib
        import urllib.request
        boundary = f"----WebKitFormBoundary{int(time.time()*1000)}"
        body = []

        def add_field(name: str, value: str):
            body.append(f"--{boundary}\r\n".encode("utf-8"))
            body.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
            body.append(f"{value}\r\n".encode("utf-8"))

        add_field("api_key", api_key)
        add_field("timestamp", timestamp)
        add_field("public_id", public_id)
        add_field("signature", signature)

        # File part
        body.append(f"--{boundary}\r\n".encode("utf-8"))
        body.append(f'Content-Disposition: form-data; name="file"; filename="{clean_name}"\r\n'.encode("utf-8"))
        body.append(b"Content-Type: application/octet-stream\r\n\r\n")
        body.append(data)
        body.append(b"\r\n")
        body.append(f"--{boundary}--\r\n".encode("utf-8"))

        payload = b"".join(body)

        req = urllib.request.Request(
            upload_url,
            data=payload,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Content-Length": str(len(payload)),
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                secure_url = res_data.get("secure_url") or res_data.get("url")
                size_str = format_file_size(len(data))
                print(f"[StorageService] Uploaded to Cloudinary successfully: {secure_url}")
                return clean_name, secure_url, size_str
        except Exception as e:
            print(f"[StorageService] Cloudinary upload warning: {e}, falling back to local storage.")
            return None

    @classmethod
    def save_file(cls, filename: str, data: bytes) -> Tuple[str, str, str]:
        """
        Chiến lược lưu file:
        1. Luôn lưu 1 bản sao Local (để app truy cập nội bộ nhanh).
        2. Nếu có cấu hình Cloudinary: Tự động upload lên Cloudinary và trả về HTTPS link công khai toàn cầu.
        3. Nếu không có Cloudinary hoặc upload lỗi: Trả về URL Local /_upload/filename.
        """
        # Lưu bản local
        clean_name, local_url, size_str = cls.save_file_locally(filename, data)

        # Nếu có cấu hình Cloudinary $\to$ upload lên Cloud
        if cls.is_cloudinary_configured():
            cloud_res = cls.save_file_cloudinary_rest(clean_name, data)
            if cloud_res:
                return cloud_res

        return clean_name, local_url, size_str
