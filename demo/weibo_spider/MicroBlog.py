import os
import re
import csv
import sys
import random
import requests
import traceback

from tqdm import tqdm
from time import sleep
from lxml import etree
from collections import OrderedDict
from datetime import datetime, timedelta

"""
deal_html(): 处理html ------√
deal_garbled(): 处理乱码 ------√
get_nickname(): 获取用户昵称 ------√
get_user_info(): 获取用户昵称、微博数、关注数、粉丝数 ------√
get_page_num(): 获取微博总页数 ------√
is_original(): 判断微博是否为原创微博 ------√
get_original_microblog(): 获取原创微博 ------√
get_retweet_microblog(): 获取转发微博 ------√
get_microblog_content(): 获取微博内容 ------√
extract_picture_urls():提取微博原始图片url ------√
get_picture_url(): 获取微博原始图片url ------√
get_publish_place(): 获取微博地理位置 ------√
get_publish_time_tool(): 获取微博发布时间、工具 ------√
get_weibo_footer(): 获取微博点赞数、转发数、评论数 ------√
get_one_microblog(): 获取一条微博的全部信息 ------√
get_one_page(): 获取第page页的全部微博 ------√
get_filepath(): 获取结果文件路径 ------√
write_csv(): 将爬取的信息写入csv文件 ------√
write_txt(): 将爬取的信息写入txt文件 ------√
get_microblog_info(): 获取微博信息 ------√
download_pictures(): 下载微博图片 ------√
start(): 运行爬虫 ------√
"""


