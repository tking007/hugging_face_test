from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QMessageBox

def create_connection():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setHostName("127.0..0.1")
    # db.setDatabaseName("Z:/db.sqlite3")  # 连接的数据库
    db.setDatabaseName("db.sqlite3")  # 连接的数据库
    db.setPort(3306)
    db.setUserName("root")
    # db.setPassword("123")

    if not db.open():
        QMessageBox.warning(None, "Database Error", db.lastError().text())
        return False
    else:
        # print("Connected to SQLite")
        return True

def close_connection():
    db = QSqlDatabase.database()
    db.close()

# # 使用数据库
# if create_connection():
#     query = QSqlQuery()
#     query.exec_("SELECT * FROM student")  # 遍历数据表格 student 每一行，从第 0 行到最后一行
#
#     while query.next():
#         name = query.value(0).toString().strip()  # strip函数表示去除字符串两边的空格
#         age = query.value(1).toString().strip()
#         print(name, age)
#
#     close_connection()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    while True:
        create_connection()
    # create_connection()
    # sys.exit(app.exec_())