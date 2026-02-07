# Database Connection Guide - Neon PostgreSQL

## Connection String

```
postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Components:**
- **Protocol:** postgresql://
- **Username:** neondb_owner
- **Password:** npg_p7umtUsZckD6
- **Host:** ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech
- **Port:** 5432 (default, omitted)
- **Database:** neondb
- **SSL Mode:** require (mandatory)
- **Channel Binding:** require (enhanced security)

---

## Python (psycopg2) - Recommended for Backend

### Installation
```bash
pip install psycopg2-binary
```

### Basic Connection
```python
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connection string
CONNECTION_STRING = "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Connect
conn = psycopg2.connect(CONNECTION_STRING)
cursor = conn.cursor()

# Execute query
cursor.execute("SELECT COUNT(*) FROM users;")
user_count = cursor.fetchone()[0]
print(f"Total users: {user_count}")

# Close
cursor.close()
conn.close()
```

### With Connection Pool (Production)
```python
from psycopg2 import pool

# Create connection pool (singleton)
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn="postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# Get connection from pool
conn = connection_pool.getconn()

try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
    user = cursor.fetchone()
finally:
    cursor.close()
    connection_pool.putconn(conn)  # Return to pool
```

### With SQLModel/SQLAlchemy (ORM)
```python
from sqlmodel import create_engine, Session

# Create engine
DATABASE_URL = "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging
    pool_pre_ping=True,  # Verify connections before use
    pool_size=10,  # Connection pool size
    max_overflow=5  # Max overflow connections
)

# Use session
with Session(engine) as session:
    users = session.query(User).filter(User.email == email).all()
```

---

## Python (asyncpg) - For Async FastAPI

### Installation
```bash
pip install asyncpg
```

### Async Connection
```python
import asyncpg

DATABASE_URL = "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Create connection pool
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=1,
    max_size=10,
    command_timeout=60
)

# Execute query
async with pool.acquire() as conn:
    rows = await conn.fetch("SELECT * FROM users WHERE email = $1;", email)

# Close pool (on shutdown)
await pool.close()
```

### With Databases Library (Recommended for FastAPI)
```python
import databases

DATABASE_URL = "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

database = databases.Database(DATABASE_URL)

# Startup (in FastAPI)
@app.on_event("startup")
async def startup():
    await database.connect()

# Shutdown
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Query
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    query = "SELECT * FROM users WHERE id = :user_id"
    user = await database.fetch_one(query, values={"user_id": user_id})
    return user
```

---

## Node.js (pg) - For JavaScript/TypeScript

### Installation
```bash
npm install pg
```

### Basic Connection
```javascript
const { Client } = require('pg');

const client = new Client({
  connectionString: 'postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require',
  ssl: {
    rejectUnauthorized: true
  }
});

await client.connect();

// Query with parameters (prevents SQL injection)
const result = await client.query(
  'SELECT * FROM users WHERE email = $1',
  [email]
);

console.log(result.rows);

await client.end();
```

### With Connection Pool
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: 'postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require',
  ssl: {
    rejectUnauthorized: true
  },
  max: 10,  // Pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Query
const { rows } = await pool.query(
  'SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC',
  [userId]
);

// Don't forget to end pool on shutdown
await pool.end();
```

---

## psql (Command Line) - For Development/Debugging

### Connect
```bash
psql "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

### Common Commands
```sql
-- List tables
\dt

-- Describe users table
\d users

-- Describe tasks table
\d tasks

-- List indexes
\di

-- View table sizes
\dt+

-- Execute query
SELECT * FROM users LIMIT 5;

-- Quit
\q
```

---

## Environment Variables (Recommended)

### .env File (DO NOT COMMIT!)
```bash
# Database Configuration
DATABASE_URL=postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require

# Alternative: Separate components
DB_HOST=ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_p7umtUsZckD6
DB_SSL_MODE=require
```

### Load in Python
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
```

### Load in Node.js
```javascript
require('dotenv').config();

const DATABASE_URL = process.env.DATABASE_URL;
```

---

## Connection Pooling Best Practices

### Pool Size Guidelines

**Development:**
- Min: 1 connection
- Max: 5 connections

**Production:**
- Min: 5 connections
- Max: 20 connections (adjust based on load)

**Formula:**
```
max_pool_size = (num_workers * expected_concurrent_queries) + buffer
```

**Example:**
- 4 Uvicorn workers
- 3 concurrent queries per worker
- 2 connection buffer
- Result: 4 * 3 + 2 = 14 connections

### Connection Timeout Configuration

```python
# Python (psycopg2)
connection_pool = pool.SimpleConnectionPool(
    minconn=5,
    maxconn=20,
    dsn=DATABASE_URL,
    connect_timeout=10,  # Connection timeout (seconds)
    options="-c statement_timeout=30000"  # Query timeout (ms)
)
```

```javascript
// Node.js (pg)
const pool = new Pool({
  connectionString: DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,  // Close idle connections after 30s
  connectionTimeoutMillis: 10000,  // Connection timeout: 10s
  statement_timeout: 30000  // Query timeout: 30s
});
```

