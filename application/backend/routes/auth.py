# routes/auth.py

from flask import Blueprint, request, jsonify
from db_helper import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')  # 前端传来的: student, teacher, counselor, admin

    if not all([username, password, role]):
        return jsonify({"code": 400, "msg": "信息不完整"})

    user = None
    
    try:
        # === 变化点开始 ===
        if role == 'student':
            # 1. 学生：查 Student 表
            sql = "INSERT INTO student (student_id, name, password, class_id, status) VALUES (%s, %s, %s, 1, 1)"
            result = db.fetch_all(sql, (username, password))
            if result:
                user = result[0]
                # 强行补充 role 字段给前端用
                user['role'] = 'student' 
        
        else:
            # 2. 非学生（老师/辅导员/管理员）：全部查 Teacher 表
            sql = "SELECT * FROM teacher WHERE teacher_id = %s AND password = %s"
            result = db.fetch_all(sql, (username, password))
            
            if result:
                temp_user = result[0]
                # 3. 权限校验：数据库里的 role 必须和前端请求的 role 一致
                # 比如：数据库存的是 'teacher'，前端请求 'admin' -> 拒绝
                if temp_user['role'] == role:
                    user = temp_user
                else:
                    return jsonify({"code": 403, "msg": "您没有该角色的登录权限"})
        # === 变化点结束 ===

        if user:
            user.pop('password', None) # 安全起见，移除密码
            return jsonify({
                "code": 200,
                "msg": "登录成功",
                "data": {
                    "token": "demo_token", 
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
#添加到 routes/auth.py 中

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    # 1. 获取前端填写的注册信息
    uid = data.get('username')   # 学号或工号
    password = data.get('password')
    name = data.get('name')
    role = data.get('role')      # student, teacher, counselor, admin
    
    # 必填项检查
    if not all([uid, password, name, role]):
        return jsonify({"code": 400, "msg": "所有字段（账号、密码、姓名、角色）均为必填"})

    try:
        # 2. 根据角色判断插入哪张表
        if role == 'student':
            # 插入学生表 (注意：class_id 这里为了简化，你可以先写死一个存在的班级ID，比如1)
            # 或者前端注册时必须填班级ID，这里假设先填 1 保证能跑
            sql = "INSERT INTO student (student_id, name, password, class_id, status) VALUES (%s, %s, %s, 1, 1)"
            db.execute_update(sql, (uid, name, password))
            
        elif role in ['teacher', 'counselor', 'admin']:
            # 插入教工表
            # 注意：dept_id 写死为 1 (计算机学院)，简化流程
            sql = "INSERT INTO teacher (teacher_id, name, password, dept_id, role, status) VALUES (%s, %s, %s, 1, %s, 1)"
            db.execute_update(sql, (uid, name, password, role))
            
        else:
            return jsonify({"code": 400, "msg": "无效的角色"})

        return jsonify({"code": 200, "msg": "注册成功，请直接登录"})

    except Exception as e:
        # 最常见的报错是：主键冲突 (学号已存在)
        if "Duplicate entry" in str(e):
            return jsonify({"code": 400, "msg": "该账号已被注册"})
        print(f"Register Error: {e}")
        return jsonify({"code": 500, "msg": "注册失败: 服务器内部错误"})