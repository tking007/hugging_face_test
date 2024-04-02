import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Crawling of microblog information')

    # cookie
    # parser.add_argument('--cookie', default=your cookie)

    # user
    """
    user_id: the id of user, such as 1669879400(迪丽热巴)  
    user_url: the url of user's information
    """
    parser.add_argument('--user_id', default=7906382865)
    parser.add_argument('--user_url', default='https://weibo.cn/')

    # information
    """
    filter: 0 or 1 (0: 原创微博 + 转发微博; 1:原创微博)
    pic_download: 0 or 1 (0: 不下载原始微博图片; 1: 下载微博原始图片)
    """
    parser.add_argument('--filter', default=1)
    parser.add_argument('--pic_download', default=1)

    return parser.parse_args()