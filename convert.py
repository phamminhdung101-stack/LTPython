import re
import os

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add load static if not present
    if '{% load static %}' not in content:
        content = re.sub(r'(<!DOCTYPE html>\s*<html[^>]*>\s*)', r'\1{% load static %}\n', content)

    # Replace static links
    content = re.sub(r'(href|src)="(\.\./)+static/([^"]+)"', r'\1="{% static \'\3\' %}"', content)
    content = re.sub(r'(href|src)="/static/([^"]+)"', r'\1="{% static \'\2\' %}"', content)

    # Replace specific URLs for student portal
    content = content.replace('href="home.html"', 'href="{% url \'documents:home\' %}"')
    content = content.replace('href="document_list.html"', 'href="{% url \'documents:document_list\' %}"')
    content = content.replace('action="document_list.html"', 'action="{% url \'documents:document_list\' %}"')

    # Replace specific URLs for admin portal
    content = content.replace('href="../accounts/user_management.html"', 'href="{% url \'accounts:user_list\' %}"')
    content = content.replace('href="../academics/organization_management.html"', 'href="{% url \'academics:organization_management\' %}"')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for root, dirs, files in os.walk('frontend/templates'):
    for file in files:
        if file.endswith('.html'):
            process_file(os.path.join(root, file))

print("Done converting static and basic links!")

