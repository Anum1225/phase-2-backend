-- Database Quick Reference - Common Operations
-- Neon PostgreSQL Task API Backend

-- ============================================================================
-- CONNECTION STRING
-- ============================================================================

-- psql connection:
-- psql "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

-- Python connection:
-- import psycopg2
-- conn = psycopg2.connect("postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require")

-- ============================================================================
-- VIEW TABLE SCHEMAS
-- ============================================================================

-- View users table structure
\d users

-- View tasks table structure
\d tasks

-- View all tables
\dt

-- View all indexes
\di

-- ============================================================================
-- CHECK TABLE CONTENTS
-- ============================================================================

-- Count users
SELECT COUNT(*) as total_users FROM users;

-- Count tasks
SELECT COUNT(*) as total_tasks FROM tasks;

-- View all users (limited)
SELECT id, email, created_at, updated_at
FROM users
ORDER BY created_at DESC
LIMIT 10;

-- View all tasks (limited)
SELECT id, user_id, title, completed, created_at
FROM tasks
ORDER BY created_at DESC
LIMIT 10;

-- ============================================================================
-- USER QUERIES
-- ============================================================================

-- Find user by email
SELECT id, email, created_at
FROM users
WHERE email = 'user@example.com';

-- Find user by ID
SELECT id, email, created_at
FROM users
WHERE id = '550e8400-e29b-41d4-a716-446655440000';

-- List all users with task counts
SELECT
    u.id,
    u.email,
    u.created_at,
    COUNT(t.id) as task_count,
    COUNT(CASE WHEN t.completed = true THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.completed = false THEN 1 END) as pending_tasks
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.email, u.created_at
ORDER BY u.created_at DESC;

-- ============================================================================
-- TASK QUERIES
-- ============================================================================

-- List all tasks for a specific user
SELECT id, title, description, completed, created_at, updated_at
FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at DESC;

-- List incomplete tasks for a user
SELECT id, title, description, created_at
FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND completed = false
ORDER BY created_at DESC;

-- List completed tasks for a user
SELECT id, title, description, completed_at
FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
AND completed = true
ORDER BY updated_at DESC;

-- Get task by ID (with user info)
SELECT
    t.id,
    t.title,
    t.description,
    t.completed,
    t.created_at,
    t.updated_at,
    u.email as user_email
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE t.id = '123e4567-e89b-12d3-a456-426614174000';

-- ============================================================================
-- VERIFY FOREIGN KEY CONSTRAINT
-- ============================================================================

-- View foreign key details
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule,
    rc.update_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name = 'tasks';

-- ============================================================================
-- CHECK INDEXES
-- ============================================================================

-- View all indexes with usage stats
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- View index definitions
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('users', 'tasks')
ORDER BY tablename, indexname;

-- ============================================================================
-- CHECK TRIGGERS
-- ============================================================================

-- View all triggers
SELECT
    trigger_name,
    event_manipulation,
    event_object_table,
    action_timing,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- ============================================================================
-- TEST DATA OPERATIONS
-- ============================================================================

-- Create test user
INSERT INTO users (email, password_hash)
VALUES ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eBHnhxhIlqWK')
RETURNING id, email, created_at;

-- Create test task for user
INSERT INTO tasks (user_id, title, description, completed)
VALUES (
    (SELECT id FROM users WHERE email = 'test@example.com'),
    'Test Task',
    'This is a test task',
    false
)
RETURNING id, title, created_at;

-- Update task to completed
UPDATE tasks
SET completed = true
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
RETURNING id, title, completed, updated_at;

-- Delete task
DELETE FROM tasks
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
RETURNING id, title;

-- Delete user (CASCADE will delete their tasks)
DELETE FROM users
WHERE email = 'test@example.com'
RETURNING id, email;

-- ============================================================================
-- PERFORMANCE ANALYSIS
-- ============================================================================

-- Analyze query performance (add EXPLAIN ANALYZE before SELECT)
EXPLAIN ANALYZE
SELECT id, title, description, completed
FROM tasks
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at DESC
LIMIT 20;

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check for unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
AND idx_scan = 0
ORDER BY tablename, indexname;

-- Check table statistics
SELECT
    schemaname,
    tablename,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- ============================================================================
-- DATA VALIDATION QUERIES
-- ============================================================================

-- Find orphaned tasks (should return 0 rows if FK working)
SELECT t.*
FROM tasks t
LEFT JOIN users u ON t.user_id = u.id
WHERE u.id IS NULL;

-- Find duplicate emails (should return 0 rows if UNIQUE working)
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

-- Find invalid email formats (should return 0 rows if CHECK working)
SELECT id, email
FROM users
WHERE email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';

-- Find tasks with empty titles (should return 0 rows if CHECK working)
SELECT id, title
FROM tasks
WHERE LENGTH(TRIM(title)) = 0;

-- ============================================================================
-- CLEANUP OPERATIONS
-- ============================================================================

-- Delete all test data (use with caution!)
-- DELETE FROM tasks WHERE title LIKE '%test%';
-- DELETE FROM users WHERE email LIKE '%test%';

-- Reset sequences (if needed)
-- ALTER SEQUENCE users_id_seq RESTART WITH 1;
-- ALTER SEQUENCE tasks_id_seq RESTART WITH 1;

-- ============================================================================
-- BACKUP & RESTORE HINTS
-- ============================================================================

-- Export users table to CSV
-- \copy users TO '/path/to/users.csv' WITH CSV HEADER;

-- Export tasks table to CSV
-- \copy tasks TO '/path/to/tasks.csv' WITH CSV HEADER;

-- Import from CSV
-- \copy users FROM '/path/to/users.csv' WITH CSV HEADER;
-- \copy tasks FROM '/path/to/tasks.csv' WITH CSV HEADER;

-- ============================================================================
-- TROUBLESHOOTING
-- ============================================================================

-- Check current connections
SELECT
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'neondb';

-- Check for long-running queries
SELECT
    pid,
    now() - query_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
AND query_start < now() - interval '5 seconds'
ORDER BY duration DESC;

-- Kill a specific connection (if needed)
-- SELECT pg_terminate_backend(pid) WHERE pid = 12345;

-- ============================================================================
-- NOTES
-- ============================================================================

-- 1. Always use parameterized queries in application code to prevent SQL injection
-- 2. Use transactions for operations that modify multiple rows
-- 3. The CASCADE DELETE is automatic - deleting a user deletes their tasks
-- 4. Neon provides automatic backups - check Neon console for restore options
-- 5. Connection pooling is enabled via the pooler endpoint
-- 6. All timestamps are in UTC
-- 7. UUIDs are automatically generated via gen_random_uuid()
