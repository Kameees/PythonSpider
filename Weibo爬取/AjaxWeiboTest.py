from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient
base_url = 'https://m.weibo.cn/api/container/getIndex?'

headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/6048193311',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

def get_page(page):
    params = {
        'type': 'uid',
        'value': '6048193311',
        'containerid': '1076036048193311',
        'page': page
    }
    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return  response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)

def parse_page(json):   #   解析json格式的数据
    if json:
        items = json.get('data').get('cards')
        for item in items:
            item = item.get('mblog')
            weibo = {}
            weibo['id'] = item.get('id')
            weibo['text'] = pq(item.get('text')).text()
            weibo['attitudes'] = item.get('attitudes_count')
            weibo['comments'] = item.get('comments_count')
            weibo['reposts'] = item.get('reposts_count')
            yield weibo

client = MongoClient()
db = client['weibo']
collection = db['weibo']

def save_to_mongo(result):  #   存入MongoDB
    if collection.insert(result):
        print('Saved to Mongo')

if __name__ == '__main__':
    for page in range(1,11):
        json = get_page(page)
        results = parse_page(json)
        for result in results:
            print('====================')
            print(result)
            save_to_mongo(result)
