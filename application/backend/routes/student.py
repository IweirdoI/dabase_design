from flask import Blueprint, request, jsonify
from db_helper import db

student_bp = Blueprint('student', __name__)


@student_bp.route('/enroll', methods=['POST'])
def enroll_course():
    data = request.json
    student_id = data.get('student_id')
    schedule_id = data.get('schedule_id')

    # ★★★ 核心高分点 ★★★
    # 不要在 Python 里写 if (count > capacity)，直接调存储过程！
    # 假设存储过程 sp_enroll_course(uid, sid, @out_result)
    try:
        # 这里需要根据你实际的存储过程写法调整
        # 有些存储过程是通过 SELECT 返回结果，有些是通过 OUT 参数
        # 简单起见，假设你的存储过程若成功无报错，若失败抛出 SQL 异常
        db.call_procedure('sp_student_enroll', (student_id, schedule_id, ''))

        # 或者是读取 OUT 参数逻辑 (视具体 SQL 写法而定)
        return jsonify({"code": 200, "msg": "选课成功"})

    except Exception as e:
        return jsonify({"code": 500, "msg": f"选课失败: {str(e)}"})