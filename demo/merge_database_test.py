import os
import sqlite3

# 指定要合并的SQLite文件所在的文件夹
folder_path = r"D:\c_question\prep_c_train_data\data\database"

# 指定要生成的合并后的数据库文件
output_db_file = r"D:\c_question\prep_c_train_data\data\merged.db"

# 创建新数据库文件
conn_main = sqlite3.connect(output_db_file)
cursor_main = conn_main.cursor()

# 循环遍历文件夹中的SQLite文件并执行合并操作
for subfolder in os.listdir(folder_path):
    subfolder_path = os.path.join(folder_path, subfolder)

    if os.path.isdir(subfolder_path):
        sqlite_file = os.path.join(subfolder_path, f"{subfolder}.sqlite")

        if os.path.isfile(sqlite_file):
            print(f"处理文件夹: {subfolder}")
            print(f"处理SQLite文件: {sqlite_file}")

            # 附加数据库
            cursor_main.execute(f"ATTACH DATABASE '{sqlite_file}' AS {subfolder}")

            # 复制表结构和数据
            for table_name in cursor_main.execute(f"SELECT name FROM {subfolder}.sqlite_master WHERE type='table'"):
                table_name = table_name[0]
                cursor_main.execute(
                    f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM {subfolder}.{table_name}"
                )

            # 分离数据库
            cursor_main.execute(f"DETACH DATABASE {subfolder}")

# 提交更改并关闭连接
conn_main.commit()
conn_main.close()

print("合并完成")
