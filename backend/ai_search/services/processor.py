"""
DocUni - Document Processor Service
Trích xuất văn bản từ nhiều định dạng học liệu (PDF, DOCX, PPTX, TXT, MD, CSV, JSON)
hỗ trợ phân tách theo từng trang/slide phục vụ trích dẫn số trang chính xác trong RAG.
"""

import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional


class DocumentProcessor:
    """Xử lý và trích xuất nội dung văn bản từ các tệp học liệu."""

    @classmethod
    def extract_pages(cls, file_path: str, filename: str = "") -> List[Dict[str, Any]]:
        """
        Trích xuất văn bản theo từng trang/slide.
        Trả về danh sách: [{'page_number': 1, 'text': '...'}]
        """
        if not file_path or not os.path.exists(file_path):
            return []

        fname = (filename or os.path.basename(file_path)).lower()
        ext = os.path.splitext(fname)[1]

        if ext in ['.txt', '.md', '.csv', '.json', '.py', '.sql', '.html']:
            return cls._extract_text_file(file_path)
        elif ext == '.docx':
            return cls._extract_docx(file_path)
        elif ext == '.pptx':
            return cls._extract_pptx(file_path)
        elif ext == '.pdf':
            return cls._extract_pdf(file_path)
        else:
            return cls._extract_generic(file_path)

    @classmethod
    def extract_full_text(cls, file_path: str, filename: str = "") -> str:
        """Trích xuất toàn bộ văn bản của tài liệu gom lại thành một chuỗi."""
        pages = cls.extract_pages(file_path, filename)
        return "\n\n".join([p['text'] for p in pages if p.get('text')]).strip()

    @classmethod
    def _extract_text_file(cls, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
            if not content:
                return []
            # Chia thành các trang giả định cứ mỗi 500 từ hoặc theo ký tự phân trang
            raw_pages = content.split('\f')
            if len(raw_pages) > 1:
                return [{'page_number': i + 1, 'text': p.strip()} for i, p in enumerate(raw_pages) if p.strip()]
            
            lines = content.splitlines()
            pages = []
            chunk_size = 40
            for i in range(0, len(lines), chunk_size):
                page_text = "\n".join(lines[i:i + chunk_size]).strip()
                if page_text:
                    pages.append({'page_number': (i // chunk_size) + 1, 'text': page_text})
            return pages or [{'page_number': 1, 'text': content}]
        except Exception:
            return []

    @classmethod
    def _extract_docx(cls, file_path: str) -> List[Dict[str, Any]]:
        try:
            with zipfile.ZipFile(file_path) as z:
                if 'word/document.xml' not in z.namelist():
                    return []
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                
                paragraphs = []
                for p_node in tree.findall('.//w:p', namespaces):
                    texts = [t.text for t in p_node.findall('.//w:t', namespaces) if t.text]
                    if texts:
                        paragraphs.append("".join(texts))

                full_text = "\n".join(paragraphs).strip()
                if not full_text:
                    return []

                # Gom thành từng trang giả định (ước lượng khoảng 300 từ / trang)
                words = full_text.split()
                words_per_page = 300
                pages = []
                for idx in range(0, len(words), words_per_page):
                    page_text = " ".join(words[idx:idx + words_per_page])
                    pages.append({
                        'page_number': (idx // words_per_page) + 1,
                        'text': page_text
                    })
                return pages
        except Exception:
            return []

    @classmethod
    def _extract_pptx(cls, file_path: str) -> List[Dict[str, Any]]:
        try:
            with zipfile.ZipFile(file_path) as z:
                slide_files = [f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
                # Sắp xếp đúng thứ tự slide 1, 2, 3...
                def slide_key(f):
                    m = re.search(r'slide(\d+)\.xml', f)
                    return int(m.group(1)) if m else 9999
                slide_files.sort(key=slide_key)

                pages = []
                for idx, sfile in enumerate(slide_files, start=1):
                    xml_content = z.read(sfile)
                    tree = ET.fromstring(xml_content)
                    texts = []
                    for elem in tree.iter():
                        if elem.text and elem.text.strip():
                            texts.append(elem.text.strip())
                    slide_text = " ".join(texts).strip()
                    if slide_text:
                        pages.append({'page_number': idx, 'text': slide_text})
                return pages
        except Exception:
            return []

    @classmethod
    def _extract_pdf(cls, file_path: str) -> List[Dict[str, Any]]:
        # 1. Thử dùng thư viện pypdf nếu có
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            pages = []
            for i, page in enumerate(reader.pages, start=1):
                txt = page.extract_text() or ""
                txt = txt.strip()
                if txt:
                    pages.append({'page_number': i, 'text': txt})
            if pages:
                return pages
        except Exception:
            pass

        # 2. Thử dùng thư viện pdfminer/pymupdf nếu có
        try:
            import fitz
            doc = fitz.open(file_path)
            pages = []
            for i, page in enumerate(doc, start=1):
                txt = page.get_text() or ""
                txt = txt.strip()
                if txt:
                    pages.append({'page_number': i, 'text': txt})
            if pages:
                return pages
        except Exception:
            pass

        # 3. Fallback trích xuất binary streams từ PDF (không cần thư viện bên ngoài)
        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            # Tách các stream text
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
                full_text = " ".join(clean_strs).strip()
                words = full_text.split()
                pages = []
                words_per_page = 250
                for idx in range(0, len(words), words_per_page):
                    pages.append({
                        'page_number': (idx // words_per_page) + 1,
                        'text': " ".join(words[idx:idx + words_per_page])
                    })
                return pages
        except Exception:
            pass

        return []

    @classmethod
    def _extract_generic(cls, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(5000).strip()
            if content:
                return [{'page_number': 1, 'text': content}]
        except Exception:
            pass
        return []
