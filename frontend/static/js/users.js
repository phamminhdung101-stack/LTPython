// Mock Data cho Quản lý người dùng
let users = [
    {
        id: 1,
        fullName: 'Nguyễn Văn Admin',
        username: 'admin',
        email: 'admin@school.edu.vn',
        role: 'ADMIN',
        faculty: '',
        cohort: '',
        status: 'ACTIVE',
        createdAt: '2023-09-01'
    },
    {
        id: 2,
        fullName: 'Trần Thị Giảng Viên',
        username: 'gv_tranthi',
        email: 'tranthi@school.edu.vn',
        role: 'LECTURER',
        faculty: 'CNTT',
        cohort: '',
        status: 'ACTIVE',
        createdAt: '2023-10-15'
    },
    {
        id: 3,
        fullName: 'Lê Sinh Viên',
        username: 'sv_lesinhvien',
        email: 'lesinhvien@student.school.edu.vn',
        role: 'STUDENT',
        faculty: 'KT',
        cohort: 'K65-CA',
        status: 'INACTIVE',
        createdAt: '2023-12-05'
    }
];

let currentUserIdToDelete = null;

// Khởi tạo khi load trang
document.addEventListener('DOMContentLoaded', () => {
    renderUsers(users);
    setupEventListeners();
});

// Thiết lập các sự kiện lắng nghe (Filters, Searches)
function setupEventListeners() {
    const filterInputs = ['globalSearch', 'filterSearch', 'filterRole', 'filterFaculty', 'filterStatus'];
    filterInputs.forEach(id => {
        document.getElementById(id).addEventListener('input', applyFilters);
        document.getElementById(id).addEventListener('change', applyFilters);
    });
}

// Render dữ liệu ra bảng
function renderUsers(data) {
    const tbody = document.getElementById('userTableBody');
    tbody.innerHTML = '';

    if (data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="px-6 py-8 text-center text-gray-500">Không tìm thấy người dùng nào.</td></tr>`;
        updatePaginationInfo(0);
        return;
    }

    data.forEach(user => {
        const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.fullName)}&background=random&color=fff`;
        
        const roleBadge = getRoleBadge(user.role);
        const statusBadge = getStatusBadge(user.status);
        const lockIcon = user.status === 'ACTIVE' ? 'fa-lock' : 'fa-lock-open';
        const lockTitle = user.status === 'ACTIVE' ? 'Khóa tài khoản' : 'Mở khóa tài khoản';

        const tr = document.createElement('tr');
        tr.className = "hover:bg-gray-50 transition-colors";
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">#${user.id}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                        <img class="h-10 w-10 rounded-full border border-gray-200 shadow-sm" src="${avatarUrl}" alt="">
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${user.fullName}</div>
                        <div class="text-sm text-gray-500">@${user.username}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.email}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">${roleBadge}</div>
                <div class="text-sm text-gray-500 mt-1">${getFacultyName(user.faculty)} ${user.cohort ? `(${user.cohort})` : ''}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${statusBadge}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.createdAt}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="viewUser(${user.id})" class="text-indigo-600 hover:text-indigo-900 mx-1 p-1" title="Xem">
                    <i class="fas fa-eye"></i>
                </button>
                <button onclick="openModal('edit', ${user.id})" class="text-blue-600 hover:text-blue-900 mx-1 p-1" title="Sửa">
                    <i class="fas fa-pen"></i>
                </button>
                <button onclick="toggleLockUser(${user.id})" class="text-orange-500 hover:text-orange-700 mx-1 p-1" title="${lockTitle}">
                    <i class="fas ${lockIcon}"></i>
                </button>
                <button onclick="openDeleteModal(${user.id})" class="text-red-600 hover:text-red-900 mx-1 p-1" title="Xóa">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    updatePaginationInfo(data.length);
}

// Cập nhật thông tin phân trang
function updatePaginationInfo(count) {
    document.getElementById('paginationInfo').innerHTML = `Hiển thị <span class="font-medium">${count > 0 ? 1 : 0}</span> đến <span class="font-medium">${count}</span> trong số <span class="font-medium">${count}</span> kết quả`;
}

// Utils: Lấy class badge dựa trên role
function getRoleBadge(role) {
    switch (role) {
        case 'ADMIN': return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">Admin</span>`;
        case 'LECTURER': return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">Giảng viên</span>`;
        case 'STUDENT': return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Sinh viên</span>`;
        default: return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">N/A</span>`;
    }
}

// Utils: Lấy class badge dựa trên status
function getStatusBadge(status) {
    if (status === 'ACTIVE') {
        return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"><span class="w-1.5 h-1.5 rounded-full bg-green-500 mr-1 mt-1.5"></span> Active</span>`;
    } else {
        return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800"><span class="w-1.5 h-1.5 rounded-full bg-red-500 mr-1 mt-1.5"></span> Inactive</span>`;
    }
}

