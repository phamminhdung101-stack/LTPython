"""
DocUni - Tag Suggestion Service
Phân tích nội dung tài liệu và đề xuất nhãn (tags) học liệu thông minh:
- Loại bỏ stopwords tiếng Việt và tiếng Anh
- Trích xuất từ khóa, thuật ngữ chuyên ngành
- Đối chiếu với các thẻ đang tồn tại trong bảng tags
- Trả về danh sách thẻ đề xuất để người dùng xác nhận trước khi lưu
"""

import os
import re
from typing import List, Dict, Any, Set
from documents.models import Document, Tag
from .processor import DocumentProcessor


class TagSuggestionService:
    """Dịch vụ AI phân tích nội dung và đề xuất thẻ tài liệu."""

    VIETNAMESE_STOPWORDS = {
        'và', 'là', 'của', 'trong', 'với', 'cho', 'về', 'các', 'những', 'được',
        'có', 'tại', 'theo', 'như', 'từ', 'này', 'đó', 'khi', 'đến', 'để', 'một',
        'nhiều', 'ra', 'vào', 'lại', 'qua', 'thì', 'mà', 'nếu', 'hoặc', 'hay',
        'vì', 'do', 'bởi', 'rất', 'quá', 'lắm', 'ai', 'gì', 'nào', 'sao', 'bao',
        'tài', 'liệu', 'bài', 'giảng', 'chương', 'phần', 'học', 'môn', 'viên'
    }

    @classmethod
    def suggest_tags(cls, document_id: int) -> Dict[str, Any]:
        """
        Đề xuất danh sách nhãn phù hợp cho tài liệu.
        """
        doc = Document.objects.filter(pk=document_id).first()
        if not doc:
            return {'status': 'error', 'message': 'Không tìm thấy tài liệu.'}

        # 1. Thu thập văn bản
        text_corpus = f"{doc.title} {doc.description or ''}"
        if doc.subject:
            text_corpus += f" {doc.subject.subject_name}"

        latest = doc.latest_version
        if latest and latest.file:
            fpath = str(latest.file)
            if not os.path.exists(fpath):
                from django.conf import settings
                alt = os.path.join(settings.BASE_DIR, 'media', fpath)
                if os.path.exists(alt):
                    fpath = alt
            extracted = DocumentProcessor.extract_full_text(fpath)
            if extracted:
                text_corpus += f" {extracted[:3000]}"

        # 2. Lấy danh sách tag hiện có trong PostgreSQL
        all_db_tags = list(Tag.objects.all())
        existing_tag_names = {t.tag_name.lower(): t for t in all_db_tags}

        # 3. Phân tích tần suất từ và cụm từ
        words = re.findall(r'[\w\-]+', text_corpus.lower())
        word_counts = {}
        for w in words:
            if len(w) >= 3 and w not in cls.VIETNAMESE_STOPWORDS and not w.isdigit():
                word_counts[w] = word_counts.get(w, 0) + 1

        # Trích xuất bigrams
        bigram_counts = {}
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i+1]
            if (len(w1) >= 2 and len(w2) >= 2 and
                w1 not in cls.VIETNAMESE_STOPWORDS and w2 not in cls.VIETNAMESE_STOPWORDS):
                bi = f"{w1} {w2}"
                bigram_counts[bi] = bigram_counts.get(bi, 0) + 1

        # 4. Tìm các tag trong DB xuất hiện trong văn bản
        matched_existing = []
        lower_corpus = text_corpus.lower()
        for t_lower, tag_obj in existing_tag_names.items():
            if t_lower in lower_corpus:
                matched_existing.append({
                    'tag_id': tag_obj.id,
                    'tag_name': tag_obj.tag_name,
                    'is_existing': True,
                    'confidence': 0.95
                })

        # 5. Đề xuất thêm các từ khóa nổi bật chưa có trong DB
        sorted_bigrams = sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)
        new_suggestions = []
        for bi, count in sorted_bigrams[:5]:
            if bi not in existing_tag_names and count >= 2:
                new_suggestions.append({
                    'tag_id': None,
                    'tag_name': bi.title(),
                    'is_existing': False,
                    'confidence': round(min(0.9, 0.4 + count * 0.1), 2)
                })

        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        for w, count in sorted_words[:4]:
            if w not in existing_tag_names and count >= 3:
                new_suggestions.append({
                    'tag_id': None,
                    'tag_name': w.title(),
                    'is_existing': False,
                    'confidence': round(min(0.85, 0.35 + count * 0.08), 2)
                })

        combined_tags = matched_existing + new_suggestions[:5]

        return {
            'status': 'success',
            'document_id': doc.id,
            'title': doc.title,
            'suggested_tags': combined_tags[:8],
            'existing_count': len(matched_existing),
            'new_count': len(new_suggestions),
        }
