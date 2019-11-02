# -*- coding: utf-8 -*-

import logging
import json
import time
from datetime import timedelta
import datetime
import requests
import re
import time
import random
import socket



logger = logging.getLogger("ecommercecrawler")

def local2utc(local_st):
    assert isinstance(local_st, datetime.datetime)
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st

def convert_price(text):
    text = text.strip()
    if not isinstance(text,unicode):
        text = unicode(text,"utf-8")
    if (text[0] or text[-1]) == u'¥':
        price = float(text.replace(u'¥','').replace(",",""))
    elif (text[0] or text[-1]) == u'￥':
        price = float(text.replace(u'￥','').replace(",",""))
    elif (text[0] or text[-1]) == u'$':
        price = float(text.replace(u'$','').replace(",",""))*0.16
    elif (text[0] or text[-1]) == u'€':
        price = float(text.replace(u'€','').replace(",",""))*0.15
    else :
        price = float(text.replace(",",""))
    return price

def convert_imgs(imgs):
    if not isinstance(imgs, list):
        raise TypeError

    for i in range(len(imgs)):
        imgs[i] = str(imgs[i])
    return imgs

def get_ctime():
    lo_time = time.time()
    crtimes = {
        "crtime_int": int(lo_time*1000000),
        "crtime": datetime.datetime.utcfromtimestamp(lo_time),
    }
    return crtimes

def get_version(summary, introduce):
    version = summary[u"型号名称"] if summary.get(u"型号名称") else ""
    if version:
        return version
    version = summary[u"型号"] if summary.get(u"型号") else ""
    if version:
        return version
    version = summary[u"产品型号"] if summary.get(u"产品型号") else ""
    if version:
        return version
    version = summary[u"零件编号"] if summary.get(u"零件编号") else ""
    if version:
        return version
    version = introduce[u"型号名称"] if introduce.get(u"型号名称") else ""
    if version:
        return version
    version = introduce[u"型号"] if introduce.get(u"型号") else ""
    if version:
        return version
    version = introduce[u"产品型号"] if introduce.get(u"产品型号") else ""
    if version:
        return version
    version = introduce[u"零件编号"] if introduce.get(u"零件编号") else ""
    return version

def get_series(summary, introduce):
    series = summary[u"系列"] if summary.get(u"系列") else ""
    if series:
        return series
    series = summary[u"系列名称"] if summary.get(u"系列名称") else ""
    if series:
        return series
    series = summary[u"产品系列"] if summary.get(u"产品系列") else ""
    if series:
        return series
    series = introduce[u"系列"] if introduce.get(u"系列") else ""
    if series:
        return series
    series = introduce[u"系列名称"] if introduce.get(u"系列名称") else ""
    if series:
        return series
    series = introduce[u"产品系列"] if introduce.get(u"产品系列") else ""

    return series

def get_brand(summary, introduce):
    brand = summary[u"品牌"] if summary.get(u"品牌") else ""
    if brand:
        return brand
    brand = summary[u"品牌名称"] if summary.get(u"品牌名称") else ""
    if brand:
        return brand
    brand = summary[u"产品品牌"] if summary.get(u"产品品牌") else ""
    if brand:
        return brand
    brand = summary[u"Brand"] if summary.get(u"Brand") else ""
    if brand:
        return brand
    brand = summary[u"brand"] if summary.get(u"brand") else ""
    if brand:
        return brand
    brand = introduce[u"品牌"] if introduce.get(u"品牌") else ""
    if brand:
        return brand
    brand = introduce[u"品牌名称"] if introduce.get(u"品牌名称") else ""
    if brand:
        return brand
    brand = introduce[u"Brand"] if introduce.get(u"Brand") else ""
    if brand:
        return brand
    brand = introduce[u"brand"] if introduce.get(u"brand") else ""
    return brand

def get_name(introduce):
    ecname = introduce[u"商品名称"] if introduce.get(u"商品名称") else ""
    if ecname:
        return ecname
    ecname = introduce[u"商品名"] if introduce.get(u"商品名") else ""
    if ecname:
        return ecname
    ecname = introduce[u"产品名称"] if introduce.get(u"产品名称") else ""
    if ecname:
        return ecname
    ecname = introduce[u"产品名"] if introduce.get(u"产品名") else ""
    return ecname

def get_address(summary, introduce):
    address = introduce[u"商品产地"] if introduce.get(u"商品产地") else ""
    if address:
        return address
    address = introduce[u"产品产地"] if introduce.get(u"产品产地") else ""
    if address:
        return address
    address = introduce[u"产地"] if introduce.get(u"产地") else ""
    if address:
        return address
    address = summary[u"商品产地"] if summary.get(u"商品产地") else ""
    if address:
        return address
    address = summary[u"产品产地"] if summary.get(u"产品产地") else ""
    if address:
        return address
    address = summary[u"产地"] if summary.get(u"产地") else ""
    return address

