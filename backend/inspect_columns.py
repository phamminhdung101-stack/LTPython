import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def inspect_columns():
    with connection.cursor() as cursor:
        for table in ['departments', 'classes', 'subjects', 'folders', 'documents', 'document_activity_logs', 'ai_queries']:
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = '{table}'
                ORDER BY ordinal_position;
            """)
            cols = cursor.fetchall()
            print(f"\nTable: {table}")
            for col, dtype, nullable in cols:
                print(f"  - {col} ({dtype}, nullable: {nullable})")

if __name__ == '__main__':
    inspect_columns()

