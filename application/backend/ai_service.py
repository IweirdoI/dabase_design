# ai_service.py
from openai import OpenAI
import json

# 配置 DeepSeek 客户端
# 如果你用其他模型（如阿里通义、Kimi），只需要改 base_url 和 api_key
client = OpenAI(
    api_key=MC-"74B26A8448B84629A44E384CEC648F44",  # ★★★ 记得替换成你的 Key ★★★
    base_url="https://api.mindcraft.com.cn/v1"
)

def generate_academic_report(student_name, grades_data):
    """
    调用 AI 生成学业分析报告
    :param student_name: 学生姓名
    :param grades_data: 成绩列表 [{'course_name': '数据库', 'score': 88}, ...]
    :return: AI 生成的文本
    """
    
    # 1. 构造提示词 (Prompt) - 这是拿高分的关键！
    # 把枯燥的数据转换成 AI 能看懂的自然语言
    data_str = json.dumps(grades_data, ensure_ascii=False)
    
    system_prompt = """
    你是一位经验丰富的大学辅导员，负责学生学业预警和指导工作。
    你的任务是根据学生的成绩单，生成一份简短、专业且带有某种程度人文关怀的学业诊断报告。
    """
    
    user_prompt = f"""
    学生姓名：{student_name}
    成绩数据：{data_str}
    
    请输出一段分析，要求：
    1. 字数控制在 200 字以内。
    2. 首先总结该生的整体表现（优秀/良好/需努力）。
    3. 重点指出不及格的课程（如果有），并分析可能的原因（逻辑严厉）。
    4. 对高分课程给予肯定。
    5. 最后给出具体的学习建议。
    6. 语气要像老师对学生说话，不要用 markdown 格式，直接输出纯文本。
    """

    try:
        # 2. 发送请求给 AI
        response = client.chat.completions.create(
            model="deepseek-chat",  # 使用 DeepSeek V3 模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
            temperature=0.7, # 创造性 (0-1)，0.7 比较自然
        )
        
        # 3. 获取结果
        return response.choices[0].message.content

    except Exception as e:
        print(f"AI 调用失败: {e}")
        return "（系统提示：AI 服务暂时不可用，请联系管理员。但这不影响系统其他功能。）"