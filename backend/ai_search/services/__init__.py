"""
DocUni AI Services Module
Kiến trúc RAG (Retrieval-Augmented Generation) độc lập, mô-đun hóa cao:
- DocumentProcessor: Trích xuất nội dung văn bản theo trang/slide
- TextChunker: Phân đoạn văn bản có overlap
- EmbeddingService: Sinh vector nhúng Cosine Normalized
- VectorSearchService: Tìm kiếm tương đồng vector kết hợp RBAC ACL
- LLMService: Tương tác với LLM / Extractive Synthesizer
- CitationService: Định dạng trích dẫn nguồn học liệu
- SummaryService: Tóm tắt nội dung tài liệu
- TagSuggestionService: Đề xuất nhãn tài liệu thông minh
- RAGService: Bộ điều phối trung tâm
"""

from .processor import DocumentProcessor
from .chunker import TextChunker
from .embedding import EmbeddingService
from .vector_search import VectorSearchService
from .llm_service import LLMService
from .citation_service import CitationService
from .summary_service import SummaryService
from .tag_suggester import TagSuggestionService
from .rag_service import RAGService

__all__ = [
    'DocumentProcessor',
    'TextChunker',
    'EmbeddingService',
    'VectorSearchService',
    'LLMService',
    'CitationService',
    'SummaryService',
    'TagSuggestionService',
    'RAGService',
]
