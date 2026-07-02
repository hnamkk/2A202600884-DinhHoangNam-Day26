import sqlite3
import os

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    score REAL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    credits INTEGER
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
);
"""

SEED_SQL = """
INSERT INTO students (name, cohort, score) VALUES 
('Alice', 'A1', 85.5),
('Bob', 'A1', 92.0),
('Charlie', 'B2', 78.5),
('Diana', 'A1', 95.0),
('Eve', 'B2', 88.0);

INSERT INTO courses (title, credits) VALUES 
('Database Systems', 3),
('Machine Learning', 4),
('Web Development', 3);

INSERT INTO enrollments (student_id, course_id, status) VALUES 
(1, 1, 'enrolled'),
(1, 2, 'enrolled'),
(2, 1, 'completed'),
(3, 3, 'enrolled'),
(4, 2, 'completed');
"""

def create_database(db_path="sqlite_lab.db"):
    """
    1. Open SQLite database file.
    2. Execute schema SQL.
    3. Execute seed SQL.
    4. Commit.
    5. Return database path.
    """
    # Ensure directory exists if path has one
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    # Remove existing db to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.executescript(SCHEMA_SQL)
        cursor.executescript(SEED_SQL)
        conn.commit()
        print(f"Database successfully created and seeded at: {db_path}")
    except Exception as e:
        conn.rollback()
        print(f"Error creating database: {e}")
        raise
    finally:
        conn.close()
        
    return db_path

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "sqlite_lab.db")
    create_database(db_path)
