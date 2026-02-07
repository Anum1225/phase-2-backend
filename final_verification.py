"""
Final Verification - Quick check of database state
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

CONNECTION_STRING = "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def main():
    print("\n" + "="*80)
    print("FINAL DATABASE VERIFICATION")
    print("="*80)

    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("\n✓ Connected to Neon PostgreSQL")

        # Check tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name IN ('users', 'tasks')
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n✓ Tables: {', '.join(tables)}")

        # Check foreign key
        cursor.execute("""
            SELECT tc.constraint_name, rc.delete_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
            WHERE tc.table_name = 'tasks' AND tc.constraint_type = 'FOREIGN KEY';
        """)
        fk = cursor.fetchone()
        print(f"✓ Foreign Key: {fk[0]} (ON DELETE {fk[1]})")

        # Check indexes
        cursor.execute("""
            SELECT COUNT(*) FROM pg_indexes
            WHERE schemaname = 'public' AND tablename IN ('users', 'tasks');
        """)
        index_count = cursor.fetchone()[0]
        print(f"✓ Indexes: {index_count} total")

        # Check triggers
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.triggers
            WHERE trigger_schema = 'public' AND event_object_table IN ('users', 'tasks');
        """)
        trigger_count = cursor.fetchone()[0]
        print(f"✓ Triggers: {trigger_count} active")

        # Check row counts
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks;")
        task_count = cursor.fetchone()[0]

        print(f"\n✓ Data: {user_count} users, {task_count} tasks")

        print("\n" + "="*80)
        print("✓ DATABASE READY FOR BACKEND API")
        print("="*80)
        print("\nStart backend: uvicorn src.main:app --reload")
        print("API docs: http://localhost:8000/docs\n")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
