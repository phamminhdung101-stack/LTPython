import re

filepath = 'frontend/templates/accounts/user_management.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the static filter divs with a real form
old_filter = r'<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 mb-6">.*?<div class="mt-4 flex justify-end">.*?</div>\s*</div>'
new_filter = '''<form method="GET" action="{% url 'accounts:user_list' %}" class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Tìm kiếm chi tiết</label>
            <input type="text" name="q" value="{{ filters.q }}" placeholder="Tên, Email, Username..." class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary sm:text-sm">
        </div>
        <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Vai trò (Role)</label>
            <select name="role" class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary sm:text-sm bg-white">
                <option value="">Tất cả vai trò</option>
                {% for role in roles %}
                <option value="{{ role.role_name }}" {% if filters.role == role.role_name %}selected{% endif %}>{{ role.role_name }}</option>
                {% endfor %}
            </select>
        </div>
        <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Khoa</label>
            <select name="department" class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary sm:text-sm bg-white">
                <option value="">Tất cả khoa</option>
                {% for dept in departments %}
                <option value="{{ dept.id }}" {% if filters.department == dept.id|stringformat:"s" %}selected{% endif %}>{{ dept.department_name }}</option>
                {% endfor %}
            </select>
        </div>
        <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Trạng thái</label>
            <select name="status" class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary sm:text-sm bg-white">
                <option value="">Tất cả trạng thái</option>
                <option value="ACTIVE" {% if filters.status == 'ACTIVE' %}selected{% endif %}>Hoạt động (Active)</option>
                <option value="INACTIVE" {% if filters.status == 'INACTIVE' %}selected{% endif %}>Vô hiệu (Inactive)</option>
            </select>
        </div>
    </div>
    <div class="mt-4 flex justify-end gap-2">
        <a href="{% url 'accounts:user_list' %}" class="text-sm text-gray-600 hover:text-gray-900 font-medium px-3 py-1 rounded border border-transparent hover:border-gray-200 transition-colors flex items-center">
            <i class="fas fa-undo mr-1"></i> Reset
        </a>
        <button type="submit" class="bg-primary text-white text-sm font-medium px-4 py-1.5 rounded hover:bg-primary-hover transition-colors">
            Lọc
        </button>
    </div>
</form>'''

content = re.sub(old_filter, new_filter, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated user_management.html filters")

