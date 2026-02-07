"""
Database Setup Script for Neon PostgreSQL
Executes schema.sql and runs comprehensive verification tests
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Database connection string
CONNECTION_STRING = "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def execute_sql_file(cursor, file_path):
    """Execute SQL commands from a file"""
    print(f"\n{'='*80}")
    print(f"Executing SQL from: {file_path}")
    print(f"{'='*80}\n")

    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split by semicolons, but this is a simple approach
    # For production, use a proper SQL parser
    cursor.execute(sql_content)
    print("✓ SQL executed successfully")

def verify_tables(cursor):
    """Verify tables were created"""
    print("\n" + "="*80)
    print("1. VERIFYING TABLES")
    print("="*80)

    cursor.execute("""
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN ('users', 'tasks')
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()
    print(f"\nFound {len(tables)} tables:")
    for table in tables:
        print(f"  ✓ {table[0]} ({table[1]})")

    if len(tables) != 2:
        print("  ✗ ERROR: Expected 2 tables (users, tasks)")
        return False
    return True

def verify_foreign_key(cursor):
    """Verify foreign key constraint exists with CASCADE"""
    print("\n" + "="*80)
    print("2. VERIFYING FOREIGN KEY CONSTRAINT")
    print("="*80)

    cursor.execute("""
        SELECT
            tc.constraint_name,
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule AS on_delete,
            rc.update_rule AS on_update
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        JOIN information_schema.referential_constraints AS rc
            ON tc.constraint_name = rc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = 'tasks'
        ORDER BY tc.constraint_name;
    """)

    fks = cursor.fetchall()
    print(f"\nFound {len(fks)} foreign key constraint(s):")
    for fk in fks:
        constraint_name, table, column, foreign_table, foreign_column, delete_rule, update_rule = fk
        print(f"\n  ✓ Constraint: {constraint_name}")
        print(f"    Table: {table}.{column}")
        print(f"    References: {foreign_table}.{foreign_column}")
        print(f"    ON DELETE: {delete_rule}")
        print(f"    ON UPDATE: {update_rule}")

        if constraint_name == 'fk_tasks_user_id' and delete_rule == 'CASCADE':
            print(f"    ✓ Constraint correctly configured")
        else:
            print(f"    ✗ WARNING: Expected fk_tasks_user_id with CASCADE DELETE")

    return len(fks) > 0

def verify_indexes(cursor):
    """Verify all indexes were created"""
    print("\n" + "="*80)
    print("3. VERIFYING INDEXES")
    print("="*80)

    cursor.execute("""
        SELECT
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename IN ('users', 'tasks')
        ORDER BY tablename, indexname;
    """)

    indexes = cursor.fetchall()
    print(f"\nFound {len(indexes)} indexes:")

    users_indexes = [idx for idx in indexes if idx[0] == 'users']
    tasks_indexes = [idx for idx in indexes if idx[0] == 'tasks']

    print(f"\n  Users table ({len(users_indexes)} indexes):")
    for idx in users_indexes:
        print(f"    ✓ {idx[1]}")

    print(f"\n  Tasks table ({len(tasks_indexes)} indexes):")
    for idx in tasks_indexes:
        print(f"    ✓ {idx[1]}")

    # Check for critical indexes
    critical_indexes = [
        'idx_users_email',
        'idx_tasks_user_id',
        'idx_tasks_user_id_created_at'
    ]

    found_indexes = [idx[1] for idx in indexes]
    missing = [idx for idx in critical_indexes if idx not in found_indexes]

    if missing:
        print(f"\n  ✗ WARNING: Missing critical indexes: {missing}")
        return False

    print(f"\n  ✓ All critical indexes present")
    return True

def verify_triggers(cursor):
    """Verify triggers for automatic updated_at"""
    print("\n" + "="*80)
    print("4. VERIFYING TRIGGERS")
    print("="*80)

    cursor.execute("""
        SELECT
            trigger_name,
            event_manipulation,
            event_object_table,
            action_timing
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        AND event_object_table IN ('users', 'tasks')
        ORDER BY event_object_table, trigger_name;
    """)

    triggers = cursor.fetchall()
    print(f"\nFound {len(triggers)} trigger(s):")
    for trigger in triggers:
        trigger_name, event, table, timing = trigger
        print(f"  ✓ {trigger_name} ({timing} {event} on {table})")

    expected_triggers = ['update_users_updated_at', 'update_tasks_updated_at']
    found_triggers = [t[0] for t in triggers]

    if all(trig in found_triggers for trig in expected_triggers):
        print("\n  ✓ All expected triggers present")
        return True
    else:
        print("\n  ✗ WARNING: Missing expected triggers")
        return False

