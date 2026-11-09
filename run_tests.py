"""
DocUni - Script Chạy Kiểm Thử Tự Động Toàn Diện (Task 2 & Task 3)
Chạy bằng lệnh: python run_tests.py
"""

import sys
import os

# Thiết lập encoding UTF-8 cho terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Thêm đường dẫn project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "venv", "Lib", "site-packages"))
sys.path.append(os.path.join(BASE_DIR, "frontend_app"))

from frontend_app.data_store import GlobalDocState, PRESET_USERS, INITIAL_DOCUMENTS

def run_all_tests():
    print("=" * 65)
    print("      DOCUNI - BỘ KIỂM THỬ TỰ ĐỘNG TASK 2 & TASK 3 (NHÓM 3)      ")
    print("=" * 65)

    # Khởi tạo state test
    state = object.__new__(GlobalDocState)
    state.dirty_vars = set()
    state.dirty_substates = set()
    state.parent_state = None
    state.substates = {}
    state._was_touched = False

    state.users = [dict(u) for u in PRESET_USERS]
    state.documents = [dict(d) for d in INITIAL_DOCUMENTS]
    state.current_user_id = "u1"
    state.selected_faculty = "ALL"
    state.selected_subject = "ALL"
    state.selected_folder = "ALL"
    state.selected_tag = "ALL"
    state.search_query = ""
    state.detail_modal_open = False
    state.active_doc = {}
    state.acl_denied_open = False
    state.acl_denied_doc_title = ""
    state.acl_denied_target_class = ""
    state.acl_denied_current_class = ""
    state.version_modal_open = False
    state.active_version_doc = {}
    state.new_version_summary = ""
    state.audit_modal_open = False
    state.active_audit_doc = {}
    state.reject_modal_open = False
    state.rejecting_doc_id = ""
    state.reject_feedback_input = ""

    # ──────────────────────────────────────────────────────────────────────────
    # 1. KIỂM TRA TRẠNG THÁI KHỞI TẠO
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[BƯỚC 1] KIỂM TRA KHỞI TẠO DỮ LIỆU:")
    user = state.current_user
    print(f"  • Người dùng mặc định: {user['full_name']} ({user['class_name']})")
    print(f"  • Tổng số tài liệu mẫu: {len(state.documents)}")
    print(f"  • Số tài liệu công khai: {len(state.public_documents)}")
    print(f"  • Số tài liệu chờ duyệt (PENDING): {state.pending_count}")

    # ──────────────────────────────────────────────────────────────────────────
    # 2. KIỂM TRA TASK 2: PHÂN QUYỀN ACL (LỚP A VS LỚP B)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[BƯỚC 2] KIỂM TRA TASK 2 - ACL (LỚP A VS LỚP B):")
    # 2.1 Sinh viên Nam (Lớp A) mở tài liệu Lớp A
    state.switch_user("u1")
    print(f"  2.1. Đăng nhập: {state.current_user['full_name']} ({state.current_user['class_name']})")
    state.open_document("doc_acl_class_a")
    print(f"       -> Mở tài liệu Lớp A: detail_modal_open = {state.detail_modal_open} | acl_denied_open = {state.acl_denied_open}")
    assert state.detail_modal_open == True, "LỖI: Sinh viên Lớp A phải mở được tài liệu Lớp A"
    assert state.acl_denied_open == False
    print("       ==> [PASS] Sinh viên Lớp A mở tài liệu Lớp A THÀNH CÔNG!")
    state.close_detail_modal()

    # 2.2 Sinh viên Mai (Lớp B) cố mở tài liệu Lớp A
    state.switch_user("u2")
    print(f"  2.2. Chuyển sang: {state.current_user['full_name']} ({state.current_user['class_name']})")
    state.open_document("doc_acl_class_a")
    print(f"       -> Mở tài liệu Lớp A: detail_modal_open = {state.detail_modal_open} | acl_denied_open = {state.acl_denied_open}")
    print(f"       -> Cảnh báo 403: Quyền yêu cầu '{state.acl_denied_target_class}'")
    assert state.detail_modal_open == False, "LỖI: Sinh viên Lớp B KHÔNG ĐƯỢC mở tài liệu Lớp A"
    assert state.acl_denied_open == True, "LỖI: Hệ thống phải bật cảnh báo Từ chối truy cập 403"
    print("       ==> [PASS] Sinh viên Lớp B BỊ CHẶN (HTTP 403) ĐÚNG YÊU CẦU ĐỀ BÀI!")
    state.close_acl_denied()

    # ──────────────────────────────────────────────────────────────────────────
    # 3. KIỂM TRA TASK 3: QUY TRÌNH DUYỆT (PENDING -> APPROVE -> PUBLIC)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[BƯỚC 3] KIỂM TRA TASK 3 - QUY TRÌNH PHÊ DUYỆT:")
    state.switch_user("u3")
    print(f"  3.1. Chuyển sang: {state.current_user['full_name']} ({state.current_user['role_label']})")
    
    target_pending = state.pending_docs[0]
    target_id = target_pending["id"]
    print(f"       -> Tài liệu chờ duyệt: '{target_pending['title']}' (ID: {target_id})")
    
    count_before = len(state.public_documents)
    print(f"       -> Số tài liệu công khai trước khi duyệt: {count_before}")
    
    # Giảng viên bấm duyệt
    state.approve_document(target_id)
    count_after = len(state.public_documents)
    print(f"       -> Số tài liệu công khai sau khi duyệt: {count_after}")
    
    assert count_after == count_before + 1, "LỖI: Tài liệu được duyệt phải xuất hiện trên kho công khai"
    
    # Kiểm tra log kiểm toán (Audit log)
    doc_approved = next(d for d in state.documents if d["id"] == target_id)
    latest_log = doc_approved["activity_logs"][0]
    print(f"       -> Trạng thái mới: status = {doc_approved['status']} | is_public = {doc_approved['is_public']}")
    print(f"       -> Nhật ký kiểm toán ghi nhận: {latest_log['action']} bởi {latest_log['user_name']}")
    assert latest_log["action"] == "APPROVE"
    print("       ==> [PASS] Duyệt tài liệu và xuất bản công khai THÀNH CÔNG!")

    # ──────────────────────────────────────────────────────────────────────────
    # 4. KIỂM TRA TASK 3: LƯU PHIÊN BẢN (VERSIONING v1.0 -> v2.0)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[BƯỚC 4] KIỂM TRA TASK 3 - QUẢN LÝ PHIÊN BẢN:")
    state.open_version_modal(target_id)
    state.new_version_summary = "Cập nhật bài tập cây AVL và Đồ thị"
    state.submit_new_version()
    
    doc_updated = next(d for d in state.documents if d["id"] == target_id)
    print(f"       -> Phiên bản hiện tại mới: {doc_updated['current_version']}")
    print(f"       -> Danh sách các version lưu trữ: {[v['version'] for v in doc_updated['versions']]}")
    assert doc_updated["current_version"] == "v2.0"
    print("       ==> [PASS] Tự động nâng phiên bản v1.0 -> v2.0 THÀNH CÔNG!")

    print("\n" + "=" * 65)
    print("   🎉 KẾT QUẢ: TOÀN BỘ 4 BỘ TEST NGHIỆP VỤ ĐẠT 100% PASS!   ")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_all_tests()
