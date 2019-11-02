# -*- coding: utf-8 -*-

import sys
root_mod = '/Users/liujiasheng/workspace/crawler/crawler'
sys.path.append(root_mod)
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development");
django.setup()
import re
from datetime import datetime

from apps.base.models import ScarletOnsell
from context.context import Context

htmlutil = Context().get("htmlutil")
Url = Context().get("Url")
SearchContentCrawler = Context().get("SearchContentCrawler")
FatherCrawler = Context().get("FatherCrawler")
Field = Context().get("Field")
Crawler = Context().get("Crawler")


class BuffOnsellCrawler(Crawler):

    type = "buff.onsell"

    def __init__(self, task):
        pass
        # super(BuffOnsellCrawler, self).__init__(task)

    def crawl(self):
        url = 'https://buff.163.com/api/market/goods?game=dota2&page_num=1'
        headers = {
        }

        response = htmlutil.get_response(url, headers=headers)

        model = ScarletOnsell(name='test scarlet')
        model.save()

        print response.text
        # soup = Readability(response.text, url)
        # comment = {
        #     'count': str(self.data.get('count','')),
        # }
        # if self.data.get('industry'):
        #     comment.update({'industry': self.data.get('industry')})

        # tag = str(getTag(clear_space(htmlutil.extract_text(soup.content))))

        # crawl_data = {
        #     'title': self.data['title'],
        #     'pubtime': self.data.get('pubtime', datetime.utcnow),
        #     'source': self.data['source'],
        #     'publisher': self.data.get('publisher', ''),
        #     'origin_source': self.data.get('origin_source', ''),
        #     'url': url,
        #     'key': self.data.get('key', ''),
        #     'content': soup.content,
        #     'tag': tag,
        #     'comment': comment,
        #     'producer_id': self.task.producer_id,
        #     'category': self.task.category,
        #     'application': self.task.application,
        # }
        # crawl_data.update(new_time())
        # if crawl_data['content']:
        #     model = SearchArticleModel(crawl_data)
        #     export(model)


if __name__ == "__main__":
    # from apps.base.models import Task
    # from json import dumps
    # t = Task(key=u"杭州煤气汽车爆炸 1人死亡", data=dumps({"last_info": {"pubtime": "2015-1-1 00:00:00"}}), crawler="sogou.news", producer_id=1, category="event", application="yqj")
    # t.save()
    # BaiduCrawler(t).crawl()
    # SogouCrawler(key="it168", data={"source": "sogou"}).crawl()

    BuffOnsellCrawler({}).crawl()