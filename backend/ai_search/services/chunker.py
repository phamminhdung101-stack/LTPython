"""
DocUni - Text Chunker Service
Chia nhỏ văn bản thành các đoạn (chunks) có overlap để duy trì ngữ cảnh cho mô hình ngôn ngữ và vector search.
Lưu giữ siêu dữ liệu số trang (page_number) phục vụ trích dẫn số trang chính xác trong RAG.
"""

import re
from typing import List, Dict, Any, Optional


class TextChunker:
    """Chia nhỏ văn bản theo độ dài từ có gối đầu (overlap) và đánh dấu số trang."""

    DEFAULT_CHUNK_SIZE = 120    # số từ mỗi chunk
    DEFAULT_CHUNK_OVERLAP = 25  # số từ overlap giữa các chunk kề nhau

    @classmethod
    def chunk_pages(
        cls,
        pages: List[Dict[str, Any]],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ) -> List[Dict[str, Any]]:
        """
        Chia các trang tài liệu thành các chunks, duy trì số trang nguồn.
        Input: [{'page_number': 1, 'text': '...'}]
        Output: [{'chunk_index': 0, 'page_number': 1, 'chunk_text': '...', 'word_count': 105}]
        """
        if not pages:
            return []

        all_chunks = []
        current_chunk_idx = 0

        for page in pages:
            p_num = page.get('page_number', 1)
            p_text = page.get('text', '').strip()
            if not p_text:
                continue

            # Phân tách theo đoạn / câu
            sentences = cls._split_into_sentences(p_text)
            current_words = []
            
            for sentence in sentences:
                s_words = sentence.split()
                if not s_words:
                    continue

                if len(current_words) + len(s_words) <= chunk_size:
                    current_words.extend(s_words)
                else:
                    if current_words:
                        chunk_str = " ".join(current_words).strip()
                        all_chunks.append({
                            'chunk_index': current_chunk_idx,
                            'page_number': p_num,
                            'chunk_text': chunk_str,
                            'word_count': len(current_words)
                        })
                        current_chunk_idx += 1
                        
                        # Giữ lại phần overlap từ cuối chunk trước
                        overlap_words = current_words[-chunk_overlap:] if chunk_overlap < len(current_words) else current_words
                        current_words = list(overlap_words) + s_words
                    else:
                        current_words = s_words

            # Lưu phần từ còn lại của trang
            if current_words:
                chunk_str = " ".join(current_words).strip()
                all_chunks.append({
                    'chunk_index': current_chunk_idx,
                    'page_number': p_num,
                    'chunk_text': chunk_str,
                    'word_count': len(current_words)
                })
                current_chunk_idx += 1

        return all_chunks

    @classmethod
    def chunk_plain_text(
        cls,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        default_page: int = 1
    ) -> List[Dict[str, Any]]:
        """Chia một đoạn văn bản thuần bất kỳ."""
        return cls.chunk_pages(
            [{'page_number': default_page, 'text': text}],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """Tách văn bản thành các câu dựa trên dấu chấm, hỏi, than hoặc ngắt dòng."""
        paragraphs = text.split('\n')
        sentences = []
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            # Tách theo dấu câu
            raw_sents = re.split(r'(?<=[.?!;:])\s+', p)
            for s in raw_sents:
                s = s.strip()
                if s:
                    sentences.append(s)
        return sentences
