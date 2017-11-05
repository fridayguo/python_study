import requests
import time
import json
import re
import random
import json

def gen_url(keyword):
    api_host = 'http://apinew.ezoption.cn/pre_order/all_share'
    type_b_r = 'cn'
    curr_time = str(long(time.time() * 1000))
    query_url = '%s?callback=callback&keyword=%s&type_b_r=%s&_=%s' \
                % (api_host, keyword, type_b_r, curr_time)
    #print curr_time
    return query_url

def get_and_write_one(query_url):
    r = requests.get(query_url, headers=headers, cookies=cookies)
    # print r.text
    res = re.match(r'\/\*\*\/callback\((.*)\);$', r.text)
    # print res.group(1)
    js = json.loads(res.group(1))
    code = js['code']

    if code == 0 :
        fd = open('./epo.json', 'a')
        #fd.write(query_url)
        fd.write(res.group(1))
        fd.close()

    return code

#########################################################################

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1;Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Referer': 'http://www.ezoption.cn/goods/diy'
}

host_url='http://www.ezoption.cn/goods/diy'
r=requests.get(host_url)
cookies=r.cookies

print cookies
print headers

#range_lists = [('000001','000999'), ('002001','002910'),('300001','300726'),('600000','603999')]
range_lists = [('000001','000091')]
err_map = {}
for s,e in range_lists:
    s,e = int( ( int(s)/10) ), int( ( int(e)/10) )
    print s,e
    for c in range(s,e+1):
        keyword = '%05d'%(c)
        print keyword
        query_url = gen_url(keyword)
        code = get_and_write_one(query_url)
        err_map[keyword] = code
        sleep_sec = random.random()*5
        time.sleep(1)


fd = open('./err_map.json', 'w')
#fd.write(query_url)
fd.write(str(err_map))
fd.close()

