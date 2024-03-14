import pandas as pd
import sqlite3
import json

# 读取 JSON 文件
with open('school_detail.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取 'data' 部分
df = pd.json_normalize(data['data'])

# 创建 SQLite 数据库连接
conn = sqlite3.connect('school_detail.sqlite')

# 将 DataFrame 写入 SQLite 数据库
df.to_sql('school_detail', conn, if_exists='replace', index=False)

# 关闭数据库连接
conn.close()
print("Done!")