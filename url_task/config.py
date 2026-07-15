# for database connection
import sqlite3

DB_NAME = "url_shortener.db"

def get_db_connection():
    
    conn = sqlite3.connect(DB_NAME)
    
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    
    # it will create the necessary db table if doesn't exit alredy
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls(
            short_code TEXT PRIMARY KEY, 
            original_url TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            click_count INTEGER DEFAULT 0,
            last_accessed TEXT
        )
                   
                   """)
    conn.commit()
    conn.close()
