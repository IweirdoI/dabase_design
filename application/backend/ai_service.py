# 这里模拟一个 AI，或者你可以接入 DeepSeek/OpenAI 的 API
import random


def analyze_student_grades(student_name, grades_list):
    """
    grades_list 格式: [{'course': '数据库', 'score': 55}, {'course': 'Java', 'score': 88}]
    """

    # --- 方案 A: 真正的 API 调用 (推荐) ---
    # client = OpenAI(api_key="你的KEY", base_url="...")
    # prompt = f"分析学生 {student_name} 的成绩: {grades_list}..."
    # ...

    # --- 方案 B: 快速 Mock (省钱省事，演示用) ---
    # 计算不及格科目
    failed_courses = [g['course'] for g in grades_list if g['score'] < 60]

    if failed_courses:
        return f"【AI学业预警】该生在 {', '.join(failed_courses)} 课程中存在挂科风险。建议辅导员立即安排面谈，重点辅导基础薄弱环节。"
    else:
        return f"【AI综合评价】该生学业表现良好，基础扎实。建议鼓励其参加学科竞赛，进一步提升专业能力。"