def get_press_time(summary, introduce):
    press_time_str = introduce[u"上架时间"] if introduce.get(u"上架时间") else ""
    if press_time_str:
        press_time = for_time(press_time_str)
    return press_time

def check_encoding(html_stream):
    encoding = html_stream.encoding.lower()
    if encoding == "utf-8":
        return html_stream
    elif encoding == "gbk":
        return html_stream
    elif encoding == "gb2312":
        return html_stream
    else:
        html_stream.encoding = "utf-8"
        return html_stream

def clean_space(text):
    if not isinstance(text,unicode):
        text = unicode(text,'utf-8')
    return "".join(text.split(' '))

def extract_text(text):
    if not isinstance(text,unicode):
        text = unicode(text,'utf-8')
    chinese_symbols = u"[“”‘’！？…。]"
    en_symbols = r"[`~!@#\$%\^&\*\(\)_\+=\{\}\[\];\",<>/\?\\|' + \"\']"
    text = re.sub(chinese_symbols, ' ', text)
    text = re.sub(en_symbols, ' ', text)
    return text

def extract_title(text):
    if not isinstance(text,unicode):
        text = unicode(text,'utf-8')
    chinese_symbols = u"[“”‘’！？—…。，·：、（）【】《》〖〗]"
    en_symbols = r"[`~!@#\$%\^&\*\(\)_\+=\-\{\}\[\];:\",\.<>/\?\\|' + \"\']+"
    text = re.sub(chinese_symbols, ' ', text)
    text = re.sub(en_symbols, ' ', text)
    text = text.strip()
    return text

def extract_category(self):
  
    priorcategory = self.data['priorcategory']
    mappriorcategory = {
        'first':priorcategory[0],
        'second':priorcategory[1],
        'third':priorcategory[2]
    }
    category_data = {
        'source_level': mappriorcategory,
        'current_level': mappriorcategory['third'],
    }
    return category_data

