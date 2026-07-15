# in this we'll do the creation, updation, read on database

import sqlite3
from config import get_db_connection
from schema import ShortenRequest
from short_code import generate_short_code
from datetime import datetime, timezone, timedelta


def get_active_url(original_url:str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #let's check whether there is any existing short code alrready exist in the db for the url
    
    try:
        cursor.execute("Select * from urls where original_url = ?", (original_url,))
        now = datetime.now(timezone.utc)
        rows = cursor.fetchall()
        for row in rows:
            
            if row['expires_at'] is None:
                return dict(row)
            
            expiry = datetime.fromisoformat(row['expires_at'])
            
            if expiry > now:
                return dict(row)
            
        return None
    except Exception as e:
        raise e
    
    finally:
        conn.close()
        

def create_short_url(payload: ShortenRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now(timezone.utc)
        expires_at = None
        if payload.expires_in_days is not None and payload.expires_in_days > 0:
            expires_at = (now + timedelta(days = payload.expires_in_days) ).isoformat()       

        while True:
            short_code = generate_short_code()
            cursor.execute("Select 1 FROM urls WHERE short_code=?", (short_code,))
            
            if not cursor.fetchone():
                break
            
        cursor.execute(
            """INSERT INTO urls (short_code, original_url, created_at, expires_at)
            VALUES (?,?,?,?)
            """,
            (short_code, payload.original_url, now.isoformat(), expires_at)
        )
        conn.commit()
        return {
            "short_code": short_code,
            "original_url": payload.original_url,
            "expires_at": expires_at
            
            }
    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()        
        

def get_url_record(short_code:str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM urls WHERE short_code = ?", (short_code, ))
        row = cursor.fetchone()
        return dict(row)
    except Exception as e:
        raise e
    finally: 
        conn.close()

def update_clicks(short_code:str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
        """ 
            UPDATE urls 
            SET click_count = click_count+1, last_accessed = ?
            WHERE short_code = ?""",
            (now, short_code)
        )
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
        
    finally:
        conn.close()
        
        
def get_all_urls(page:int, limit: int):
    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        offset = (page-1)*limit
        
        cursor.execute("SELECT*FROM urls LIMIT ? OFFSET ?",(limit, offset))
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]

    
    
    except Exception as e:
        raise e
        
    finally:
        conn.close()
        
    