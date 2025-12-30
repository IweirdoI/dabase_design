# check_db.py
from db_helper import db

print("====== 数据库连接检查 ======")
try:
    # 1. 检查当前连的是哪个数据库
    db_name = db.fetch_all("SELECT DATABASE() as db_name")[0]['db_name']
    print(f"✅ Python 当前连接的数据库名: 【{db_name}】")

    # 2. 检查 student 表里到底有哪些列
    print(f"正在检查 {db_name} 库中的 student 表结构...")
    columns = db.fetch_all("DESCRIBE student")

    found_dept_id = False
    print("------------------------------------------------")
    print(f"{'字段名 (Field)':<20} | {'类型 (Type)':<20}")
    print("------------------------------------------------")
    for col in columns:
        print(f"{col['Field']:<20} | {col['Type']:<20}")
        if col['Field'] == 'dept_id':
            found_dept_id = True

    print("------------------------------------------------")
    if found_dept_id:
        print("🎉 结果: student 表里【有】dept_id 字段！")
        print("👉 如果你还是报错，说明你可能没重启 app.py，或者报错的是 teacher 表。")
    else:
        print("❌ 结果: student 表里【没有】dept_id 字段！")
        print("👉 真相只有一个：你刚才修复的是另一个数据库，或者另一个表。")

        # 尝试自动修复
        print("\n正在尝试通过 Python 自动修复...")
        db.execute_update("ALTER TABLE student ADD COLUMN dept_id VARCHAR(45) NOT NULL DEFAULT '1'")
        print("✅ 修复指令已发送，请重启 app.py 再试！")

except Exception as e:
    print(f"❌ 发生错误: {e}")