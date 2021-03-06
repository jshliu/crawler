# -*- coding: utf-8 -*-

import sys
root_mod = '/Users/liujiasheng/workspace/crawler/crawler'
sys.path.append(root_mod)
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development");
django.setup()
import re
import json
from datetime import datetime

from apps.base.models import ScarletOnsell
from context.context import Context

htmlutil = Context().get("htmlutil")
Url = Context().get("Url")
Crawler = Context().get("Crawler")


class OnsellCrawler(Crawler):

    type = "buff.accessory.onsell" # 第一个 . 前面的为爬虫的数据源，该爬虫为 buff

    def __init__(self, task):
        pass
        super(OnsellCrawler, self).__init__(task)

    def crawl(self):
        keyword = self.key # key在这里可以当作搜索关键词
        print keyword
        print '-----'
        url = 'https://buff.163.com/api/market/goods?game=dota2&page_num=1'
        headers = {
        }

        response = htmlutil.get_response(url, headers=headers)

        data = json.loads(response.text)

        for item in data['data']['items']:
            exist = ScarletOnsell.objects.filter(name=item['name'])
            if not exist:
                model = ScarletOnsell(name=item['name'], buy_num=item['buy_num'],
                    sell_num=item['sell_num'], price=item['quick_price'])
                model.save()


if __name__ == "__main__":
    from apps.base.models import Task
    t = Task.objects.filter(id=1).first()

    OnsellCrawler(t).crawl()