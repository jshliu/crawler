# -*- coding: utf-8 -*-

import logging, json, time, datetime, requests, re, random, socket
from lxml import etree
from bs4 import BeautifulSoup

from context.context import Context
join_path = Context().get("pathutil.join_path")
correct_link = Context().get("pathutil.correct_link")
fmt_time = Context().get("datetimeutil.fmt_time") 
local2utc = Context().get("datetimeutil.local2utc")


def get_web_data(url, data=None, headers={}, proxies={}, allow_redirects=True, timeout=None):
    count = 0
    html_stream = None
    while count < 2:
        try:
            if data is not None:
                html_stream = requests.post(url, timeout=timeout, data=data, headers=headers
                        , proxies=proxies, allow_redirects=allow_redirects)
            else:
                html_stream = requests.get(url, timeout=timeout, headers=headers
                        , proxies=proxies, allow_redirects=allow_redirects)
        except requests.exceptions.Timeout:
            time.sleep(random.randint(1,5))
            count += 1
        except socket.timeout:
            time.sleep(random.randint(1,8))
            count += 1
        except Exception, e:
            raise RuntimeError("requests fail, error: %s" % e)
        else:
            count = 2
            break
    return html_stream


def get_charset(html_stream):
    xpath = "//meta[@http-equiv='Content-Type']/@content"
    charset = ""
    try:
        content = html_stream.headers["Content-Type"]
        if not content:
            content = etree.HTML(html_stream.text).xpath(xpath)[0]
        charset = re.findall("charset=(.*)", content)[0]
    except:
        return html_stream.apparent_encoding

    if len(charset) < 3:
        return html_stream.apparent_encoding
    return charset


def get_response(url, data=None, headers={}, proxies={}, allow_redirects=True, timeout=None):
    response = get_web_data(url, data=data, headers=headers, proxies=proxies, allow_redirects=allow_redirects
        ,timeout=timeout)
    response.encoding = get_charset(response)
    return response


def clear_label(text, current=None):
    if not isinstance(text, unicode):
        text = unicode(text)
    text = text.strip()
    cins_str = r"(class=[\'\"].*?[\"\']|id=[\'\"].*?[\"\']|name=[\'\"].*?[\"\']"\
                "|<!--.*?-->|<a.*?javascript.*?>|<script.*?script>|<\?xml.*?>|(?<=>).*?(?=\S))"
    cins_re = re.compile(cins_str, re.S)
    text = re.sub(cins_re, '',text)
    #correct the path of links
    if current:
        correct_link(text, current)
    return text


def extract_html(text):
    re_str = re.compile(r"<html>.*</html>", re.S)
    match = re.search(re_str, text)
    return match.group(0)


def extract_xml(text):
    re_str = re.compile(r"<\?xml.*</xml>", re.S)
    match = re.search(re_str, text)
    return match.group(0)


def get_text(tree, path):
    match = tree.xpath(path)
    if match:
        if isinstance(match[0], basestring):
            return match[0].strip()
        elif isinstance(match[0], etree._Element):
            return match[0].xpath("string(.)").strip()
    return ""


def get_datetime(tree, path):
    pub_str = get_text(tree, path)
    if pub_str:
        time = fmt_time(pub_str)
        if time:
            return local2utc(time)
    return None


def get_list(tree, path):
    if isinstance(tree, basestring):
        return re.findall(path, tree, re.S)
    elif isinstance(tree, etree._Element):
        return tree.xpath(path)
    return None


def extract_text(text):
    return BeautifulSoup(text).text


def filter_url(urls):
    for i in urls:
        if not is_url(i):
            urls.remove(i)
    return urls
    

def is_url(url):
    if re.search('(ist)|(.doc)|(.rar)|(.css)|(;)|(\')|(\")', url) or url[-1] in ['/','#','='] \
        or url.find('javascript:') >= 0: 
        return False   
    return True
