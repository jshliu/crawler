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
SearchContentCrawler = Context().get("SearchContentCrawler")
FatherCrawler = Context().get("FatherCrawler")
Field = Context().get("Field")
Crawler = Context().get("Crawler")
Handler = Context().get("Handler")


class BuffOnsellCrawler(Crawler):

    type = "buff.onsell"

    def __init__(self, task):
        # Handler.handle(self.type)
        pass
        # super(BuffOnsellCrawler, self).__init__(task)

    def crawl(self):
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
    # from apps.base.models import Task
    # from json import dumps
    # t = Task(key=u"杭州煤气汽车爆炸 1人死亡", data=dumps({"last_info": {"pubtime": "2015-1-1 00:00:00"}}), crawler="sogou.news", producer_id=1, category="event", application="yqj")
    # t.save()
    # BaiduCrawler(t).crawl()
    # SogouCrawler(key="it168", data={"source": "sogou"}).crawl()

    BuffOnsellCrawler({}).crawl()