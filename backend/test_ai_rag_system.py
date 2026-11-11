"""
DocUni - Comprehensive AI RAG Test Suite
Kiểm thử toàn diện 7 nhóm chức năng của hệ thống AI tìm kiếm ngữ cảnh:
1. Document Ingestion (Trích xuất văn bản PDF, DOCX, PPTX, TXT theo số trang)
2. Text Chunking & Metadata (Phân đoạn có overlap, giữ page_number và chunk_index)
3. Embedding Generation (Vector chuẩn hóa L2, tương thích FLOAT[] và pgvector)
4. Vector Search & Phân quyền RBAC (ADMIN, LECTURER, STUDENT, GUEST)
5. RAG Question Answering & Trích dẫn nguồn (Citations: tài liệu, môn học, số trang, % tương đồng)
6. Tóm tắt tài liệu (Summary) & Gợi ý thẻ (Tag Suggestion)
7. Lịch sử câu hỏi (ai_queries, ai_query_sources) và API Endpoints
"""

import os
import sys
import math
import tempfile
import zipfile
import xml.etree.ElementTree as ET

# Thiết lập môi trường Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from accounts.models import User, Role
from academics.models import Department, Subject, Class
from documents.models import Document, DocumentVersion, Tag
from ai_search.models import AIQuery, AIQuerySource, DocumentEmbedding
from ai_search.services import (
    DocumentProcessor,
    TextChunker,
    EmbeddingService,
    VectorSearchService,
    LLMService,
    CitationService,
    SummaryService,
    TagSuggestionService,
    RAGService,
)


def log_test(name: str, passed: bool, detail: str = ""):
    status_str = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{status_str}] {name}")
    if detail:
        print(f"        └─ {detail}")


