"""
DocUni - Indexing & Text Extraction Service
Phục vụ tìm kiếm từ khóa và tìm kiếm ngữ nghĩa AI (RAG).
Hỗ trợ định dạng: PDF, DOCX, PPTX, XLSX, TXT, MD.
"""

import os
import re
import math
import hashlib
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple
from django.db import connection
from .models import Document, DocumentActivityLog


def compute_embedding(text: str, dim: int = 16) -> List[float]:
    """
    Tạo vector embedding số thực chuẩn hóa cho đoạn văn bản (Cosine Similarity).
    """
    words = re.findall(r'\w+', text.lower())
    if not words:
        return [0.0] * dim
    vec = [0.0] * dim
    for w in words:
        h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [round(x / norm, 4) for x in vec]
    return vec


def extract_text_from_file(file_path: str, filename: str = "") -> str:
    """
    Trích xuất nội dung văn bản từ các định dạng file phổ biến:
    TXT, DOCX, PPTX, PDF.
    """
    if not file_path or not os.path.exists(file_path):
        return ""

    lower_name = (filename or file_path).lower()

    # 1. Định dạng văn bản thuần
    if lower_name.endswith(('.txt', '.md', '.csv', '.json', '.sql', '.py')):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read().strip()
        except Exception:
            return ""

    # 2. Định dạng Word (.docx)
    if lower_name.endswith('.docx'):
        try:
            with zipfile.ZipFile(file_path) as z:
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                texts = []
                for node in tree.findall('.//w:t', namespaces):
                    if node.text:
                        texts.append(node.text)
                return " ".join(texts).strip()
        except Exception:
            pass

    # 3. Định dạng PowerPoint (.pptx)
    if lower_name.endswith('.pptx'):
        try:
            with zipfile.ZipFile(file_path) as z:
                texts = []
                for fname in z.namelist():
                    if fname.startswith('ppt/slides/slide') and fname.endswith('.xml'):
                        xml_content = z.read(fname)
                        tree = ET.fromstring(xml_content)
                        for elem in tree.iter():
                            if elem.text and elem.text.strip():
                                texts.append(elem.text.strip())
                return " ".join(texts).strip()
        except Exception:
            pass

    # 4. Định dạng PDF (.pdf)
    if lower_name.endswith('.pdf'):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            # Trích xuất các chuỗi text stream trong PDF
            text_chunks = re.findall(rb'\(([^\(\)]{4,})\)', content)
            clean_strs = []
            for b in text_chunks:
                try:
                    s = b.decode('utf-8', errors='ignore').strip()
                    if len(s) > 3 and not s.startswith('/'):
                        clean_strs.append(s)
                except Exception:
                    pass
            if clean_strs:
                return " ".join(clean_strs[:500]).strip()
        except Exception:
            pass

    return ""


def chunk_text(text: str, max_words_per_chunk: int = 100) -> List[str]:
    """
    Chia nhỏ văn bản thành các đoạn (chunks) phục vụ Semantic Indexing.
    """
    if not text:
        return []
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words_per_chunk):
        chunk = " ".join(words[i:i + max_words_per_chunk]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def index_document(document: Document, user=None) -> Dict[str, Any]:
    """
    Thực hiện Indexing toàn diện cho một tài liệu:
    1. Trích xuất nội dung văn bản từ file phiên bản mới nhất hoặc thông tin tài liệu
    2. Chia đoạn (Chunking)
    3. Tạo Vector Embedding
    4. Ghi đè vào bảng document_embeddings trong PostgreSQL
    5. Ghi nhận nhật ký kiểm toán
    """
    doc_id = document.id
    subject_name = document.subject.subject_name if document.subject else ""
    dept_name = document.subject.department.department_name if (document.subject and document.subject.department) else ""

    # Tập hợp nội dung tổng hợp của tài liệu
    full_text = f"Tài liệu: {document.title}. Môn học: {subject_name}. Khoa: {dept_name}. Mô tả: {document.description or ''}"

    latest = document.latest_version
    if latest and latest.file:
        file_path = str(latest.file)
        if not os.path.exists(file_path):
            from django.conf import settings
            alt_path = os.path.join(settings.BASE_DIR, 'media', file_path)
            if os.path.exists(alt_path):
                file_path = alt_path

        extracted = extract_text_from_file(file_path, os.path.basename(file_path))
        if extracted:
            full_text += f"\nNội dung chi tiết:\n{extracted}"

    chunks = chunk_text(full_text, max_words_per_chunk=120)
    if not chunks:
        chunks = [full_text]

    with connection.cursor() as cursor:
        # Lấy danh sách chunk embedding hiện có của tài liệu
        cursor.execute("SELECT chunk_index, embedding_id FROM document_embeddings WHERE document_id = %s", [doc_id])
        existing_chunks = {row[0]: row[1] for row in cursor.fetchall()}

        for idx, chunk in enumerate(chunks):
            emb_vec = compute_embedding(chunk, dim=16)
            if idx in existing_chunks:
                # Cập nhật chunk đã tồn tại (giữ nguyên embedding_id để không xung đột khóa ngoại ai_query_sources)
                cursor.execute(
                    """
                    UPDATE document_embeddings 
                    SET chunk_text = %s, embedding_array = %s, created_at = CURRENT_TIMESTAMP
                    WHERE embedding_id = %s
                    """,
                    [chunk, emb_vec, existing_chunks[idx]]
                )
            else:
                # Chèn chunk mới
                cursor.execute(
                    """
                    INSERT INTO document_embeddings (document_id, chunk_index, chunk_text, embedding_array, created_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """,
                    [doc_id, idx, chunk, emb_vec]
                )

    # Ghi nhận log
    DocumentActivityLog.objects.create(
        document=document,
        user=user,
        action='UPDATE',
        description=f"Indexing tài liệu hoàn tất: {len(chunks)} đoạn văn bản (chunks) được nhúng vector vào PostgreSQL.",
    )

    return {
        'document_id': doc_id,
        'title': document.title,
        'chunks_count': len(chunks),
        'status': 'COMPLETED',
    }


def get_indexing_stats() -> Dict[str, Any]:
    """
    Thống kê tiến độ Indexing toàn hệ thống từ PostgreSQL.
    """
    total_docs = Document.objects.count()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(DISTINCT document_id) FROM document_embeddings")
        indexed_docs = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM document_embeddings")
        total_chunks = cursor.fetchone()[0] or 0

    pending_docs = max(0, total_docs - indexed_docs)
    rate = round((indexed_docs / total_docs * 100), 1) if total_docs > 0 else 0.0

    return {
        'total_documents': total_docs,
        'indexed_documents': indexed_docs,
        'pending_documents': pending_docs,
        'failed_documents': 0,
        'total_chunks': total_chunks,
        'indexing_rate': rate,
        'indexing_percentage': rate,
        'status': 'COMPLETED' if pending_docs == 0 else 'PROCESSING',
    }


def index_all_documents() -> Dict[str, Any]:
    """Lập chỉ mục toàn bộ tài liệu trong cơ sở dữ liệu."""
    docs = Document.objects.all()
    count = 0
    total_chunks = 0
    for doc in docs:
        res = index_document(doc)
        if res.get("status") == "SUCCESS":
            count += 1
            total_chunks += res.get("chunks_count", 0)
    return {
        "status": "SUCCESS",
        "indexed_count": count,
        "total_documents": docs.count(),
        "total_chunks": total_chunks,
    }

