"""
DocUni - Service Lưu Trữ Cloudflare R2 (S3-Compatible Object Storage)
Phần 2:
- Tải file lên Cloudflare R2 Bucket
- Tạo Presigned URL tải file an toàn có thời hạn (mặc định 1 giờ)
- Xóa file trên R2 khi tài liệu bị gỡ bỏ
- Tự động Fallback sang Local Storage khi chưa cấu hình R2 credentials hoặc offline
"""

import os
import io
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from django.conf import settings

logger = logging.getLogger(__name__)


class CloudflareR2Service:
    """
    Service quản lý giao tiếp với Cloudflare R2 qua giao thức S3-compatible.
    Sử dụng botocore client chuẩn hoặc boto3.
    """

    def __init__(self):
        self.account_id = getattr(settings, 'R2_ACCOUNT_ID', os.getenv('R2_ACCOUNT_ID', ''))
        self.access_key_id = getattr(settings, 'R2_ACCESS_KEY_ID', os.getenv('R2_ACCESS_KEY_ID', ''))
        self.secret_access_key = getattr(settings, 'R2_SECRET_ACCESS_KEY', os.getenv('R2_SECRET_ACCESS_KEY', ''))
        self.bucket_name = getattr(settings, 'R2_BUCKET_NAME', os.getenv('R2_BUCKET_NAME', ''))
        self.public_domain = getattr(settings, 'R2_PUBLIC_DOMAIN', os.getenv('R2_PUBLIC_DOMAIN', '')).rstrip('/')

        self._client = None
        self._init_client()

    def _init_client(self):
        if not (self.account_id and self.access_key_id and self.secret_access_key and self.bucket_name):
            # Chưa cấu hình R2 credentials -> Sẽ dùng Local Storage Fallback
            return

        try:
            import botocore.session
            session = botocore.session.get_session()
            endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
            self._client = session.create_client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name='auto',
            )
        except Exception as e:
            logger.warning(f"Không thể khởi tạo Cloudflare R2 client: {e}. Sẽ dùng Local Storage.")
            self._client = None

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def upload_file(
        self,
        file_obj,
        object_key: str,
        content_type: str = 'application/octet-stream',
    ) -> Dict[str, Any]:
        """
        Upload file lên Cloudflare R2 hoặc Local Fallback.

        Returns:
            dict: {
                'storage_provider': 'R2' hoặc 'LOCAL',
                'object_key': str,
                'url': str,
                'bucket': str
            }
        """
        # Đảm bảo đọc nội dung bytes
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)

        if hasattr(file_obj, 'read'):
            body_bytes = file_obj.read()
        elif isinstance(file_obj, (bytes, bytearray)):
            body_bytes = bytes(file_obj)
        else:
            raise ValueError("file_obj không hợp lệ")

        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)

        if self.is_configured:
            try:
                self._client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=body_bytes,
                    ContentType=content_type,
                )
                url = self.generate_download_url(object_key)
                return {
                    'storage_provider': 'R2',
                    'object_key': object_key,
                    'url': url,
                    'bucket': self.bucket_name,
                }
            except Exception as e:
                logger.error(f"Lỗi khi upload lên Cloudflare R2: {e}. Đang fallback lưu local...")

        # --- LOCAL STORAGE FALLBACK ---
        local_base = Path(getattr(settings, 'MEDIA_ROOT', Path(settings.BASE_DIR) / 'media'))
        dest_path = local_base / object_key
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'wb') as f:
            f.write(body_bytes)

        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        local_url = f"{media_url.rstrip('/')}/{object_key}"

        return {
            'storage_provider': 'LOCAL',
            'object_key': object_key,
            'url': local_url,
            'bucket': 'local_storage',
        }

    def generate_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        """
        Sinh URL tải xuống an toàn:
        - Nếu có custom public domain: https://cdn.domain.com/object_key
        - Nếu là R2: Presigned S3 GET URL có hạn dùng (mặc định 1 giờ)
        - Nếu là Local: Đường dẫn media cục bộ
        """
        if self.public_domain:
            return f"{self.public_domain}/{object_key}"

        if self.is_configured:
            try:
                url = self._client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': object_key},
                    ExpiresIn=expires_in,
                )
                return url
            except Exception as e:
                logger.error(f"Lỗi sinh Presigned URL từ R2: {e}")

        # Local Fallback
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        return f"{media_url.rstrip('/')}/{object_key}"

    def delete_file(self, object_key: str) -> bool:
        """
        Xóa file khỏi Cloudflare R2 hoặc Local Storage.
        """
        success = False
        if self.is_configured:
            try:
                self._client.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                )
                success = True
            except Exception as e:
                logger.error(f"Lỗi khi xóa file trên R2 ({object_key}): {e}")

        # Xóa cả bản local nếu có
        try:
            local_base = Path(getattr(settings, 'MEDIA_ROOT', Path(settings.BASE_DIR) / 'media'))
            dest_path = local_base / object_key
            if dest_path.exists():
                dest_path.unlink()
                success = True
        except Exception as e:
            logger.warning(f"Lỗi khi xóa local file ({object_key}): {e}")

        return success


# Singleton instance để tái sử dụng
r2_service = CloudflareR2Service()
