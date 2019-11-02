# coding=utf8
import os
import re
import uuid
import hashlib


def ensure_paths(paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


def ensure_dir(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def filemd5(path):
    with open(path) as fp:
        data = fp.read()
        return hashlib.md5(data).hexdigest()


def get_tmppath(ext=""):
    while True:
        tmppath = os.path.join("/tmp/", uuid.uuid4().hex)
        if ext:
            tmppath = tmppath + "." + ext
        if not os.path.exists(tmppath):
            return tmppath


def exists_ignore_case(path):
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    for name in os.listdir(dirname):
        if name.lower() == basename.lower():
            return True
    return False


def find_files(path, pattern, ignore_case=False):
    items = []
    for name in os.listdir(path):
        subpath = os.path.join(path, name)
        if os.path.isdir(subpath):
            subitems = find_files(subpath, pattern, ignore_case)
            items.extend(subitems)
        elif os.path.isfile(subpath):
            if ignore_case:
                if re.match(pattern.lower(), subpath.lower()):
                    items.append(subpath)
            else:
                if re.match(pattern, subpath):
                    items.append(subpath)
    return items


def find_dirs(path, pattern, ignore_case=False):
    for name in os.listdir(path):
        subpath = os.path.join(path, name)
        if os.path.isdir(subpath):
            if ignore_case:
                if re.match(pattern.lower(), subpath.lower()):
                    yield subpath
            else:
                if re.match(pattern, subpath):
                    yield subpath

            for item in find_dirs(subpath, pattern, ignore_case):
                yield item


def correct_link(text, current):
    link_re = r"href=[\'\"](.*?)[\'\"]|src=[\'\"](.*?)[\'\"]|background=[\'\"](.*?)[\'\"]"
    link_list = re.findall(link_re, text) 
    for link_tuple in link_list:
        for link in link_tuple:
            if link:
                new_link = join_path(current, link)
                text = text.replace(link, new_link)
    return text   


def join_paths(urls, end_url):
    tmp = []
    for url in urls:
        tmp.apppend(join_path(url, end_url))
    return tmp


def join_path(url, end_url):
    new_url = ""
    # url =  http(s)://demo1/demo2/demo3
    # ../demo.jpg => http(s)://demo1/demo2/demo.jpg
    if end_url.startswith("../"):
        count = end_url.count("../")
        index = _findstr(url,count=count+1)
        url = url[:index+1]
        if not re.search("://",url):
            return ""
        end_url = re.findall("../"*count + "(.*)",end_url)[0]
        new_url = url + end_url
    # /demo.jpg => http(s)://demo1/demo,jpg
    elif end_url.startswith("/"):
        if url.startswith("http"):
            urls = url.split("://")
            root = urls[0] + "://" + re.match("(?<=).*?(?=/)",urls[1]).group(0)
            new_url = root + end_url
    elif end_url.startswith("./"):
        temp_url = ""
        parts = url.split("/")
        for i in range(len(parts)-1):
            temp_url += parts[i] + "/"
        new_url = temp_url + end_url.replace("./", "")
    # http(s)://demo1/demo2/demo3/demo.jpg => just return self
    elif end_url.startswith("http"):
        return end_url
    else:
        temp_url = ""
        parts = url.split("/")
        for i in range(len(parts)-1):
            temp_url += parts[i] + "/"
        if temp_url.endswith("/"):
            new_url = temp_url + end_url
        else:
            new_url = temp_url + "/" + end_url
    return new_url


def _findstr(text,count=1): 
    index = 0
    for i in range(0,count):
        if not index:
            index = text.rfind("/")
        else:
            index = text[:index].rfind("/")
    return index