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
        url = 'https://buff.163.com/api/market/goods/price_history/buff?game=dota2&goods_id=761789&currency=CNY&days=30&_=1568013505458'
        headers = {
            'Accept': 'application/json,*/*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh,zh-TW;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': '_ntes_nuid=7860c8b217b51019150195a405295bc5; __oc_uuid=332d8cb0-434f-11e7-aa76-ebe540339a0c; mail_psc_fingerprint=53e5fb42385ef3ac88db3f20b0f03f02; __gads=ID=fd90af187e4e12f6:T=1524358131:S=ALNI_MZBBPkA1Uy8BqHqrfWwgfPJDj3Gyw; vjuids=2b45c9c5c.162ead334aa.0.ebc9f1e264d8b; __utma=187553192.1882018305.1495939310.1536454015.1539008417.5; vjlast=1524358133.1546664750.22; vinfo_n_f_l_n3=6517a6e9ed8525ab.1.6.1524358132918.1543473586230.1546665185872; nts_mail_user=17612187302@163.com:-1:1; UM_distinctid=16a785729e916b-0672447f8a994b-e323069-e1000-16a785729ea553; _ntes_nnid=7860c8b217b51019150195a405295bc5,1560001666391; __f_=1566654113586; _ga=GA1.2.1882018305.1495939310; csrf_token=f431d5fec80864356eae6d4a7147ed7a2df94983; _gid=GA1.2.135073570.1570893275; NTES_YD_SESS=Gtlj0aV9iVVozRHU.b_0n1jv.l4f4FqLUFq.gGXarbRd5EnP5.MfeYz6rmQOtmg_UxH6ZXynKmmsW1gblTJ83Zzo57dRmOHJ1yj3ZwU9O5swgbuPHDugb1dIx39uUtzCVV6FIdYsPNMND.Z9XBhLdMiMoI36H1caPBYhqCHpz3XjXHe5eaU93KZiSYN3EO9Dhg4C244.777hY1p8vGM4Rdmj1lrphCn.Lcn2.5Gc57UdO; S_INFO=1570893318|0|3&80##|17612187302; P_INFO=17612187302|1570893318|0|netease_buff|00&99|shh&1570214596&netease_buff#shh&null#10#0#0|&0|null|17612187302; session=1-ABgRBa1ii3ZYy8AvNGsibA80964Dwf2HIW9eO-4SPoJJ2042637597; Locale-Supported=zh-Hans; game=dota2',
            'Host': 'buff.163.com',
            'Referer': 'https://buff.163.com/market/?game=dota2',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
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