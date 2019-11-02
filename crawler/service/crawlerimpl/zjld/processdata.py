#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib , urlparse
import chardet
import requests
import datetime
import time
from bs4 import BeautifulSoup
from lxml import etree
from utils.datetimeutil import fmt_time

def get_urls_re(homepage, time = 10):

    html_stream = None
    count = 0
    while count < 2:
        try:
            html_stream = requests.get(homepage, timeout = time)
        except:
            count += 1
        else:
            break
    return html_stream

def _wrap(lit):
    if isinstance(lit, list):
        return list(lit)
    else:
        return None

def new_time():
    lo_time = time.time()
    crtimes = {
        "crtime_int": int(lo_time*1000000),
        "crtime": datetime.datetime.utcfromtimestamp(lo_time),
    }
    return crtimes

def utc2local(utc_st):
    assert isinstance(local_st, datetime.datetime)
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st

def local2utc(local_st):
    assert isinstance(local_st, datetime.datetime)
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st

def get_code(url):
    codes = {}
    count = 0
    parts = urlparse.urlsplit(url)
    parts = parts._replace(path=urllib.quote(parts.path.encode('utf8')))
    url = parts.geturl()
    while count < 2:
        try:
            data = urllib.urlopen(url).read()
            codes =  chardet.detect(data)
        except IOError:
            count +=1
        else:
            break
    return codes

def get_charset(html):
    try:
        soup = BeautifulSoup(html[html.find(">")+1:])
    except:
        return 'utf-8'
    tags = soup.find_all(re.compile(r'meta', re.I))
    for tag in tags:
        if tag.get('content'):
            match = re.search(r'charset=(.*)',tag['content'])
            if match:
                coding = match.group(1)
                return coding
    return 'utf-8'

