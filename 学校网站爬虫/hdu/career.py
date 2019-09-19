# -*- coding: utf-8 -*-

import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd())))
sys.path.append(path)

import requests, config, log, time, urllib3
from fake_useragent import UserAgent
from lxml import etree
from tweet.school.school_config import Publish
from hashlib import md5
from tweet.school import school_config
from collections import OrderedDict
from datetime import datetime
from random import randint
from time import sleep
from urllib.parse import urljoin
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

db = school_config.mongodb_cline
techweb = db['%s' % (config.mongo_authSource)]['ganhuo_hdu']  # 职位库

ip_port = 'transfer.mogumiao.com:9001'
proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
ua = UserAgent(verify_ssl=False)
appKey = config.APPKEY
headers = {
    "Proxy-Authorization": 'Basic ' + appKey,
    'User-Agent': ua.random,
}
publish = Publish(connect=True)

class TWT(object):
    def __init__(self) -> None:
        super().__init__()
        self.A = 0
        self.B = 0

    def md5_generator(self, url):
        return md5(url.encode()).hexdigest()

    def reqs(self, url_items, num = 0):
        url = url_items[0]
        category_id = url_items[1]
        # new_day = datetime.now().day
        self.A = 0
        self.B = 0
        if num > 4:
            return None
        res = requests.get(url, headers=headers, verify=False, allow_redirects=False, timeout=5)
        if res.status_code == 200:
            con_et = res.json()
            try:
                gs_con = con_et['data']
            except:
                num += 1
            for con_li in gs_con:
                data_id = con_li['notice_id']
                title = con_li['notice_name']
                save = OrderedDict()
                url_one = "http://career.hdu.edu.cn/detail/news?id=%s&menu_id=6435&type_id=3155"%(data_id)
                save['_id'] = self.md5_generator(url_one)
                save['url'] = url_one
                save['title'] = title
                save['category_id'] = category_id
                save['insert_time'] = datetime.now()
                save['state'] = 0
                save['source'] = '杭州电子科技大学'
                try:
                    techweb.insert_one(save)
                    self.gevent_down(url_one, save)
                    self.A += 1
                except Exception as e:
                    if str(e).find("E11000") > -1:
                        self.B += 1
                        continue
                    print("插入失败：%s" % (e))
        else:
            num += 1
            self.reqs(url, num)
        print("第 %s 页， 插入 %s 条， 重复 %s 条， 共% s 条"%(url, self.A, self.B, len(gs_con)))

    def reqs_two(self, url_items, num = 0):
        url = url_items[0]
        category_id = url_items[1]
        self.A = 0
        self.B = 0
        if num > 4:
            return None
        res = requests.get(url, headers=headers, verify=False, allow_redirects=False, timeout=5)
        if res.status_code == 200:
            con_et = etree.HTML(res.text)
            try:
                gs_con = con_et.xpath('//div[@class="sub_lbox"]/div[@class="sub_lcon"]//a')
            except:
                num += 1
                self.reqs_two(url, num)
            for con_li in gs_con:
                try:
                    url_one = con_li.xpath('./@href')[0].strip()
                except:
                    continue
                save = OrderedDict()
                save['_id'] = self.md5_generator(url_one)
                save['url'] = url_one
                save['category_id'] = category_id
                save['insert_time'] = datetime.now()
                save['state'] = 0
                save['source'] = '杭州电子科技大学'
                try:
                    techweb.insert_one(save)
                    self.gevent_down(url_one, save)
                    self.A += 1
                except Exception as e:
                    if str(e).find("E11000") > -1:
                        self.B += 1
                        continue
                    print("插入失败：%s" % (e))
        else:
            num += 1
            self.reqs_two(url, num)
        print("第 %s 页， 插入 %s 条， 重复 %s 条， 共% s 条"%(url, self.A, self.B, len(gs_con)))

    def gevent_down(self, url, item):
        a = 0
        while True:
            a += 1
            if a > 5:
                return None
            try:
                req = requests.get(url=url, headers=headers, verify=False, timeout=10)
                sleep(1)
                if req.status_code != 200:
                    continue
                break
            except:
                sleep(3)
                pass
        try:
            dom_tree = etree.HTML(req.content.decode('utf-8', 'ignore'))
            title = item['title']
            author = ''
            source = '杭州电子科技大学'
            p_s = dom_tree.xpath('//div[@class="details-content"]/p')
            nr_s = []
            for x in p_s:
                conts = x.xpath('.//text()')
                cont = "".join(conts).strip()
                nr_s.append(cont)
            content = "<br/>".join(nr_s)
            img_address = ""
            TF = self.insert_sql_nr(title, source, author, content, img_address, item['category_id'])
            if TF:
                techweb.update_many({'_id': item['_id']}, {'$set': {'state': 2}})
        except Exception as e:
            print(e)

    def insert_sql_nr(self, *args):
        item = {}
        item['category_id'] = args[5]
        item['title'] = args[0]
        item['path'] = args[4]
        item['abstract'] = args[3][:60] + '...'
        item['content'] = publish.unhtml(publish.emoji_gl(args[3]))
        item['hits'] = randint(201, 300)
        item['add_time'] = int(time.time())
        item['display'] = 0
        item['user_id'] = 0
        item['last_user_id'] = 0
        item['last_add_time'] = int(time.time())
        item['batch_path_ids'] = ''
        item['author'] = args[2]
        item['source'] = args[1]
        item['keyword'] = '杭州电子科技大学'
        try:
            publish.upload_data(item, 'customize')
            return True
        except Exception as e:
            print(e)
            return False

    def find_one(self):
        #获取每一页的详情链接 存入mongo
        for i in [['http://career.hdu.edu.cn/module/getnotices?start_page=1&k=&type_id=3155&count=15&start=1', 1266], ['http://career.hdu.edu.cn/module/getnotices?start_page=1&k=&type_id=3160&count=15&start=1', 1266]]:
             self.reqs(i)

if __name__ == '__main__':
    tw = TWT()
    tw.find_one()