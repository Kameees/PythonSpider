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
#   通知公告

class TWT(object):
    def __init__(self) -> None:
        super().__init__()
        self.A = 0
        self.B = 0

    def md5_generator(self, url):
        return md5(url.encode()).hexdigest()

    def reqs(self, url_items, sum_num, num = 0):
        url = url_items[0]
        category_id = url_items[1]
        # new_day = datetime.now().day
        self.A = 0
        self.B = 0
        if num > 4:
            return None
        res = requests.get(url, headers=headers, verify=False, allow_redirects=False, timeout=10)
        gs_con = []
        if res.status_code == 200:
            con_et = etree.HTML(res.content.decode('utf-8', 'ignore'))
            try:
                gs_con = con_et.xpath('.//*[@id="tag-article"]/li')
                for con_li in gs_con:
                    data_id = con_li.xpath('.//a/@href')[0].strip()
                    title = con_li.xpath('.//a/text()')[0].strip()
                    save = OrderedDict()
                    url_one = urljoin(url, data_id)
                    save['_id'] = self.md5_generator(url_one)
                    save['url'] = url_one
                    save['title'] = title
                    save['category_id'] = category_id
                    save['insert_time'] = datetime.now()
                    save['state'] = 0
                    save['source'] = '广东财经大学'
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
                self.reqs(url, sum_num, num)
        else:
            num += 1
            self.reqs(url, sum_num, num)
        print("第 %s 页， 插入 %s 条， 重复 %s 条， 共 %s 条"%(url, self.A, self.B, len(gs_con)))

    def gevent_down(self, url, item):
        a = 0
        while True:
            a += 1
            if a > 3:
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
            source = '广东财经大学'
            author = ''
            bendi_img_address = []
            nr_s = []
            A = 0
            p_s = dom_tree.xpath('.//section[@class="maintext sp-toscroll"]//p')
            img_l = dom_tree.xpath('.//div[@class="m-scooch-inner m-dragging"]//div')
            for x in p_s:
                conts = x.xpath('.//text()')
                cont = "".join(conts).strip()
                nr_s.append(cont)
            for i in img_l:
                    try:
                        img_list_one_ = i.xpath('.//img/@src')[0].strip()
                        img_list_one = urljoin(url, img_list_one_)
                        try:
                            A += 1
                            if A == 1:
                                img_list = publish.save_images_to_local([img_list_one], ifthumb=True)  # 获取图片地址
                            else:
                                img_list = publish.save_images_to_local([img_list_one], ifthumb=False)  # 获取图片地址
                            img_addr = "uploads" + str(img_list[0]).split('uploads')[1].replace("\\", '/')
                            bendi_img_address.append(img_addr)
                            cont = '<p><img src="%s"/></p>' % (img_addr)
                            nr_s.append(cont)
                        except Exception as e:
                            print(e, img_list_one)
                            continue
                    except:
                        continue
            while '' in nr_s:
                nr_s.remove('')
            content = "<br/>".join(nr_s)
            if bendi_img_address:
                img_address = bendi_img_address[0]
            else:
                img_address = ""
            if len(title) > 100:
                title = title[:97] + '...'
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
        if -1 < str(args[3]).find("<img") < 15:
            abstract = str(args[3]).split("</p>", 1)[1]
        else:
            abstract = args[3]
        item['abstract'] = abstract[:60] + '...'
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
        item['keyword'] = '广东财经大学'
        try:
            publish.upload_data(item, 'customize')
            return True
        except Exception as e:
            print(e)
            return False

    def find_one(self):
        # 访问第一页
        # url = 'http://www.hdu.edu.cn/news/important'
        #获取每一页的详情链接 存入mongo
        for sum_num, i in enumerate([['http://news.gdufe.edu.cn/t/5', 1306], ['http://news.gdufe.edu.cn/t/3', 1306], ['http://news.gdufe.edu.cn/t/2', 1306], ['http://news.gdufe.edu.cn/t/7', 1306], ['http://news.gdufe.edu.cn/t/8', 1306], ['http://news.gdufe.edu.cn/t/9', 1306], ['http://news.gdufe.edu.cn/t/10', 1306]]):
             self.reqs(i, sum_num)

if __name__ == '__main__':
    tw = TWT()
    tw.find_one()
