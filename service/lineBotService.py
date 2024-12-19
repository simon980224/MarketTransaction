from datetime import datetime
import sqlite3

# 統一管理資料庫位置
DATABASE_PATH = 'transaction.db'


def insert_data(user_id, message, event_time):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql = '''
            INSERT INTO LineBot (Line_Id, Text, Event_Time)
            VALUES (?, ?, ?)
        '''
        cursor.execute(sql, (user_id, message, event_time))

        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
