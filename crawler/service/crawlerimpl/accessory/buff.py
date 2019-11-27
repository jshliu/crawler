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


htmlutil = Context().get("htmlutil")
Url = Context().get("Url")
Crawler = Context().get("Crawler")


class OnsellCrawler(Crawler):

    type = "buff.accessory.onsell" # 第一个 . 前面的为爬虫的数据源，该爬虫为 buff

    def __init__(self, task):
        super(OnsellCrawler, self).__init__(task)
        
        # 自己设置？
        self.cookie = '_ntes_nuid=381eb0cf251ceb61e0ee8a6ba286329a; mail_psc_fingerprint=62de6e42b1950700695d64b56236996b; usertrack=CrH4J114YBNYc2T2Ax2iAg==; __f_=1568170005560; _ntes_nnid=445ee384372e9f0d406b990b861f7336,1568170007323; NTES_CMT_USER_INFO=270037309%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B0g674Z%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CemFuZ2h5dTA0MjdAMTYzLmNvbQ%3D%3D; nts_mail_user=zanghyu0427@163.com:-1:1; hb_MA-9F44-2FC2BD04228F_source=www.baidu.com; _ga=GA1.2.1590061055.1572319762; __root_domain_v=.163.com; _qddaz=QD.rzjxg0.3d5bl2.k2bal8r6; from=bd2jjX4978; Device-Id=3W4V7frpBq97K1au34ue; _gid=GA1.2.302684570.1574511050; csrf_token=ImU0NjJjYTBiM2UxMDVlN2Y4MDRlOWQ3ZTE1Y2Y1OGQ2YmE4NDQzYzYi.ELt82Q.17tXW7upo42-9e8Z89oDD9SkSgs; game=csgo; NTES_YD_SESS=HuFI3BFt_tqtasJDnRdDjqD70aWBg.cgi3IdDtwiDBo7FjMNF3qU1PHrhbIfnWbVLzzwCFNxd_AeZvnBAZlWs1SfouM0OfiO65_zvOcWQ0RDAHDpuPshPlHJb5X0i4eDdL7HHAwwC4iqPHdy3VlY68d.W1rsRModvqoUtKWclKeievEQQGCAyC1AYo6J0F0UJtNOUcvQm3BYRN69kBAHORPIMXJDANXY8E0Rqb7fcJmX6; S_INFO=1574562722|0|3&80##|17888802383; P_INFO=17888802383|1574562722|0|netease_buff|00&99|bej&1572847581&netease_buff#bej&null#10#0#0|&0|null|17888802383; session=1-qUSfY4-mBeUHNgwoF8erb04LIEHg7LwEBrl4wlid0ufK2043589924'
        
        self.buff_headers = {
                'Accept': 'application/json,*/*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh,zh-TW;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Cookie': self.cookie,
                'Host': 'buff.163.com',
                'Referer': 'https://buff.163.com/market/?game=dota2',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            
        }
        self.buff_url = 'https://buff.163.com/api/market/goods?game=dota2&page_num={page_num}&search={key}'



    def crawl(self):
        keyword = self.key # key在这里可以当作搜索关键词
        
        origin_name = self.type.split('.')[0]

        p_num = 1
        total_num = 0

        while(True):
            true_url = self.buff_url.format(page_num=p_num,key=keyword).decode('unicode_escape')
            response = htmlutil.get_response(true_url, headers=self.buff_headers)
            data = json.loads(response.text)
            if p_num > total_num and p_num > 1:
                break
            if p_num == 1:
                total_num = int(data['data']['total_page'])
                print('total page num is :' + str(total_num))

            for item in data['data']['items']:
                exist = ScarletOnsell.objects.filter(name=item['name'])
                if not exist:
                    model = ScarletOnsell(name=item['name'], buy_num=item['buy_num'],
                        sell_num=item['sell_num'], price=item['quick_price'], origin=origin_name)
                    model.save()
            p_num += 1

if __name__ == "__main__":
    from apps.base.models import Task
    t = Task.objects.filter(id=1).first()
    OnsellCrawler(t).crawl()