---

## Error Handling

### Python
```python
import psycopg2
from psycopg2 import errorcodes

try:
    cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s);", (email, hash))
    conn.commit()
except psycopg2.errors.UniqueViolation:
    print("Error: Email already exists")
    conn.rollback()
except psycopg2.errors.ForeignKeyViolation:
    print("Error: Referenced user does not exist")
    conn.rollback()
except psycopg2.Error as e:
    print(f"Database error: {e}")
    conn.rollback()
```

### Node.js
```javascript
try {
  await client.query(
    'INSERT INTO users (email, password_hash) VALUES ($1, $2)',
    [email, hash]
  );
} catch (err) {
  if (err.code === '23505') {  // Unique violation
    console.error('Email already exists');
  } else if (err.code === '23503') {  // Foreign key violation
    console.error('Referenced user does not exist');
  } else {
    console.error('Database error:', err);
  }
}
```

---

## Security Checklist

- [ ] Never commit connection string to Git
- [ ] Use environment variables for credentials
- [ ] Always use parameterized queries (never string concatenation)
- [ ] Enable SSL mode (required for Neon)
- [ ] Use connection pooling (don't create new connections per request)
- [ ] Set query timeouts to prevent long-running queries
- [ ] Validate input at application layer before database queries
- [ ] Use least-privilege database user (current user is owner, consider read-only users for reporting)
- [ ] Monitor connection pool exhaustion
- [ ] Log connection errors for debugging

---

## Troubleshooting

### Problem: Connection Refused
```
Error: connection refused at host:port
```

**Solutions:**
1. Check if host/port are correct
2. Verify SSL mode is set to "require"
3. Check network/firewall settings
4. Verify Neon database is not paused (auto-scales from 0)

### Problem: Too Many Connections
```
Error: FATAL: sorry, too many clients already
```

**Solutions:**
1. Reduce connection pool size
2. Use Neon pooler endpoint (already used in current connection string)
3. Close connections properly (use try/finally)
4. Investigate connection leaks

### Problem: SSL/TLS Error
```
Error: SSL connection has been closed unexpectedly
```

**Solutions:**
1. Ensure `sslmode=require` is in connection string
2. Update SSL certificates on client machine
3. Check if SSL library is installed (psycopg2 needs libpq)

### Problem: Query Timeout
```
Error: canceling statement due to statement timeout
```

**Solutions:**
1. Optimize query (check EXPLAIN ANALYZE)
2. Add appropriate indexes
3. Increase statement_timeout if legitimate slow query
4. Use pagination for large result sets

### Problem: Foreign Key Violation
```
Error: insert or update on table "tasks" violates foreign key constraint "fk_tasks_user_id"
```

**Solutions:**
1. Verify user_id exists before inserting task
2. Check JWT token for correct user_id
3. Ensure user was not deleted (CASCADE DELETE)

---

## Performance Testing

### Connection Test Script (Python)
```python
import time
import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_p7umtUsZckD6@ep-bitter-shadow-aixb0dsf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Test connection time
start = time.time()
conn = psycopg2.connect(DATABASE_URL)
connect_time = (time.time() - start) * 1000
print(f"Connection time: {connect_time:.2f}ms")

# Test query time
cursor = conn.cursor()
start = time.time()
cursor.execute("SELECT COUNT(*) FROM users;")
query_time = (time.time() - start) * 1000
print(f"Query time: {query_time:.2f}ms")

cursor.close()
conn.close()
```

### Expected Results
- **Connection time:** 100-500ms (first connection)
- **Connection time (pooled):** 1-10ms (subsequent)
- **Simple query:** 5-50ms
- **Indexed query:** 10-100ms
- **Complex join:** 50-500ms

---

## Quick Reference

### Python Connection Template
```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

try:
    cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
    user = cursor.fetchone()
finally:
    cursor.close()
    conn.close()
```

### Python Transaction Template
```python
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id;", (email, hash))
    user_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO tasks (user_id, title) VALUES (%s, %s);", (user_id, title))

    conn.commit()
except Exception as e:
    conn.rollback()
    raise e
finally:
    cursor.close()
    conn.close()
```

---

## Next Steps

1. **Test Connection:** Run `python final_verification.py` to verify database setup
2. **Configure Backend:** Update `backend/database.py` with connection string (use env vars)
3. **Test API:** Start backend and test endpoints at http://localhost:8000/docs
4. **Monitor Performance:** Use Neon console to monitor query performance
5. **Set Up CI/CD:** Add database URL to deployment environment variables

---

## Support

**Neon Documentation:** https://neon.tech/docs
**PostgreSQL Documentation:** https://www.postgresql.org/docs/
**psycopg2 Documentation:** https://www.psycopg.org/docs/

**Database Status:**
- Tables: ✓ Created
- Foreign Keys: ✓ Active
- Indexes: ✓ Optimized
- Triggers: ✓ Active
- Ready: ✓ Yes
