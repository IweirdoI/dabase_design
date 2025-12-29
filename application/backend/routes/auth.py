# routes/auth.py

from flask import Blueprint, request, jsonify
from db_helper import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')  # 这里通常是学号或工号
    password = data.get('password')
    role = data.get('role')  # 必须由前端传过来: 'admin', 'student', 'teacher', 'counselor'

    if not all([username, password, role]):
        return jsonify({"code": 400, "msg": "信息不完整"})

    # 1. 根据角色确定查询哪张表
    # 注意：这里假设你数据库里的表名分别是 Student, Teacher, Counselor, Admin
    # 且主键/账号字段分别是 student_id, teacher_id 等
    table_map = {
        'student': {'table': 'Student', 'id_col': 'student_id'},
        'teacher': {'table': 'Teacher', 'id_col': 'teacher_id'},
        'counselor': {'table': 'Counselor', 'id_col': 'counselor_id'},
        'admin': {'table': 'Admin', 'id_col': 'admin_id'}
    }

    if role not in table_map:
        return jsonify({"code": 400, "msg": "无效的角色类型"})

    target = table_map[role]
    table_name = target['table']
    id_col = target['id_col']

    # 2. 执行查询
    # 为了高分：这里其实应该用哈希加密 (MD5/SHA256)，但为了3天做完，先用明文对比
    # SQL: SELECT * FROM Student WHERE student_id = %s AND password = %s
    sql = f"SELECT * FROM {table_name} WHERE {id_col} = %s AND password = %s"

    try:
        users = db.fetch_all(sql, (username, password))

        if users:
            user = users[0]
            # 登录成功，返回用户信息
            # 注意：不要把 password 返回给前端
            user.pop('password', None)

            return jsonify(
                {
                    "code": 200,
                    "msg": "登录成功",
                    "data": {
                        "token": "fake-jwt-token-for-demo",  # 简单的项目不需要真 token，前端存一下 user info 即可
                        "role": role,
                        "info": user
                    }
                })
        else:
            return jsonify({"code": 401, "msg": "账号或密码错误"})

    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"code": 500, "msg": "服务器内部错误"})


# --- 扩展功能：注册 (满足文档中的人员注册要求) ---
@auth_bp.route('/register', methods=['POST'])
def register():
    # 这是一个简单的注册接口，你可以根据时间决定是否实现
    # 文档提到"人员注册审核" [cite: 40]，简单的做法是注册后 status=0 (待审核)
    return jsonify({"code": 200, "msg": "注册接口开发中"})