class MicroBlog(object):
    def __init__(self, cookie, user_id, user_url, filter, pic_download):
        """
        :param cookie: your cookie
        :param user_id: the id of user, such as 1669879400(迪丽热巴)
        :param user_url: the user's url
        :param filter: 0 or 1 (0: 原创微博 + 转发微博; 1:原创微博)
        :param pic_download: 0 or 1 (0: 不下载原始微博图片; 1: 下载微博原始图片)
        :param nickname: the user's name, such as 'Dear-迪丽热巴'
        :param microblog_num: 微博数
        :param get_num: 爬取的微博数
        :param following: 用户关注数
        :param fans: 用户粉丝数
        :param microblog: 存储爬取的所有微博信息
        """
        self.cookie = cookie
        self.user_id = user_id
        self.user_url = user_url
        self.filter = filter
        self.pic_download = pic_download
        self.nickname = ''
        self.microblog_num = 0
        self.get_num = 0
        self.following = 0
        self.fans = 0
        self.microblog = []

    def get_microblog_info(self):
        """ 获取微博信息 """
        try:
            # print('------Get Crawler Information------')
            url = self.user_url + 'u/' + str(self.user_id)
            selector = self.deal_html(url)

            # 获取用户昵称、微博数、关注数、粉丝数
            self.get_user_info(selector)

            # 获取微博总页数
            page_num = self.get_page_num(selector)

            wrote_num = 0
            page_index = 0
            random_pages = random.randint(1, 5)

            for page in tqdm(range(1, page_num + 1), desc=u'进度'):
                # 获取第page页的全部微博
                self.get_one_page(page)
                print('第{}页微博爬取完毕！'.format(page))

                # 每爬取一页写入一次文件
                if self.get_num > wrote_num:
                    self.write_csv(wrote_num)
                    self.write_txt(wrote_num)
                    wrote_num = self.get_num

                    # 图片的存储
                    if self.pic_download == 1:
                        # pic_download: 0 or 1 (0: 不下载原始微博图片; 1: 下载微博原始图片)
                        self.download_pictures()

                """
                通过加入随机等待避免被限制。
                爬虫速度过快容易被系统限制(一段时间后限制会自动解除)，
                加入随机等待模拟人的操作，可降低被系统限制的风险。
                默认是每爬取1到5页随机等待6到10秒，如果仍然被限，可适当增加sleep时间
                """
                if page - page_index == random_pages and page < page_num:
                    sleep(random.randint(6, 10))
                    page_index = page
                    random_pages = random.randint(1, 5)
            if not self.filter:
                print(u'共爬取{}条微博'.format(self.get_num))
            else:
                print(u'共爬取{}条原创微博'.format(self.get_num))
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_user_info(self, selector):
        """ 获取用户昵称、微博数、关注数、粉丝数 """
        try:
            # print('------Get user nickname, microblog_num, following, fans------')
            self.get_nickname()  # get user's name

            user_info = selector.xpath("//div[@class='tip2']/*/text()")

            self.microblog_num = int(user_info[0][3: -1])
            print(u'微博数: ', self.microblog_num)

            self.following = int(user_info[1][3: -1])
            print(u'关注数: ', self.following)

            self.fans = int(user_info[2][3: -1])
            print(u'粉丝数: ', self.fans)
            print('*' * 100)
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_nickname(self):
        """ 获取用户昵称 """
        try:
            # print('------Get user’s Name------')
            url = self.user_url + str(self.user_id) + '/info'
            selector = self.deal_html(url)
            # nickname: the user's name
            nickname = selector.xpath('//title/text()')[0]
            self.nickname = nickname[: -3]

            if self.nickname == u'登录 - 新' or self.nickname == u'新浪':
                """
                sys.exit(): 抛出一个SystemExit异常来尝试结束程序
                """
                sys.exit(u'cookie错误或已过期,请重新获取cookie!')
            else:
                print(u'用户名: ', self.nickname)
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_page_num(self, selector):
        """ 获取微博总页数 """
        try:
            # print('------Get Page_Num------')
            if selector.xpath("//input[@name='mp']") == []:
                page_num = 1
            else:
                page_num = (int)(selector.xpath("//input[@name='mp']")[0].attrib['value'])
                return page_num
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_one_page(self, page):
        """ 获取第page页的全部微博 """
        try:
            # print('------Get the {}th page’s microblogs------'.format(page))
            url = self.user_url + 'u/' + str(self.user_id) + '?page=' + str(page)
            selector = self.deal_html(url)
            info = selector.xpath("//div[@class='c']")
            is_exist = info[0].xpath("div/span[@class='ctt']")
            if is_exist:
                for i in range(0, len(info) - 2):
                    microblog = self.get_one_microblog(info[i])
                    if microblog:
                        self.microblog.append(microblog)
                        self.get_num += 1
                        print('-' * 100)
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_one_microblog(self, info):
        """ 获取一条微博的全部信息 """
        try:
            # print('------Get One MicroBlog------')
            """
            OrderedDict: 是 collections 提供的一种数据结构， 它提供了有序的dict结构。
            该类型存放顺序和添加顺序一致
            """
            microblog = OrderedDict()
            is_original = self.is_original(info)

            """
            self.filter = 1: 原创微博
            is_original = True: 该微博为原创微博
            解释：
            如果想要爬取的内容为原创微博，则self.filter = 1, 那么is_original = True，执行
            如果想要爬取额内容为原创 + 转发， 则self.filter = 0, 那么is_original = True/False，执行
            """
            if (not self.filter) or is_original:
                """
                microblog['id']: 微博id
                microblog['content']: 微博内容
                microblog['original_pictures']: 原创微博图片地址
                microblog['retweet_pictures']: 转发微博图片地址
                microblog['original']: 是否为原创微博
                microblog['publish_place']: 微博发布位置
                microblog['publish_time']: 微博发布时间
                microblog['publish_tool']: 微博发布工具
                microblog['up_num']: 微博点赞数
                microblog['retweet_num']: 转发数
                microblog['comment_num']: 评论数
                """
                microblog['id'] = info.xpath('@id')[0][2:]  # 微博id
                microblog['content'] = self.get_microblog_content(info, is_original)  # 微博内容

                picture_urls = self.get_picture_url(info, is_original)
                microblog['original_pictures'] = picture_urls['original_pictures']  # 原创微博图片地址
                if not self.filter:
                    microblog['retweet_pictures'] = picture_urls['retweet_pictures']  # 转发微博图片地址
                    microblog['original'] = is_original  # 是否为原创微博

                microblog['publish_place'] = self.get_publish_place(info)  # 微博发布位置

                publish_time_tool = self.get_publish_time_tool(info)
                microblog['publish_time'] = publish_time_tool['time']  # 微博发布时间
                microblog['publish_tool'] = publish_time_tool['tool']  # 微博发布工具

                footer = self.get_weibo_footer(info)
                microblog['up_num'] = footer['up_num']  # 微博点赞数
                microblog['retweet_num'] = footer['retweet_num']  # 转发数
                microblog['comment_num'] = footer['comment_num']  # 评论数
            else:
                microblog = None
            return microblog
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def is_original(self, info):
        """ 判断微博是否为原创微博 """
        """
        info: 获取的微博信息
        return: bool(True: 原创微博; False: 非原创微博，即转发微博)
        """
        is_original = info.xpath("div/span[@class='cmt']")
        if len(is_original) > 3:
            return False
        else:
            return True

    def get_microblog_content(self, info, is_original):
        """ 获取微博内容 """
        try:
            # print('------Get the Content of Microblog------')
            microblog_id = info.xpath('@id')[0][2:]
            """
            if is_original: get the original content
            if not is_original: get the retweet content
            """
            if is_original:
                microblog_content = self.get_original_microblog(info, microblog_id)
            else:
                microblog_content = self.get_retweet_microblog(info, microblog_id)

            print(microblog_content)
            return microblog_content
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_original_microblog(self, info, microblog_id):
        """ 获取原创微博 """
        try:
            # print('------Get the Original MicroBlog')
            microblog_content = self.deal_garbled(info)
            # rfind(): 返回字符串最后一次出现的位置(从右向左查询)，如果没有匹配项则返回-1
            microblog_content = microblog_content[: microblog_content.rfind(u'赞')]

            # ['组图共4张', '原图', '赞[7]', '转发[0]', '评论[3]', '收藏']
            a_text = info.xpath('div//a/text()')

            if u'全文' in a_text:
                url = self.user_url + 'comment/' + microblog_id
                """ 获取长的原创微博 """
                """
                long_content: the long microblog’s information
                microblog_time: the time
                """
                selector = self.deal_html(url)
                info = selector.xpath("//div[@class='c']")[1]
                long_content = self.deal_garbled(info)
                microblog_time = info.xpath("//span[@class='ct']/text()")[0]
                long_content = long_content[long_content.find(':') +
                                            1: long_content.rfind(microblog_time)]
                if long_content:
                    microblog_content = long_content
            return microblog_content
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_retweet_microblog(self, info, microblog_id):
        """ 获取转发微博 """
        try:
            # print('------Get the Retweet Microblog------')

            original_user = info.xpath("div/span[@class='cmt']/a/text()")

            if not original_user:
                retweet_content = u'转发微博已被删除'
                return retweet_content
            else:
                original_user = original_user[0]

            retweet_content = self.deal_garbled(info)
            # 转发后的赞， 原创微博的赞
            retweet_content = retweet_content[retweet_content.find(':') +
                                              1: retweet_content.rfind(u'赞')]
            retweet_content = retweet_content[: retweet_content.rfind(u'赞')]

            a_text = info.xpath('div//a/text()')

            if u'全文' in a_text:
                url = self.user_url + 'comment/' + microblog_id
                """ 获取长转发微博 """
                """
                long_content: the long microblog’s information
                microblog_time: the time
                """
                selector = self.deal_html(url)
                info = selector.xpath("//div[@class='c']")[1]
                long_content = self.deal_garbled(info)
                microblog_time = info.xpath("//span[@class='ct']/text()")[0]
                long_content = long_content[long_content.find(':') +
                                            1: long_content.rfind(microblog_time)]
                long_content = long_content[: long_content.rfind(u'原文转发')]
                if long_content:
                    retweet_content = long_content
                # 转发理由
                retweet_reason = self.deal_garbled(info.xpath('div')[-1])
                retweet_reason = retweet_reason[:retweet_reason.rindex(u'赞')]
                retweet_content = (retweet_reason + '\n' + u'原始用户: ' + original_user +
                                   '\n' + u'转发内容: ' + retweet_content)
                return retweet_content
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_picture_url(self, info, is_original):
        """ 获取微博原始图片url """
        try:
            """
            microblog_id: id
            picture_urls: the original picture’s url
            is_original: bool(True: 原创微博; False: 非原创微博，即转发微博)
            """
            # print('------Get the Original Picture’s Url------')
            microblog_id = info.xpath('@id')[0][2:]
            picture_urls = {}
            if is_original:
                picture_urls['original_pictures'] = self.extract_picture_urls(info, microblog_id)
                # filter: 0 or 1 (0: 原创微博 + 转发微博; 1:原创微博)
                if not self.filter:
                    picture_urls['retweet_pictures'] = '无'
            else:
                # div/a[@class='cc']/@href: 获取div元素中的a元素，且这些元素的属性为class，值为cc的href
                """
                retweet_url: https://weibo.cn/comment/JhKDyomnO?rl=0#cmtfrm
                retweet_id: 'JhKEG6sp2'
                spilt('/')[-1]: 以'/'为分割符保留最后一段        
                spilt('?')[0]: 以'?'为分隔符，返回'?'的一段    
                """
                retweet_url = info.xpath("div/a[@class='cc']/@href")[0]
                retweet_id = retweet_url.split('/')[-1].split('?')[0]
                picture_urls['retweet_pictures'] = self.extract_picture_urls(info, retweet_id)

                a_list = info.xpath('div[last()]/a/@href')
                original_picture = '无'
                """
                endswith(): 用于判断字符串是否以指定后缀结尾，如果以指定后缀结尾返回True，否则返回False。
                """
                for a in a_list:
                    if a.endswith(('.gif', '.jpeg', '.jpg', '.png')):
                        original_picture = a
                        break
                picture_urls['original_pictures'] = original_picture
            return picture_urls
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def extract_picture_urls(self, info, microblog_id):
        """ 提取微博原始图片url """
        try:
            # print('------Extract Picture Url------')
            a_list = info.xpath('div/a/@href')
            first_pic = self.user_url + 'mblog/pic/' + microblog_id + '?rl=0'
            all_pic = self.user_url + 'mblog/picAll' + microblog_id + '?rl=1'
            if first_pic in a_list:
                # 一张图片 or 多张图片
                if all_pic in a_list:
                    selector = self.deal_html(all_pic)
                    preview_pic_list = selector.xpath('//img/@src')
                    """
                    replace(): 把字符串中的 old（旧字符串）替换成 new(新字符串)
                               如果指定第三个参数max，则替换不超过 max 次
                    """
                    picture_list = [
                        p.replace('/thumb180/', '/large/') for p in preview_pic_list
                    ]
                    """
                    join():用于将序列中的元素（必须是str）以指定的字符,连接生成一个新的字符串。
                    """
                    picture_urls = ','.join(picture_list)
                else:
                    if info.xpath('.//img/@src'):
                        preview_picture = info.xpath('.//img/@src')[-1]
                        picture_urls = preview_picture.replace(
                            '/wap180/', '/large/'
                        )
                    else:
                        sys.exit(
                            u"爬虫微博可能被设置成了'不显示图片'，请前往"
                            u"'https://weibo.cn/account/customize/pic'，修改为'显示'"
                        )
            else:
                picture_urls = '无'
            return picture_urls
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_publish_place(self, info):
        """ 获取微博发布位置 """
        try:
            # print('--Get Publish_Place------')
            div_first = info.xpath('div')[0]
            a_list = div_first.xpath('a')
            publish_place = u'无'
            for a in a_list:
                if 'place.weibo.com' in a.xpath('@href')[0] and a.xpath('text()')[0] == u'显示地图':
                    microblog_list = div_first.xpath("span[@class='ctt']/a")
                    if len(microblog_list) >= 1:
                        publish_place = microblog_list[-1]
                        # tmp = div_first.xpath("span[@class='ctt']/a/text()")
                        # tmp_1 = div_first.xpath("span[@class='ctt']/a/text()")[-1]
                        # tmp_2 = div_first.xpath("span[@class='ctt']/a/text()")[-1][-2:]
                        if u'视频' == div_first.xpath("span[@class='ctt']/a/text()")[-1][-2:]:
                            if len(microblog_list) >= 2:
                                publish_place = microblog_list[-2]
                            else:
                                publish_place = u'无'
                        publish_place = self.deal_garbled(publish_place)  # '厦门·观音山梦幻世界乐园'
                        break
            print(u'微博发布位置: ', publish_place)
            return publish_place
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_publish_time_tool(self, info):
        """ 获取微博发布时间、工具 """
        try:
            # print('------ Get the Time of Microblog------')
            """
            str_time_tool: '10月19日 14:49 来自iPhone 11 Pro Max'
            str_time_tool.split(u'来自'): ['10月19日 14:49', 'iPhone 11 Pro Max']
            publish_time: 10月19日 14:49
            publish_tool: iPhone 11 Pro Max
            """
            str_time_time = info.xpath("div/span[@class='ct']")
            str_time_time = self.deal_garbled(str_time_time[0])

            publish = {}

            publish_time = str_time_time.split(u'来自')[0]

            """ 获取微博发布工具 """
            if len(str_time_time.split(u'来自')) > 1:
                publish_tool = str_time_time.split(u'来自')[1]
            else:
                publish_tool = u'无'
            publish['tool'] = publish_tool

            """ 获取微博发布时间 """
            if u'刚刚' in publish_time:
                publish_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            elif u'分钟' in publish_time:
                """
                publish_time: '4分钟前 '
                publish_time[: publish_time.find(u'分钟')]: 4
                timedelta(minutes=int(minute)): 0:04:00
                minute: 0:04:00
                """
                minute = publish_time[: publish_time.find(u'分钟')]
                minute = timedelta(minutes=int(minute))
                publish_time = (datetime.now() - minute).strftime('%Y-%m-%d %H:%M')
            elif u'今天' in publish_time:
                """
                publish_time: '今天 14:10 '
                time: '14:10 '
                """
                today = datetime.now().strftime('%Y-%m-%d')
                time = publish_time[3:]
                publish_time = today + ' ' + time
            elif u'月' in publish_time:
                """
                publish_time = 10月19日 14:49
                year = '2020'
                month = '10'
                day = '19'
                time = '14:49'
                """
                year = datetime.now().strftime('%Y')
                month = publish_time[0: 2]
                day = publish_time[3: 5]
                time = publish_time[7: 12]
                publish_time = year + '-' + month + '-' + day + ' ' + time
            else:
                """
                '2019-04-26 18:19:58 '
                publish_time[:16]: 2019-04-26 18:19
                """
                publish_time = publish_time[:16]
            publish['time'] = publish_time
            print(u'微博发布时间: ', publish_time)
            print(u'微博发布工具: ', publish_tool)
            return publish
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_weibo_footer(self, info):
        """ 获取微博点赞数、转发数、评论数 """
        try:
            # print('------Get the Number of Microblog’ s Likes, Reposts, and Comments------')
            footer = {}
            # \d+表示匹配数字1次或多次
            """
            re.findall(pattern,string,flags):
                flags:
                    - re.I: 使匹配对大小写不敏感
                    - re.L: 做本地化识别（locale-aware）匹配
                    - re.M: 多行匹配, 影响^和 $, 让^匹配每行的开头，$匹配每行的结尾
                    - re.S: 使.匹配包括换行在内的所有字符
                    - re.U: 根据Unicode字符集解析字符。这个标志影响 \w, \W, \b, \B.
                    - re.X: 该标志通过给予你更灵活的格式以便你将正则表达式写得更易于理解。
                    换句话说，使用了 re.M以后，运行效果看起来就像是程序首先根据换行符把字符串拆分成了多个子字符串，然后再在子字符串中执行正则表达式。
            """
            """
            str_footer: '转发理由:转发微博  已赞[1] 转发[0] 评论[0] 收藏 08月26日 23:06 来自iPhone X'
            str_footer[str_footer.rfind(u'赞'):]: '赞[1] 转发[0] 评论[0] 收藏 08月26日 23:06 来自iPhone X'
            microblog_footer: ['1', '0', '0', '08', '26', '23', '06']
            """
            pattern = r'\d+'
            str_footer = info.xpath('div')[-1]
            str_footer = self.deal_garbled(str_footer)
            str_footer = str_footer[str_footer.rfind(u'赞'):]
            microblog_footer = re.findall(pattern, str_footer, re.M)

            up_num = int(microblog_footer[0])
            print(u'点赞数: ', str(up_num))
            footer['up_num'] = up_num

            retweet_num = int(microblog_footer[1])
            print(u'转发数: ', str(retweet_num))
            footer['retweet_num'] = retweet_num

            comment_num = int(microblog_footer[2])
            print(u'评论数: ', str(comment_num))
            footer['comment_num'] = comment_num

            return footer
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def write_csv(self, wrote_num):
        """ 将爬取的信息写入csv文件 """
        try:
            # print('------Write CSV------')
            result_headers = [
                '微博id',
                '微博正文',
                '原始图片url',
                '发布位置',
                '发布时间',
                '发布工具',
                '点赞数',
                '转发数',
                '评论数',
            ]
            # filter: 0 or 1 (0: 原创微博 + 转发微博; 1:原创微博)
            if not self.filter:
                result_headers.insert(3, '被转发微博原始图片url')
                result_headers.insert(4, '是否为原创微博')
            result_data = [w.values() for w in self.microblog][wrote_num:]

            # python 3.x
            """
            路径
            """
            """
            os.path.realpath(__file__): 返回指定文件的标准路径
                - 'E:\\py_project\\Crawling of microblog information\\MicroBlog.py'
            os.path.abspath(): 返回一个目录的绝对路径
            os.path.split()：按照路径将文件名和路径分割开
                - ('E:\\py_project\\Crawling of microblog information', 'MicroBlog.py')
            os.sep: 由于python是跨平台, windows中文件分隔符为'\', linux中文件分隔符为'/'
                os.sep根据你所处的平台，自动采用相应的分隔符号。
            """
            # newline表示换行标志，取值一般是 None，'\n'，'\r' 或者'\r\n'
            csv_path = self.get_filepath('csv')
            with open(csv_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if wrote_num == 0:
                    writer.writerows([result_headers])
                writer.writerows(result_data)
            print(u'{}条微博写入csv文件完毕, '.format(self.get_num))
            # print(csv_path)
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def write_txt(self, wrote_num):
        """ 将爬取的信息写入txt文件 """
        try:
            # print('------Write TXT------')
            tmp = []
            if wrote_num == 0:
                # filter: 0 or 1 (0: 原创微博 + 转发微博; 1:原创微博)
                if self.filter:
                    result_header = u'\n\n原创微博内容: \n'
                else:
                    result_header = u'\n\n微博内容: \n'

                result_header = (u'用户信息\n用户昵称：' + self.nickname
                                 + u'\n用户id: ' + str(self.user_id)
                                 + u'\n微博数: ' + str(self.microblog_num)
                                 + u'\n关注数: ' + str(self.following)
                                 + u'\n粉丝数: ' + str(self.fans)
                                 + result_header)
                tmp.append(result_header)

            for i, w in enumerate(self.microblog[wrote_num:]):
                tmp.append(
                    str(wrote_num + i + 1) + ':' + w['content'] + '\n'
                    + u'微博位置: ' + w['publish_place'] + '\n'
                    + u'发布时间: ' + w['publish_time'] + '\n'
                    + u'点赞数: ' + str(w['up_num']) + '\n'
                    + u'转发数: ' + str(w['retweet_num']) + '\n'
                    + u'评论数: ' + str(w['comment_num']) + '\n'
                    + u'发布工具: ' + w['publish_tool'] + '\n\n'
                )
            result = ''.join(tmp)

            # txt path
            """
            open打开形式:
                a表示append
                r表示read
                +表示读写模式
                b表示二进制
                t表示文本模式, 是默认的模式
                - a: 以追加模式打开 (从 EOF 开始, 必要时创建新文件)
                - w: 以写方式打开
                - r+: 以读写模式打开
                - w+: 以读写模式打开 (参见 w)
                - a+: 以读写模式打开 (参见 a)
                - ab: 以二进制追加模式打开 (参见 a)
            """
            txt_path = self.get_filepath('txt')
            with open(txt_path, 'ab') as f:
                f.write(result.encode(sys.stdout.encoding))
            print(u'{}条微博写入txt文件完毕！'.format(self.get_num))
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def download_pictures(self):
        """ 下载微博图片 """
        try:
            # print('------Download the Pictures------')
            print(u'------------即将下载图片------------')
            """
            img_dir: 图片存储路径
            pic_prefix: 图片名称前缀, such as '20201023 _Jxxxxxxxk'
            pic_suffix: 图片名称后缀, such as 'jpg', 'png'
            pic_name: pic_prefix + (j + 1) + pic_suffix, such as '20201023 _Jxxxxxxxk_1.jpg'
            pic_path: 图片地址
            """
            img_dir = self.get_filepath('img')
            for w in tqdm(self.microblog, desc=u'图片下载进度'):
                if w['original_pictures'] != '无':
                    # replace('-', ''): 将字符串中的'-'替换成'', 即2020-10-23 --> 20201023
                    pic_prefix = w['publish_time'][:11].replace('-', '') + '_' + w['id']

                    # if 多张图片，则w['original_pictures']中的图片地址以','隔开
                    if ',' in w['original_pictures']:
                        w['original_pictures'] = w['original_pictures'].split(',')

                        for j, url in enumerate(w['original_pictures']):
                            pic_suffix = url[url.rfind('.'):]
                            pic_name = pic_prefix + '_' + str(j + 1) + pic_suffix
                            pic_path = img_dir + os.sep + pic_name

                            """ 下载单张图片 """
                            # requests.get(): 用于请求目标网站
                            # response.content: 图片
                            try:
                                response = requests.get(url)
                                with open(pic_path, 'wb') as f:
                                    f.write(response.content)
                            except Exception as e:
                                error_file = self.get_filepath('img') + os.sep + 'not_downloaded_pictures.txt'
                                with open(error_file, 'ab') as f:
                                    url = url + '\n'
                                    f.write(url.encode(sys.stdout.encoding))
                                print('Error: ', e)
                                traceback.print_exc()
                    else:
                        pic_suffix = w['original_pictures'][w['original_pictures'].rfind('.'):]
                        pic_name = pic_prefix + pic_suffix  # such as 20161031 _Jxxxxxxxk.jpg
                        pic_path = img_dir + os.sep + pic_name
                        """ 下载单张图片 """
                        # requests.get(): 用于请求目标网站
                        # response.content: 图片
                        try:
                            response = requests.get(w['original_pictures'])
                            with open(pic_path, 'wb') as f:
                                f.write(response.content)
                        except Exception as e:
                            error_file = self.get_filepath('img') + os.sep + 'not_downloaded_pictures.txt'
                            with open(error_file, 'ab') as f:
                                url = w['original_pictures'] + '\n'
                                f.write(url.encode(sys.stdout.encoding))
                            print('Error: ', e)
                            traceback.print_exc()
            print(u'图片下载完毕!')
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_filepath(self, type):
        """ 获取结果文件路径 """
        try:
            # print('------Get the Path of File------')
            file_dir = os.path.split(os.path.realpath(__file__))[0]
            file_dir = file_dir + os.sep + 'user_information' + os.sep + self.nickname
            if type == 'img':
                file_dir = file_dir + os.sep + 'img'
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            if type == 'img':
                return file_dir
            file_path = file_dir + os.sep + '{}'.format(self.user_id) + '.' + type
            return file_path
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def deal_html(self, url):
        """ 处理html """
        try:
            # print('------Deal HTML------')
            """
            requests.get(): 用于请求目标网站，类型是一个HTTPresponse类型
                <Response [200]>:是HTTP状态码,表示网络请求成功的意思
            etree.HTML(): 可以用来解析字符串格式的HTML文档对象，将传进去的字符串转变成_Element对象
            """
            response = requests.get(url, cookies=self.cookie)
            html = response.content
            selector = etree.HTML(html)
            return selector
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def deal_garbled(self, info):
        """ 处理乱码 """
        try:
            # print('------Deal With Garbled------')
            """
            string(.): 可以用于提取标签嵌套标签的内容
            replace(u'\u200b', ''): 去除不可见字符
            encode(): 编码--将其他编码的字符串转换成unicode编码
            decode(): 解码--将unicode编码转换成其他编码的字符串
            将其他的编码转换成utf-8: 1.其他编码 --> unicode; 2.unicode --> utf-8
            sys.stdout.encoding: 默认输出编码问题
            在编码过程中，可能会出现非法字符，可设置第二个参数，第二个参数默认值为strict
                -strict--抛出异常
                -ignore--则会忽略非法字符
                -replace--则会用?取代非法字符；
                -xmlcharrefreplace--则使用XML的字符引用
            """
            info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
                sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))
            return info
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def start(self):
        """ 运行爬虫 """
        try:
            # print('------Start Crawling------')
            self.get_microblog_info()
            print(u'------信息抓取完毕------')
            print('*' * 100)
        except Exception as e:
            print('ERROR: ', e)
            traceback.print_exc()  # 捕获并打印异常的方法