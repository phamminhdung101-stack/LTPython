// Mock Data
let faculties = [
    { id: 1, code: 'CNTT', name: 'Công nghệ thông tin', dean: 'TS. Nguyễn Văn A', desc: 'Đào tạo kỹ sư CNTT' },
    { id: 2, code: 'KT', name: 'Kinh tế', dean: 'PGS. TS Lê Thị B', desc: 'Đào tạo cử nhân kinh tế' },
    { id: 3, code: 'NN', name: 'Ngoại ngữ', dean: 'TS. Trần Văn C', desc: 'Đào tạo ngôn ngữ học' }
];

let classes = [
    { id: 1, code: 'K65-CA', name: 'Khoa học máy tính A', facultyId: 1, size: 60 },
    { id: 2, code: 'K65-CB', name: 'Khoa học máy tính B', facultyId: 1, size: 55 },
    { id: 3, code: 'K65-KT1', name: 'Kinh tế quốc tế 1', facultyId: 2, size: 70 }
];

let subjects = [
    { id: 1, code: 'IT101', name: 'Nhập môn lập trình', credits: 3, facultyId: 1, desc: 'Học C/C++ cơ bản' },
    { id: 2, code: 'IT202', name: 'Cấu trúc dữ liệu', credits: 3, facultyId: 1, desc: 'CTDL và giải thuật' },
    { id: 3, code: 'ECO101', name: 'Kinh tế vi mô', credits: 2, facultyId: 2, desc: 'Cơ bản về kinh tế' }
];

let currentDelete = { type: null, id: null };

// Init
document.addEventListener('DOMContentLoaded', () => {
    updateFacultySelects();
    renderFaculties();
    renderClasses();
    renderSubjects();
    setupFilters();
});

// Tab Switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.add('hidden');
        el.classList.remove('block');
    });
    // Remove active styles
    document.querySelectorAll('nav button').forEach(el => {
        el.classList.remove('border-primary', 'text-primary');
        el.classList.add('border-transparent', 'text-gray-500');
    });

    // Show target tab
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
    document.getElementById(`content-${tabName}`).classList.add('block');
    
    // Add active styles
    const activeTab = document.getElementById(`tab-${tabName}`);
    activeTab.classList.remove('border-transparent', 'text-gray-500');
    activeTab.classList.add('border-primary', 'text-primary');
}

// Helpers
function getFacultyName(id) {
    const f = faculties.find(x => x.id == id);
    return f ? f.name : '-';
}

function updateFacultySelects() {
    const selects = ['filterClassFaculty', 'classFaculty', 'filterSubjectFaculty', 'subjectFaculty'];
    selects.forEach(id => {
        const el = document.getElementById(id);
        const isFilter = id.startsWith('filter');
        el.innerHTML = isFilter ? '<option value="">Tất cả khoa</option>' : '';
        
        faculties.forEach(f => {
            el.innerHTML += `<option value="${f.id}">${f.name}</option>`;
        });
    });
}