def for_time(old_time):
    old_time = old_time.strip()
    # old_time == ''
    if not old_time:
        return None
    old_time = old_time.replace(u"年", " ").replace(u"月", " ").replace(u"日", " ")
    #match include "2015-11-25 10:10:10", "2015/11/25 10:10:10","2015 11 25 10:10:10", "2015\11\25 10:10:10" 
    match = re.search("\d{4}([-\/ ])+?\d{1,2}([-\/ ])+?\d{1,2}\D*?\d{1,2}:\d{1,2}:\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d"+\
            " "+"%H"+":"+"%M"+":"+"%S")
    #match include "2015-11-25 10:10", "2015/11/25 10:10","2015 11 25 10:10", "2015\11\25 10:10" 
    match = re.search("\d{4}([-\/ ])+?\d{1,2}([-\/ ])+?\d{1,2}\D*?\d{1,2}:\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d"+\
            " "+"%H"+":"+"%M")
    #match include "10:10:10 2015-11-25", "10:10:10 2015/11/25","10:10:10 2015 11 25", "10:10:10 2015\11\25" 
    match = re.search("\d{1,2}:\d{1,2}:\d{1,2}\D*?\d{4}([-\/ ])+?\d{1,2}([-\/ ])+?\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%H"+":"+"%M"+":"+"%S"+" "+"%Y"+match.group(1)+\
            "%m"+match.group(2)+"%d")
    #match include "10:10 2015-11-25", "10:10 2015/11/25","10:10 2015 11 25", "10:10 2015\11\25" 
    match = re.search("\d{1,2}:\d{1,2}\D*?\d{4}([-\/ ])+?\d{1,2}([-\/ ])+?\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%H"+":"+"%M"+" "+"%Y"+match.group(1)+\
            "%m"+match.group(2)+"%d")
    #match include "10:10:10 25-11-2015", "10:10:10 25-11-2015","10:10:10 25-11-2015", "10:10:10 25-11-2015" 
    match = re.search("\d{1,2}:\d{1,2}:\d{1,2}\D*?\d{1,2}([-\/ ])+?\d{1,2}([-\/ ])+?\d{4}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%S"+":"+"%M"+":"+"%H"+" "+"%d"+match.group(1)+\
            "%m"+match.group(2)+"%Y")
    #match include "10:10 25-11-2015", "10:10 25-11-2015","10:10 25-11-2015", "10:10 25-11-2015" 
    match = re.search("\d{1,2}:\d{1,2}\D*?\d{1,2}([-\/ ])+?\d{1,2}([-\/ ])+?\d{4}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%M"+":"+"%H"+" "+"%d"+match.group(1)+\
            "%m"+match.group(2)+"%Y")
    #match include "2015-11-25", "2015/11/25","2015 11 25", "2015\11\25" 
    match = re.search("(\d{4})([-\/ ])(\d{1,2})([-\/ ])(\d{1,2})", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%Y"+match.group(2)+"%m"+match.group(4)+"%d")
    #match include "10天前"
    match = re.search(u"(\d+?)天前", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(days=int(match.group(1)))
    #match include "10小时前", "10时前", "10钟头前", "10个小时前", "10个时前", "10个钟头前"
    match = re.search(u"(\d+?)(小时前|时前|钟头前|个小时前|个时前|个钟头前)", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(hours=int(match.group(1)))
    #match include "10分钟前", "10分前"
    match = re.search(u"(\d+?)(分钟前|分前)", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(minutes=int(match.group(1)))
    #match include "10秒前"
    match = re.search(u"(\d+?)秒前", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(seconds=int(match.group(1)))
    #match include "15-11-25 10:10:10", "15/11/25 10:10:10","15 11 25 10:10:10", "15年11月25日 10:10:10" 
    match = re.search("\d{2}([-\/ ])+?\d{1,2}([-\/ ])+?\d{1,2}\D*?\d{1,2}:\d{1,2}:\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime("20"+match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d"+\
            " "+"%H"+":"+"%M"+":"+"%S")
    #match include "2015-11-25 10:10", "2015/11/25 10:10","2015 11 25 10:10", "15年11月25日 10:10" 
    match = re.search("\d{2}([-\/ ])+?\d{1,2}([-\/ ])+?\d{1,2}\D*?\d{1,2}:\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime("20"+match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d"+\
            " "+"%H"+":"+"%M")
    return None

class ProcessData():

    @staticmethod
    def str_datetime(str_time):
        str_time = str_time.strip()
        if str_time.count(':')==2:
            time_format = '%Y-%m-%d %H:%M:%S'
        elif str_time.count(':')==1:
            time_format = '%Y-%m-%d %H:%M'
        elif str_time.count('-') == 2:
            time_format = '%Y-%m-%d'
        try:
            times = datetime.datetime.strptime(str_time,time_format) - timedelta(hours = 8)
        except:
            times = datetime.datetime.strptime("1900-01-01",'%Y-%m-%d')
        return times

    @staticmethod
    def get_web_data(url):
        count = 0
        html_stream = {}
        while count < 2:
            try:
                html_stream = requests.get(url, timeout = 5)
            except requests.exceptions.Timeout:
                time.sleep(random.randint(1,5))
                count += 1
            except socket.timeout:
                time.sleep(random.randint(1,8))
                count += 1                
            except Exception,e:
                logger.error(e)
                logger.error(url)
                return html_stream
            else:
                count = 2
                break
        if count != 2:
            logger.error("timeout: %s"%url)
        return html_stream

    @staticmethod
    def get_json_data(url,**keys):
        count = 0
        while count < 2:
            try :
                html_stream = requests.get(url ,params = keys.get('parameter',{}),timeout = 3)
            except requests.exceptions.Timeout:
                time.sleep(random.randint(1,5))
                count += 1
            except socket.timeout:
                time.sleep(random.randint(1,8))
                count += 1
            except Exception,e:
                logger.error(e)
                logger.error(url)
                return {}
            else:
                count = 2
                break
        if count != 2:
            logger.error("timeout: %s"%url)
        try:
            jsons = json.loads(html_stream.text)
        except:
            jsons = {}

        return jsons

    @staticmethod
    def get_json_post(url,**keys):
        count = 0
        while count < 2:
            try :
                html_stream = requests.post(url ,params=keys.get('parameter',{}), 
                        data=keys.get("data", {}), timeout=3)
            except requests.exceptions.Timeout:
                time.sleep(random.randint(1,5))
                count += 1
            except socket.timeout:
                time.sleep(random.randint(1,8))
                count += 1
            except Exception,e:
                logger.error(e)
                logger.error(url)
                return {}
            else:
                count = 2
                break
        if count != 2:
            logger.error("timeout: %s"%url)
        try:
            jsons = json.loads(html_stream.text)
        except:
            jsons = {}

        return jsons

if __name__ == "__main__":
    url = 'http://mobile.gome.com.cn/mobile/product/search/keywordsSearch.jsp?\
          body=%7B%22searchType%22%3A%20%220%22%2C%20%22catId%22%3A%20%22cat10000230\
          %22%2C%20%22regionID%22%3A%20%2211010200%22%2C%20%22sortBy%22%3A%20%227%22%\
          2C%20%22currentPage%22%3A%20234%2C%20%22pageSize%22%3A%2010%7D'

    ProcessData.get_json_data(url)