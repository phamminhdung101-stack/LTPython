import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_type='BASE TABLE'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    print(f"Total tables: {len(tables)}")
    for (t,) in tables:
        cursor.execute(f'SELECT count(*) FROM "{t}"')
        count = cursor.fetchone()[0]
        print(f"  {t}: {count} rows")
