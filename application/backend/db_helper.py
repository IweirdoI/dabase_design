import pymysql
from config import DB_CONFIG

class DBHelper:
    def get_connection(self):
        return pymysql.connect(**DB_CONFIG)

    # 1. 普通查询 (用于查表、视图)
    def fetch_all(self, sql, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    # 2. 执行更新 (增删改)
    def execute_update(self, sql, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()

    # 3. ★★★ 高分点：调用存储过程 ★★★
    # 专门用于调用你在数据库里写的 sp_student_enroll 等过程
    def call_procedure(self, proc_name, args=()):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.callproc(proc_name, args)
                # 获取存储过程的返回结果 (如果有 SELECT 输出)
                result = cursor.fetchall()
                conn.commit()
                return result
        finally:
            conn.close()

db = DBHelper()