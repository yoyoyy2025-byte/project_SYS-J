# user_db.py (새로 만들기)
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "monitor/user_history.db"

def init_user_db():
    """사용자 데이터 저장용 DB 테이블 생성"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 자소서 내용(input)과 AI의 조언(output)을 모두 저장
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_input TEXT,
            ai_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_message(user_input, ai_response):
    """채팅 내용 저장"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO history (timestamp, user_input, ai_response) 
        VALUES (?, ?, ?)
    ''', (now, user_input, ai_response))
    
    conn.commit()
    conn.close()

def get_all_history():
    """저장된 모든 데이터 가져오기 (관리자용)"""
    conn = sqlite3.connect(DB_NAME)
    # pandas를 이용해 보기 좋은 표 형태로 가져옴
    df = pd.read_sql_query("SELECT * FROM history ORDER BY id DESC", conn)
    conn.close()
    return df