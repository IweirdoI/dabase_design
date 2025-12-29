# config.py
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',      # 数据库地址，通常是 localhost
    'port': 3306,             # 默认端口
    'user': 'root',           # 你的数据库用户名
    'password': '050818', # ★★★ 记得改成你的 MySQL 密码 ★★★
    'db': 'teaching_system',  # 你的数据库名
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor # 让查询结果返回字典 {'id': 1} 而不是元组 (1,)
}

# Flask配置
SECRET_KEY = 'super_secret_key_for_session' # 用于加密 Session，随便填一串字符