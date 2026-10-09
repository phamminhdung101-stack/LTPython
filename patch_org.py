import re

def process_org_management():
    filepath = 'frontend/templates/academics/organization_management.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Department table
    dept_body = '''<tbody id="facultyTableBody" class="bg-white divide-y divide-gray-200">
        {% for dept in departments %}
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ dept.department_code }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ dept.department_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ dept.head_of_department|default:"-" }}</td>
            <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{{ dept.description|default:"-" }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="openModal('faculty', 'edit', {{ dept.id }})" class="text-blue-600 hover:text-blue-900 mx-2"><i class="fas fa-pen"></i></button>
                <button onclick="promptDelete('faculty', {{ dept.id }})" class="text-red-600 hover:text-red-900"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
        {% empty %}
        <tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">Không tìm thấy khoa nào.</td></tr>
        {% endfor %}
    </tbody>'''
    content = re.sub(r'<tbody id="facultyTableBody"[^>]*>.*?</tbody>', dept_body, content, flags=re.DOTALL)

    # Class table
    class_body = '''<tbody id="classTableBody" class="bg-white divide-y divide-gray-200">
        {% for cls in classes %}
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ cls.class_code }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ cls.class_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ cls.department.department_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ cls.student_count|default:"0" }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="openModal('class', 'edit', {{ cls.id }})" class="text-blue-600 hover:text-blue-900 mx-2"><i class="fas fa-pen"></i></button>
                <button onclick="promptDelete('class', {{ cls.id }})" class="text-red-600 hover:text-red-900"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
        {% empty %}
        <tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">Không tìm thấy lớp nào.</td></tr>
        {% endfor %}
    </tbody>'''
    content = re.sub(r'<tbody id="classTableBody"[^>]*>.*?</tbody>', class_body, content, flags=re.DOTALL)

    # Subject table
    subj_body = '''<tbody id="subjectTableBody" class="bg-white divide-y divide-gray-200">
        {% for sub in subjects %}
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ sub.subject_code }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ sub.subject_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ sub.credits }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ sub.department.department_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="openModal('subject', 'edit', {{ sub.id }})" class="text-blue-600 hover:text-blue-900 mx-2"><i class="fas fa-pen"></i></button>
                <button onclick="promptDelete('subject', {{ sub.id }})" class="text-red-600 hover:text-red-900"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
        {% empty %}
        <tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">Không tìm thấy môn học nào.</td></tr>
        {% endfor %}
    </tbody>'''
    content = re.sub(r'<tbody id="subjectTableBody"[^>]*>.*?</tbody>', subj_body, content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

process_org_management()
print("Organization Management Patched!")

