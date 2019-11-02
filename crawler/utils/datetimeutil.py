# -*- coding: utf-8 -*-
import calendar, time, re, datetime


def unix_time(dt=datetime.datetime.utcnow()):
    return calendar.timegm(dt.utctimetuple())


def parse_date(text, formats=[]):
    if not text:
        return None
    if not formats:
        formats = [u"%Y-%m-%d", u"%Y-%m", u"%Y",
                   u"%Y年%m月%d日", u"%Y年%m月", u"%Y年"]
    for f in formats:
        try:
            dt = datetime.datetime.strptime(
                text.strip().encode('utf8'), f.encode('utf8'))
            return dt
        except:
            pass


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


MONTH_DICT = {
    "january": 1,
    "february": 2,
    "march": 3,
    "apri": 4,
    "may":5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def fmt_time(old_time):
    old_time = old_time.strip().lower()
    # old_time == ''
    if not old_time:
        return None
    old_time = old_time.replace(u"年", " ").replace(u"月", " ").replace(u"日", " ")
    #match include "2015-11-25 10:10:10", "2015/11/25 10:10:10","2015 11 25 10:10:10", "2015\11\25 10:10:10"
    match = re.search(r"\d{4}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{1,2}\D*?\d{1,2}:\d{1,2}:\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d"+\
            " "+"%H"+":"+"%M"+":"+"%S")
    #match include "2015-11-25 10:10", "2015/11/25 10:10","2015 11 25 10:10", "2015\11\25 10:10"
    match = re.search(r"\d{4}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{1,2}\D*?\d{1,2}:\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d"+\
            " "+"%H"+":"+"%M")
    #match include "10:10:10 2015-11-25", "10:10:10 2015/11/25","10:10:10 2015 11 25", "10:10:10 2015\11\25"
    match = re.search(r"\d{1,2}:\d{1,2}:\d{1,2}\D*?\d{4}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%H"+":"+"%M"+":"+"%S"+" "+"%Y"+match.group(1)+\
            "%m"+match.group(2)+"%d")
    #match include "10:10 2015-11-25", "10:10 2015/11/25","10:10 2015 11 25", "10:10 2015\11\25"
    match = re.search(r"\d{1,2}:\d{1,2}\D*?\d{4}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%H"+":"+"%M"+" "+"%Y"+match.group(1)+\
            "%m"+match.group(2)+"%d")
    #match include "10:10:10 25-11-2015", "10:10:10 25-11-2015","10:10:10 25-11-2015", "10:10:10 25-11-2015"
    match = re.search(r"\d{1,2}:\d{1,2}:\d{1,2}\D*?\d{1,2}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{4}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%S"+":"+"%M"+":"+"%H"+" "+"%d"+match.group(1)+\
            "%m"+match.group(2)+"%Y")
    #match include "10:10 25-11-2015", "10:10 25-11-2015","10:10 25-11-2015", "10:10 25-11-2015"
    match = re.search(r"\d{1,2}:\d{1,2}\D*?\d{1,2}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{4}", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%M"+":"+"%H"+" "+"%d"+match.group(1)+\
            "%m"+match.group(2)+"%Y")
    #match include "2015-11-25", "2015/11/25","2015 11 25", "2015\11\25"
    match = re.search(r"(\d{4})([-\\/ \.])(\d{1,2})([-\\/ \.])(\d{1,2})", old_time)
    if match:
        return datetime.datetime.strptime(match.group(0), "%Y"+match.group(2)+"%m"+match.group(4)+"%d")
    #match include "10天前"
    match = re.search(ur"(\d+?)天前", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(days=int(match.group(1)))
    #match include "10小时前", "10时前", "10钟头前", "10个小时前", "10个时前", "10个钟头前"
    match = re.search(ur"(\d+?)(小时前|时前|钟头前|个小时前|个时前|个钟头前)", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(hours=int(match.group(1)))
    #match include "10分钟前", "10分前"
    match = re.search(ur"(\d+?)(分钟前|分前)", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(minutes=int(match.group(1)))
    #match include "10秒前"
    match = re.search(ur"(\d+?)秒前", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(seconds=int(match.group(1)))
    #match include "15-11-25 10:10:10", "15/11/25 10:10:10","15 11 25 10:10:10", "15年11月25日 10:10:10"
    match = re.search(r"\d{2}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{1,2}\D*?\d{1,2}:\d{1,2}:\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime("20"+match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d"+\
            " "+"%H"+":"+"%M"+":"+"%S")
    #match include "15-11-25", "15/11/25","15 11 25", "15年11月25日"
    match = re.search(r"\d{2}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime("20"+match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d")
    #match include "2015-11-25 10:10", "2015/11/25 10:10","2015 11 25 10:10", "15年11月25日 10:10"
    match = re.search(r"\d{2}([-\\/ \.])+?\d{1,2}([-\\/ \.])+?\d{1,2}\D*?\d{1,2}:\d{1,2}", old_time)
    if match:
        return datetime.datetime.strptime("20"+match.group(0), "%Y"+match.group(1)+"%m"+match.group(2)+"%d"+\
            " "+"%H"+":"+"%M")
    #match include "1 Aug 2015", "1-Aug-2015", "1/Aug/2015"
    match = re.search(r"\d{1,2}([-\\/ \.])+?([a-z]{3,8})([-\\/ \.])+?\d{4}", old_time)
    if match:
        for i in MONTH_DICT.keys():
            if i.startswith(match.group(2).lower()):
                month = MONTH_DICT[i]
                break
        return datetime.datetime.strptime(match.group(0).replace(match.group(2), str(month))
            , "%d"+match.group(1)+"%m"+match.group(3)+"%Y")
    #match include "1 day ago", "2 days ago"
    match = re.search(r"(\d+?).*?days?.*?ago", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(days=int(match.group(1)))
    #match include "1 hour ago", "2 hours ago"
    match = re.search(r"(\d+?).*?hours?.*?ago", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(hours=int(match.group(1)))
    #match include "1 minute ago", "2 minutes ago"
    match = re.search(r"(\d+?).*?minutes?.*?ago", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(minutes=int(match.group(1)))
    #match include "1 second ago", "2 seconds ago"
    match = re.search(r"(\d+?).*?seconds?.*?ago", old_time)
    if match:
        return datetime.datetime.now() - datetime.timedelta(minutes=int(match.group(1)))
    return None


def str2time(data):
    for i in data.keys():
        if isinstance(data[i], basestring):
            if re.match(r"\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}", data[i]):
                data[i] = datetime.datetime.strptime(data[i], "%Y-%m-%d %H:%M:%S")
        elif isinstance(data[i], dict):
            str2time(data[i])


def time2str(data):
    for i in data.keys():
        if isinstance(data[i], datetime.datetime):
            data[i] = datetime.datetime.strftime(data[i], "%Y-%m-%d %H:%M:%S")
        elif isinstance(data[i], dict):
            time2str(data[i])


