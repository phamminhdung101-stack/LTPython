import re

filepath = 'frontend/templates/accounts/user_management.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Update form attributes
content = content.replace('name="fullName"', 'name="full_name"')
content = content.replace('id="fullName"', 'id="full_name"')
content = content.replace('id="error-fullName"', 'id="error-full_name"')

content = content.replace('name="cohort"', 'name="student_class"')
content = content.replace('id="cohort"', 'id="student_class"')

content = content.replace('name="faculty"', 'name="department"')
content = content.replace('id="faculty"', 'id="department"')

content = content.replace('name="status"', 'name="is_active"')
content = content.replace('id="status"', 'id="is_active"')
# Note: Since value="ACTIVE" and "INACTIVE" might be used in the table filter, let's be careful.
# But wait, we replaced the filter form entirely in patch_filter.py! The only ACTIVE/INACTIVE left is in the User Add/Edit modal.
content = content.replace('value="ACTIVE"', 'value="true"')
content = content.replace('value="INACTIVE"', 'value="false"')

# Add CSRF token to form and set ID and method
content = content.replace('<form id="userForm" class="space-y-4" novalidate>', '<form id="userForm" class="space-y-4" novalidate method="POST">\n                        {% csrf_token %}')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Form patched!")