// Utils: Map faculty code to Name
function getFacultyName(code) {
    const map = {
        'CNTT': 'Công nghệ thông tin',
        'KT': 'Kinh tế',
        'NN': 'Ngoại ngữ'
    };
    return map[code] || code || '-';
}

// Xử lý bộ lọc
function applyFilters() {
    const globalSearch = document.getElementById('globalSearch').value.toLowerCase();
    const filterSearch = document.getElementById('filterSearch').value.toLowerCase();
    const role = document.getElementById('filterRole').value;
    const faculty = document.getElementById('filterFaculty').value;
    const status = document.getElementById('filterStatus').value;

    const filteredUsers = users.filter(user => {
        const matchGlobal = !globalSearch || 
            user.fullName.toLowerCase().includes(globalSearch) || 
            user.email.toLowerCase().includes(globalSearch) || 
            user.username.toLowerCase().includes(globalSearch);
            
        const matchSearch = !filterSearch || 
            user.fullName.toLowerCase().includes(filterSearch) || 
            user.email.toLowerCase().includes(filterSearch) || 
            user.username.toLowerCase().includes(filterSearch);

        const matchRole = !role || user.role === role;
        const matchFaculty = !faculty || user.faculty === faculty;
        const matchStatus = !status || user.status === status;

        return matchGlobal && matchSearch && matchRole && matchFaculty && matchStatus;
    });

    renderUsers(filteredUsers);
}

// Xóa bộ lọc
function resetFilters() {
    document.getElementById('globalSearch').value = '';
    document.getElementById('filterSearch').value = '';
    document.getElementById('filterRole').value = '';
    document.getElementById('filterFaculty').value = '';
    document.getElementById('filterStatus').value = '';
    applyFilters();
}

