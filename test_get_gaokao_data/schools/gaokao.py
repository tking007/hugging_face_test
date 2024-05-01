# coding:utf-8
import requests
import json
import codecs
import time
from lxml import etree
import xlsxwriter

file = codecs.open("college1111.json", 'a', encoding='utf-8')
# 存储学校名字
names = []
# 学校详情页链接
college_urls = []
# 学校所在地
places = []
# 学校特色
tesess = []
# 学校类型
TYPEs = []
# 学校隶属部门
bumens = []
# 学校性质
xingzhis = []
# 学校主页官方链接
school_urls = []
# 总共有107页，依次遍历所有页面，获取学校数据
for i in range(1, 108):
    # 构造页面链接
    url = 'http://college.gaokao.com/schlist/p' + str(i) + '/'
    print(url)
    try:
        # 使用requests获取网页数据
        # 该网页没有反爬虫，不需要修改请求头部照样可以获取网页数据
        htmls = requests.get(url)
        html = htmls.text
        tree = etree.HTML(html)
        # 所有的数据都在dl节点下，先获取所有的dl节点，再依次遍历该节点
        universitys = tree.xpath('//*[@id="wrapper"]/div[4]/div[1]/dl')
        print(len(universitys))
        # 遍历所有的dl节点，提取数据
        for j in range(len(universitys)):
            university = universitys[j]
            # 学校名字
            name = university.xpath('dt/strong/a/text()')
            names.append(name[0])
            # 详情链接
            college_url = university.xpath('dt/strong/a/@href')
            college_urls.append(college_url[0])

            # 学校地点
            place = university.xpath('dd/ul/li[1]/text()')
            places.append(place[0])
            # 学校特色
            tese = university.xpath('dd/ul/li[2]/text()|dd/ul/li[2]/span/text()')
            teses = ' '.join(tese)
            tesess.append(teses)
            # 学校类型
            TYPE = university.xpath('dd/ul/li[3]/text()')
            TYPEs.append(TYPE[0])
            # 学校隶属
            bumen = university.xpath('dd/ul/li[4]/text()')
            bumens.append(bumen[0])
            # 学校性质
            xingzhi = university.xpath('dd/ul/li[5]/text()')
            xingzhis.append(xingzhi[0])
            # 学校官方链接主页
            school_url = university.xpath('dd/ul/li[6]/text()')
            school_urls.append(school_url[0])
            # dic = {'高校所在地':place[0],'院校特色':teses,'高校类型':TYPE[0],'高校隶属':bumen[0],'高校性质':xingzhi[0],'学校网址':school_url[0]}
            # dic = {'place':place[0],'teses':teses,'TYPE':TYPE[0],'bumen':bumen[0],'xingzhi':xingzhi[0],'school_url':school_url[0]}
            # 构造json文件，保存
            dic = [name[0], college_url[0], place[0], teses, TYPE[0], bumen[0], xingzhi[0], school_url[0]]
            data = json.dumps(dic, ensure_ascii=False)
            line = data + '\n'
            file.write(line)


    except:
        print("ERROR....")

    # workbook.save('gaokao.xlsx')
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
    # print len(tese)
    # for pl in tese:
    # print pl
    time.sleep(3)
# 使用excel方式保存获取的数据

schools = []
workbook = xlsxwriter.Workbook('gaokao_schools.xlsx')
worksheet = workbook.add_worksheet('school')
j = 1
for i in range(len(names)):
    # 由于部分页面有重复的学校数据，所以，判断是否数据重复
    if names[i] not in schools:
        schools.append(names[i])
        line = j
        # 写入数据
        worksheet.write(line, 1, names[i])
        worksheet.write(line, 2, college_urls[i])
        worksheet.write(line, 3, places[i][6:])
        worksheet.write(line, 4, tesess[i][5:])
        worksheet.write(line, 5, TYPEs[i][5:])
        worksheet.write(line, 6, bumens[i][5:])
        worksheet.write(line, 7, xingzhis[i][5:])
        worksheet.write(line, 8, school_urls[i][5:])
        j = j + 1
# 数据写入结束，保存并关闭excel文件
workbook.close()