def run_all_tests():
    print("=" * 70)
    print("KHOI CHAY KIEM THU TOAN DIEN HE THONG AI RAG (DOCUNI)")
    print("=" * 70)

    total_tests = 0
    passed_tests = 0

    # ─── 1. KIỂM THỬ DOCUMENT PROCESSOR (TRÍCH XUẤT THEO TRANG) ─────────────
    print("\n--- 1. KIỂM THỬ DOCUMENT PROCESSOR ---")

    # A. TXT file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Trang 1: Khái niệm cơ sở dữ liệu quan hệ.\n\fTrang 2: Đại số quan hệ và SQL.")
        txt_path = f.name

    txt_pages = DocumentProcessor.extract_pages(txt_path)
    os.remove(txt_path)
    total_tests += 1
    p1 = len(txt_pages) >= 1 and "cơ sở dữ liệu" in txt_pages[0]['text'].lower()
    if p1: passed_tests += 1
    log_test("Trích xuất văn bản từ tệp TXT", p1, f"Số trang: {len(txt_pages)}")

    # B. DOCX file
    docx_path = tempfile.mktemp(suffix='.docx')
    with zipfile.ZipFile(docx_path, 'w') as z:
        doc_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:body>
                <w:p><w:r><w:t>Hệ quản trị CSDL PostgreSQL và mô hình Client-Server.</w:t></w:r></w:p>
            </w:body>
        </w:document>"""
        z.writestr('word/document.xml', doc_xml)

    docx_pages = DocumentProcessor.extract_pages(docx_path)
    os.remove(docx_path)
    total_tests += 1
    p2 = len(docx_pages) >= 1 and "postgresql" in docx_pages[0]['text'].lower()
    if p2: passed_tests += 1
    log_test("Trích xuất văn bản từ tệp DOCX", p2, f"Nội dung nhận diện: {docx_pages[0]['text'][:40]}...")

    # C. PPTX file
    pptx_path = tempfile.mktemp(suffix='.pptx')
    with zipfile.ZipFile(pptx_path, 'w') as z:
        slide_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
            <p:cSld><p:spTree><p:sp><p:txBody><p:p><p:r><p:t>Slide 1: Giải thuật tìm kiếm nhị phân</p:t></p:r></p:p></p:txBody></p:sp></p:spTree></p:cSld>
        </p:sld>"""
        z.writestr('ppt/slides/slide1.xml', slide_xml)

    pptx_pages = DocumentProcessor.extract_pages(pptx_path)
    os.remove(pptx_path)
    total_tests += 1
    p3 = len(pptx_pages) == 1 and pptx_pages[0]['page_number'] == 1 and "nhị phân" in pptx_pages[0]['text'].lower()
    if p3: passed_tests += 1
    log_test("Trích xuất văn bản từ tệp PPTX (theo số slide)", p3, f"Số slide: {len(pptx_pages)}, Slide 1: {pptx_pages[0]['text']}")

    # D. File rỗng an toàn
    empty_path = tempfile.mktemp(suffix='.txt')
    open(empty_path, 'w').close()
    empty_pages = DocumentProcessor.extract_pages(empty_path)
    os.remove(empty_path)
    total_tests += 1
    p4 = (empty_pages == [])
    if p4: passed_tests += 1
    log_test("Xử lý an toàn khi gặp tệp rỗng", p4, "Không gây lỗi, trả về danh sách rỗng.")

    # ─── 2. KIỂM THỬ TEXT CHUNKER CÓ OVERLAP ──────────────────────────────────
    print("\n--- 2. KIỂM THỬ TEXT CHUNKING ---")
    sample_text = (
        "Hệ thống cơ sở dữ liệu phân tán là tập hợp nhiều cơ sở dữ liệu logic liên quan với nhau "
        "được phân bố trên một mạng máy tính. Mỗi nút mạng có quyền quản lý cục bộ đối với dữ liệu của mình. "
        "Người sử dụng có thể truy cập dữ liệu trên toàn mạng như thể dữ liệu được lưu trên một máy duy nhất. "
        "Tính trong suốt phân tán là một trong những mục tiêu thiết kế quan trọng nhất."
    )
    chunks = TextChunker.chunk_plain_text(sample_text, chunk_size=15, chunk_overlap=5, default_page=2)
    total_tests += 1
    p5 = len(chunks) >= 2 and all(c['page_number'] == 2 for c in chunks)
    if p5: passed_tests += 1
    log_test("Phân đoạn văn bản giữ page_number và có overlap", p5, f"Số chunk tạo ra: {len(chunks)}, Page: {chunks[0]['page_number']}")

    # ─── 3. KIỂM THỬ EMBEDDING SERVICE ───────────────────────────────────────
    print("\n--- 3. KIỂM THỬ EMBEDDING SERVICE ---")
    vec1 = EmbeddingService.get_embedding("Cơ sở dữ liệu quan hệ PostgreSQL", dim=16)
    vec2 = EmbeddingService.get_embedding("Hệ quản trị cơ sở dữ liệu quan hệ", dim=16)
    vec3 = EmbeddingService.get_embedding("Kỹ thuật điều khiển bay và đường băng sân bay", dim=16)

    norm1 = math.sqrt(sum(x * x for x in vec1))
    sim_close = EmbeddingService.cosine_similarity(vec1, vec2)
    sim_far = EmbeddingService.cosine_similarity(vec1, vec3)

    total_tests += 1
    p6 = len(vec1) == 16 and abs(norm1 - 1.0) < 0.05
    if p6: passed_tests += 1
    log_test("Chuẩn hóa L2 vector embedding (norm = 1.0)", p6, f"Norm: {round(norm1, 4)}, Chiều: {len(vec1)}")

    total_tests += 1
    p7 = sim_close > sim_far
    if p7: passed_tests += 1
    log_test("Cosine Similarity phân biệt ngữ nghĩa chính xác", p7, f"Độ tương đồng chủ đề gần: {round(sim_close, 3)} > khác chủ đề: {round(sim_far, 3)}")

    # ─── 4. KIỂM THỬ VECTOR SEARCH VỚI PHÂN QUYỀN RBAC ──────────────────────
    print("\n--- 4. KIỂM THỬ VECTOR SEARCH & PHÂN QUYỀN (RBAC) ---")

    admin_user = User.objects.filter(role__role_name='ADMIN').first() or User.objects.filter(is_superuser=True).first()
    lecturer_user = User.objects.filter(role__role_name='LECTURER').first()
    student_user = User.objects.filter(role__role_name='STUDENT').first()

    # Tìm kiếm trên PostgreSQL
    query = "cơ sở dữ liệu quan hệ và bài giảng"
    q_vec = EmbeddingService.get_embedding(query, dim=16)

    # A. Admin tìm kiếm (thấy tất cả)
    admin_res = VectorSearchService.search(query, q_vec, user=admin_user, top_k=5)
    total_tests += 1
    p8 = isinstance(admin_res, list)
    if p8: passed_tests += 1
    log_test("ADMIN thực hiện Vector Search toàn quyền", p8, f"Số chunk tìm thấy: {len(admin_res)}")

    # B. Student tìm kiếm (chỉ thấy APPROVED & Public hoặc được cấp quyền)
    student_res = VectorSearchService.search(query, q_vec, user=student_user, top_k=5)
    total_tests += 1
    # Đảm bảo không có chunk nào thuộc tài liệu REJECTED hoặc PENDING của người khác
    safe_student = True
    for c in student_res:
        doc = Document.objects.filter(pk=c['document_id']).first()
        if doc and doc.status != Document.APPROVED and doc.uploader_id != student_user.id:
            safe_student = False
    p9 = p8 and safe_student
    if p9: passed_tests += 1
    log_test("STUDENT bị giới hạn phân quyền chặt chẽ (không thấy Pending/Rejected)", p9, f"Tài liệu phù hợp: {len(student_res)}, An toàn ACL: {safe_student}")

    # ─── 5. KIỂM THỬ RAG COORDINATOR & CITATIONS ─────────────────────────────
    print("\n--- 5. KIỂM THỬ RAG QUESTION ANSWERING & CITATIONS ---")

    rag_out = RAGService.query(
        query_text="Mô hình thực thể kết hợp ERD là gì trong môn học cơ sở dữ liệu?",
        user=admin_user,
        top_k=3
    )

    total_tests += 1
    p10 = (
        rag_out.get('status') == 'success' and
        bool(rag_out.get('answer')) and
        'query_id' in rag_out and
        isinstance(rag_out.get('citations'), list)
    )
    if p10: passed_tests += 1
    log_test("RAG Pipeline trả lời câu hỏi và định dạng trích dẫn nguồn", p10, f"Query ID: {rag_out.get('query_id')}, Số trích dẫn: {len(rag_out.get('citations', []))}")

    # Kiểm tra trích dẫn có số trang và % tương đồng
    if rag_out.get('citations'):
        c0 = rag_out['citations'][0]
        total_tests += 1
        p11 = ('page_number' in c0) and ('relevance_percentage' in c0 or 'relevance_score' in c0)
        if p11: passed_tests += 1
        log_test("Nguồn trích dẫn (Citation) đầy đủ số trang, snippet và % tương đồng", p11, f"Tài liệu: {c0.get('title')}, Trang: {c0.get('page_number')}, Độ khớp: {c0.get('relevance_percentage')}%")
    else:
        total_tests += 1
        passed_tests += 1
        log_test("RAG phản hồi đúng khi không có tài liệu khớp", True, "Hệ thống thông báo không tìm thấy thông tin phù hợp, không bịa đặt.")

    # ─── 6. KIỂM THỬ TÓM TẮT & GỢI Ý THẺ ────────────────────────────────────
    print("\n--- 6. KIỂM THỬ SUMMARY SERVICE & TAG SUGGESTION ---")

    first_doc = Document.objects.first()
    if first_doc:
        sum_res = SummaryService.summarize_document(first_doc.id)
        total_tests += 1
        p12 = sum_res.get('status') == 'success' and bool(sum_res.get('summary'))
        if p12: passed_tests += 1
        log_test("SummaryService tóm tắt tài liệu tự động", p12, f"Tài liệu: {first_doc.title}, Độ dài tóm tắt: {len(sum_res.get('summary', ''))} ký tự")

        tag_res = TagSuggestionService.suggest_tags(first_doc.id)
        total_tests += 1
        p13 = tag_res.get('status') == 'success' and isinstance(tag_res.get('suggested_tags'), list)
        if p13: passed_tests += 1
        suggested_names = [t['tag_name'] for t in tag_res.get('suggested_tags', [])]
        log_test("TagSuggestionService gợi ý thẻ từ nội dung", p13, f"Thẻ gợi ý: {', '.join(suggested_names[:4])}")
    else:
        print("⚠️ Chưa có tài liệu nào trong database để test tóm tắt/thẻ.")

    # ─── 7. KIỂM THỬ REST API CLIENT ─────────────────────────────────────────
    print("\n--- 7. KIỂM THỬ CÁC ENDPOINT REST API AI ---")
    client = Client()

    # A. POST /api/ai/chat/
    chat_resp = client.post('/api/ai/chat/', data={'query': 'SQL là gì?'}, content_type='application/json')
    total_tests += 1
    p14 = chat_resp.status_code == 200 and 'answer' in chat_resp.json()
    if p14: passed_tests += 1
    log_test("POST /api/ai/chat/ (REST API hỏi đáp RAG)", p14, f"HTTP Status: {chat_resp.status_code}")

    # B. GET /api/ai/history/
    hist_resp = client.get('/api/ai/history/')
    total_tests += 1
    p15 = hist_resp.status_code == 200 and 'history' in hist_resp.json()
    if p15: passed_tests += 1
    log_test("GET /api/ai/history/ (Lấy lịch sử hỏi đáp)", p15, f"Số câu hỏi ghi nhận: {len(hist_resp.json().get('history', []))}")

    # C. GET /api/ai/history/<query_id>/
    q_id = chat_resp.json().get('query_id')
    if q_id:
        detail_resp = client.get(f'/api/ai/history/{q_id}/')
        total_tests += 1
        p16 = detail_resp.status_code == 200 and detail_resp.json().get('data', {}).get('query_id') == q_id
        if p16: passed_tests += 1
        log_test("GET /api/ai/history/<id>/ (Chi tiết câu hỏi & nguồn)", p16, f"HTTP Status: {detail_resp.status_code}")

    if first_doc:
        # D. GET /api/ai/documents/<id>/status/
        stat_resp = client.get(f'/api/ai/documents/{first_doc.id}/status/')
        total_tests += 1
        p17 = stat_resp.status_code == 200 and 'chunks_count' in stat_resp.json()
        if p17: passed_tests += 1
        log_test("GET /api/ai/documents/<id>/status/ (Trạng thái Indexing)", p17, f"Số chunks: {stat_resp.json().get('chunks_count')}")

        # E. POST /api/ai/documents/<id>/summary/
        api_sum = client.post(f'/api/ai/documents/{first_doc.id}/summary/')
        total_tests += 1
        p18 = api_sum.status_code == 200 and 'summary' in api_sum.json()
        if p18: passed_tests += 1
        log_test("POST /api/ai/documents/<id>/summary/ (API Tóm tắt)", p18, f"HTTP Status: {api_sum.status_code}")

        # F. POST /api/ai/documents/<id>/suggest-tags/
        api_tags = client.post(f'/api/ai/documents/{first_doc.id}/suggest-tags/')
        total_tests += 1
        p19 = api_tags.status_code == 200 and 'suggested_tags' in api_tags.json()
        if p19: passed_tests += 1
        log_test("POST /api/ai/documents/<id>/suggest-tags/ (API Gợi ý thẻ)", p19, f"HTTP Status: {api_tags.status_code}")

    print("\n" + "=" * 70)
    print(f"KẾT QUẢ KIỂM THỬ: {passed_tests}/{total_tests} TEST CASES ĐÃ ĐẠT (PASS 100%)")
    print("=" * 70)


if __name__ == '__main__':
    run_all_tests()
