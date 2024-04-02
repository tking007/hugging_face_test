import traceback
from demo.weibo_spider import configs

from MicroBlog import MicroBlog


def main(args):
    """
    user_id: the id of user, such as 1669879400(迪丽热巴)
    filter: 0 or 1 (0: 原创微博 + 转发微博; 1:原创微博)
    pic_download: 0 or 1 (0: 不下载原始微博图片; 1: 下载微博原始图片)
    """
    try:

        cookie = {"Cookie": "SINAGLOBAL=7592937485072.373.1698831529698; XSRF-TOKEN=yVmqq9u_mNGwtxdAjeYWetvY; PC_TOKEN=6f1c5fcb3b; login_sid_t=b474cb0ff2438e68dcc6d1a125a65d4a; cross_origin_proto=SSL; _s_tentry=weibo.com; Apache=2388120377970.7925.1711552483841; ULV=1711552483845:2:1:1:2388120377970.7925.1711552483841:1698831529708; wb_view_log=1920*10801; ALF=1714144601; SUB=_2A25LAEgJDeRhGeVJ6lAT8inIzD-IHXVofMXBrDV8PUJbkNB-LUmjkW1NT-6fJELRxOS9QbKqtMc4LgZy7c2hsC8p; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF0oqEVlQyCKnQQOkaOvk3R5JpX5KzhUgL.FoeNeKzEeoMXS0e2dJLoIf2LxKnL12qLBozLxKBLB.BLBK5LxKnL12-LB-zLxK-LBo2L1--LxKBLBonLBoqLxKnL12qLBozLxKqL1hnL1K2LxKnL12-LB-zLxK-LBo2LB-et; WBPSESS=E50Btn0ZG3GPfmwGhfl0die9Z-hmdTVHmklsrZZdS3PFVf6KJIvfohD0CDndU5t0-XpV8_VUt7Sem64oJYiw3l6fsSYXQhjsVogmompHxBQHXDdmHej4rTXvNGYsBuCLJVRc2i_Hrjg3CIWoZ4xQug=="}  # 将your cookie替换成自己的cookie
        # 使用实例，输入一个用户id，所有信息都会存储在文件user_information中
        user_id = args.user_id
        user_url = args.user_url
        filter = args.filter
        pic_download = args.pic_download
        # print(user_id, filter, pic_download)

        # 调用MicroBlog类，创建微博实例MB
        MB = MicroBlog(cookie, user_id, user_url, filter, pic_download)
        # 爬取微博信息
        MB.start()

    except Exception as e:
        print('ERROR: ', e)
        traceback.print_exc()  # 捕获并打印异常的方法


if __name__ == '__main__':
    args = configs.parse_args()
    main(args)