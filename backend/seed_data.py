"""
DocUni - Database Seeder Script
Nạp đầy đủ dữ liệu mẫu chuẩn từ database/schema.sql vào cơ sở dữ liệu
(Hỗ trợ cả PostgreSQL và SQLite)
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# UTF-8 stdout on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent / 'venv' / 'Lib' / 'site-packages'))
local_python_pkgs = r'C:\Users\Thai anh ky\AppData\Local\Programs\Python\Python313\Lib\site-packages'
if os.path.exists(local_python_pkgs) and local_python_pkgs not in sys.path:
    sys.path.insert(0, local_python_pkgs)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.db import transaction
from accounts.models import Role, User
from academics.models import Department, Class, Subject
from documents.models import Folder, Document, DocumentVersion, Tag, DocumentActivityLog
from permissions.models import DocumentPermission


def seed_all():
    print("[+] Bat dau nap du lieu mau DocUni...")

    with transaction.atomic():
        # 1. ROLES
        roles_data = [
            (1, Role.ADMIN),
            (2, Role.LECTURER),
            (3, Role.STUDENT),
        ]
        role_objs = {}
        for r_id, r_name in roles_data:
            role, _ = Role.objects.get_or_create(id=r_id, defaults={'role_name': r_name})
            role_objs[r_id] = role
        print(f"  [OK] Da nap {len(role_objs)} vai tro (Roles)")

        # 2. DEPARTMENTS
        depts_data = [
            (1, 'Cong nghe thong tin'),
            (2, 'Kinh te'),
            (3, 'Ngoai ngu'),
        ]
        dept_objs = {}
        for d_id, d_name in depts_data:
            dept, _ = Department.objects.get_or_create(id=d_id, defaults={'department_name': d_name})
            dept_objs[d_id] = dept
        print(f"  [OK] Da nap {len(dept_objs)} khoa (Departments)")

        # 3. CLASSES
        classes_data = [
            (1, 'CNTT-K1', 1, False),
            (2, 'CNTT-K2', 1, False),
            (3, 'KT-K1', 2, False),
            (4, 'KT-K2', 2, False),
            (5, 'NN-K1', 3, False),
            (6, 'CNTT-Khoa', 1, True),  # Lop khoa
        ]
        class_objs = {}
        for c_id, c_name, d_id, locked in classes_data:
            cls, _ = Class.objects.get_or_create(
                id=c_id,
                defaults={
                    'class_name': c_name,
                    'department': dept_objs[d_id],
                    'is_locked': locked,
                }
            )
            class_objs[c_id] = cls
        print(f"  [OK] Da nap {len(class_objs)} lop hoc (Classes)")

        # 4. SUBJECTS
        subjects_data = [
            (1, 'Lap trinh Python', 1),
            (2, 'Co so du lieu', 1),
            (3, 'Lap trinh Web', 1),
            (4, 'Kinh te vi mo', 2),
            (5, 'Nguyen ly ke toan', 2),
            (6, 'Tieng Anh chuyen nganh IT', 3),
            (7, 'Tieng Anh giao tiep', 3),
        ]
        sub_objs = {}
        for s_id, s_name, d_id in subjects_data:
            sub, _ = Subject.objects.get_or_create(
                id=s_id,
                defaults={'subject_name': s_name, 'department': dept_objs[d_id]}
            )
            sub_objs[s_id] = sub
        print(f"  [OK] Da nap {len(sub_objs)} mon hoc (Subjects)")

        # 5. USERS
        users_data = [
            (1, 'admin', 'hash_admin', 'Quan tri vien', 1, None, None),
            (2, 'admin02', 'hash_admin', 'Quan tri vien 2', 1, None, None),
            (3, 'gv01', 'hash_gv', 'Nguyen Van An', 2, 1, None),
            (4, 'gv02', 'hash_gv', 'Tran Thi Binh', 2, 1, None),
            (5, 'gv03', 'hash_gv', 'Le Van Cuong', 2, 2, None),
            (6, 'gv04', 'hash_gv', 'Pham Thi Dung', 2, 3, None),
            (7, 'sv01', 'hash_sv', 'Hoang Minh Khoa', 3, 1, 1),
            (8, 'sv02', 'hash_sv', 'Vu Thanh Lam', 3, 1, 1),
            (9, 'sv03', 'hash_sv', 'Dang Quoc Minh', 3, 1, 1),
            (10, 'sv04', 'hash_sv', 'Bui Thu Nga', 3, 1, 2),
            (11, 'sv05', 'hash_sv', 'Do Van Phuc', 3, 1, 2),
            (12, 'sv06', 'hash_sv', 'Ngo Thi Quynh', 3, 2, 3),
            (13, 'sv07', 'hash_sv', 'Duong Van Son', 3, 2, 3),
            (14, 'sv08', 'hash_sv', 'Ly Thi Thao', 3, 2, 4),
            (15, 'sv09', 'hash_sv', 'Trinh Van Uy', 3, 3, 5),
            (16, 'sv10', 'hash_sv', 'Mai Thi Van', 3, 3, 5),
            (17, 'sv11', 'hash_sv', 'Cao Van Xuan', 3, 1, 6),
        ]
        user_objs = {}
        for u_id, uname, pwd, fname, r_id, d_id, c_id in users_data:
            user, created = User.objects.get_or_create(
                id=u_id,
                defaults={
                    'username': uname,
                    'full_name': fname,
                    'password': pwd,
                    'role': role_objs[r_id],
                    'department': dept_objs[d_id] if d_id else None,
                    'student_class': class_objs[c_id] if c_id else None,
                    'is_staff': (r_id == 1),
                    'is_active': True,
                }
            )
            user_objs[u_id] = user
        print(f"  [OK] Da nap {len(user_objs)} nguoi dung (Users)")

        # 6. FOLDERS
        folders_data = [
            (1, 'Bai giang', 1, None, 3),
            (2, 'Chuong 1 - Co ban', 1, 1, 3),
            (3, 'Chuong 2 - OOP', 1, 1, 3),
            (4, 'Bai tap thuc hanh', 1, None, 3),
            (5, 'Ly thuyet RDBMS', 2, None, 4),
            (6, 'SQL co ban', 2, 5, 4),
            (7, 'Frontend HTML-CSS', 3, None, 3),
            (8, 'Backend Django', 3, None, 3),
            (9, 'Vi mo chuong 1', 4, None, 5),
            (10, 'Vi mo chuong 2', 4, None, 5),
            (11, 'Bai tap dinh khoan', 5, None, 5),
            (12, 'Reading Unit 1-5', 6, None, 6),
        ]
        folder_objs = {}
        for f_id, f_name, s_id, p_id, u_id in folders_data:
            parent = folder_objs.get(p_id) if p_id else None
            f, _ = Folder.objects.get_or_create(
                id=f_id,
                defaults={
                    'folder_name': f_name,
                    'subject': sub_objs[s_id],
                    'parent_folder': parent,
                    'created_by': user_objs.get(u_id),
                }
            )
            folder_objs[f_id] = f
        print(f"  [OK] Da nap {len(folder_objs)} thu muc (Folders)")

        # 7. TAGS
        tags_data = [
            (1, 'python'), (2, 'oop'), (3, 'sql'), (4, 'database'),
            (5, 'django'), (6, 'react'), (7, 'kinhte'), (8, 'vimo'),
            (9, 'ketoan'), (10, 'english'), (11, 'it-english'),
            (12, 'slide'), (13, 'baitap'), (14, 'detai'),
        ]
        tag_objs = {}
        for t_id, t_name in tags_data:
            tag, _ = Tag.objects.get_or_create(id=t_id, defaults={'tag_name': t_name})
            tag_objs[t_id] = tag
        print(f"  [OK] Da nap {len(tag_objs)} the phan loai (Tags)")

        # 8. DOCUMENTS
        docs_data = [
            (1, 'Giao trinh Python co ban', 'Tai lieu day du tu bien den ham', 1, 2, 3, 'APPROVED', True, 120, 45, 1),
            (2, 'Huong dan OOP trong Python', 'Class, Object, Ke thua, Da hinh', 1, 3, 3, 'APPROVED', False, 85, 30, 1),
            (3, 'Tong hop bai tap thuc hanh Python', '50 bai tap co dap an chi tiet', 1, 4, 3, 'APPROVED', False, 200, 95, 1),
            (4, 'Ly thuyet Co so du lieu quan he', 'Mo hinh thuc the quan he ERD', 2, 5, 4, 'APPROVED', True, 60, 15, 1),
            (5, 'Thuc hanh truy van SQL tu A-Z', 'SELECT, JOIN, GROUP BY, Subquery', 2, 6, 4, 'APPROVED', True, 310, 150, 1),
            (6, 'Slide Xay dung Web voi Django REST', 'Kien truc MTV va RESTful API', 3, 8, 3, 'APPROVED', False, 90, 40, 1),
            (7, 'Tai lieu Kinh te vi mo chuong 1', 'Cung cau va co che thi truong', 4, 9, 5, 'APPROVED', True, 45, 10, 1),
            (8, 'Giao trinh Tieng Anh CNTT', 'Tu vung va bai doc chuyen nganh', 6, 12, 6, 'APPROVED', False, 130, 55, 1),
            (9, 'Bao cao de tai Web Ban Hang (sv01)', 'Nhom 1 lam web thuong mai dien tu', 3, 8, 7, 'PENDING', False, 10, 0, None),
            (10, 'Bao cao de tai AI Chatbot (sv02)', 'Nhom 2 lam tro ly ao', 1, 4, 8, 'PENDING', False, 8, 0, None),
            (11, 'De cuong on tap Ke toan tai chinh', 'Tong hop cong thuc va dang bai', 5, 11, 5, 'APPROVED', False, 75, 25, 1),
            (12, 'Slide Tieng Anh Giao Tiep Unit 1', 'Greetings and Introductions', 7, None, 6, 'APPROVED', True, 50, 12, 1),
            (13, 'Bao cao cuoi ky LTM (sv06)', 'Bao cao vi mo ngan hang trung uong', 4, 10, 12, 'REJECTED', False, 15, 1, None),
            (14, 'Bai tap lon Co so du lieu (sv04)', 'Thiet ke CSDL quan ly benh vien', 2, 6, 10, 'PENDING', False, 5, 0, None),
        ]
        doc_objs = {}
        for d_id, title, desc, s_id, f_id, u_id, st, pub, vcnt, dcnt, app_id in docs_data:
            doc, _ = Document.objects.get_or_create(
                id=d_id,
                defaults={
                    'title': title,
                    'description': desc,
                    'subject': sub_objs[s_id],
                    'folder': folder_objs.get(f_id) if f_id else None,
                    'uploader': user_objs.get(u_id),
                    'status': st,
                    'is_public': pub,
                    'view_count': vcnt,
                    'download_count': dcnt,
                    'approved_by': user_objs.get(app_id) if app_id else None,
                    'approved_at': datetime.now() if app_id else None,
                }
            )
            doc_objs[d_id] = doc
        print(f"  [OK] Da nap {len(doc_objs)} tai lieu (Documents)")

        # 9. DOCUMENT VERSIONS
        versions_data = [
            (1, 1, 'documents/1/1/v1_Giao_trinh_Python_co_ban.pdf', 1, 3, 'Ban phat hanh dau tien'),
            (2, 1, 'documents/1/1/v2_Giao_trinh_Python_co_ban_cap_nhat.pdf', 2, 3, 'Cap nhat Python 3.12 va vi du moi'),
            (3, 2, 'documents/1/2/v1_Huong_dan_OOP_Python.pdf', 1, 3, 'Ban khoi tao'),
            (4, 3, 'documents/1/3/v1_Bai_tap_thuc_hanh_Python.docx', 1, 3, 'De bai 50 cau'),
            (5, 3, 'documents/1/3/v2_Bai_tap_thuc_hanh_Python_dap_an.docx', 2, 3, 'Bo sung dap an chi tiet'),
            (6, 4, 'documents/2/4/v1_CSDL_Quan_he.pdf', 1, 4, 'Noi dung chuan'),
            (7, 5, 'documents/2/5/v1_Truy_van_SQL.sql', 1, 4, 'File script SQL thuc hanh'),
            (8, 6, 'documents/3/6/v1_Django_REST_Slide.pptx', 1, 3, 'Slide trinh chieu'),
            (9, 7, 'documents/4/7/v1_Kinh_te_vi_mo_C1.pdf', 1, 5, 'Chuong 1 toan tap'),
            (10, 8, 'documents/6/8/v1_English_for_IT.pdf', 1, 6, 'Ban chinh thuc'),
            (11, 9, 'documents/3/9/v1_Bao_cao_Web_Nhom1.docx', 1, 7, 'Nop bao cao lan 1'),
            (12, 10, 'documents/1/10/v1_Bao_cao_AI_Nhom2.docx', 1, 8, 'Nop de tai'),
            (13, 11, 'documents/5/11/v1_De_cuong_Ke_toan.pdf', 1, 5, 'De cuong on tap'),
            (14, 12, 'documents/7/12/v1_Tieng_Anh_Unit1.pptx', 1, 6, 'Slide bai giang'),
            (15, 13, 'documents/4/13/v1_Bao_cao_Vi_mo_sv06.docx', 1, 12, 'Ban nop ban dau'),
            (16, 13, 'documents/4/13/v2_Bao_cao_Vi_mo_sv06_sua.docx', 2, 12, 'Sua theo gop y cua GV'),
            (17, 14, 'documents/2/14/v1_BTL_CSDL_sv04.docx', 1, 10, 'De tai benh vien'),
        ]
        ver_count = 0
        for v_id, d_id, fpath, vnum, uid, summ in versions_data:
            doc = doc_objs.get(d_id)
            if doc:
                DocumentVersion.objects.get_or_create(
                    id=v_id,
                    defaults={
                        'document': doc,
                        'file': fpath,
                        'version_number': vnum,
                        'updated_by': user_objs.get(uid),
                        'change_summary': summ,
                    }
                )
                ver_count += 1
        print(f"  [OK] Da nap {ver_count} phien ban (Versions)")

        # 10. DOCUMENT PERMISSIONS (ACL)
        perms_data = [
            (1, 2, 'DEPARTMENT', 1, None, None, True, True),
            (2, 2, 'USER', None, None, 10, True, False),
            (3, 3, 'CLASS', None, 1, None, True, True),     # Document 3 cho CNTT-K1 (sv01, sv02, sv03)
            (4, 3, 'CLASS', None, 2, None, True, False),    # Document 3 cho CNTT-K2 chi xem (sv04, sv05)
            (5, 3, 'USER', None, None, 4, True, True),
            (6, 6, 'CLASS', None, 1, None, True, True),
            (7, 6, 'CLASS', None, 2, None, True, True),
            (8, 6, 'USER', None, None, 17, False, False),
            (9, 8, 'DEPARTMENT', 1, None, None, True, True),
            (10, 11, 'DEPARTMENT', 2, None, None, True, True),
            (11, 11, 'USER', None, None, 5, True, True),
        ]
        perm_count = 0
        for p_id, d_id, p_type, dept_id, c_id, u_id, c_view, c_down in perms_data:
            doc = doc_objs.get(d_id)
            if doc:
                DocumentPermission.objects.get_or_create(
                    id=p_id,
                    defaults={
                        'document': doc,
                        'permission_type': p_type,
                        'department': dept_objs.get(dept_id) if dept_id else None,
                        'student_class': class_objs.get(c_id) if c_id else None,
                        'user': user_objs.get(u_id) if u_id else None,
                        'can_view': c_view,
                        'can_download': c_down,
                    }
                )
                perm_count += 1
        print(f"  [OK] Da nap {perm_count} quyen truy cap ACL (Permissions)")

    print("[SUCCESS] Hoan tat nap du lieu DocUni thanh cong!")


if __name__ == '__main__':
    seed_all()
