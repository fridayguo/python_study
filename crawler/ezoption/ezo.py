#!/root/anaconda2/bin/python
#coding=utf-8

import requests
import time
import json
import re
import random
import json
import pandas as pd
import numpy as np

#将cookies转换成字典形式，zhihu_cookie为保存的cookie文件，跟程序处在同一路径
def get_cookie():
    with open('./cookie.txt','r') as f:
        cookies={}
        for line in f.read().split(';'):
            name,value=line.strip().split('=',1)  #1代表只分割一次
            cookies[name]=value
        return cookies

def get_type_b_r():
    with open('./type_b_r.txt','r') as f:
        for line in f.readlines():
            return line

def gen_query_url(keyword):
    api_host = 'http://apinew.ezoption.cn/pre_order/all_share'
    type_b_r = 'cn'
    type_b_r = '26c948cad12d7d5a81c5323a55e3c4a92599b4478ebc705bee2b6226679f8e42'
    curr_time = str(long(time.time() * 1000))
    query_url = '%s?callback=callback&keyword=%s&type_b_r=%s&_=%s' \
                % (api_host, keyword, type_b_r, curr_time)
    #print curr_time
    return query_url

def get_and_write_one(query_url, json_file):
    r = requests.get(query_url, headers=headers, cookies=cookies)
    # print r.text
    res = re.match(r'\/\*\*\/callback\((.*)\);$', r.text)
    # print res.group(1)
    js = json.loads(res.group(1))
    code = js['code']

    if code == 0 :
        fd = open(json_file, 'a')
        #fd.write(query_url)
        fd.write(res.group(1))
        fd.close()

    return code

def get_cal_one(cal_url):
    r = requests.get(cal_url, headers=headers, cookies=get_cookie(), proxies=proxies)
    print r.text
    res = re.match(r'\/\*\*\/callback\((.*)\);$', r.text)
    # print res.group(1)
    js = json.loads(res.group(1))
    code = js['code']
    if code == 1:
        result = js['data']
        return code, result


    return code,0

#########################################################################

def init_cookies():
    host_url='http://www.ezoption.cn/goods/diy'
    r=requests.get(host_url,headers=headers)
    cookies=r.cookies
    return cookies

def get_all_sk():
    range_lists = [('000001','000999'), ('002001','002910'),('300001','300726'),('600000','603999')]
    #range_lists = [('000001','000091')]
    err_map = {}
    for s,e in range_lists:
        s,e = int( ( int(s)/10) ), int( ( int(e)/10) )
        print s,e
        for c in range(s,e+1):
            keyword = '%05d'%(c)
            #print keyword
            query_url = gen_query_url(keyword)
            print query_url
            code = get_and_write_one(query_url, json_file)
            err_map[keyword] = code
            print keyword,code
            sleep_sec = random.random()*10
            time.sleep(sleep_sec)


    fd = open('./err_map.json', 'w')
    #fd.write(query_url)
    fd.write(str(err_map))
    fd.close()

def gen_sk_data(json_file):
    fd = open(json_file)

    df = pd.DataFrame()
    for line in fd.readlines():
        line = line.strip('\n')
        if len(line) < 10:
            continue
        # print 'aaaa',line

        js = json.loads(line)
        # print js['data']
        js_str = json.dumps(js['data'])
        js_df = pd.read_json(js_str, orient='records')
        df = pd.concat([df, js_df], ignore_index=True)

    df.drop_duplicates(inplace=True)

    return df

def req_cal_res(df):
    #for i in range(3):
    for i in range(df.shape[0]):
        if df.loc[i, 'res'] != 0.0:
            continue
        cal_url = gen_cal_url(df.iloc[i, :])
        #print cal_url
        code, res = get_cal_one(cal_url)
        if code != 1:
            return
        df.loc[i, 'res'] = res
        # print df.iloc[i, :]
        df.to_csv('./data_src.csv', encoding='utf8')

        time.sleep(1)

def gen_tran(ezo_df):
    vol_list = ['week_volatility', 'month1_volatility', 'month3_volatility', 'month6_volatility', 'year_volatility']
    ezo_df['c_sigma'] = np.max(ezo_df[vol_list], axis=1)

    # ezo_df['c_sigma']
    ezo_df['c_S'] = ezo_df['close_price']
    ezo_df['c_K'] = ezo_df['close_price']
    ezo_df['c_r'] = 3.73 # fix
    ezo_df['c_T'] = 2  # 2周
    ezo_df['res'] = 0.0

    return ezo_df


def gen_cal_url(row):
    #query_url = 'http://apinew.ezoption.cn/pre_order/do_calculate?callback=callback&c_K=13.80&c_T=2&c_S=13.80&c_r=3.73&c_sigma=59.71&share_symbol=sh600111&type_b_r=55d083e33def6ca15494c670d3bd8972d5540a55c5635833151e083f29c716ec91db4913134a080bcbe29e7b60921c0ef77a76ef9c19fe06e94360dde26f7ad7835dfdf653fbde52&_=1509943988724'
    #print query_url

    cal_host='http://apinew.ezoption.cn/pre_order/do_calculate'
    type_b_r='09e29f1d964f241733778dfba39dd74ef1fc326c10e57bb019e4452679e66c6f91db4913134a080bcbe29e7b60921c0e6d35914f13b1990f62c1bf8c75e09091835dfdf653fbde52'
    type_b_r = get_type_b_r()
    curr_time = str(long(time.time()*1000))
    cal_url = '''%s?callback=callback&c_K=%.2f&c_T=%d&c_S=%.2f&c_r=%.2f&c_sigma=%.2f&share_symbol=%s&type_b_r=%s&_=%d'''%(cal_host,row['c_K'], row['c_T'], row['c_S'],row['c_r'],row['c_sigma'], row['share_symbol'],type_b_r, int(curr_time))
    return cal_url

def std_hand_share2opt(share_price, goods_price):
    return (100000 * ( goods_price / share_price ))

def gen_res():
    #share_price = ezo_df['c_S']
    # 请求URL之后获得的结果
    #goods_price = cal_url_res
    share_price = 13.80
    goods_price = 1.0446

    # 期权标准手估算价格/元
    std_result = std_hand_share2opt(share_price, goods_price)
    # 权利金比例/%
    pay_amount_rate = std_result / 100000 * 100


###########################################################

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1;Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
    'Accept':'*/*',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding':'gzip, deflate, br',
    'Referer': 'http://www.ezoption.cn/goods/diy'
}

#cookies = init_cookies()

proxies  = {'http':'http://182.90.11.12:8118'}
json_file = './epo.json'
data_file = './data_src.csv'
#print cookies
print headers
# get_all_sk()
df = pd.DataFrame()
#df = gen_sk_data(json_file)

df = pd.read_csv('./data_src.csv')
print len(df[df['res']!=0.0])
#gen_tran(df)
print df.info()
req_cal_res(df)
df.to_csv(data_file, encoding='utf8')

