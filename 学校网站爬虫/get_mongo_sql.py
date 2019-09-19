# -*- coding: utf-8 -*-

import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd())))
sys.path.append(path)

from tweet.school.hdu import career, jwc, nimportant
from tweet.school.zjgsu import international, jyw, kyc, news
from tweet.school.zufe import xsgl, ygw
from tweet.school.hznu import jxb, qjxgb, xinwenlanmu
from tweet.school.gzhu import news_gzhu, tzgg, xsdt, zpxj
from tweet.school.gdut import gdutnews, gdut_jwc, tupian_news, xsc
from tweet.school.gdc import Announcement, gdc_news, JobFair
from tweet.school.sysu import sysu_career,sysu_news
from tweet.school.scut import scut_edu, scut_news, scut_swtz
from tweet.school.szu import szu_edu
from tweet.school.jnu import jnu_edu, jnu_news
from tweet.school.scnu import scnu_news, scnu_career
from tweet.school.scau import scau_edu, scau_jobfairs
from tweet.school.smu import fimmu, smu_news
from tweet.school.gdufs import gdufs_career, gdufs_edu
from tweet.school.gzucm import gzucm_edu
from tweet.school.dgut import dgut_edu, dgut_tzgg
from tweet.school.gzhmu import gzhmu_news
from tweet.school.gdufe import gdufe_news, gdufe_tzgg
from tweet.school.tsinghua import tsinghua_news, tsinghua_edu, tsinghua_career
from tweet.school.pku import pku_news, pku_tzgg, pku_oir, pku_scc
from tweet.school.ruc import ruc_news, ruc_edu, ruc_rdjy, ruc_io, ruc_keyan

if __name__ == '__main__':
    '''
    print("杭州电子大学运行开始---共7个---")
    career.TWT().find_one()
    jwc.TWT().find_one()
    nimportant.TWT().find_one()
    print("杭州电子大学运行结束")
    print("浙江工商大学运行开始---共10个---")
    international.TWT().find_one()
    jyw.TWT().find_one()
    kyc.TWT().find_one()
    news.TWT().find_one()
    print("浙江工商大学运行结束")
    print("开始财经大学 --- 共4个---")
    xsgl.TWT().find_one()
    ygw.TWT().find_one()
    print("开始杭州师范大学钱江学院 --- 共5个 ----")
    jxb.TWT().find_one()
    qjxgb.TWT().find_one()
    xinwenlanmu.TWT().find_one()
    print("杭州师范大学钱江学院运行结束")
    #   以下是翁诗梦写的
    print("开始广州大学 --- 共7个 ----")
    news_gzhu.TWT().find_one()
    tzgg.TWT().find_one()
    xsdt.TWT().find_one()
    zpxj.TWT().find_one()
    print("广州大学运行结束")
    print("开始广东工业大学 --- 共7个 ----")
    gdutnews.TWT().find_one()
    gdut_jwc.TWT().find_one()
    tupian_news.TWT().find_one()
    xsc.TWT().find_one()
    print("广东工业大学运行结束")
    print("开始汕头大学 --- 共6个 ----")
    Announcement.TWT().find_one()
    gdc_news.TWT().find_one()
    JobFair.TWT().find_one()
    print("汕头大学运行结束")
    print("开始中山大学 --- 共4个 ----")
    sysu_news.TWT().find_one()
    #print('注意：运行sysu_career前要改cookie！！！')
    #sysu_career.TWT().find_one()
    print("中山大学运行结束")
    print("开始华南理工大学 --- 共7个 ----")
    scut_edu.TWT().find_one()
    scut_news.TWT().find_one()
    scut_swtz.TWT().find_one()
    print("华南理工大学运行结束")
    print("开始深圳大学 --- 共6个 ----")
    szu_edu.TWT().find_one()
    print("深圳大学运行结束")
    print("开始暨南大学 --- 共11个 ----")
    jnu_edu.TWT().find_one()
    jnu_news.TWT().find_one()
    print("暨南大学运行结束")
    print("开始华南师范大学 --- 共5个 ----")
    scnu_news.TWT().find_one()
    scnu_career.TWT().find_one()
    print("华南师范大学运行结束")
    print("开始华南农业大学 --- 共7个 ----")
    scau_edu.TWT().find_one()
    scau_jobfairs.TWT().find_one()
    print("华南农业大学运行结束")
    print("开始南方医科大学 --- 共8个 ----")
    fimmu.TWT().find_one()
    smu_news.TWT().find_one()
    print("南方医科大学运行结束")
    print("开始广东外语外贸大学 --- 共3个 ----")
    gdufs_edu.TWT().find_one()
    gdufs_career.TWT().find_one()
    print("广东外语外贸大学运行结束")
    print("广州中医药大学开始 --- 共2个 ----")
    gzucm_edu.TWT().find_one()
    print("广州中医药大学运行结束")
    print("东莞理工学院开始 --- 共6个 ----")
    dgut_edu.TWT().find_one()
    dgut_tzgg.TWT().find_one()
    print("东莞理工学院运行结束")
    print("广州医科大学开始 --- 共5个 ----")
    gzhmu_news.TWT().find_one()
    print("广州医科大学运行结束")
    print("广东财经大学开始 --- 共8个 ----")
    gdufe_news.TWT().find_one()
    gdufe_tzgg.TWT().find_one()
    print("广东财经大学运行结束")
    print("清华大学开始 --- 共11个 ----")
    tsinghua_news.TWT().find_one()
    tsinghua_edu.TWT().find_one()
    tsinghua_career.TWT().find_one()
    print("清华大学运行结束")
     '''
    print("北京大学开始 --- 共11个 ----")
    pku_news.TWT().find_one()
    pku_tzgg.TWT().find_one()
    pku_oir.TWT().find_one()
    pku_scc.TWT().find_one()
    print("北京大学运行结束")
    print("中国人民大学开始 --- 共8个 ----")
    ruc_news.TWT().find_one()
    ruc_edu.TWT().find_one()
    ruc_keyan.TWT().find_one()
    ruc_rdjy.TWT().find_one()
    ruc_io.TWT().find_one()
    print("中国人民大学运行结束")

