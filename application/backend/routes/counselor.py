from flask import Blueprint, request, jsonify
from db_helper import db
from ai_service import analyze_student_grades

counselor_bp = Blueprint('counselor', __name__)


@counselor_bp.route('/analyze_student', methods=['POST'])
def analyze():
    data = request.json
    student_id = data.get('student_id')

    # 1. 先从数据库查出成绩 (利用视图 v_student_grades)
    sql = "SELECT course_name as course, score FROM v_student_grades WHERE student_id = %s"
    grades = db.fetch_all(sql, (student_id,))

    if not grades:
        return jsonify({"msg": "该生无成绩记录"})

    # 2. 调用 AI 模块进行分析
    # 假设查出来名字叫 "张三"
    report = analyze_student_grades("张三", grades)

    return jsonify(
        {
            "code": 200,
            "student_id": student_id,
            "ai_report": report  # 前端直接把这段字展示在弹窗里
        })