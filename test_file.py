# import re
#
# pattern = re.compile(r'\d+[\u4e00-\u9fa5]+')
#
# # 测试
# text = "select T2.名称 , T2.类型 from 学校毕业人数 as T1 join 学校 as T2 on 学校毕业人数.学校id == 学校.词条id where T1.2016届人数 <= 4000 order by T1.2014届人数 asc"
# matches = pattern.findall(text)
# print(matches)


import sqlglot

sql = "select a.'25-30岁会员数量' / b.'25-30岁会员数量' from ( select 25-30岁会员数量 from 会员年龄分布 where 软件id == 'item_software_9_108' and 会员性别 == '男' ) a , ( select sum ( '25-30岁会员数量') from 会员年龄分布 where 软件id == 'item_software_9_108' ) b"

print(sqlglot.transpile(sql, identity=True)[0])