// Xử lý Modal Đóng/Mở
function openModal(action, userId = null) {
    resetFormErrors();
    const modal = document.getElementById('userModal');
    const form = document.getElementById('userForm');
    const modalTitle = document.getElementById('modalTitle');
    
    if (action === 'add') {
        modalTitle.textContent = 'Thêm người dùng mới';
        form.reset();
        document.getElementById('userId').value = '';
        document.getElementById('username').disabled = false;
        document.getElementById('username').classList.remove('bg-gray-100');
        
        // Bắt buộc nhập mật khẩu khi thêm mới
        document.getElementById('passwordLabel').innerHTML = 'Mật khẩu <span class="text-red-500">*</span>';
        document.getElementById('hint-password').classList.add('hidden');
    } else if (action === 'edit' && userId) {
        modalTitle.textContent = 'Sửa thông tin người dùng';
        const user = users.find(u => u.id === userId);
        if (user) {
            document.getElementById('userId').value = user.id;
            document.getElementById('fullName').value = user.fullName;
            document.getElementById('username').value = user.username;
            document.getElementById('email').value = user.email;
            document.getElementById('role').value = user.role;
            document.getElementById('faculty').value = user.faculty;
            document.getElementById('cohort').value = user.cohort;
            document.getElementById('status').value = user.status;
            document.getElementById('password').value = '';
            
            // Username không cho sửa
            document.getElementById('username').disabled = true;
            document.getElementById('username').classList.add('bg-gray-100');

            // Không bắt buộc mật khẩu khi sửa
            document.getElementById('passwordLabel').innerHTML = 'Mật khẩu';
            document.getElementById('hint-password').classList.remove('hidden');
        }
    }
    
    modal.classList.remove('hidden');
    // Animation tick
    setTimeout(() => {
        modal.querySelector('.transform').classList.remove('scale-95', 'opacity-0');
        modal.querySelector('.transform').classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if(modal.querySelector('.transform')) {
        modal.querySelector('.transform').classList.remove('scale-100', 'opacity-100');
        modal.querySelector('.transform').classList.add('scale-95', 'opacity-0');
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 200);
    } else {
        modal.classList.add('hidden');
    }
}

// Xử lý Form Lưu/Sửa Người dùng
function saveUser() {
    resetFormErrors();
    
    const id = document.getElementById('userId').value;
    const fullName = document.getElementById('fullName').value.trim();
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    const faculty = document.getElementById('faculty').value;
    const cohort = document.getElementById('cohort').value.trim();
    const status = document.getElementById('status').value;

    let isValid = true;

    // Validation
    if (!fullName) {
        showError('fullName');
        isValid = false;
    }
    if (!username) {
        showError('username');
        isValid = false;
    } else if (!id) {
        // Check trùng username khi thêm mới
        if (users.some(u => u.username === username)) {
            showError('username');
            isValid = false;
        }
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        showError('email');
        isValid = false;
    }
    
    if (!id && !password) { // Thêm mới bắt buộc pass
        showError('password');
        isValid = false;
    }

    if (!isValid) return;

    if (id) {
        // Cập nhật
        const index = users.findIndex(u => u.id == id);
        if (index !== -1) {
            users[index].fullName = fullName;
            users[index].email = email;
            users[index].role = role;
            users[index].faculty = faculty;
            users[index].cohort = cohort;
            users[index].status = status;
            // Nếu có password mới thì cập nhật (logic xử lý backend)
            showToast('Cập nhật người dùng thành công', 'success');
        }
    } else {
        // Thêm mới
        const newUser = {
            id: users.length > 0 ? Math.max(...users.map(u => u.id)) + 1 : 1,
            fullName,
            username,
            email,
            role,
            faculty,
            cohort,
            status,
            createdAt: new Date().toISOString().split('T')[0]
        };
        users.unshift(newUser);
        showToast('Thêm người dùng thành công', 'success');
    }

    closeModal('userModal');
    applyFilters(); // Render lại bảng
}

// Xử lý Lỗi Form
function showError(fieldId) {
    document.getElementById(fieldId).classList.add('border-red-500', 'focus:ring-red-500', 'focus:border-red-500');
    document.getElementById(`error-${fieldId}`).classList.remove('hidden');
}

function resetFormErrors() {
    const fields = ['fullName', 'username', 'email', 'password'];
    fields.forEach(field => {
        const el = document.getElementById(field);
        if(el) {
            el.classList.remove('border-red-500', 'focus:ring-red-500', 'focus:border-red-500');
            el.classList.add('border-gray-300', 'focus:ring-primary', 'focus:border-primary');
        }
        const err = document.getElementById(`error-${field}`);
        if(err) err.classList.add('hidden');
    });
}

// Xem chi tiết người dùng
function viewUser(id) {
    const user = users.find(u => u.id === id);
    if (!user) return;

    document.getElementById('viewAvatar').src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.fullName)}&background=random&color=fff&size=128`;
    document.getElementById('viewFullName').textContent = user.fullName;
    document.getElementById('viewUsername').textContent = `@${user.username}`;
    document.getElementById('viewEmail').textContent = user.email;
    document.getElementById('viewRole').innerHTML = getRoleBadge(user.role);
    document.getElementById('viewFaculty').textContent = getFacultyName(user.faculty);
    document.getElementById('viewCohort').textContent = user.cohort || '-';
    document.getElementById('viewStatus').innerHTML = getStatusBadge(user.status);
    document.getElementById('viewCreatedAt').textContent = user.createdAt;

    const modal = document.getElementById('viewModal');
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.querySelector('.transform').classList.remove('scale-95', 'opacity-0');
        modal.querySelector('.transform').classList.add('scale-100', 'opacity-100');
    }, 10);
}

// Khóa/Mở khóa tài khoản nhanh
function toggleLockUser(id) {
    const index = users.findIndex(u => u.id === id);
    if (index !== -1) {
        if (users[index].status === 'ACTIVE') {
            users[index].status = 'INACTIVE';
            showToast(`Đã khóa tài khoản ${users[index].username}`, 'warning');
        } else {
            users[index].status = 'ACTIVE';
            showToast(`Đã mở khóa tài khoản ${users[index].username}`, 'success');
        }
        applyFilters();
    }
}

// Mở Modal Xóa
function openDeleteModal(id) {
    currentUserIdToDelete = id;
    const user = users.find(u => u.id === id);
    if (user) {
        document.getElementById('deleteUserName').textContent = user.fullName;
        
        const modal = document.getElementById('deleteModal');
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.querySelector('.transform').classList.remove('scale-95', 'opacity-0');
            modal.querySelector('.transform').classList.add('scale-100', 'opacity-100');
        }, 10);
    }
}

// Xác nhận Xóa
function confirmDelete() {
    if (currentUserIdToDelete) {
        users = users.filter(u => u.id !== currentUserIdToDelete);
        closeModal('deleteModal');
        showToast('Xóa người dùng thành công', 'success');
        applyFilters();
        currentUserIdToDelete = null;
    }
}

// Toast Notification
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    
    // Icon & Color based on type
    let icon = 'fa-check-circle';
    let bgColor = 'bg-white';
    let iconColor = 'text-green-500';
    let borderColor = 'border-l-4 border-green-500';

    if (type === 'error') {
        icon = 'fa-times-circle';
        iconColor = 'text-red-500';
        borderColor = 'border-l-4 border-red-500';
    } else if (type === 'warning') {
        icon = 'fa-exclamation-circle';
        iconColor = 'text-orange-500';
        borderColor = 'border-l-4 border-orange-500';
    }

    toast.className = `flex items-center w-full max-w-xs p-4 space-x-3 text-gray-700 ${bgColor} rounded-lg shadow-lg border-y border-r border-gray-100 ${borderColor} transform transition-all duration-300 translate-x-full opacity-0 pointer-events-auto`;
    
    toast.innerHTML = `
        <i class="fas ${icon} ${iconColor} text-xl"></i>
        <div class="text-sm font-medium flex-1">${message}</div>
        <button class="text-gray-400 hover:text-gray-900 transition-colors" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
        toast.classList.add('translate-x-0', 'opacity-100');
    });

    // Auto remove after 3s
    setTimeout(() => {
        toast.classList.remove('translate-x-0', 'opacity-100');
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

