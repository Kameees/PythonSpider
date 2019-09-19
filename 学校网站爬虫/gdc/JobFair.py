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
techweb = db['%s' % (config.mongo_authSource)]['ganhuo_school']  # 职位库

ip_port = 'transfer.mogumiao.com:9001'
proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
ua = UserAgent(verify_ssl=False)
appKey = config.APPKEY
headers = {
    "Proxy-Authorization": 'Basic ' + appKey,
    'User-Agent': ua.random,
}

publish = Publish(connect=True)
#   双选会

class TWT(object):
    def __init__(self) -> None:
        super().__init__()
        self.A = 0
        self.B = 0

    def md5_generator(self, url):
        return md5(url.encode()).hexdigest()

    def reqs_two(self, url, num = 0):
        self.A = 0
        self.B = 0
        if num > 4:
            return None
        res = requests.get(url, headers=headers, verify=False, allow_redirects=False, timeout=5)
        gs_con = []
        if res.status_code == 200:
            con_et = etree.HTML(res.content.decode('utf-8', 'ignore'))
            try:
                gs_con = con_et.xpath('.//div[@class="articlelist"]/div')
                for con_li in gs_con:
                    try:
                        title = con_li.xpath('.//div[@class="itemtitle"]/text()')[0].strip()
                        url_one_ = con_li.xpath('./@onclick')[0].split("'")[1].strip()
                        url_one = urljoin(url, url_one_)
                    except:
                        continue
                    save = OrderedDict()
                    save['_id'] = self.md5_generator(url_one)
                    save['url'] = url_one
                    save['title'] = title
                    save['category_id'] = 1266
                    save['insert_time'] = datetime.now()
                    save['state'] = 0
                    save['source'] = '汕头大学'
                    try:
                        techweb.insert_one(save)
                        self.gevent_down(url_one, save)
                        self.A += 1
                    except Exception as e:
                        if str(e).find("E11000") > -1:
                            self.B += 1
                            continue
                        print("插入失败：%s" % (e))
            except:
                num += 1
                self.reqs_two(url, num)
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
            author = ""
            source = "汕头大学"
            nr_s = []
            p_s = dom_tree.xpath('.//*[@id="dualbox"]/div[1]/div[1]/p')
            if len(p_s) == 0:
                p_s = dom_tree.xpath('.//*[@id="dualbox"]/div[1]/div[1]/div')
                if len(p_s) == 0:
                    p_s = dom_tree.xpath('.//*[@id="dualbox"]/div[1]/div[1]/span')

            for x in p_s:
                conts = x.xpath('.//text()')
                cont = "".join(conts).strip()
                nr_s.append(cont)
            nr_s_two = []
            try:
                p_s_two = dom_tree.xpath('.//*[@id="dualbox"]/div[1]/div[2]/div')
                if len(p_s_two) == 0:
                    p_s_two = dom_tree.xpath('.//*[@id="dualbox"]/div[1]/div[2]//div//p')
                    if len(p_s_two) == 0:
                        p_s_two = dom_tree.xpath('.//*[@id="dualbox"]/div[1]/div[1]/div')
                for x in p_s_two:
                    conts = x.xpath('.//text()')
                    cont = "".join(conts).strip()
                    nr_s_two.append(cont)
            except:
                nr_s_two = []
            if nr_s_two == nr_s:
                nr_s_two = []
            if len(nr_s) != 0:
                nr_s.insert(0, '招聘会概况：')
            if len(nr_s_two) != 0:
                nr_s_two.insert(0, '单位邀请函：')
            for n in nr_s:
                if '.xlsx' in n:
                    del nr_s[-1]
            for x in p_s:
                try:
                    style = x.xpath('./@style')[0]
                    if style.find('line-height: 2;') > -1:
                        a_s = x.xpath('./span/a')
                        if len(a_s) != 0:
                            for a in a_s:
                                try:
                                    href_one = a.xpath('.//@href')[0]
                                    href_text = a.xpath('.//text()')[0]
                                except:
                                    continue
                                cont = '<p>附件：<a href="%s">%s</a></p>' % (href_one, href_text)
                                nr_s.append(cont)
                except:
                    continue
            nr_s = nr_s + nr_s_two
            while '' in nr_s:
                nr_s.remove('')
            content = "<br/>".join(nr_s)
            img_address = ""
            TF = self.insert_sql_nr(title, source, author, content, img_address)
            if TF:
                techweb.update_many({'_id': item['_id']}, {'$set': {'state': 2}})
        except Exception as e:
            print(e)

    def insert_sql_nr(self, *args):
        item = {}
        item['category_id'] = 1266
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
        item['keyword'] = '汕头大学'
        try:
            publish.upload_data(item, 'customize')
            return True
        except Exception as e:
            print(e)
            return False

    def find_one(self):
        # 访问第一页
        # 获取每一页的详情链接 存入mongo
        url = "http://gdc.stu.edu.cn/JobFair/DualMeeting"
        self.reqs_two(url)

if __name__ == '__main__':
    tw = TWT()
    tw.find_one()