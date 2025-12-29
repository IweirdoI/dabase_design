from openai import OpenAI
import json

# ================= 配置区域 =================
# 替换为你自己的 API Key
API_KEY = "MC-74B26A8448B84629A44E384CEC648F44" 
BASE_URL = 'https://api.mindcraft.com.cn/v1/'
MODEL_NAME = "deepseek-reasoner" # 使用你示例代码中的模型
# ===========================================

# 初始化客户端
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def generate_academic_report(student_name, grades_data):
    """
    调用 MindCraft AI 生成学业分析报告
    :param student_name: 学生姓名
    :param grades_data: 成绩列表 (字典或列表)
    :return: AI 生成的文本字符串
    """
    
    # 1. 把成绩数据转换成字符串，方便 AI 阅读
    data_str = json.dumps(grades_data, ensure_ascii=False)
    
    # 2. 定义角色 (System Prompt) - 这里不能用“智酱”，要设定为“辅导员”
    system_prompt = """
    你是一名大学辅导员，负责学生学业预警工作。
    你的任务是根据学生的成绩单，生成一份简短、专业但有人情味的学业分析报告。
    """
    
    # 3. 定义用户输入 (User Prompt)
    user_prompt = f"""
    学生姓名：{student_name}
    成绩数据：{data_str}
    
    请生成一段200字以内的分析，要求：
    1. 先总结整体表现。
    2. 如果有不及格（<60分）的科目，请严肃指出并分析原因。
    3. 如果有高分科目，给予表扬。
    4. 最后给出具体的学习建议。
    5. 不要使用Markdown格式，直接输出纯文本。
    """

    try:
        # 4. 调用 MindCraft 接口
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2, # 降低随机性，让回答更稳定
            max_tokens=2000,
            stream=False,    # ★★★ 关键修改：改为 False，方便后端直接获取完整结果
            extra_body={
                'reason': False, # 按照你的示例，关闭深度思考模式以加快速度
            }
        )

        # 5. 提取并返回内容 (非流式写法)
        # 检查是否有返回内容
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "AI 未返回有效内容。"

    except Exception as e:
        print(f"MindCraft API 调用失败: {e}")
        return "（系统提示：AI 服务暂时繁忙，请稍后再试。）"

# --- 测试代码 (你可以直接运行这个文件测试 key 对不对) ---
if __name__ == '__main__':
    print("正在测试连接 MindCraft...")
    test_grades = [{'course_name': '数据库', 'score': 55}, {'course_name': 'Java', 'score': 88}]
    print(generate_academic_report("测试学生", test_grades))