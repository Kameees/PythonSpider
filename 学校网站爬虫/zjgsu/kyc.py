# -*- coding: utf-8 -*-

import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd())))
sys.path.append(path)

import requests, config, log, time, urllib3, re
from fake_useragent import UserAgent
from lxml import etree
from tweet.school.school_config import Publish
from hashlib import md5
from tweet.school import school_config
from collections import OrderedDict
from datetime import datetime
from random import randint
from time import sleep
from json import dumps
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
    'Content-Type': 'text/plain'
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
        if sum_num == 0:
            data =  {
                "callCount": "1",
                "page": "/typePage.do?yygrlxym=null&lmdm=1070113&kjdm=",
                "httpSessionId": "9B8849C94E6291B2CE6878542918DB7E",
                "scriptSessionId": "F1E29E3A74A2839A992334CE72F64BC6370",
                "c0-scriptName": "typePageContentAjax",
                "c0-methodName": "getNewsList",
                "c0-id": "0",
                "c0-param0": "string:149023632368278722",
                "c0-param1": "string:1070113",
                "c0-e1": "number:15",
                "c0-e2": "number:1",
                "c0-e3": "number:0",
                "c0-param2": "Object_Object:{pageSize:reference:c0-e1, currentPage:reference:c0-e2, startRecord:reference:c0-e3}",
                "batchId": "0",
            }
        elif sum_num == 1:
            data = {
                "callCount": "1",
                "page": "/typePage.do?yygrlxym=null&lmdm=1070107&kjdm=",
                "httpSessionId": "D9E270084A2D47D51D7FBF652822D0FD",
                "scriptSessionId": "994FF63B4ADDB3E2FD9B6E6828FD74D8784",
                "c0-scriptName": "typePageContentAjax",
                "c0-methodName": "getNewsList",
                "c0-id": "0",
                "c0-param0": "string:149023632368278722",
                "c0-param1": "string:1070107",
                "c0-e1": "number:15",
                "c0-e2": "number:1",
                "c0-e3": "number:0",
                "c0-param2": "Object_Object:{pageSize:reference:c0-e1, currentPage:reference:c0-e2, startRecord:reference:c0-e3}",
                "batchId": "0",
            }
        else:
            return
        res = requests.post(url, headers=headers, data=data, verify=False, allow_redirects=False, timeout=5)
        if res.status_code == 200:
            con_et = res.text
            try:
                gs_con = [u.split('"')[0] for u in con_et.split('jtymdz="')[1:]]
            except:
                num += 1
                self.reqs(url, num)
            for con_li in gs_con:
                save = OrderedDict()
                url_one = "http://kyc.zjgsu.edu.cn//news/%s"%(con_li)
                save['_id'] = self.md5_generator(url_one)
                save['url'] = url_one
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
            title = dom_tree.xpath('//div[@class="title"]/div[@class="btbt"]/h3/text()')[0]
            author = ''
            try:
                source = str(dom_tree.xpath('//div[@class="title"]/h4/span[@class="bm"]/text()')[0]).replace("单位：","")
            except:
                source = "浙江工商大学"
            p_s = dom_tree.xpath('//div[@id="xwcontentdisplay"]/p')
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
        for sum_num, i in enumerate([['http://kyc.zjgsu.edu.cn/dwr/call/plaincall/typePageContentAjax.getNewsList.dwr', 1256], ['http://kyc.zjgsu.edu.cn/dwr/call/plaincall/typePageContentAjax.getNewsList.dwr', 1306]]):
             self.reqs(i, sum_num)

if __name__ == '__main__':
    tw = TWT()
    tw.find_one()