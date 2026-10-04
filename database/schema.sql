CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,

    CONSTRAINT chk_role_name
        CHECK (role_name IN ('ADMIN', 'LECTURER', 'STUDENT'))
);

CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE classes (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(255) NOT NULL UNIQUE,

    department_id INT NOT NULL,

    is_locked BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_class_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE CASCADE
);

CREATE TABLE subjects (
    subject_id SERIAL PRIMARY KEY,

    subject_name VARCHAR(255) NOT NULL,
    department_id INT NOT NULL,

    CONSTRAINT uq_subject_department
        UNIQUE (subject_name, department_id),

    CONSTRAINT fk_subject_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE CASCADE
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,

    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    full_name VARCHAR(255) NOT NULL,

    role_id INT NOT NULL,
    department_id INT,
    class_id INT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_role
        FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_user_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_user_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id)
        ON DELETE SET NULL
);

CREATE TABLE folders (
    folder_id SERIAL PRIMARY KEY,

    folder_name VARCHAR(255) NOT NULL,

    subject_id INT NOT NULL,

    parent_folder_id INT,

    created_by INT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_folder_subject
        FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_folder_parent
        FOREIGN KEY (parent_folder_id)
        REFERENCES folders(folder_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_folder_creator
        FOREIGN KEY (created_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT uq_folder_name
        UNIQUE (subject_id, parent_folder_id, folder_name),

    CONSTRAINT chk_folder_name
        CHECK (LENGTH(TRIM(folder_name)) > 0)
);

CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    subject_id INT NOT NULL,
    folder_id INT,

    uploader_id INT,

    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',

    is_public BOOLEAN NOT NULL DEFAULT FALSE,

    view_count INT NOT NULL DEFAULT 0,
    download_count INT NOT NULL DEFAULT 0,

    approved_by INT,
    approved_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_document_subject
        FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_document_folder
        FOREIGN KEY (folder_id)
        REFERENCES folders(folder_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_document_uploader
        FOREIGN KEY (uploader_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_document_approver
        FOREIGN KEY (approved_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_document_status
        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),

    CONSTRAINT chk_document_view_count
        CHECK (view_count >= 0),

    CONSTRAINT chk_document_download_count
        CHECK (download_count >= 0),

    CONSTRAINT chk_document_approval
        CHECK (
            (status = 'APPROVED' AND approved_by IS NOT NULL AND approved_at IS NOT NULL)
            OR
            (status <> 'APPROVED')
        )
);

CREATE TABLE document_versions (
    version_id SERIAL PRIMARY KEY,

    document_id INT NOT NULL,

    file_path VARCHAR(500) NOT NULL,

    version_number INT NOT NULL,

    updated_by INT,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    change_summary TEXT,

    CONSTRAINT fk_version_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_version_user
        FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT uq_document_version
        UNIQUE (document_id, version_number),

    CONSTRAINT chk_version_number
        CHECK (version_number > 0),

    CONSTRAINT chk_file_path
        CHECK (LENGTH(TRIM(file_path)) > 0)
);

CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,

    tag_name VARCHAR(100) NOT NULL UNIQUE,

    CONSTRAINT chk_tag_name
        CHECK (LENGTH(TRIM(tag_name)) > 0)
);

CREATE TABLE document_tags (
    document_id INT NOT NULL,
    tag_id INT NOT NULL,

    PRIMARY KEY (document_id, tag_id),

    CONSTRAINT fk_document_tag_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_document_tag_tag
        FOREIGN KEY (tag_id)
        REFERENCES tags(tag_id)
        ON DELETE CASCADE
);

CREATE TABLE document_permissions (
    permission_id SERIAL PRIMARY KEY,

    document_id INT NOT NULL,

    permission_type VARCHAR(50) NOT NULL,

    department_id INT,
    class_id INT,
    user_id INT,

    can_view BOOLEAN NOT NULL DEFAULT TRUE,
    can_download BOOLEAN NOT NULL DEFAULT TRUE,
    can_edit BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_permission_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_permission_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_permission_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_permission_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_permission_type
        CHECK (
            permission_type IN (
                'DEPARTMENT',
                'CLASS',
                'USER'
            )
        ),

    CONSTRAINT chk_permission_target
        CHECK (
            (permission_type = 'DEPARTMENT' AND department_id IS NOT NULL
                AND class_id IS NULL AND user_id IS NULL)

            OR

            (permission_type = 'CLASS' AND class_id IS NOT NULL
                AND department_id IS NULL AND user_id IS NULL)

            OR

            (permission_type = 'USER' AND user_id IS NOT NULL
                AND department_id IS NULL AND class_id IS NULL)
        ),

    CONSTRAINT uq_document_department_permission
        UNIQUE (document_id, department_id),

    CONSTRAINT uq_document_class_permission
        UNIQUE (document_id, class_id),

    CONSTRAINT uq_document_user_permission
        UNIQUE (document_id, user_id)
);

CREATE TABLE document_activity_logs (
    log_id SERIAL PRIMARY KEY,

    document_id INT NOT NULL,

    user_id INT,

    action VARCHAR(100) NOT NULL,

    description TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_activity_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_activity_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_activity_action
        CHECK (
            action IN (
                'CREATE',
                'UPDATE',
                'DELETE',
                'APPROVE',
                'REJECT',
                'VIEW',
                'DOWNLOAD',
                'CHANGE_PERMISSION',
                'ADD_TAG',
                'REMOVE_TAG'
            )
        )
);

CREATE TABLE document_embeddings (
    embedding_id SERIAL PRIMARY KEY,

    document_id INT NOT NULL,

    chunk_index INT NOT NULL,

    chunk_text TEXT NOT NULL,

    embedding_array FLOAT[] NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_embedding_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_document_chunk
        UNIQUE (document_id, chunk_index),

    CONSTRAINT chk_chunk_index
        CHECK (chunk_index >= 0),

    CONSTRAINT chk_chunk_text
        CHECK (LENGTH(TRIM(chunk_text)) > 0),

    CONSTRAINT chk_embedding_not_empty
        CHECK (CARDINALITY(embedding_array) > 0)
);

CREATE TABLE ai_queries (
    query_id SERIAL PRIMARY KEY,

    user_id INT,

    query_text TEXT NOT NULL,

    ai_response TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ai_query_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_ai_query_text
        CHECK (LENGTH(TRIM(query_text)) > 0)
);

CREATE TABLE ai_query_sources (
    query_id INT NOT NULL,

    document_id INT NOT NULL,

    embedding_id INT,

    PRIMARY KEY (query_id, document_id, embedding_id),

    CONSTRAINT fk_ai_source_query
        FOREIGN KEY (query_id)
        REFERENCES ai_queries(query_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_ai_source_document
        FOREIGN KEY (document_id)
        REFERENCES documents(document_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_ai_source_embedding
        FOREIGN KEY (embedding_id)
        REFERENCES document_embeddings(embedding_id)
        ON DELETE SET NULL
);

CREATE INDEX idx_users_role
    ON users(role_id);

CREATE INDEX idx_users_department
    ON users(department_id);

CREATE INDEX idx_users_class
    ON users(class_id);

CREATE INDEX idx_subjects_department
    ON subjects(department_id);

CREATE INDEX idx_documents_subject
    ON documents(subject_id);

CREATE INDEX idx_documents_folder
    ON documents(folder_id);

CREATE INDEX idx_documents_uploader
    ON documents(uploader_id);

CREATE INDEX idx_documents_status
    ON documents(status);

CREATE INDEX idx_documents_public
    ON documents(is_public);

CREATE INDEX idx_document_versions_document
    ON document_versions(document_id);

CREATE INDEX idx_document_permissions_document
    ON document_permissions(document_id);

CREATE INDEX idx_document_permissions_department
    ON document_permissions(department_id);

CREATE INDEX idx_document_permissions_class
    ON document_permissions(class_id);

CREATE INDEX idx_document_permissions_user
    ON document_permissions(user_id);

CREATE INDEX idx_activity_document
    ON document_activity_logs(document_id);

CREATE INDEX idx_activity_user
    ON document_activity_logs(user_id);

CREATE INDEX idx_embeddings_document
    ON document_embeddings(document_id);

CREATE INDEX idx_ai_queries_user
    ON ai_queries(user_id);

CREATE INDEX idx_ai_sources_query
    ON ai_query_sources(query_id);

CREATE INDEX idx_ai_sources_document
    ON ai_query_sources(document_id);
-- 1.ROLES (1=ADMIN, 2=LECTURER, 3=STUDENT)
INSERT INTO roles(role_name) VALUES ('ADMIN'), ('LECTURER'), ('STUDENT');
 
-- 2. DEPARTMENTS (1=CNTT, 2=Kinh te, 3=Ngoai ngu)
INSERT INTO departments(department_name) VALUES
 ('Cong nghe thong tin'),
 ('Kinh te'),
 ('Ngoai ngu');
 
-- 3. CLASSES (6 = lop bi khoa)
INSERT INTO classes(class_name, department_id, is_locked) VALUES
 ('CNTT-K1', 1, FALSE),   -- 1
 ('CNTT-K2', 1, FALSE),   -- 2
 ('KT-K1',   2, FALSE),   -- 3
 ('KT-K2',   2, FALSE),   -- 4
 ('NN-K1',   3, FALSE),   -- 5
 ('CNTT-K0', 1, TRUE);    -- 6 (lop cu, da khoa)
 
-- 4. SUBJECTS
INSERT INTO subjects(subject_name, department_id) VALUES
 ('Lap trinh Java',          1),   -- 1
 ('Co so du lieu',           1),   -- 2
 ('Mang may tinh',           1),   -- 3
 ('Kinh te vi mo',           2),   -- 4
 ('Ke toan dai cuong',       2),   -- 5
 ('Tieng Anh chuyen nganh',  3),   -- 6
 ('Ngu phap co ban',         3);   -- 7
 
-- 5. USERS
-- 1 admin | 2 admin02 | 3 gv01 | 4 gv02 | 5 gv03 | 6 gv04
-- 7-9 sv01-03 (lop 1) | 10-11 sv04-05 (lop 2) | 12-13 sv06-07 (lop 3)
-- 14 sv08 (lop 4) | 15-16 sv09-10 (lop 5) | 17 sv11 (lop 6 - bi khoa)
INSERT INTO users(username, password_hash, full_name, role_id, department_id, class_id) VALUES
 ('admin',   'hash_admin', 'Quan tri vien',      1, NULL, NULL),
 ('admin02', 'hash_admin', 'Quan tri vien 2',    1, NULL, NULL),
 ('gv01',    'hash_gv',    'Nguyen Van An',      2, 1, NULL),
 ('gv02',    'hash_gv',    'Tran Thi Binh',      2, 1, NULL),
 ('gv03',    'hash_gv',    'Le Van Cuong',       2, 2, NULL),
 ('gv04',    'hash_gv',    'Pham Thi Dung',      2, 3, NULL),
 ('sv01',    'hash_sv',    'Hoang Minh Khoa',    3, 1, 1),
 ('sv02',    'hash_sv',    'Vu Thanh Lam',       3, 1, 1),
 ('sv03',    'hash_sv',    'Dang Quoc Minh',     3, 1, 1),
 ('sv04',    'hash_sv',    'Bui Thu Nga',        3, 1, 2),
 ('sv05',    'hash_sv',    'Do Van Phuc',        3, 1, 2),
 ('sv06',    'hash_sv',    'Ngo Thi Quynh',      3, 2, 3),
 ('sv07',    'hash_sv',    'Duong Van Son',      3, 2, 3),
 ('sv08',    'hash_sv',    'Ly Thi Thao',        3, 2, 4),
 ('sv09',    'hash_sv',    'Trinh Van Uy',       3, 3, 5),
 ('sv10',    'hash_sv',    'Mai Thi Van',        3, 3, 5),
 ('sv11',    'hash_sv',    'Cao Van Xuan',       3, 1, 6);
 
-- 6. FOLDERS (folder thuoc dung subject; folder con cung subject voi cha)
INSERT INTO folders(folder_name, subject_id, parent_folder_id, created_by) VALUES
 ('Bai giang',          1, NULL, 3),   -- 1
 ('Bai tap',            1, NULL, 3),   -- 2
 ('Tuan 1',             1, 1,    3),   -- 3
 ('Tuan 2',             1, 1,    3),   -- 4
 ('Bai giang',          2, NULL, 4),   -- 5
 ('De thi',             2, NULL, 4),   -- 6
 ('Chuong 1',           2, 5,    4),   -- 7
 ('Bai giang',          3, NULL, 4),   -- 8
 ('Bai giang',          4, NULL, 5),   -- 9
 ('Bai tap',            4, NULL, 5),   -- 10
 ('Tai lieu tham khao', 5, NULL, 5),   -- 11
 ('Bai giang',          6, NULL, 6);   -- 12
 
-- 7. DOCUMENTS (view_count / download_count cap nhat o buoc 13)
INSERT INTO documents(title, description, subject_id, folder_id, uploader_id, status, is_public, approved_by, approved_at) VALUES
 ('Slide Java tuan 1',        'Gioi thieu Java va cai dat moi truong', 1, 3,    3, 'APPROVED', TRUE,  1, now() - interval '20 days'),  -- 1
 ('Slide Java tuan 2',        'Bien, kieu du lieu, toan tu',           1, 4,    3, 'APPROVED', FALSE, 1, now() - interval '18 days'),  -- 2
 ('Bai tap Java OOP',         'Bai tap lap trinh huong doi tuong',     1, 2,    3, 'APPROVED', FALSE, 2, now() - interval '15 days'),  -- 3
 ('De cuong Java',            'De cuong chi tiet hoc phan',            1, 1,    3, 'PENDING',  FALSE, NULL, NULL),                     -- 4
 ('Bai giang CSDL chuong 1',  'Tong quan he co so du lieu',            2, 7,    4, 'APPROVED', TRUE,  1, now() - interval '25 days'),  -- 5
 ('Bai giang SQL nang cao',   'JOIN, subquery, window function',       2, 5,    4, 'APPROVED', FALSE, 1, now() - interval '12 days'),  -- 6
 ('De thi CSDL 2024',         'De thi cu',                             2, 6,    4, 'REJECTED', FALSE, NULL, NULL),                     -- 7
 ('Bai giang Mang may tinh',  'Mo hinh OSI va TCP/IP',                 3, 8,    4, 'APPROVED', FALSE, 2, now() - interval '10 days'),  -- 8
 ('Giao trinh Kinh te vi mo', 'Cung cau va thi truong',                4, 9,    5, 'APPROVED', TRUE,  1, now() - interval '30 days'),  -- 9
 ('Bai tap Kinh te vi mo',    'Bai tap chuong 1-3',                    4, 10,   5, 'PENDING',  FALSE, NULL, NULL),                     -- 10
 ('Tai lieu ke toan',         'Nguyen ly ke toan co ban',              5, 11,   5, 'APPROVED', FALSE, 2, now() - interval '8 days'),   -- 11
 ('English for IT',           'Tu vung tieng Anh nganh CNTT',          6, 12,   6, 'APPROVED', TRUE,  1, now() - interval '5 days'),   -- 12
 ('Ngu phap co ban',          'Cac thi trong tieng Anh',               7, NULL, 6, 'PENDING',  FALSE, NULL, NULL),                     -- 13
 ('Ghi chu Java cua SV',      'Sinh vien nop dong gop',                1, NULL, 7, 'PENDING',  FALSE, NULL, NULL);                     -- 14
 
-- 8. DOCUMENT_VERSIONS (doc 1 co 2 ban, doc 6 co 3 ban)
INSERT INTO document_versions(document_id, file_path, version_number, updated_by, change_summary) VALUES
 (1,  '/storage/java/slide_tuan1_v1.pdf',   1, 3, 'Ban dau'),
 (1,  '/storage/java/slide_tuan1_v2.pdf',   2, 3, 'Sua loi chinh ta'),
 (2,  '/storage/java/slide_tuan2_v1.pdf',   1, 3, 'Ban dau'),
 (3,  '/storage/java/bai_tap_oop_v1.docx',  1, 3, 'Ban dau'),
 (4,  '/storage/java/de_cuong_v1.pdf',      1, 3, 'Ban dau'),
 (5,  '/storage/csdl/chuong1_v1.pdf',       1, 4, 'Ban dau'),
 (6,  '/storage/csdl/sql_nang_cao_v1.pdf',  1, 4, 'Ban dau'),
 (6,  '/storage/csdl/sql_nang_cao_v2.pdf',  2, 4, 'Them vi du window function'),
 (6,  '/storage/csdl/sql_nang_cao_v3.pdf',  3, 4, 'Bo sung bai tap'),
 (7,  '/storage/csdl/de_thi_2024_v1.pdf',   1, 4, 'Ban dau'),
(8,  '/storage/mang/osi_tcpip_v1.pptx',    1, 4, 'Ban dau'),
 (9,  '/storage/ktvm/giao_trinh_v1.pdf',    1, 5, 'Ban dau'),
 (10, '/storage/ktvm/bai_tap_v1.docx',      1, 5, 'Ban dau'),
 (11, '/storage/kt/nguyen_ly_v1.pdf',       1, 5, 'Ban dau'),
 (12, '/storage/nn/english_it_v1.pdf',      1, 6, 'Ban dau'),
 (13, '/storage/nn/ngu_phap_v1.pdf',        1, 6, 'Ban dau'),
 (14, '/storage/java/ghi_chu_sv_v1.pdf',    1, 7, 'Ban dau');
 
-- 9. TAGS + DOCUMENT_TAGS
INSERT INTO tags(tag_name) VALUES
 ('java'), ('oop'), ('sql'), ('csdl'), ('mang'),
 ('kinh-te'), ('tieng-anh'), ('bai-tap'), ('de-thi'), ('slide');
 
INSERT INTO document_tags(document_id, tag_id) VALUES
 (1, 1), (1, 10),
 (2, 1), (2, 10),
 (3, 1), (3, 2), (3, 8),
 (4, 1),
 (5, 4), (5, 3),
 (6, 3), (6, 4),
 (7, 4), (7, 9),
 (8, 5), (8, 10),
 (9, 6),
 (10, 6), (10, 8),
 (11, 6),
 (12, 7),
 (13, 7);
 
-- 10. DOCUMENT_PERMISSIONS (khong co dong nao vi pham can_view/can_download)
INSERT INTO document_permissions(document_id, permission_type, department_id, class_id, user_id, can_view, can_download, can_edit) VALUES
 (2,  'DEPARTMENT', 1,    NULL, NULL, TRUE,  TRUE,  FALSE),  -- ca khoa CNTT xem + tai
 (2,  'USER',       NULL, NULL, 10,   TRUE,  FALSE, FALSE),  -- sv04 chi xem
 (3,  'CLASS',      NULL, 1,    NULL, TRUE,  TRUE,  FALSE),  -- lop CNTT-K1
 (3,  'CLASS',      NULL, 2,    NULL, TRUE,  FALSE, FALSE),  -- lop CNTT-K2 chi xem
 (3,  'USER',       NULL, NULL, 4,    TRUE,  TRUE,  TRUE),   -- gv02 duoc sua
 (6,  'CLASS',      NULL, 1,    NULL, TRUE,  TRUE,  FALSE),
 (6,  'CLASS',      NULL, 2,    NULL, TRUE,  TRUE,  FALSE),
 (6,  'USER',       NULL, NULL, 17,   FALSE, FALSE, FALSE), -- sv11 (lop khoa) bi chan
 (8,  'DEPARTMENT', 1,    NULL, NULL, TRUE,  TRUE,  FALSE),
 (11, 'DEPARTMENT', 2,    NULL, NULL, TRUE,  TRUE,  FALSE),
 (11, 'USER',       NULL, NULL, 5,    TRUE,  TRUE,  TRUE);
 
-- 11. DOCUMENT_EMBEDDINGS (vector 3 chieu, chi de demo)
INSERT INTO document_embeddings(document_id, chunk_index, chunk_text, embedding_array) VALUES
 (1,  0, 'Java la ngon ngu lap trinh huong doi tuong, chay tren JVM',        ARRAY[0.10, 0.20, 0.30]),  -- 1
 (1,  1, 'Cai dat JDK va cau hinh bien moi truong PATH, JAVA_HOME',          ARRAY[0.12, 0.18, 0.33]),  -- 2
 (2,  0, 'Cac kieu du lieu nguyen thuy: int, double, boolean, char',         ARRAY[0.15, 0.25, 0.28]),  -- 3
 (5,  0, 'Co so du lieu la tap hop du lieu co to chuc, luu tru tren may',    ARRAY[0.80, 0.10, 0.05]),  -- 4
 (5,  1, 'He quan tri CSDL quan he gom bang, khoa chinh va khoa ngoai',      ARRAY[0.78, 0.12, 0.07]),  -- 5
 (6,  0, 'INNER JOIN tra ve cac dong co gia tri khop o ca hai bang',         ARRAY[0.75, 0.20, 0.10]),  -- 6
 (9,  0, 'Cung la luong hang hoa nguoi mua san sang mua o moi muc gia',      ARRAY[0.05, 0.90, 0.10]),  -- 7
 (12, 0, 'Database nghia la co so du lieu, server nghia la may chu',         ARRAY[0.20, 0.10, 0.85]);  -- 8
 
-- 12. AI_QUERIES + AI_QUERY_SOURCES
INSERT INTO ai_queries(user_id, query_text, ai_response, created_at) VALUES
 (7,  'Java la gi?',                     'Java la ngon ngu lap trinh huong doi tuong, chay tren may ao JVM.',   now() - interval '6 days'),   -- 1
 (8,  'Khoa chinh khac khoa ngoai the nao?', 'Khoa chinh dinh danh duy nhat mot dong, khoa ngoai tham chieu den khoa chinh bang khac.', now() - interval '5 days'), -- 2
 (10, 'INNER JOIN hoat dong ra sao?',    'INNER JOIN chi tra ve cac dong khop dieu kien o ca hai bang.',        now() - interval '4 days'),   -- 3
 (12, 'Cung cau la gi?',                 'Cung la luong hang hoa ban ra, cau la luong hang hoa mua vao theo gia.', now() - interval '3 days'), -- 4
 (15, 'Database dich sang tieng Viet?',  'Database dich la co so du lieu.',                                     now() - interval '2 days'),   -- 5
 (7,  'Cach cai dat JDK?',               'Tai JDK, cai dat roi dat bien moi truong JAVA_HOME va PATH.',         now() - interval '1 day');    -- 6
 
INSERT INTO ai_query_sources(query_id, document_id, embedding_id) VALUES
 (1, 1, 1),
 (2, 5, 5),
 (2, 5, 4),
 (3, 6, 6),
 (4, 9, 7),
 (5, 12, 8),
 (6, 1, 2),
 (6, 1, 1);
 
-- 13. ACTIVITY LOGS
-- 13a. Cac su kien quan trong (audit)
INSERT INTO document_activity_logs(document_id, user_id, action, description, created_at) VALUES
 (1,  3, 'CREATE',            'Upload Slide Java tuan 1',            now() - interval '21 days'),
 (1,  1, 'APPROVE',           'Admin duyet tai lieu',                now() - interval '20 days'),
 (1,  3, 'UPDATE',            'Upload version 2',                    now() - interval '19 days'),
 (2,  3, 'CREATE',            'Upload Slide Java tuan 2',            now() - interval '19 days'),
 (2,  1, 'APPROVE',           'Admin duyet tai lieu',                now() - interval '18 days'),
 (2,  3, 'CHANGE_PERMISSION', 'Cap quyen cho khoa CNTT',             now() - interval '17 days'),
 (3,  3, 'CREATE',            'Upload Bai tap Java OOP',             now() - interval '16 days'),
 (3,  2, 'APPROVE',           'Admin02 duyet tai lieu',              now() - interval '15 days'),
 (3,  3, 'ADD_TAG',           'Them tag oop',                        now() - interval '15 days'),
 (3,  3, 'CHANGE_PERMISSION', 'Cap quyen cho lop CNTT-K1, CNTT-K2', now() - interval '14 days'),
 (4,  3, 'CREATE',            'Upload De cuong Java',                now() - interval '2 days'),
 (5,  4, 'CREATE',            'Upload Bai giang CSDL chuong 1',      now() - interval '26 days'),
 (5,  1, 'APPROVE',           'Admin duyet tai lieu',                now() - interval '25 days'),
 (6,  4, 'CREATE',            'Upload Bai giang SQL nang cao',       now() - interval '14 days'),
 (6,  1, 'APPROVE',           'Admin duyet tai lieu',                now() - interval '12 days'),
 (6,  4, 'UPDATE',            'Upload version 2',                    now() - interval '9 days'),
 (6,  4, 'UPDATE',            'Upload version 3',                    now() - interval '4 days'),
(6,  4, 'REMOVE_TAG',        'Go tag de-thi',                       now() - interval '4 days'),
 (7,  4, 'CREATE',            'Upload De thi CSDL 2024',             now() - interval '11 days'),
 (7,  1, 'REJECT',            'Ly do: de thi cu, khong duoc phep chia se', now() - interval '10 days'),
 (8,  4, 'CREATE',            'Upload Bai giang Mang may tinh',      now() - interval '11 days'),
 (8,  2, 'APPROVE',           'Admin02 duyet tai lieu',              now() - interval '10 days'),
 (9,  5, 'CREATE',            'Upload Giao trinh Kinh te vi mo',     now() - interval '31 days'),
 (9,  1, 'APPROVE',           'Admin duyet tai lieu',                now() - interval '30 days'),
 (10, 5, 'CREATE',            'Upload Bai tap Kinh te vi mo',        now() - interval '3 days'),
 (11, 5, 'CREATE',            'Upload Tai lieu ke toan',             now() - interval '9 days'),
 (11, 2, 'APPROVE',           'Admin02 duyet tai lieu',              now() - interval '8 days'),
 (12, 6, 'CREATE',            'Upload English for IT',               now() - interval '6 days'),
 (12, 1, 'APPROVE',           'Admin duyet tai lieu',                now() - interval '5 days'),
 (13, 6, 'CREATE',            'Upload Ngu phap co ban',              now() - interval '1 day'),
 (14, 7, 'CREATE',            'Sinh vien nop ghi chu Java',          now() - interval '1 day');
 
-- 13b. 300 luot VIEW ngau nhien tren cac tai lieu da duyet, boi sv01..sv10
INSERT INTO document_activity_logs(document_id, user_id, action, created_at)
SELECT (ARRAY[1,2,3,5,6,8,9,11,12])[1 + floor(random() * 9)::int],
       7 + floor(random() * 10)::int,
       'VIEW',
       now() - random() * interval '30 days'
FROM generate_series(1, 300);
 
-- 13c. 80 luot DOWNLOAD ngau nhien
INSERT INTO document_activity_logs(document_id, user_id, action, created_at)
SELECT (ARRAY[1,2,3,5,6,8,9,11,12])[1 + floor(random() * 9)::int],
       7 + floor(random() * 10)::int,
       'DOWNLOAD',
       now() - random() * interval '30 days'
FROM generate_series(1, 80);
 
-- 13d. Dong bo view_count / download_count tu log
UPDATE documents d
SET view_count     = (SELECT COUNT(*) FROM document_activity_logs l WHERE l.document_id = d.document_id AND l.action = 'VIEW'),
    download_count = (SELECT COUNT(*) FROM document_activity_logs l WHERE l.document_id = d.document_id AND l.action = 'DOWNLOAD');
