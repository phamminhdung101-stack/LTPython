// Mock Documents Data
const documents = [
    {
        id: 1,
        title: 'Giáo trình Cấu trúc dữ liệu và giải thuật',
        type: 'book',
        typeLabel: 'Giáo trình',
        typeClass: 'bg-blue-100 text-blue-800',
        icon: 'fa-file-pdf',
        iconColor: 'text-red-500',
        desc: 'Tài liệu chính thức dành cho sinh viên CNTT học phần CTDL&GT.',
        subjectCode: 'IT202',
        downloads: '1.2k',
        uploaderName: 'Thầy Nguyễn Văn A',
        uploaderType: 'GV',
        time: '2 ngày trước',
        faculty: 'CNTT'
    },
    {
        id: 2,
        title: 'Slide Chương 1 - 5: Kinh tế vi mô',
        type: 'slide',
        typeLabel: 'Slide Bài giảng',
        typeClass: 'bg-orange-100 text-orange-800',
        icon: 'fa-file-powerpoint',
        iconColor: 'text-orange-500',
        desc: 'Tổng hợp toàn bộ slide bài giảng trên lớp kèm ví dụ minh họa.',
        subjectCode: 'ECO101',
        downloads: '856',
        uploaderName: 'Cô Lê Thị B',
        uploaderType: 'Admin',
        time: '5 ngày trước',
        faculty: 'KT'
    },
    {
        id: 3,
        title: 'Đề thi cuối kỳ Nhập môn lập trình (2022-2023)',
        type: 'exam',
        typeLabel: 'Đề thi',
        typeClass: 'bg-red-100 text-red-800',
        icon: 'fa-file-word',
        iconColor: 'text-blue-600',
        desc: 'Bộ 3 mã đề thi cuối kỳ có đáp án chi tiết.',
        subjectCode: 'IT101',
        downloads: '2.1k',
        uploaderName: 'SV_K65',
        uploaderType: 'SV',
        time: '1 tuần trước',
        faculty: 'CNTT'
    },
    {
        id: 4,
        title: 'Bản tóm tắt Kinh tế vi mô thi giữa kỳ',
        type: 'reference',
        typeLabel: 'Tham khảo',
        typeClass: 'bg-green-100 text-green-800',
        icon: 'fa-file-alt',
        iconColor: 'text-green-500',
        desc: 'Tài liệu ôn thi tóm tắt các công thức quan trọng.',
        subjectCode: 'ECO101',
        downloads: '3.4k',
        uploaderName: 'Nhóm học tập KT',
        uploaderType: 'SV',
        time: '2 tháng trước',
        faculty: 'KT'
    }
];

function renderDocumentList() {
    const grid = document.getElementById('documentsGrid');
    if(!grid) return; // Only run on list page

    // Get filter states
    const query = (document.getElementById('navSearch')?.value || '').toLowerCase();
    
    // Checkboxes
    const checkedSubjects = Array.from(document.querySelectorAll('.subject-filter:checked')).map(cb => cb.value);
    const checkedTypes = Array.from(document.querySelectorAll('.type-filter:checked')).map(cb => cb.value);
    
    // Select
    const faculty = document.getElementById('facultyFilter')?.value;

    let filtered = documents;

    // Apply filters logic
    if (query) {
        filtered = filtered.filter(d => d.title.toLowerCase().includes(query) || d.subjectCode.toLowerCase().includes(query));
    }
    
    if (checkedSubjects.length > 0) {
        filtered = filtered.filter(d => checkedSubjects.includes(d.subjectCode));
    }

    if (checkedTypes.length > 0) {
        filtered = filtered.filter(d => checkedTypes.includes(d.type));
    }

    if (faculty) {
        filtered = filtered.filter(d => d.faculty === faculty);
    }

    // Render
    document.getElementById('resultCount').textContent = filtered.length;
    grid.innerHTML = '';

    if(filtered.length === 0) {
        grid.innerHTML = `<div class="col-span-1 sm:col-span-2 text-center py-12 text-gray-500">
            <i class="fas fa-folder-open text-4xl mb-3 text-gray-300"></i>
            <p>Không tìm thấy tài liệu nào phù hợp với bộ lọc.</p>
        </div>`;
        return;
    }

    filtered.forEach(doc => {
        grid.innerHTML += `
            <a href="document_detail.html?id=${doc.id}" class="doc-card bg-white border border-gray-200 rounded-xl overflow-hidden flex flex-col h-full group">
                <div class="p-5 flex-grow">
                    <div class="flex justify-between items-start mb-4">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${doc.typeClass}">
                            ${doc.typeLabel}
                        </span>
                        <i class="fas ${doc.icon} ${doc.iconColor} text-2xl opacity-80 group-hover:opacity-100 transition-opacity"></i>
                    </div>
                    <h3 class="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-brand-600 transition-colors">${doc.title}</h3>
                    <p class="text-sm text-gray-500 mb-4 line-clamp-2">${doc.desc}</p>
                    <div class="flex items-center text-xs text-gray-500 gap-4 mt-auto">
                        <span class="flex items-center gap-1"><i class="fas fa-book-open"></i> ${doc.subjectCode}</span>
                        <span class="flex items-center gap-1"><i class="fas fa-download"></i> ${doc.downloads}</span>
                    </div>
                </div>
                <div class="bg-gray-50 px-5 py-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                    <div class="flex items-center gap-2">
                        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(doc.uploaderType)}&background=random" class="w-5 h-5 rounded-full" alt="User">
                        <span>${doc.uploaderName}</span>
                    </div>
                    <span>${doc.time}</span>
                </div>
            </a>
        `;
    });
}

function applyFilters() {
    renderDocumentList();
}

function resetFilters() {
    document.querySelectorAll('.subject-filter').forEach(cb => cb.checked = false);
    document.querySelectorAll('.type-filter').forEach(cb => cb.checked = false);
    if(document.getElementById('facultyFilter')) document.getElementById('facultyFilter').value = '';
    renderDocumentList();
}

// Simple Toast for Student View
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if(!container) return;

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

// If URL has search query, simulate it (for demo purposes)
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const q = urlParams.get('q');
    const type = urlParams.get('type');
    
    if(q && document.getElementById('navSearch')) {
        document.getElementById('navSearch').value = q;
    }
    
    if(type) {
        document.querySelectorAll('.type-filter').forEach(cb => cb.checked = false);
        const targetCb = document.querySelector(`.type-filter[value="${type}"]`);
        if(targetCb) targetCb.checked = true;
    }
});

