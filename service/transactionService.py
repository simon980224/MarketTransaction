from datetime import datetime
import sqlite3

# 統一管理資料庫位置
DATABASE_PATH = 'transaction.db'


def getData(userId=None, startDate=None, endDate=None, transType=None):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql = '''
            SELECT 
                User.User_Id, 
                User_Name,
                Trans_Amount, 
                Trans_Date, 
                Trans_Company,
                CASE 
                    WHEN Trans_Type = 'I' THEN '入帳'
                    WHEN Trans_Type = 'O' THEN '回款'
                    ELSE Trans_Type
                END AS Trans_Type,
                Remark
            FROM 
                "Transaction"
            JOIN User ON "Transaction".User_Id = User.User_Id
            WHERE 
                1=1
        '''
        parameters = []

        if userId:
            sql += ' AND User_Id LIKE ?'
            parameters.append(f"%{userId}%")
        if startDate and endDate:
            sql += ' AND Trans_Date BETWEEN ? AND ?'
            parameters.append(startDate)
            parameters.append(endDate)
        if transType:
            placeholders = ', '.join('?' for _ in transType)
            sql += f' AND Trans_Type IN ({placeholders})'
            parameters.extend(transType)

        sql += '''
            ORDER BY Trans_Id DESC
        '''

        cursor.execute(sql, parameters)
        results = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        Transactions = [dict(zip(column_names, row)) for row in results]

        total_Amount = sum(transaction['Trans_Amount'] for transaction in Transactions)

        return {
            'Transactions': Transactions,
            'total_Amount': f"{total_Amount:,.0f}"
        }

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return {
            'Transactions': [],
            'total_Amount': 0
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def checkUserExists(userId):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT User_Id FROM User WHERE User_Id = ?
        """, (userId,))
        result = cursor.fetchone()

        return result is not None

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def addTransaction(userId, amount, date, transType, remark):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql = '''
            INSERT INTO "Transaction" (Trans_Id, User_Id, Trans_Amount, Trans_Date, Trans_Type, Remark)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(sql, (getNewTransId(), userId,
                       amount, date, transType, remark))

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


def getNewTransId():
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        today = datetime.now()
        year = today.year % 100  # 取得年份的後兩位
        month = today.month
        day = today.day

        # 格式化日期部分
        date_part = f"{year:02}{month:02}{day:02}"

        # 查詢當日最大交易編號
        cursor.execute("""
            SELECT Trans_Id FROM "Transaction" 
            WHERE Trans_Id LIKE ? 
            ORDER BY Trans_Id DESC 
            LIMIT 1
        """, (f"%{date_part}%",))
        result = cursor.fetchone()

        if result:
            # 解析出編號部分，並遞增
            last_id = result[0]
            last_number = int(last_id.split('_')[2])
            next_number = last_number + 1
        else:
            # 如果沒有當天的交易，從1開始
            next_number = 1

        # 返回新的交易編號，並在前面加上 "T"
        return f"T_{date_part}_{next_number:03}"

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def getUserData():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    sql = '''
        SELECT 
            *
        FROM User
    '''

    cursor.execute(sql)
    results = cursor.fetchall()

    column_names = [description[0] for description in cursor.description]

    return [dict(zip(column_names, row)) for row in results]