def extract_key(text):
    if not text:
        return ""
    if not isinstance(text, unicode):
        text = unicode(text, 'utf8')
        
    chinese_symbols = u"[“”‘’！？—…。，·：、￥（）【】《》〖〗]"
    en_symbols = r"[`~!@#\$%\^&\*\(\)_\+=\-\{\}\[\];:\",\.<>/\?\\|' + \"\']"
    text = re.sub(chinese_symbols, ' ', text)
    text = re.sub(en_symbols, ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip().lower()

def clear_space(text):
    text = unicode(text) if type(text) == str else text
    assert isinstance(text,unicode)
    text = re.sub(r'\s+', '', text)
    text = text.replace(' ', '')
    text = text.replace(ur'　','')
    text = text.replace(ur' ', '')
    return text

def clear_a(text):
    assert isinstance(text,list)
    content = ''
    for item in text:
        item = unicode(item)
        str_comp = r"<a.+?</a>|<script.+?</script>|(?<=class=\").+?(?=\")|(?<=id=\").+?(?=\")"
        strinfo = re.compile(str_comp, re.DOTALL)
        item = strinfo.sub('',item)
        symbols = re.compile(ur'\s+｜')
        item = symbols.sub('',item)
        str_p = re.compile(r"<p.*?>\s+?</p>|<span .+?>\s+?</span>")
        item = str_p.sub('',item)
        content += item.strip()
    return content

def clear_label(text, root=''):
    assert isinstance(text,list)
    content = ''
    for item in text:
        item = unicode(item)
        str_comp = r"(?<=class=\").+?(?=\")|(?<=id=\").+?(?=\")|<script.+?</script>"
        strinfo = re.compile(str_comp, re.DOTALL)
        item = strinfo.sub('',item)
        imginfo = re.compile(r'\S*?src',re.I)
        item = imginfo.sub('src',item)
        if root:
            img_list=re.findall(r"(?<=src=\").+?(?=\")|(?<=src=\').+?(?=\')|(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,item)
            for img in img_list:
                new_img = ''
                if img.find('http') == -1:
                    new_img = HandleUrl.join_url_path(root,img)
                    item = item.replace(img, new_img)
                else:
                    pass
        content += item
    return content

class HandleContent(object): 

    def __init__(self):
       pass

    @staticmethod  
    def get_BScontext(html ,text=False):
        try:
            soup = BeautifulSoup(html) if text else BeautifulSoup(html.text)
        except:
            soup = ''
        return soup

    @staticmethod
    def get_item(html, xpath=''):
        tree = etree.HTML(html.text)
        dom =tree.xpath(xpath)
        return dom

    @staticmethod
    def get_context(html, xpath, text=False):
        texts = ''
        tree = html if text else etree.HTML(html.text)
        dom = tree.xpath(xpath)
        for item in dom:
            if item.strip() == '':
                continue
            else:
                texts +=item.strip() if text else ' ' + item.strip()
        return texts.strip()

    @staticmethod
    def get_author(html, xpath='', xp_text=u'作者：', STR=False):
        text = html if STR else HandleContent.get_context(html,xpath)
        author = re.search(u'%s([\u4e00-\u9fa5]+)'%xp_text, text)
        lam_aut= lambda x : x.group(1) if x else ''
        author = lam_aut(author)
        return author

    @staticmethod
    def get_title(html, xpath=''):
        title = HandleContent.get_context(html,xpath)
        if title.strip() == '':   
            soup = HandleContent.get_BScontext(html)
            title = soup.title.string.strip() if soup.title else ''
          
        return title
        
    @staticmethod
    def strformat(time_str):
        time_str = time_str.strip()
        time_format = ''
        if time_str.find('/') >0:
            if time_str.find(':') >0:
                time_format = "%Y/%m/%d %H:%M:%S"
            else:
                time_format = "%Y/%m/%d"
        elif time_str.find(':') == -1:
            time_format = "%Y-%m-%d"
        elif time_str.count(':') ==1:
            time_format = "%Y-%m-%d %H:%M"
        else:
            time_format = "%Y-%m-%d %H:%M:%S"
        try:
            pub_time = datetime.datetime.strptime(time_str, time_format)
        except:
            pub_time = ''
        return local2utc(pub_time)

    @staticmethod
    def get_pubtime(html ,xpath='', time_format='', match_str=''):
        text = HandleContent.get_context(html,xpath)
        if text.strip() == '':
            pub_time = HandleContent.find_pubtime(html.text)
        elif match_str:
            match = re.search(match_str, text)
            date_format = time_format if time_format else HandleContent.get_time_format(match)
            pub_time = datetime.datetime.strptime(text, date_format)
        else:
            pub_time = HandleContent.find_pubtime(text)
        pub_time = local2utc(pub_time) if pub_time else datetime.datetime.utcfromtimestamp(0)
        nowyear = datetime.datetime.now().year
        pubyear = pub_time.year
        if pubyear > nowyear:
            pub_time = pub_time.replace(nowyear)
        return pub_time

    @staticmethod
    def find_pubtime(text):
        return fmt_time(text)


class HandleUrl(object):

    def __init__(self):
       pass

    @staticmethod
    def join_url_path(root, path):
        path = path.strip()
        path.replace('','.')
        ls = root.split('/')
        root = ls[0] + '//' + ls[1] + ls[2]
        match = re.search(r'.*?(\w.+$)',path)
        if match:
            path=match.group(1)
        return root + '/' +path

    @staticmethod
    def get_url(data):
        link_list=re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,data)
        return _wrap(link_list)

    # @staticmethod
    # def judge_url(text, )

    @staticmethod
    def judge_url(url, homepage):
        url_res = ''
        if re.search('(ist)|(.doc)|(.rar)|(.css)|(;)|(\')|(\")',url) or url[-1] in ['/','#','=']:
            return url_res
        elif url.find('javascript') >= 0:
            return url_res
        elif url.find('http') == -1:
            url_res = HandleUrl.join_url_path(homepage, url)
        else:
            ls = homepage.split('/')
            root = ls[0] + '//' + ls[1] + ls[2]
            if url.find(root) >= 0 and url[0:4] == 'http':
                url_res = url.strip()
        return url_res
