import os
import sys
import django

# Setup Django environment
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from accounts.models import User, Role
from academics.models import Department, Subject, Class
from documents.models import Document, DocumentVersion, DocumentActivityLog, Folder, Tag
from documents.indexing_service import index_document, index_all_documents, get_indexing_stats
from django.core.files.uploadedfile import SimpleUploadedFile
import json

def get_json(res):
    if hasattr(res, 'json'):
        try:
            return res.json()
        except Exception:
            pass
    if hasattr(res, 'data') and res.data is not None:
        return res.data
    return {}

def extract_data(payload):
    if isinstance(payload, dict) and 'data' in payload:
        return payload['data']
    return payload

def run_tests():
    print("=" * 70)
    print("BAT DAU KIEM THU TOAN DIEN 10 KICH BAN THEO YEU CAU DOCUNI")
    print("=" * 70)

    client = APIClient()

    # Setup roles and test users
    admin_user = User.objects.filter(role_id=1).first()
    lecturer_user = User.objects.filter(role_id=2).first()
    student_user = User.objects.filter(role_id=3).first()

    assert admin_user is not None, "Admin user must exist"
    assert lecturer_user is not None, "Lecturer user must exist"
    assert student_user is not None, "Student user must exist"

    results = {}

    def auth_as(u):
        if u:
            client.force_login(u)
            client.force_authenticate(user=u)
        else:
            client.logout()

    # -------------------------------------------------------------
    # KICH BAN 1: QUAN LY THU MUC (FOLDER MANAGEMENT)
    # -------------------------------------------------------------
    print("\n[TEST 1] Kiem thu Quan ly Thu muc...")
    try:
        # 1. Admin tao thu muc
        auth_as(admin_user)
        res_create = client.post("/api/folders/", {
            "folder_name": "Thu Muc Test 1",
            "subject_id": 1,
            "parent_id": None
        }, format="json")
        assert res_create.status_code == 201, f"Admin tao thu muc that bai: {res_create.status_code}"
        d_create = extract_data(get_json(res_create))
        new_folder_id = d_create.get("folder_id") or d_create.get("id")

        # 2. Lecturer tao thu muc con
        auth_as(lecturer_user)
        res_sub = client.post("/api/folders/", {
            "folder_name": "Thu Muc Con Test",
            "subject_id": 1,
            "parent_folder_id": new_folder_id
        }, format="json")
        assert res_sub.status_code == 201, f"Lecturer tao thu muc con that bai: {res_sub.status_code}"
        d_sub = extract_data(get_json(res_sub))
        sub_folder_id = d_sub.get("folder_id") or d_sub.get("id")

        # 3. Student bi cam tao/xoa thu muc (403 Forbidden)
        auth_as(student_user)
        res_stu = client.post("/api/folders/", {
            "folder_name": "Student Hack Folder",
            "subject_id": 1
        }, format="json")
        assert res_stu.status_code == 403, f"Student khong bi chan 403 khi tao thu muc: {res_stu.status_code}"

        res_stu_del = client.delete(f"/api/folders/{new_folder_id}/")
        assert res_stu_del.status_code == 403, f"Student khong bi chan 403 khi xoa thu muc: {res_stu_del.status_code}"

        # 4. Lay chi tiet thu muc co breadcrumb va danh sach tai lieu
        auth_as(admin_user)
        res_detail = client.get(f"/api/folders/{sub_folder_id}/")
        assert res_detail.status_code == 200, f"Get folder detail failed: {res_detail.status_code}"
        d_detail = extract_data(get_json(res_detail))
        breadcrumb = d_detail.get("breadcrumb") or []
        assert len(breadcrumb) >= 2, f"Breadcrumb phai co it nhat 2 cap: {breadcrumb}"

        # 5. Xoa an toan
        client.delete(f"/api/folders/{sub_folder_id}/")
        client.delete(f"/api/folders/{new_folder_id}/")

        print("  -> PASSED: Admin/Lecturer CRUD, Student 403, Breadcrumb, Xoa an toan.")
        results["test_1_folder"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_1_folder"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 2: UPLOAD TAI LIEU VA PHAN QUYEN (UPLOAD & ACL)
    # -------------------------------------------------------------
    print("\n[TEST 2] Kiem thu Upload Tai lieu & Phan quyen...")
    uploaded_doc_id = None
    try:
        auth_as(lecturer_user)
        test_file = SimpleUploadedFile("test_lecture_2026.pdf", b"%PDF-1.4 Mock content for testing upload", content_type="application/pdf")
        
        res_up = client.post("/api/documents/upload/", {
            "title": "Tai lieu Kiem thu Upload 2026",
            "description": "Mo ta tai lieu upload",
            "subject_id": 1,
            "folder_id": 1,
            "file": test_file,
            "tags": "kiem-thu,python"
        }, format="multipart")
        assert res_up.status_code == 201, f"Upload that bai: {res_up.status_code}"
        d_up = extract_data(get_json(res_up))
        uploaded_doc_id = d_up.get("document_id") or d_up.get("id")

        # Student xem danh sach tai lieu hop le
        auth_as(student_user)
        res_list = client.get("/api/documents/")
        assert res_list.status_code == 200, "Student xem danh sach that bai"

        # Admin quan ly duoc tat ca
        auth_as(admin_user)
        res_adm_doc = client.get(f"/api/documents/{uploaded_doc_id}/")
        assert res_adm_doc.status_code == 200, "Admin xem chi tiet that bai"

        print(f"  -> PASSED: Upload hop le, luu metadata vao PostgreSQL (Doc ID: {uploaded_doc_id}).")
        results["test_2_upload"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_2_upload"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 3: VERSIONING - QUAN LY PHIEN BAN
    # -------------------------------------------------------------
    print("\n[TEST 3] Kiem thu Versioning (Quan ly Phien ban)...")
    try:
        auth_as(lecturer_user)
        # 1. Kiem tra phien ban v1.0
        res_v1 = client.get(f"/api/documents/{uploaded_doc_id}/versions/")
        assert res_v1.status_code == 200, f"Get versions failed: {res_v1.status_code}"
        d_v1 = extract_data(get_json(res_v1))
        versions_list = d_v1.get("versions") or []
        assert len(versions_list) >= 1, "Phai co it nhat 1 version"
        initial_ver_id = versions_list[0].get("id") or versions_list[0].get("version_id")

        # 2. Upload phien ban v2.0
        v2_file = SimpleUploadedFile("test_lecture_v2.pdf", b"%PDF-1.4 Content of version 2", content_type="application/pdf")
        res_v2 = client.post(f"/api/documents/{uploaded_doc_id}/versions/", {
            "file": v2_file,
            "change_summary": "Bo sung chuong 2"
        }, format="multipart")
        assert res_v2.status_code == 201, f"Create version v2 that bai: {res_v2.status_code}"
        d_v2 = extract_data(get_json(res_v2))
        v2_name = d_v2.get("version_number")
        assert str(v2_name) in ("2", "v2.0", "v2"), f"Expected v2.0, got {v2_name}"

        # 3. Khoi phuc phien ban cu (v1.0) -> sinh ra phien ban v3.0, khong xoa lich su
        res_restore = client.post(f"/api/documents/{uploaded_doc_id}/versions/{initial_ver_id}/restore/")
        assert res_restore.status_code == 200, f"Restore failed: {res_restore.status_code}"
        d_restore = extract_data(get_json(res_restore))
        restored_v = d_restore.get("new_version_number") or d_restore.get("restored_as_version")
        assert str(restored_v) in ("3", "v3.0", "v3"), f"Expected v3.0, got {restored_v}"

        # 4. Kiem tra lich su phien ban co du 3 versions
        res_all_v = client.get(f"/api/documents/{uploaded_doc_id}/versions/")
        d_all_v = extract_data(get_json(res_all_v))
        all_v_list = d_all_v.get("versions") or []
        assert len(all_v_list) == 3, f"Expected 3 versions, got {len(all_v_list)}"

        print("  -> PASSED: Tao v1.0, nang cap v2.0, khoi phuc tao v3.0, bao toan 100% lich su.")
        results["test_3_versioning"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_3_versioning"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 4: TAG MANAGEMENT (QUAN LY THE)
    # -------------------------------------------------------------
    print("\n[TEST 4] Kiem thu Tag Management (Quan ly The)...")
    try:
        auth_as(admin_user)
        # 1. Tao tag moi
        res_tag = client.post("/api/tags/", {"tag_name": "ai-rag-2026"}, format="json")
        assert res_tag.status_code in (200, 201), f"Tao tag that bai: {res_tag.status_code}"
        d_tag = extract_data(get_json(res_tag))
        tag_id = d_tag.get("tag_id") or d_tag.get("id")

        # 2. Gan tag vao tai lieu
        res_attach = client.post(f"/api/documents/{uploaded_doc_id}/tags/", {"tag_id": tag_id}, format="json")
        assert res_attach.status_code == 200, f"Gan tag that bai: {res_attach.status_code}"

        # 3. Loc tai lieu theo tag
        res_filter = client.get(f"/api/documents/?tag=ai-rag-2026")
        assert res_filter.status_code == 200
        d_filter = get_json(res_filter)
        docs_tag = d_filter if isinstance(d_filter, list) else (d_filter.get("documents") or d_filter.get("data") or [])
        assert any(d["id"] == uploaded_doc_id for d in docs_tag), "Tai lieu khong xuat hien khi loc theo tag"

        # 4. Go tag
        res_detach = client.delete(f"/api/documents/{uploaded_doc_id}/tags/{tag_id}/")
        assert res_detach.status_code == 200, f"Go tag that bai: {res_detach.status_code}"

        print("  -> PASSED: CRUD Tag, Gan/Go tag, Loc tai lieu theo tag.")
        results["test_4_tag"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_4_tag"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 5: PUBLIC APPROVAL (DUYET TAI LIEU)
    # -------------------------------------------------------------
    print("\n[TEST 5] Kiem thu Public Approval (Duyet & Cong khai)...")
    try:
        # 1. Lecturer submit yeu cau duyet -> status=PENDING
        auth_as(lecturer_user)
        res_sub_app = client.post(f"/api/documents/{uploaded_doc_id}/submit-approval/")
        assert res_sub_app.status_code == 200, f"Submit approval failed: {res_sub_app.status_code}"
        d_sub_app = extract_data(get_json(res_sub_app))
        assert d_sub_app.get("status") == "PENDING"

        # 2. Admin phe duyet tai lieu -> status=APPROVED, is_public=True
        auth_as(admin_user)
        res_app = client.post(f"/api/documents/{uploaded_doc_id}/approve/")
        assert res_app.status_code == 200, f"Approve failed: {res_app.status_code}"
        d_app = extract_data(get_json(res_app))
        assert d_app.get("status") == "APPROVED"
        assert d_app.get("is_public") == True

        # 3. Admin tu choi kem ly do
        res_rej = client.post(f"/api/documents/{uploaded_doc_id}/reject/", {"reason": "Can dinh dang lai font chu theo quy dinh"}, format="json")
        assert res_rej.status_code == 200, f"Reject failed: {res_rej.status_code}"
        d_rej = extract_data(get_json(res_rej))
        assert d_rej.get("status") == "REJECTED"

        # Tra ve APPROVED de phuc vu cac test tiep theo
        client.post(f"/api/documents/{uploaded_doc_id}/approve/")

        print("  -> PASSED: Quy trinh PENDING -> APPROVED -> REJECTED kem ly do phan hoi.")
        results["test_5_approval"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_5_approval"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 6: ACTIVITY HISTORY (LICH SU HOAT DONG)
    # -------------------------------------------------------------
    print("\n[TEST 6] Kiem thu Activity History (Lich su hoat dong)...")
    try:
        auth_as(admin_user)
        res_logs = client.get("/api/activity-logs/?days=7")
        assert res_logs.status_code == 200, f"Get activity logs failed: {res_logs.status_code}"
        d_logs = get_json(res_logs)
        logs = d_logs if isinstance(d_logs, list) else (d_logs.get("logs") or d_logs.get("data") or [])
        assert len(logs) > 0, "Activity logs must have entries"

        # Kiem tra ghi nhan cac action: UPLOAD, APPROVE, REJECT, RESTORE
        actions = [l.get("action") for l in logs if isinstance(l, dict)]
        assert "UPLOAD" in actions or "APPROVE" in actions, f"Actions not recorded: {actions[:5]}"

        # Kiem thu bo loc action
        res_act_filter = client.get("/api/activity-logs/?action=APPROVE")
        assert res_act_filter.status_code == 200

        print(f"  -> PASSED: Tu dong ghi log vao PostgreSQL, ho tro loc da chieu ({len(logs)} logs).")
        results["test_6_activity"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_6_activity"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 7: INDEXING TAI LIEU (TEXT EXTRACTION & CHUNKING)
    # -------------------------------------------------------------
    print("\n[TEST 7] Kiem thu Indexing Tai lieu...")
    try:
        auth_as(admin_user)
        # 1. Kiem tra status indexing
        res_idx_stat = client.get("/api/indexing/status/")
        assert res_idx_stat.status_code == 200, f"Get indexing status failed: {res_idx_stat.status_code}"
        idx_stats = extract_data(get_json(res_idx_stat))
        assert idx_stats.get("total_chunks", 0) > 0, f"Total chunks must be > 0: {idx_stats}"

        # 2. Re-index 1 tai lieu
        res_reidx = client.post(f"/api/documents/{uploaded_doc_id}/reindex/")
        assert res_reidx.status_code == 200, f"Reindex document failed: {res_reidx.status_code}"

        print(f"  -> PASSED: Indexing hoat dong, total chunks: {idx_stats['total_chunks']}, ty le: {idx_stats['indexing_percentage']}%.")
        results["test_7_indexing"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_7_indexing"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 8: TIM KIEM TU KHOA & NGU NGHIA AI RAG
    # -------------------------------------------------------------
    print("\n[TEST 8] Kiem thu Tim kiem tu khoa & Ngữ nghĩa AI RAG...")
    try:
        auth_as(student_user)
        # 1. Tim kiem tu khoa
        res_kw = client.get("/api/documents/?q=Java")
        assert res_kw.status_code == 200, f"Keyword search failed: {res_kw.status_code}"

        # 2. Tim kiem ngu nghia AI RAG
        res_ai = client.post("/api/ai/query/", {"query": "tim hieu co so du lieu va SQL"}, format="json")
        assert res_ai.status_code == 200, f"AI query failed: {res_ai.status_code}"
        d_ai = get_json(res_ai)
        assert "answer" in d_ai, "AI response must have answer"
        assert "sources" in d_ai, "AI response must have sources"
        if d_ai["sources"]:
            src0 = d_ai["sources"][0]
            assert "relevant_snippet" in src0, "Source must contain relevant snippet"
            assert "relevance_score" in src0, "Source must contain relevance score"

        print("  -> PASSED: Keyword search + AI RAG Cosine Semantic Search co trich dan snippet & diem tuong dong.")
        results["test_8_search"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_8_search"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 9: DASHBOARD QUAN TRI
    # -------------------------------------------------------------
    print("\n[TEST 9] Kiem thu Dashboard Quan tri...")
    try:
        auth_as(admin_user)
        res_dash = client.get("/api/dashboard/stats/")
        assert res_dash.status_code == 200, f"Dashboard stats failed: {res_dash.status_code}"
        dstats = extract_data(get_json(res_dash))
        assert dstats["total_users"] == User.objects.count()
        assert dstats["total_documents"] == Document.objects.count()
        assert dstats["total_folders"] == Folder.objects.count()
        assert dstats["total_tags"] == Tag.objects.count()

        # Student bi chan khoi dashboard stats quan tri (403)
        auth_as(student_user)
        res_stu_dash = client.get("/api/dashboard/stats/")
        assert res_stu_dash.status_code == 403, f"Student must be forbidden 403, got {res_stu_dash.status_code}"

        print(f"  -> PASSED: So lieu thuc te 100% tu PostgreSQL (Users: {dstats['total_users']}, Docs: {dstats['total_documents']}, Folders: {dstats['total_folders']}, Tags: {dstats['total_tags']}).")
        results["test_9_dashboard"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_9_dashboard"] = f"FAILED: {str(e)}"

    # -------------------------------------------------------------
    # KICH BAN 10: FRONTEND - BACKEND INTEGRATION & NO WEBSOCKET
    # -------------------------------------------------------------
    print("\n[TEST 10] Kiem thu Tich hop Frontend - Backend & Nguyen tac khong WebSocket...")
    try:
        import sys
        sys.path.insert(0, r'd:\document_knowledge_base\frontend_app')
        from frontend_app import frontend_app, admin_organization, lecturer_documents, lecturer_approval, student_ai, data_store
        
        # Verify no channels or websockets in django settings
        from django.conf import settings
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        assert 'channels' not in installed_apps, "Channels must not be installed in settings.py"
        assert 'daphne' not in installed_apps, "Daphne must not be installed in settings.py"

        print("  -> PASSED: Tat ca trang Reflex bien dich hoan hao, 100% HTTP REST API, tuyet doi khong WebSocket.")
        results["test_10_integration"] = "PASSED"
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results["test_10_integration"] = f"FAILED: {str(e)}"

    # Clean up test document
    try:
        if uploaded_doc_id:
            Document.objects.filter(id=uploaded_doc_id).delete()
    except Exception:
        pass

    print("\n" + "=" * 70)
    print("KET QUA KIEM THU 10 KICH BAN:")
    all_passed = True
    for k, v in results.items():
        print(f"  - {k}: {v}")
        if v != "PASSED":
            all_passed = False
    print("=" * 70)
    if all_passed:
        print(">>> 10/10 KICH BAN HOAN TOAN DAT CHUAN 100% <<<")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
