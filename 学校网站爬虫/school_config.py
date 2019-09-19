
import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd())))
sys.path.append(path)

import pymysql, re, config, cgi, datetime, random, socket, pymongo, ssl
from urllib.error import ContentTooShortError
from urllib.request import urlretrieve, build_opener, install_opener
from PIL import Image
ssl._create_default_https_context = ssl._create_unverified_context
opener = build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36')]
install_opener(opener)
#线上
if config.env == 1 or config.env == 2:
    mongodb_cline = pymongo.MongoClient(config.mongo_host,
                             username=config.mongo_username[0],
                             password=config.mongo_password[0],
                             authSource=config.mongo_authSource[0],
                             authMechanism='SCRAM-SHA-1')

elif config.env == 0:
    mongodb_cline = pymongo.MongoClient(config.mongo_host)

class Publish(object):
    def __init__(self, connect=True):
        self.db = pymysql.connect(
            host=config.HOST,
            user=config.USER,
            password=config.PASSWORD,
            database=config.DATABASE,
            port=config.PORT,
            charset=config.CHARSET)
        self.cursor = self.db.cursor()
        self.area ={330102: '上城区', 330103: '下城区', 330104: '江干区', 330105: '拱墅区', 330106: '西湖区',
                                       330108: '滨江区', 330109: '萧山区', 330110: '余杭区', 330122: '桐庐县', 330127: '淳安县',
                                       330182: '建德市',
                                       330183: '富阳市', 330185: '临安市'}


    def select_mysql(self, sql, size=0):
        self.cursor.execute(sql)
        if size != 0:
            res = self.cursor.fetchmany(size)
        else:
            res = self.cursor.fetchall()
        return res


    def dict_repeat_file_exists(self, filename):
        """
        判断去重文件是否存在，并返回其去重后的集合
        :param filename: 文件绝对路径
        :return: 去重后的集合
        """
        if os.path.exists(filename):
            set_file = open(filename, 'r', encoding='utf-8', errors='ignore')
            set_data = set_file.readlines()
            set_dict = str(set_data).replace('"', '').replace('\\n', '')[1:-1]
            set_dict = eval('{' + set_dict + '}')
        else:
            set_dict = dict()
        return set_dict

    def repeat_file_exists(self, filename):
        """
        判断去重文件是否存在，并返回其去重后的集合
        :param filename: 文件绝对路径
        :return: 去重后的集合
        """
        if os.path.exists(filename):
            set_file = open(filename, 'r', encoding='utf-8', errors='ignore')
            set_data = set([i.replace('\n', '') for i in set_file.readlines()])
            set_file.close()
        else:
            set_data = set()
        return set_data

    def data_repeat(self, filename, repeat_data):
        """
        数据去重
        :param filename: 去重文件的绝对路径
        :param repeat: 去重的数据
        :return: 返回成功或者错误
        """
        try:
            with open(filename, 'a+', encoding='utf-8', errors='ignore') as f:
                f.write(repeat_data + '\n')
                f.flush()
            return 'ok'
        except Exception as e:
            return e

    def get_area_id(self, area):
        for i in self.area:
            value = self.area[i]
            if str(area).find(value)>-1:
                return i, value
        return 0, ''

    def emoji_gl(self, content):
        """
        过滤emoji字符，防止存入数据库错误
        :param content: 要过滤的字符串内容
        :return: 返回过滤后的字符串
        """
        try:
            highpoints = re.compile('[\U00010000-\U0010ffff]')
        except re.error:
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        resovle_value = highpoints.sub('', content)
        return resovle_value

    def unhtml(self, content):
        """
        将html代码中的特殊字符进行转义，保证传入数据库不出错
        :param content: html代码
        :return: 返回转义后的html代码
        """
        res = cgi.escape(content)
        return res

    def save_images_to_local(self, img_urls, ifformat=False, ifbig=False, ifthumb=False, **kwargs):
        """
        保存图片到本地，图片格式：项目地址 + uploads/2018/1116/20181116102417518242.png
        :param img_urls: 图片集合
        :param ifformat: 是否按原图片到链接下载图片，默认否
        :param ifbig: 是否排除不符合大小到图片
        :param ifthumb: 是否限制图片到大小
        :param kwargs: 参数：
            w_size: 存储时，过滤到最小宽度
            num：过滤后返回到图片路径数，默认9张
        :return: 返回图片到路径
        """
        img_list_ = []
        img_list = []
        for img_url in img_urls:
            img_url_ = img_url
            index1 = img_url.find('@')
            if index1 != -1:
                img_url = img_url[:index1]
            index2 = img_url.find('?')
            if index2 != -1:
                img_url = img_url[:index2]
            a, b = os.path.splitext(img_url)
            if b.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                img_path = self.mkfile(a=b)
            else:
                b = '.jpg'
                img_path = self.mkfile(a=b)
            if ifformat:
                result = self.auto_down(img_url_, img_path)
            else:
                result = self.auto_down(img_url, img_path)
            if result == 'none':
                print('下载图片出错，不保存！')
                continue
            else:
                img_list_.append(img_path)
        w_size = kwargs.get('w_size')
        num = kwargs.get('num')
        if ifbig:
            img_list_ = self.get_big_pic(img_list_)
            if w_size:
                img_list_ = self.get_big_pic(img_list_, w_size=w_size)
            if num:
                img_list_ = self.get_big_pic(img_list_, num=num)
            if w_size and num:
                img_list_ = self.get_big_pic(img_list_, w_size=w_size, num=num)

        if ifthumb:
            width = kwargs.get('width')
            if width != None:
                for img in img_list_:
                    thumb_img = self.thumbnail_pic(img, width=width)
                    img_list += [img]
            else:
                for img in img_list_:
                    thumb_img = self.thumbnail_pic(img)
                    img_list += [img]
        else:
            img_list = img_list_
        return img_list

    def mkfile(self, a='.jpg', *args, **kwargs):
        """
        生成年-月日文件夹和不重复的文件名，并判断是否已经存在
        :param args:
        :param kwargs:
        :return: 返回不重复的文件名
        """
        date = str(datetime.datetime.now().strftime('%Y %m%d %H%M%S'))
        one_dir, two_dir, h_m_s = date.split(' ')
        if sys.platform != 'win32':
            # linux file path
            path = config.UPLOADS_PATH + 'uploads/%s/%s/' % (one_dir, two_dir)
        else:
            # windows file path
            path = os.getcwd() + '\\uploads\\%s\\%s\\' % (one_dir, two_dir)
        if not os.path.exists(path):
            os.makedirs(path)
            if sys.platform != 'win32' and config.TRUE_FALSE == True:
                os.chown(path, 1001, 1001)
                os.chmod(path, 0o777)
        file_name = one_dir + two_dir + h_m_s + str(
            random.randint(100000, 999999))
        file_path = path + file_name + a
        if os.path.exists(file_path):
            return self.mkfile(path=file_path)
        else:
            return file_path

    def auto_down(self, url, filename, count=0):
        """
        防止从网络下载图片下载不完整
        :param url: 网络图片的地址
        :param filename: 要存入的文件名字，绝对路径
        """
        try:
            socket.setdefaulttimeout(20)
            urlretrieve(url, filename)
            if sys.platform != 'win32' and config.TRUE_FALSE == True:
                os.chown(filename, 1001, 1001)
            return 'yes'
        except ContentTooShortError:
            print('Network conditions is not good.Reloading.')
            return self.auto_down(url, filename)
        except TimeoutError:
            print('Time Out Error: Retry！！！')
            return self.auto_down(url, filename)
        except Exception as e:
            count += 1
            if count >= 3:
                return 'none'
            else:
                print('error', url)
                return self.auto_down(url, filename, count)

    def get_big_pic(self, img_list, w_size=400, num=9):
        """
        将图片宽度小于指定大小的图片进行排除
        :param img_list: 图片绝对地址列表
        :param size: 指定的宽度
        :return: 返回符合宽度的图片路径列表
        """
        big_pic = []
        for img in img_list:
            im = Image.open(img)
            w, h = im.size
            if w >= w_size:
                big_pic.append(img)
                if len(big_pic) > num:
                    return big_pic[:num]
        return big_pic

    def thumbnail_pic(self, path, width=300, height=300, count=0):
        """
        生成缩略图文件
        :param path: 图片路径
        :param width: 最大宽度，默认300像素
        :param height: 最大高度，默认300像素
        :return: 返回缩略图文件名
        """
        try:
            im = Image.open(path)
            im.thumbnail((width, height))
            start, end = os.path.splitext(path)
            thumb_path = start + '_thumb' + end
            im.save(thumb_path)
            if sys.platform != 'win32' and config.TRUE_FALSE == True:
                os.chown(thumb_path, 1001, 1001)
        except:
            count += 1
            if count >= 3:
                return path
            else:
                return self.thumbnail_pic(path, count=count)
        return thumb_path

    def upload_img(self, img_path_list, uploads='uploads', table='attachment'):
        """
        将图片信息存储到mysql中
        :param img_path_list: 图片绝对路径列表
        :param uploads: 切割的位置，默认uploads文件夹开始
        :param table: 存储的表名
        :yield: 缩略图片在表中的位置
        """
        for img_path in img_path_list:
            try:
                size = os.path.getsize(img_path)
                index = img_path.find(uploads)
                path = img_path[index:].replace('_thumb', '')
                item = {'path': path, 'size': size}
                # 准备sql语句
                cols, values = zip(*item.items())
                sql = 'insert into `' + table + '` (%s) values (%s)' % (','.join(
                    ['`%s`' % k for k in cols]), ','.join(['%s'] * len(cols)))
                # 游标执行sql语句
                self.cursor.execute(sql, values)
                # if '_thumb' in img_path:
                yield int(self.cursor.lastrowid)
            except Exception as e:
                print(e)
        # 提交sql语句 默认没有自动提交
        self.db.commit()

    def upload_data(self, data_list, table):
        """
        将获取到的数据存入mysql中
        :param data: 接受的数据
        """
        # 准备sql语句
        if not (isinstance(data_list, list) or isinstance(data_list, tuple)
                or isinstance(data_list, set)):
            data_list = [data_list]
        for data_ in data_list:
            cols, values = zip(*data_.items())
            sql = 'insert into `' + table + '`(%s) values (%s)' % (','.join(
                ['`%s`' % k for k in cols]), ','.join(['%s'] * len(cols)))
            # 游标执行sql语句
            self.cursor.execute(sql, values)
            aaa = int(self.cursor.lastrowid)
            self.db.commit()
            return aaa
        # 提交sql语句 默认没有自动提交


    def dict_data_repeat(self, filename, k, v):
        """
        数据去重
        :param filename: 去重文件的绝对路径
        :param repeat: 去重的数据
        :return: 返回成功或者错误
        """
        try:
            with open(filename, 'a+', encoding='utf-8', errors='ignore') as f:
                f.write("'%s': %s\n" % (k, v))
            return 'ok'
        except Exception as e:
            return e

    def upload_data2(self, data_list, table):
        """
        将获取到的数据存入mysql中
        :param data: 接受的数据
        """
        # 准备sql语句
        if not (isinstance(data_list, list) or isinstance(data_list, tuple)
                or isinstance(data_list, set)):
            data_list = [data_list]
        for data_ in data_list:
            cols, values = zip(*data_.items())
            sql = 'insert into `' + table + '`(%s) values (%s)' % (','.join(
                ['`%s`' % k for k in cols]), ','.join(['%s'] * len(cols)))
            # 游标执行sql语句
            self.cursor.execute(sql, values)
        # 提交sql语句 默认没有自动提交
        self.db.commit()

if __name__ == '__main__':
    Publish().get_area_id("shenmo下城区")


