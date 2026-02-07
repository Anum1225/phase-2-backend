-- Task API Backend Database Schema
-- Database: Neon PostgreSQL (serverless)
-- Purpose: Multi-user todo application with strict data isolation

-- ============================================================================
-- EXTENSIONS (if needed)
-- ============================================================================

-- Enable UUID generation (Neon PostgreSQL has this by default)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- USERS TABLE
-- ============================================================================

-- Drop existing tables if they exist (for clean reinstall)
-- CASCADE ensures dependent tasks are also dropped
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Additional constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT password_hash_length CHECK (LENGTH(password_hash) >= 59)  -- bcrypt outputs 60 chars
);

-- Create unique index on email for fast lookup during signin
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Create index on created_at for user queries
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts with authentication credentials';
COMMENT ON COLUMN users.id IS 'Unique user identifier (UUID)';
COMMENT ON COLUMN users.email IS 'User email address (used for login, must be unique)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password (never store plain text)';
COMMENT ON COLUMN users.created_at IS 'Account creation timestamp (UTC)';
COMMENT ON COLUMN users.updated_at IS 'Last modification timestamp (UTC)';

-- ============================================================================
-- TASKS TABLE WITH FOREIGN KEY
-- ============================================================================

-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint with CASCADE delete
    -- When a user is deleted, all their tasks are automatically deleted
    CONSTRAINT fk_tasks_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    -- Additional constraints
    CONSTRAINT title_not_empty CHECK (LENGTH(TRIM(title)) > 0),
    CONSTRAINT title_length CHECK (LENGTH(title) <= 500),
    CONSTRAINT description_length CHECK (description IS NULL OR LENGTH(description) <= 5000)
);

-- Create index on user_id for fast filtering by owner
-- This is CRITICAL for performance when listing user's tasks
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Create composite index for paginated list queries (user_id + created_at)
-- Used for: SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC
CREATE INDEX idx_tasks_user_id_created_at ON tasks(user_id, created_at DESC);

-- Create index on completed status for filtered queries
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- Add comments for documentation
COMMENT ON TABLE tasks IS 'Todo tasks owned by users';
COMMENT ON COLUMN tasks.id IS 'Unique task identifier (UUID)';
COMMENT ON COLUMN tasks.user_id IS 'Owner of this task (foreign key to users.id with CASCADE delete)';
COMMENT ON COLUMN tasks.title IS 'Task title (required, max 500 characters)';
COMMENT ON COLUMN tasks.description IS 'Optional task description (max 5000 characters, can be NULL)';
COMMENT ON COLUMN tasks.completed IS 'Task completion status (true/false, defaults to false)';
COMMENT ON COLUMN tasks.created_at IS 'Task creation timestamp (UTC)';
COMMENT ON COLUMN tasks.updated_at IS 'Last modification timestamp (UTC)';

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATED_AT
-- ============================================================================

-- Function to automatically update updated_at timestamp on row updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger for tasks table
CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables created successfully
SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('users', 'tasks')
ORDER BY table_name;

-- Verify foreign key constraint exists
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
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name = 'tasks'
ORDER BY tc.constraint_name;

-- Verify indexes created successfully
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('users', 'tasks')
ORDER BY tablename, indexname;

-- Verify triggers created successfully
SELECT
    trigger_name,
    event_manipulation,
    event_object_table,
    action_timing
FROM information_schema.triggers
WHERE trigger_schema = 'public'
AND event_object_table IN ('users', 'tasks')
ORDER BY event_object_table, trigger_name;

-- ============================================================================
-- TEST DATA (OPTIONAL - for development only)
-- ============================================================================

-- Uncomment below to insert test users and tasks

/*
-- Insert test user
INSERT INTO users (id, email, password_hash, created_at, updated_at)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'test@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eBHnhxhIlqWK',  -- 'password123'
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert test tasks
INSERT INTO tasks (user_id, title, description, completed)
VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'Buy groceries', 'Milk, eggs, bread', false),
    ('550e8400-e29b-41d4-a716-446655440000', 'Finish project', 'Complete backend implementation', true),
    ('550e8400-e29b-41d4-a716-446655440000', 'Call dentist', NULL, false);

-- Verify test data
SELECT
    u.email,
    COUNT(t.id) as task_count
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.email;
*/

-- ============================================================================
-- NOTES
-- ============================================================================

-- Data Isolation Strategy:
-- 1. All task queries MUST include "WHERE user_id = <authenticated_user_id>"
-- 2. Foreign key constraint (fk_tasks_user_id) prevents orphaned tasks
-- 3. CASCADE DELETE removes user's tasks when user is deleted
-- 4. CASCADE UPDATE updates task.user_id if user.id changes (unlikely with UUID)
-- 5. Application layer validates URL user_id matches JWT user_id (403 if mismatch)

-- Security Considerations:
-- 1. Never store plain-text passwords (use bcrypt hash with 12+ rounds)
-- 2. Email uniqueness enforced at database level (UNIQUE constraint)
-- 3. UUIDs prevent enumeration attacks (unlike sequential integers)
-- 4. Timestamps provide audit trail for creation and modifications
-- 5. Email format validation at database level (CHECK constraint)

-- Performance Optimizations:
-- 1. UNIQUE index on users.email for fast login queries
-- 2. INDEX on tasks.user_id for fast owner-based filtering
-- 3. COMPOSITE index (user_id, created_at) for sorted list queries
-- 4. INDEX on tasks.completed for filtered queries (future enhancement)
-- 5. Connection pooling at application layer (see database.py)

-- Foreign Key Details:
-- - Constraint name: fk_tasks_user_id
-- - Column: tasks.user_id
-- - References: users.id
-- - ON DELETE CASCADE: Deleting user deletes all their tasks
-- - ON UPDATE CASCADE: Updating user.id updates all task.user_id (rare with UUID)
-- - Prevents: Creating tasks with non-existent user_id
-- - Prevents: Orphaned tasks if user is deleted

-- Testing Foreign Key:
-- 1. Try inserting task with non-existent user_id (should fail with FK violation)
-- 2. Create user, create tasks, delete user (tasks should auto-delete)
-- 3. Query tasks after user deletion (should return 0 rows)

-- Future Enhancements (not in v1):
-- 1. Soft delete for tasks (add deleted_at TIMESTAMP column, filter WHERE deleted_at IS NULL)
-- 2. Task sharing/collaboration (create user_task_access junction table)
-- 3. Task categories/tags (create tags table with many-to-many)
-- 4. Task due dates (add due_date TIMESTAMP column)
-- 5. Task priority levels (add priority INTEGER column)
-- 6. Full-text search on title/description (add GIN index with tsvector)
-- 7. Task attachments (add files table with FK to tasks.id)
