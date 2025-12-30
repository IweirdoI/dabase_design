# application/backend/routes/auth.py

from flask import Blueprint, request, jsonify, current_app
from db_helper import db    # ✅ 正确写法
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)


# ================= 1. 新增：token_required 装饰器 =================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求头获取 Token (格式通常是: Bearer <token>)
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # 这里简单处理，有些前端直接传 token，有些传 'Bearer token'
            # 兼容处理：如果包含空格，取第二个元素
            if ' ' in auth_header:
                token = auth_header.split(" ")[1]
            else:
                token = auth_header

        if not token:
            return jsonify({"code": 401, "msg": "Token丢失，请重新登录"}), 401

        try:
            # 解码 Token
            # 注意：需要在 config.py 中设置 SECRET_KEY，或者直接在这里写死一个字符串用于测试
            secret_key = current_app.config.get('SECRET_KEY', 'default_secret_key')
            data = jwt.decode(token, secret_key, algorithms=["HS256"])

            # ★★★ 关键：把解析出的信息挂载到 request 对象上，供后续路由使用 ★★★
            request.user_id = data['user_id']
            request.role = data['role']
        except jwt.ExpiredSignatureError:
            return jsonify({"code": 401, "msg": "Token已过期，请重新登录"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"code": 401, "msg": "Token无效"}), 401
        except Exception as e:
            return jsonify({"code": 500, "msg": f"Token解析失败: {str(e)}"}), 500

        return f(*args, **kwargs)

    return decorated


# ================================================================

@auth_bp.route('/login', methods=['POST'])
def login():
    # ... (前面的获取参数逻辑保持不变) ...
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not all([username, password, role]):
        return jsonify({"code": 400, "msg": "信息不完整"})

    user = None

    try:
        if role == 'student':
            sql = "SELECT * FROM student WHERE student_id = %s AND password = %s"
            result = db.fetch_all(sql, (username, password))
            if result:
                user = result[0]
                user['role'] = 'student'
        else:
            sql = "SELECT * FROM teacher WHERE teacher_id = %s AND password = %s"
            result = db.fetch_all(sql, (username, password))

            if result:
                temp_user = result[0]
                # 兼容处理：数据库字段是 role_type
                db_role = temp_user.get('role_type')

                # 严格校验：数据库里的角色必须等于前端请求的角色
                if db_role == role:
                    user = temp_user
                    user['role'] = role
                else:
                    return jsonify({"code": 403, "msg": "角色不匹配"})

        if user:
            # 构造 payload
            token_payload = {
                'user_id': username,
                'role': role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            # 生成 Token
            secret_key = current_app.config.get('SECRET_KEY', 'default_secret_key')
            token = jwt.encode(token_payload, secret_key, algorithm="HS256")

            user.pop('password', None)
            return jsonify(
                {
                    "code": 200,
                    "msg": "登录成功",
                    "data": {"token": token, "role": role, "info": user}
                })
        else:
            return jsonify({"code": 401, "msg": "账号或密码错误"})

    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"code": 500, "msg": f"服务器内部错误: {str(e)}"})


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    uid = data.get('username')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role')

    if not all([uid, password, name, role]):
        return jsonify({"code": 400, "msg": "所有字段必填"})

    try:
        # ★★★ 修正点：字段名必须完全对应 version_3.sql ★★★

        if role == 'student':
            # 1. 移除了 status (数据库没这字段)
            # 2. 增加了 dept_id (数据库必填)。
            # 注意：这里硬编码 class_id='1', dept_id='1'。
            # 请确保你的 database 里 class 表有一行 class_id='1'，department 表有一行 dept_id='1'
            sql = """
                  INSERT INTO student (student_id, name, password, class_id, dept_id)
                  VALUES (%s, %s, %s, '1', '1') \
                  """
            db.execute_update(sql, (uid, name, password))

        elif role in ['teacher', 'counselor', 'admin']:
            # 1. role 改为 role_type
            # 2. 移除了 status
            # 3. 硬编码 dept_id='1' (确保 department 表有此ID)
            sql = """
                  INSERT INTO teacher (teacher_id, name, password, dept_id, role_type)
                  VALUES (%s, %s, %s, '1', %s) \
                  """
            db.execute_update(sql, (uid, name, password, role))

        else:
            return jsonify({"code": 400, "msg": "无效的角色"})

        return jsonify({"code": 200, "msg": "注册成功，请直接登录"})

    except Exception as e:
        err_msg = str(e)
        if "Duplicate entry" in err_msg:
            return jsonify({"code": 400, "msg": "该账号已被注册"})
        # 捕获外键错误 (例如 class_id='1' 不存在)
        if "foreign key constraint fails" in err_msg:
            return jsonify({"code": 400, "msg": "注册失败：默认班级或学院ID(1)在数据库中不存在，请先创建基础数据。"})

        print(f"Register Error: {e}")
        return jsonify({"code": 500, "msg": f"注册失败: {err_msg}"})