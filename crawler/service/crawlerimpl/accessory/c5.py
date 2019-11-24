# -*- coding: utf-8 -*-
import os
import sys
root_path = os.path.abspath(os.path.dirname(__file__)).split('crawler')[0]
root_path = str(root_path) + 'crawler/crawler'
sys.path.append(root_path)
sys.path.append(str(root_path) + 'crawler')
# root_mod = '/Users/liujiasheng/workspace/crawler/crawler'
# sys.path.append(root_mod)
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development")
django.setup()
import re
import json
from datetime import datetime

from apps.base.models import ScarletOnsell
from context.context import Context
from lxml import etree

htmlutil = Context().get("htmlutil")
Url = Context().get("Url")
Crawler = Context().get("Crawler")


class OnsellCrawler(Crawler):

    type = "c5.accessory.onsell" # 第一个 . 前面的为爬虫的数据源，该爬虫为 buff

    def __init__(self, task):
        super(OnsellCrawler, self).__init__(task)
        
        # 自己设置？
        self.cookie = 'C5SessionID=6kbbodr93qhkcplelqa8s0q0f7; C5Lang=zh; device_id=ee2fa4b780e8ca35c47a1d6b1e9a7e1e; Hm_lvt_86084b1bece3626cd94deede7ecf31a8=1574565880; Hm_lpvt_86084b1bece3626cd94deede7ecf31a8=1574573456'


        self.c5_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'cookie': self.cookie,
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

        
        self.c5_url = 'https://www.c5game.com/dota.html?min=&max=&k={key}&rarity=&quality=&hero=&tag=&sort=&page={page_num}'




    def crawl(self):
        keyword = self.key # key在这里可以当作搜索关键词
        origin_name = self.type.split('.')[0]
        total_num = 0
        p_num = 1
        while(True):
            true_url = self.c5_url.format(page_num=p_num,key=keyword).decode('unicode_escape')
            response = htmlutil.get_response(true_url, headers=self.c5_headers)
            html = etree.HTML(response.text)
            empty = html.xpath('//div[contains(@class,"tab-content")]/div[contains(@class,"tab-pane active")]'+
                                '/ul[contains(@class,"list-item4 clearfix")]/span[contains(@class,"empty")]')
            if len(empty) > 0:
                break

            sell_name_list = html.xpath('//li[contains(@class,"selling")]/p[contains(@class,"name")]/a/span')
            sell_num_list = html.xpath('//li[contains(@class,"selling")]/p[contains(@class,"info")]/span[contains(@class,"num")]')
            sell_price_list = html.xpath('//li[contains(@class,"selling")]/p[contains(@class,"info")]/span/span')
            
            buy_name_list = html.xpath('//li[contains(@class,"purchaseing")]/p[contains(@class,"name")]/a/span')
            buy_num_list = html.xpath('//li[contains(@class,"purchaseing")]/p[contains(@class,"info")]/span[contains(@class,"num")]')
            buy_price_list = html.xpath('//li[contains(@class,"purchaseing")]/p[contains(@class,"info")]/span/span')
            
            assert len(sell_name_list) == len(sell_price_list)
            assert len(sell_name_list) == len(sell_num_list)
            assert len(buy_name_list) == len(buy_price_list)
            assert len(buy_name_list) == len(buy_num_list)
            
            sell_name_list = [_.text for _ in sell_name_list]
            sell_num_list = [_.text[:-3] for _ in sell_num_list]
            sell_price_list = [_.text.split(u'￥')[1].strip() for _ in sell_price_list]

            buy_name_list = [_.text for _ in buy_name_list]
            buy_num_list = [_.text[:-3] for _ in buy_num_list]
            buy_price_list = [_.text.split(u'￥')[1].strip() for _ in buy_price_list]

            for item in zip(sell_name_list, sell_num_list, sell_price_list):
                exist = ScarletOnsell.objects.filter(name=item[0])
                if not exist:
                    model = ScarletOnsell(name=item[0], buy_num=0,
                        sell_num=item[1], price=item[2], origin=origin_name)
                    model.save()

            for item in zip(buy_name_list, buy_num_list, buy_price_list):
                exist = ScarletOnsell.objects.filter(name=item[0])
                if not exist:
                    model = ScarletOnsell(name=item[0], buy_num=item[1],
                        sell_num=0, price=item[2], origin=origin_name)
                    model.save()

            p_num += 1

if __name__ == "__main__":
    from apps.base.models import Task
    t = Task.objects.filter(id=1).first()
    OnsellCrawler(t).crawl()
