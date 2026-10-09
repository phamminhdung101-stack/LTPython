import re

filepath = 'frontend/templates/accounts/user_management.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix Table Body to use page_obj
django_table_body = '''<tbody id="userTableBody" class="bg-white divide-y divide-gray-200">
    {% for user in page_obj %}
    <tr class="hover:bg-gray-50 transition-colors">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">#{{ user.id }}</td>
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                    <img class="h-10 w-10 rounded-full border border-gray-200 shadow-sm" src="https://ui-avatars.com/api/?name={{ user.full_name|urlencode }}&background=random&color=fff" alt="">
                </div>
                <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ user.full_name }}</div>
                    <div class="text-sm text-gray-500">@{{ user.username }}</div>
                </div>
            </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.email }}</td>
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm text-gray-900">
                {% if user.role.role_name == 'ADMIN' %}
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">Admin</span>
                {% elif user.role.role_name == 'LECTURER' %}
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">Giảng viên</span>
                {% elif user.role.role_name == 'STUDENT' %}
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Sinh viên</span>
                {% else %}
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">{{ user.role.role_name }}</span>
                {% endif %}
            </div>
            <div class="text-sm text-gray-500 mt-1">{{ user.department.department_name|default:"-" }} {% if user.student_class %}({{ user.student_class.class_code }}){% endif %}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            {% if user.is_active %}
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"><span class="w-1.5 h-1.5 rounded-full bg-green-500 mr-1 mt-1.5"></span> Active</span>
            {% else %}
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800"><span class="w-1.5 h-1.5 rounded-full bg-red-500 mr-1 mt-1.5"></span> Inactive</span>
            {% endif %}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.created_at|date:"Y-m-d" }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <!-- Xem / Sửa -->
            <button onclick="viewUser({{ user.id }})" class="text-indigo-600 hover:text-indigo-900 mx-1 p-1" title="Xem">
                <i class="fas fa-eye"></i>
            </button>
            <button onclick="openModal('edit', {{ user.id }})" class="text-blue-600 hover:text-blue-900 mx-1 p-1" title="Sửa">
                <i class="fas fa-pen"></i>
            </button>
            
            <!-- Khóa / Mở khóa bằng JS Fetch thay vì href -->
            <button onclick="toggleUserStatus({{ user.id }})" class="text-orange-500 hover:text-orange-700 mx-1 p-1" title="{% if user.is_active %}Khóa tài khoản{% else %}Mở khóa tài khoản{% endif %}">
                <i class="fas {% if user.is_active %}fa-lock{% else %}fa-lock-open{% endif %}"></i>
            </button>
            
            <button onclick="openDeleteModal({{ user.id }}, '{{ user.username }}')" class="text-red-600 hover:text-red-900 mx-1 p-1" title="Xóa">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    </tr>
    {% empty %}
    <tr><td colspan="7" class="px-6 py-8 text-center text-gray-500">Không tìm thấy người dùng nào.</td></tr>
    {% endfor %}
</tbody>'''

content = re.sub(r'<tbody id="userTableBody"[^>]*>.*?</tbody>', django_table_body, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated user_management.html")

