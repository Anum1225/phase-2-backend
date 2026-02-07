-- Verification Script for Database Schema
-- Run this after executing schema.sql to verify everything is set up correctly

-- ============================================================================
-- 1. VERIFY TABLES EXIST
-- ============================================================================

\echo '=== Checking Tables ==='
SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('users', 'tasks')
ORDER BY table_name;

-- Expected: 2 rows (users, tasks)

-- ============================================================================
-- 2. VERIFY FOREIGN KEY CONSTRAINT
-- ============================================================================

\echo ''
\echo '=== Checking Foreign Key Constraint ==='
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

-- Expected: 1 row showing fk_tasks_user_id -> users(id) with CASCADE

-- ============================================================================
-- 3. VERIFY INDEXES
-- ============================================================================

\echo ''
\echo '=== Checking Indexes ==='
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('users', 'tasks')
ORDER BY tablename, indexname;

-- Expected indexes:
-- users: idx_users_created_at, idx_users_email, users_pkey
-- tasks: idx_tasks_completed, idx_tasks_user_id, idx_tasks_user_id_created_at, tasks_pkey

-- ============================================================================
-- 4. VERIFY CONSTRAINTS
-- ============================================================================

\echo ''
\echo '=== Checking All Constraints ==='
SELECT
    tc.constraint_name,
    tc.constraint_type,
    tc.table_name,
    cc.check_clause
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.check_constraints cc
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
AND tc.table_name IN ('users', 'tasks')
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- Expected constraints:
-- users: email_format (CHECK), password_hash_length (CHECK), users_email_key (UNIQUE), users_pkey (PRIMARY KEY)
-- tasks: fk_tasks_user_id (FOREIGN KEY), title_not_empty (CHECK), title_length (CHECK), description_length (CHECK), tasks_pkey (PRIMARY KEY)

-- ============================================================================
-- 5. VERIFY TRIGGERS
-- ============================================================================

\echo ''
\echo '=== Checking Triggers ==='
SELECT
    trigger_name,
    event_manipulation,
    event_object_table,
    action_timing,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
AND event_object_table IN ('users', 'tasks')
ORDER BY event_object_table, trigger_name;

-- Expected: 2 triggers (update_users_updated_at, update_tasks_updated_at)

-- ============================================================================
-- 6. TEST FOREIGN KEY CONSTRAINT
-- ============================================================================

\echo ''
\echo '=== Testing Foreign Key Constraint ==='

-- Test 1: Try to insert task with non-existent user_id (should fail)
\echo 'Test 1: Insert task with invalid user_id (should fail)...'
DO $$
BEGIN
    INSERT INTO tasks (user_id, title, description, completed)
    VALUES ('00000000-0000-0000-0000-000000000000', 'Invalid task', 'This should fail', false);
    RAISE EXCEPTION 'ERROR: Foreign key constraint did not prevent invalid user_id!';
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE NOTICE 'SUCCESS: Foreign key constraint working - prevented invalid user_id';
END $$;

-- Test 2: Create user, create task, verify relationship
\echo ''
\echo 'Test 2: Create user and task, verify foreign key relationship...'
DO $$
DECLARE
    test_user_id UUID;
    test_task_id UUID;
BEGIN
    -- Create test user
    INSERT INTO users (email, password_hash)
    VALUES ('fk_test@example.com', '$2b$12$test_hash_12345678901234567890123456789012345678901234')
    RETURNING id INTO test_user_id;
    RAISE NOTICE 'Created test user: %', test_user_id;

    -- Create task for test user
    INSERT INTO tasks (user_id, title, description, completed)
    VALUES (test_user_id, 'Test task', 'Testing FK relationship', false)
    RETURNING id INTO test_task_id;
    RAISE NOTICE 'Created test task: %', test_task_id;

    -- Verify relationship
    IF EXISTS (
        SELECT 1 FROM tasks WHERE id = test_task_id AND user_id = test_user_id
    ) THEN
        RAISE NOTICE 'SUCCESS: Task correctly linked to user';
    ELSE
        RAISE EXCEPTION 'ERROR: Task not linked to user correctly';
    END IF;

    -- Test CASCADE DELETE
    DELETE FROM users WHERE id = test_user_id;
    RAISE NOTICE 'Deleted test user';

    -- Verify task was also deleted (CASCADE)
    IF NOT EXISTS (SELECT 1 FROM tasks WHERE id = test_task_id) THEN
        RAISE NOTICE 'SUCCESS: CASCADE DELETE working - task automatically deleted';
    ELSE
        RAISE EXCEPTION 'ERROR: CASCADE DELETE failed - task still exists!';
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        -- Cleanup test data if any error
        DELETE FROM tasks WHERE user_id = test_user_id;
        DELETE FROM users WHERE email = 'fk_test@example.com';
        RAISE;
END $$;

-- ============================================================================
-- 7. SUMMARY
-- ============================================================================

\echo ''
\echo '=== Schema Verification Summary ==='
\echo 'If all tests passed, the database schema is correctly configured with:'
\echo '1. Users table with email uniqueness and password constraints'
\echo '2. Tasks table with foreign key to users.id'
\echo '3. CASCADE DELETE working (user deletion removes tasks)'
\echo '4. All required indexes for performance'
\echo '5. Automatic updated_at triggers'
\echo ''
\echo 'Next steps:'
\echo '1. Start the backend server: uvicorn src.main:app --reload'
\echo '2. Test API endpoints at http://localhost:8000/docs'
\echo '3. Verify data isolation between users'
