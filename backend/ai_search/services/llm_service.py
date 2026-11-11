"""
DocUni - LLM Service
Giao tiếp với mô hình ngôn ngữ lớn (OpenAI / Gemini) kết hợp Extractive Synthesizer Fallback.
Thực hiện tổng hợp câu trả lời dựa trên ngữ cảnh được trích xuất từ PostgreSQL (RAG),
tuân thủ nguyên tắc chỉ dựa vào tài liệu được cấp quyền, không bịa đặt (No Hallucination).
"""

import os
from typing import List, Dict, Any, Optional


class LLMService:
    """Dịch vụ sinh câu trả lời bằng mô hình ngôn ngữ lớn hoặc bộ tổng hợp nội bộ."""

    SYSTEM_PROMPT = """Bạn là Trợ lý Học thuật Thông minh DocUni của Trường Đại học.
Nhiệm vụ của bạn là giải đáp thắc mắc học tập của sinh viên và giảng viên dựa trên các đoạn trích từ tài liệu môn học được cung cấp.

Quy tắc bắt buộc:
1. Chỉ sử dụng thông tin có trong các đoạn trích dẫn (Context) dưới đây để trả lời.
2. Trả lời bằng tiếng Việt chuẩn mực, mạch lạc, dễ hiểu, có cấu trúc rõ ràng (dùng gạch đầu dòng nếu cần).
3. Tuyệt đối không tự bịa đặt thông tin, công thức, số liệu không có trong tài liệu.
4. Trích dẫn rõ tên tài liệu và môn học khi đề cập đến kiến thức trong bài.
5. Nếu trong ngữ cảnh không có thông tin phù hợp để trả lời, hãy thông báo lịch sự rằng tài liệu hiện có trong kho chưa đề cập đến nội dung này."""

    @classmethod
    def generate_answer(
        cls,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Tạo câu trả lời từ câu hỏi và các chunks ngữ cảnh.
        Ưu tiên OpenAI / Gemini nếu có cấu hình API KEY, fallback sang Extractive Synthesizer.
        """
        if not context_chunks:
            return (
                f"Rất tiếc, hệ thống DocUni không tìm thấy thông tin hoặc đoạn trích phù hợp với câu hỏi "
                f"'{query}' trong các tài liệu mà bạn có quyền truy cập. "
                f"Vui lòng kiểm tra lại từ khóa hoặc đảm bảo tài liệu liên quan đã được tải lên và duyệt công khai."
            )

        # Xây dựng ngữ cảnh context từ các chunk
        context_str = cls._build_context_string(context_chunks)

        # 1. Thử gọi OpenAI API
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.startswith("sk-") and not openai_key.endswith("your_key_here"):
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                
                messages = [
                    {"role": "system", "content": cls.SYSTEM_PROMPT},
                ]
                # Bổ sung lịch sử nếu có
                if conversation_history:
                    for h in conversation_history[-4:]:
                        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
                
                user_content = f"NGỮ CẢNH TÀI LIỆU:\n{context_str}\n\nCÂU HỎI CỦA NGƯỜI DÙNG:\n{query}"
                messages.append({"role": "user", "content": user_content})

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=650,
                    timeout=12.0
                )
                answer = response.choices[0].message.content.strip()
                if answer:
                    return answer
            except Exception:
                pass

        # 2. Thử gọi Google Gemini API
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key and not gemini_key.startswith("your_"):
            try:
                import httpx
                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                prompt_text = f"{cls.SYSTEM_PROMPT}\n\nNGỮ CẢNH:\n{context_str}\n\nCÂU HỎI:\n{query}"
                resp = httpx.post(
                    gemini_url,
                    json={"contents": [{"parts": [{"text": prompt_text}]}]},
                    timeout=10.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    cands = data.get("candidates", [])
                    if cands:
                        text_part = cands[0]["content"]["parts"][0]["text"]
                        return text_part.strip()
            except Exception:
                pass

        # 3. Fallback: Extractive Synthesizer (Nội suy trích xuất thông minh)
        return cls._extractive_synthesize(query, context_chunks)

    @classmethod
    def _build_context_string(cls, chunks: List[Dict[str, Any]]) -> str:
        parts = []
        for i, c in enumerate(chunks, 1):
            title = c.get('title', 'Tài liệu')
            subj = c.get('subject_name', '')
            p_num = c.get('page_number', 1)
            text = c.get('chunk_text', '').strip()
            parts.append(f"--- [Trích đoạn {i}] Từ tài liệu \"{title}\" (Môn: {subj}), Trang {p_num}: ---\n{text}")
        return "\n\n".join(parts)

    @classmethod
    def _extractive_synthesize(cls, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Bộ tổng hợp ngôn ngữ nội suy thông minh khi không có internet hoặc API key bên ngoài:
        Trích xuất các luận điểm quan trọng, phân loại ý chính và tạo câu trả lời mạch lạc bằng tiếng Việt.
        """
        # Thu thập các tài liệu nguồn
        doc_refs = []
        for c in chunks:
            t = c.get('title', 'Tài liệu')
            s = c.get('subject_name', 'Môn học')
            p = c.get('page_number', 1)
            ref_str = f"\"{t}\" (Môn: {s}, Trang {p})"
            if ref_str not in doc_refs:
                doc_refs.append(ref_str)

        sources_label = "; ".join(doc_refs)

        # Lựa chọn các đoạn trọng tâm
        bullet_points = []
        for c in chunks[:3]:
            text = c.get('chunk_text', '').strip()
            title = c.get('title', '')
            p_num = c.get('page_number', 1)
            
            # Cắt ngắn câu then chốt
            sentences = [s.strip() for s in text.split('. ') if len(s.strip()) > 15]
            summary_piece = ". ".join(sentences[:2]) if sentences else text[:180]
            if not summary_piece.endswith('.'):
                summary_piece += '.'

            bullet_points.append(
                f"• Căn cứ từ tài liệu **{title}** (Trang {p_num}):\n  \"{summary_piece}\""
            )

        points_text = "\n\n".join(bullet_points)

        answer = (
            f"Dựa trên nội dung học liệu được trích xuất từ cơ sở tri thức DocUni ({sources_label}), "
            f"hệ thống giải đáp câu hỏi **\"{query}\"** như sau:\n\n"
            f"{points_text}\n\n"
            f"💡 *Ghi chú:* Bạn có thể tham khảo chi tiết ngữ cảnh nguyên văn và tài liệu gốc trong mục trích dẫn bên dưới."
        )
        return answer