// Render Data
function renderFaculties() {
    const search = document.getElementById('searchFaculty').value.toLowerCase();
    const filtered = faculties.filter(f => f.code.toLowerCase().includes(search) || f.name.toLowerCase().includes(search));
    
    const tbody = document.getElementById('facultyTableBody');
    tbody.innerHTML = '';
    
    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">Không tìm thấy khoa nào.</td></tr>`;
        return;
    }

    filtered.forEach(f => {
        tbody.innerHTML += `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${f.code}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${f.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${f.dean || '-'}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${f.desc || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onclick="openModal('faculty', 'edit', ${f.id})" class="text-blue-600 hover:text-blue-900 mx-2"><i class="fas fa-pen"></i></button>
                    <button onclick="promptDelete('faculty', ${f.id})" class="text-red-600 hover:text-red-900"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    });
}

function renderClasses() {
    const search = document.getElementById('searchClass').value.toLowerCase();
    const filterFac = document.getElementById('filterClassFaculty').value;
    
    const filtered = classes.filter(c => {
        const matchSearch = c.code.toLowerCase().includes(search) || c.name.toLowerCase().includes(search);
        const matchFac = !filterFac || c.facultyId == filterFac;
        return matchSearch && matchFac;
    });

    const tbody = document.getElementById('classTableBody');
    tbody.innerHTML = '';
    
    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">Không tìm thấy lớp nào.</td></tr>`;
        return;
    }

    filtered.forEach(c => {
        tbody.innerHTML += `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${c.code}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${c.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${getFacultyName(c.facultyId)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${c.size || 0}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onclick="openModal('class', 'edit', ${c.id})" class="text-blue-600 hover:text-blue-900 mx-2"><i class="fas fa-pen"></i></button>
                    <button onclick="promptDelete('class', ${c.id})" class="text-red-600 hover:text-red-900"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    });
}

function renderSubjects() {
    const search = document.getElementById('searchSubject').value.toLowerCase();
    const filterFac = document.getElementById('filterSubjectFaculty').value;
    
    const filtered = subjects.filter(s => {
        const matchSearch = s.code.toLowerCase().includes(search) || s.name.toLowerCase().includes(search);
        const matchFac = !filterFac || s.facultyId == filterFac;
        return matchSearch && matchFac;
    });

    const tbody = document.getElementById('subjectTableBody');
    tbody.innerHTML = '';

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">Không tìm thấy môn học nào.</td></tr>`;
        return;
    }

    filtered.forEach(s => {
        tbody.innerHTML += `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${s.code}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${s.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${s.credits}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${getFacultyName(s.facultyId)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onclick="openModal('subject', 'edit', ${s.id})" class="text-blue-600 hover:text-blue-900 mx-2"><i class="fas fa-pen"></i></button>
                    <button onclick="promptDelete('subject', ${s.id})" class="text-red-600 hover:text-red-900"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    });
}

// Setup Filters
function setupFilters() {
    document.getElementById('searchFaculty').addEventListener('input', renderFaculties);
    
    document.getElementById('searchClass').addEventListener('input', renderClasses);
    document.getElementById('filterClassFaculty').addEventListener('change', renderClasses);
    
    document.getElementById('searchSubject').addEventListener('input', renderSubjects);
    document.getElementById('filterSubjectFaculty').addEventListener('change', renderSubjects);
}

// Modal Logic
function openModal(type, action, id = null) {
    const modal = document.getElementById(`${type}Modal`);
    const form = document.getElementById(`${type}Form`);
    const title = document.getElementById(`${type}ModalTitle`);
    
    resetErrors(type);
    
    if (action === 'add') {
        title.textContent = `Thêm mới ${type === 'faculty' ? 'Khoa' : type === 'class' ? 'Lớp/Khóa' : 'Môn học'}`;
        form.reset();
        document.getElementById(`${type}Id`).value = '';
    } else {
        title.textContent = `Sửa thông tin`;
        fillFormData(type, id);
    }
    
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.querySelector('.transform').classList.remove('scale-95', 'opacity-0');
        modal.querySelector('.transform').classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.querySelector('.transform').classList.remove('scale-100', 'opacity-100');
    modal.querySelector('.transform').classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}

function fillFormData(type, id) {
    document.getElementById(`${type}Id`).value = id;
    if (type === 'faculty') {
        const item = faculties.find(x => x.id === id);
        document.getElementById('facultyCode').value = item.code;
        document.getElementById('facultyName').value = item.name;
        document.getElementById('facultyDean').value = item.dean || '';
        document.getElementById('facultyDesc').value = item.desc || '';
    } else if (type === 'class') {
        const item = classes.find(x => x.id === id);
        document.getElementById('classCode').value = item.code;
        document.getElementById('className').value = item.name;
        document.getElementById('classFaculty').value = item.facultyId;
        document.getElementById('classSize').value = item.size || '';
    } else if (type === 'subject') {
        const item = subjects.find(x => x.id === id);
        document.getElementById('subjectCode').value = item.code;
        document.getElementById('subjectName').value = item.name;
        document.getElementById('subjectCredits').value = item.credits;
        document.getElementById('subjectFaculty').value = item.facultyId;
        document.getElementById('subjectDesc').value = item.desc || '';
    }
}

// Save Logic
function saveFaculty() {
    if (!validate('faculty', ['facultyCode', 'facultyName'])) return;
    
    const id = document.getElementById('facultyId').value;
    const data = {
        code: document.getElementById('facultyCode').value.trim(),
        name: document.getElementById('facultyName').value.trim(),
        dean: document.getElementById('facultyDean').value.trim(),
        desc: document.getElementById('facultyDesc').value.trim()
    };
    
    if (id) {
        const idx = faculties.findIndex(x => x.id == id);
        faculties[idx] = { ...faculties[idx], ...data };
        showToast('Cập nhật Khoa thành công');
    } else {
        faculties.push({ id: Date.now(), ...data });
        showToast('Thêm Khoa thành công');
    }
    updateFacultySelects();
    closeModal('facultyModal');
    renderFaculties();
}

function saveClass() {
    if (!validate('class', ['classCode', 'className', 'classFaculty'])) return;
    
    const id = document.getElementById('classId').value;
    const data = {
        code: document.getElementById('classCode').value.trim(),
        name: document.getElementById('className').value.trim(),
        facultyId: document.getElementById('classFaculty').value,
        size: document.getElementById('classSize').value
    };
    
    if (id) {
        const idx = classes.findIndex(x => x.id == id);
        classes[idx] = { ...classes[idx], ...data };
        showToast('Cập nhật Lớp thành công');
    } else {
        classes.push({ id: Date.now(), ...data });
        showToast('Thêm Lớp thành công');
    }
    closeModal('classModal');
    renderClasses();
}

function saveSubject() {
    if (!validate('subject', ['subjectCode', 'subjectName', 'subjectCredits', 'subjectFaculty'])) return;
    
    const id = document.getElementById('subjectId').value;
    const data = {
        code: document.getElementById('subjectCode').value.trim(),
        name: document.getElementById('subjectName').value.trim(),
        credits: document.getElementById('subjectCredits').value,
        facultyId: document.getElementById('subjectFaculty').value,
        desc: document.getElementById('subjectDesc').value.trim()
    };
    
    if (id) {
        const idx = subjects.findIndex(x => x.id == id);
        subjects[idx] = { ...subjects[idx], ...data };
        showToast('Cập nhật Môn học thành công');
    } else {
        subjects.push({ id: Date.now(), ...data });
        showToast('Thêm Môn học thành công');
    }
    closeModal('subjectModal');
    renderSubjects();
}

// Validation
function validate(type, fields) {
    let isValid = true;
    resetErrors(type);
    fields.forEach(field => {
        const el = document.getElementById(field);
        if (!el.value.trim()) {
            el.classList.add('border-red-500');
            document.getElementById(`err-${field}`).classList.remove('hidden');
            isValid = false;
        }
    });
    return isValid;
}

function resetErrors(type) {
    const form = document.getElementById(`${type}Form`);
    form.querySelectorAll('input, select').forEach(el => el.classList.remove('border-red-500'));
    form.querySelectorAll('p[id^="err-"]').forEach(el => el.classList.add('hidden'));
}

// Delete Logic
function promptDelete(type, id) {
    currentDelete = { type, id };
    const modal = document.getElementById('deleteModal');
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.querySelector('.transform').classList.remove('scale-95', 'opacity-0');
        modal.querySelector('.transform').classList.add('scale-100', 'opacity-100');
    }, 10);
}

function confirmDelete() {
    const { type, id } = currentDelete;
    if (type === 'faculty') {
        faculties = faculties.filter(x => x.id !== id);
        updateFacultySelects();
        renderFaculties();
        renderClasses(); // May have orphaned classes
        renderSubjects(); // May have orphaned subjects
    } else if (type === 'class') {
        classes = classes.filter(x => x.id !== id);
        renderClasses();
    } else if (type === 'subject') {
        subjects = subjects.filter(x => x.id !== id);
        renderSubjects();
    }
    
    closeModal('deleteModal');
    showToast('Xóa dữ liệu thành công', 'success');
}

// Toast
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    
    let icon = 'fa-check-circle';
    let iconColor = 'text-green-500';
    let borderColor = 'border-l-4 border-green-500';

    toast.className = `flex items-center w-full max-w-xs p-4 space-x-3 text-gray-700 bg-white rounded-lg shadow-lg border-y border-r border-gray-100 ${borderColor} transform transition-all duration-300 translate-x-full opacity-0 pointer-events-auto`;
    
    toast.innerHTML = `
        <i class="fas ${icon} ${iconColor} text-xl"></i>
        <div class="text-sm font-medium flex-1">${message}</div>
        <button class="text-gray-400 hover:text-gray-900 transition-colors" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
        toast.classList.add('translate-x-0', 'opacity-100');
    });

    setTimeout(() => {
        toast.classList.remove('translate-x-0', 'opacity-100');
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