def test_foreign_key_validation(cursor):
    """Test that foreign key prevents invalid user_id"""
    print("\n" + "="*80)
    print("5. TESTING FOREIGN KEY VALIDATION")
    print("="*80)

    print("\nTest: Insert task with non-existent user_id (should fail)...")
    try:
        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, completed)
            VALUES ('00000000-0000-0000-0000-000000000000', 'Invalid task', 'This should fail', false);
        """)
        print("  ✗ ERROR: Foreign key did NOT prevent invalid user_id!")
        cursor.connection.rollback()
        return False
    except psycopg2.errors.ForeignKeyViolation:
        print("  ✓ SUCCESS: Foreign key correctly prevented invalid user_id")
        cursor.connection.rollback()
        return True
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        cursor.connection.rollback()
        return False

def test_cascade_delete(cursor):
    """Test CASCADE DELETE by creating user, tasks, then deleting user"""
    print("\n" + "="*80)
    print("6. TESTING CASCADE DELETE")
    print("="*80)

    try:
        # Create test user
        print("\nStep 1: Creating test user...")
        cursor.execute("""
            INSERT INTO users (email, password_hash)
            VALUES ('cascade_test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eBHnhxhIlqWK')
            RETURNING id;
        """)
        user_id = cursor.fetchone()[0]
        print(f"  ✓ Created user: {user_id}")

        # Create tasks for user
        print("\nStep 2: Creating tasks for user...")
        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, completed)
            VALUES
                (%s, 'Task 1', 'Description 1', false),
                (%s, 'Task 2', 'Description 2', true),
                (%s, 'Task 3', 'Description 3', false)
            RETURNING id;
        """, (user_id, user_id, user_id))
        task_ids = [row[0] for row in cursor.fetchall()]
        print(f"  ✓ Created {len(task_ids)} tasks")
        for task_id in task_ids:
            print(f"    - {task_id}")

        # Verify tasks exist
        print("\nStep 3: Verifying tasks exist...")
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s;", (user_id,))
        task_count_before = cursor.fetchone()[0]
        print(f"  ✓ Found {task_count_before} tasks for user")

        # Delete user (should cascade to tasks)
        print("\nStep 4: Deleting user (CASCADE DELETE should remove tasks)...")
        cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        print(f"  ✓ Deleted user {user_id}")

        # Verify tasks were deleted
        print("\nStep 5: Verifying tasks were automatically deleted...")
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s;", (user_id,))
        remaining_tasks = cursor.fetchone()[0]

        if remaining_tasks == 0:
            print(f"  ✓ SUCCESS: CASCADE DELETE working correctly - all {len(task_ids)} tasks deleted")
            cursor.connection.commit()
            return True
        else:
            print(f"  ✗ ERROR: CASCADE DELETE failed - {remaining_tasks} tasks still exist!")
            cursor.connection.rollback()
            return False

    except Exception as e:
        print(f"\n  ✗ Error during CASCADE DELETE test: {e}")
        cursor.connection.rollback()
        # Cleanup
        try:
            cursor.execute("DELETE FROM users WHERE email = 'cascade_test@example.com';")
            cursor.connection.commit()
        except:
            pass
        return False

def get_summary(cursor):
    """Get final summary of database state"""
    print("\n" + "="*80)
    print("7. DATABASE SUMMARY")
    print("="*80)

    # Table row counts
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks;")
    task_count = cursor.fetchone()[0]

    print(f"\nTable Statistics:")
    print(f"  Users: {user_count} rows")
    print(f"  Tasks: {task_count} rows")

    # Constraint summary
    cursor.execute("""
        SELECT constraint_type, COUNT(*)
        FROM information_schema.table_constraints
        WHERE table_schema = 'public'
        AND table_name IN ('users', 'tasks')
        GROUP BY constraint_type
        ORDER BY constraint_type;
    """)

    print(f"\nConstraints:")
    for constraint_type, count in cursor.fetchall():
        print(f"  {constraint_type}: {count}")

    # Index summary
    cursor.execute("""
        SELECT tablename, COUNT(*)
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename IN ('users', 'tasks')
        GROUP BY tablename
        ORDER BY tablename;
    """)

    print(f"\nIndexes:")
    for table, count in cursor.fetchall():
        print(f"  {table}: {count}")

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("NEON POSTGRESQL DATABASE SETUP")
    print("="*80)

    connection = None
    cursor = None

    try:
        # Connect to database
        print("\nConnecting to Neon PostgreSQL...")
        connection = psycopg2.connect(CONNECTION_STRING)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        print("✓ Connected successfully")

        # Execute schema
        schema_file = Path(__file__).parent / "schema.sql"
        if not schema_file.exists():
            print(f"\n✗ ERROR: Schema file not found: {schema_file}")
            sys.exit(1)

        execute_sql_file(cursor, schema_file)

        # Run verifications
        results = {
            'tables': verify_tables(cursor),
            'foreign_key': verify_foreign_key(cursor),
            'indexes': verify_indexes(cursor),
            'triggers': verify_triggers(cursor),
            'fk_validation': test_foreign_key_validation(cursor),
            'cascade_delete': test_cascade_delete(cursor),
        }

        # Get summary
        get_summary(cursor)

        # Final results
        print("\n" + "="*80)
        print("VERIFICATION RESULTS")
        print("="*80)

        all_passed = all(results.values())

        print("\nTest Results:")
        for test_name, passed in results.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"  {status}: {test_name.replace('_', ' ').title()}")

        print("\n" + "="*80)
        if all_passed:
            print("✓ ALL TESTS PASSED - Database setup successful!")
            print("="*80)
            print("\nNext steps:")
            print("1. Start backend: cd backend && uvicorn src.main:app --reload")
            print("2. Test API: http://localhost:8000/docs")
            print("3. Test user signup/signin")
            print("4. Verify data isolation between users")
            sys.exit(0)
        else:
            print("✗ SOME TESTS FAILED - Please review errors above")
            print("="*80)
            sys.exit(1)

    except psycopg2.Error as e:
        print(f"\n✗ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("\n✓ Database connection closed")

if __name__ == "__main__":
    main()
