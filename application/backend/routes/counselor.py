# routes/counselor.py
from flask import Blueprint, request, jsonify
from db_helper import db
from ai_service import generate_academic_report # 导入刚才写好的 AI 模块

counselor_bp = Blueprint('counselor', __name__)

@counselor_bp.route('/analyze_student', methods=['POST'])
def analyze_student():
    data = request.json
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({"code": 400, "msg": "未提供学生ID"})

    try:
        # 1. 先去数据库查该学生的基本信息 (姓名)
        user_sql = "SELECT name FROM student WHERE student_id = %s"
        user_res = db.fetch_all(user_sql, (student_id,))
        if not user_res:
            return jsonify({"code": 404, "msg": "学生不存在"})
        student_name = user_res[0]['name']

        # 2. 利用之前建立的高分视图 v_student_grades 查成绩
        # 视图里有：course_name, score, credits...
        grade_sql = "SELECT course_name, score FROM v_student_grades WHERE student_id = %s"
        grades = db.fetch_all(grade_sql, (student_id,))

        if not grades:
            return jsonify({"code": 200, "ai_report": f"{student_name} 同学暂无任何成绩记录，无法进行分析。"})

        # 3. ★★★ 调用 AI 生成报告 ★★★
        # 这一步会稍微慢一点（约1-3秒），因为在等 AI 思考
        report = generate_academic_report(student_name, grades)

        return jsonify({
            "code": 200,
            "data": {
                "student_id": student_id,
                "name": student_name,
                "ai_report": report # 把这段话发给前端显示
            }
        })

    except Exception as e:
        print(f"Analyze Error: {e}")
        return jsonify({"code": 500, "msg": "分析服务出错"})
