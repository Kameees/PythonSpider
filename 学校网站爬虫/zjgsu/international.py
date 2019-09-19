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
techweb = db['%s' % (config.mongo_authSource)]['ganhuo_zjgsu']  # 职位库
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

    def reqs(self, url_items, sum_num, num = 0):
        url = url_items[0]
        category_id = url_items[1]
        # new_day = datetime.now().day
        self.A = 0
        self.B = 0
        if num > 4:
            return None
        res = requests.get(url, headers=headers, verify=False, allow_redirects=False, timeout=5)
        if res.status_code == 200:
            con_et = etree.HTML(res.content.decode('gb18030', 'ignore'))
            try:
                gs_con = con_et.xpath('//tr[@valign="top"]//table[@align="center"]//td//a')
            except:
                num += 1
                self.reqs(url, num)
            for con_li in gs_con:
                data_id = con_li.xpath('./@href')[0].strip()
                title = con_li.xpath('./text()')[0].strip()
                save = OrderedDict()
                url_one = urljoin(url, data_id)
                save['_id'] = self.md5_generator(url_one)
                save['url'] = url_one
                save['title'] = title
                save['category_id'] = category_id
                save['insert_time'] = datetime.now()
                save['state'] = 0
                save['source'] = '浙江工商大学'
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
            self.reqs(url, sum_num, num)
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
            dom_tree = etree.HTML(req.content.decode('gb18030', 'ignore'))
            title = item['title']
            author = ''
            source = '浙江工商大学'
            p_s = dom_tree.xpath('//tr[@valign="top"]/td[@align="center"]/table/tr[3]//p')
            bendi_img_address = []
            nr_s = []
            A = 0
            for x in p_s:
                try:
                    img_list_one_ = x.xpath('.//img/@src')[0]
                    img_list_one = urljoin(url, img_list_one_)
                    try:
                        A += 1
                        if A == 1:
                            img_list = publish.save_images_to_local([img_list_one], ifthumb=True) #获取图片地址
                        else:
                            img_list = publish.save_images_to_local([img_list_one], ifthumb=False) #获取图片地址
                        img_addr = "uploads"+ str(img_list[0]).split('uploads')[1].replace("\\",'/')
                        bendi_img_address.append(img_addr)
                        cont = '<p><img src="%s"/></p>'%(img_addr)
                    except Exception as e:
                        print(e, img_list_one)
                        continue
                except:
                    conts = x.xpath('.//text()')
                    cont = "".join(conts).strip()
                nr_s.append(cont)
            content = "<br/>".join(nr_s)
            if bendi_img_address:
                img_address = bendi_img_address[0]
            else:
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
        item['keyword'] = '浙江工商大学'
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
        for sum_num, i in enumerate([['http://international.zjsu.edu.cn/ArticleList.asp?nid=1', 1306], ['http://international.zjsu.edu.cn/ArticleList.asp?nid=2', 1306], ['http://international.zjsu.edu.cn/Articlelist.asp?nid=56', 1306], ['http://international.zjsu.edu.cn/ArticleList.asp?nid=61', 1306]]):
             self.reqs(i, sum_num)

if __name__ == '__main__':
    tw = TWT()
    tw.find_one()