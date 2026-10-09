import re

def process_home():
    filepath = 'frontend/templates/student/home.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    home_body = '''<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="recentDocsContainer">
        {% for doc in recent_docs %}
        <a href="{% url 'documents:document_detail' doc.id %}" class="doc-card bg-white border border-gray-200 rounded-xl overflow-hidden flex flex-col h-full group">
            <div class="p-5 flex-grow">
                <div class="flex justify-between items-start mb-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {{ doc.get_doc_type_display }}
                    </span>
                    <i class="fas fa-file-pdf text-red-500 text-2xl opacity-80 group-hover:opacity-100 transition-opacity"></i>
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-brand-600 transition-colors">{{ doc.title }}</h3>
                <p class="text-sm text-gray-500 mb-4 line-clamp-2">{{ doc.description }}</p>
                <div class="flex items-center text-xs text-gray-500 gap-4 mt-auto">
                    <span class="flex items-center gap-1"><i class="fas fa-book-open"></i> {{ doc.subject.subject_code }}</span>
                    <span class="flex items-center gap-1"><i class="fas fa-download"></i> {{ doc.download_count }}</span>
                </div>
            </div>
            <div class="bg-gray-50 px-5 py-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                <div class="flex items-center gap-2">
                    <img src="https://ui-avatars.com/api/?name={{ doc.uploader.full_name|urlencode }}&background=random" class="w-5 h-5 rounded-full" alt="Uploader">
                    <span>{{ doc.uploader.full_name }}</span>
                </div>
                <span>{{ doc.created_at|date:"d/m/Y" }}</span>
            </div>
        </a>
        {% endfor %}
    </div>'''
    
    content = re.sub(r'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="recentDocsContainer">.*?</div>\s*</div>', home_body + '\n            </div>', content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

process_home()
print("Student Home Patched!")

