# -*- coding: utf-8 -*-
# @Time    : 2021/3/9 10:22
# @Author  : YuDongbo
# @Email   : jayyudb@126.com
# @File    : content.py
# @Software: PyCharm


import requests
from bs4 import BeautifulSoup
from bilibili_info import sql
import re
import time
import sys
import json

# B站API详情 https://github.com/Vespa314/bilibili-api/blob/master/api.md


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': '_uuid=78A1C727-0C8A-7FA4-6D33-1F8FFCE2382426726infoc; LIVE_BUVID=AUTO8015838253343915; sid=d4szrjp1; blackside_state=1; CURRENT_FNVAL=80; DedeUserID=389085295; DedeUserID__ckMd5=58349e693e4717a6; SESSDATA=cb08288a%2C1621838668%2C01375*b1; bili_jct=1670c90553f082ffff2983841bf76dd0; fingerprint3=15ed1c9b7d68644fb3bfbfb19f2026d0; fingerprint=574b27ad7654afebbaa5c7fd20c55905; buivd_fp=E8FC1D68-EB25-4DB3-B356-7B4163B4EB9A143088infoc; buvid_fp_plain=E8FC1D68-EB25-4DB3-B356-7B4163B4EB9A143088infoc; PVID=1; CURRENT_QUALITY=80; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1609208654; fingerprint_s=3897ec48678dea71eaf424ef089b99d9; buvid_fp=E8FC1D68-EB25-4DB3-B356-7B4163B4EB9A143088infoc; buvid3=6C1DD0AC-46D8-4BD5-B984-E70710960444163158infoc; finger=-166317360; bp_t_offset_389085295=488969785998732334; bsource=search_google',
    'DNT': '1',
    'Host': 'bilibili.com',
    'Pragma': 'no-cache',
    'Referer': 'www.bilibili.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

proxies = {
  "http": "http://10.10.1.10:3128",
  "https": "http://10.10.1.10:1080",
}

# 视频AV号列表
aid_list = []

# 评论用户及其信息
info_list = []

# 获取指定UP的所有视频的AV号 mid:用户编号 size:单次拉取数目 page:页数
def saveIndexAVList():
    # 获取UP主视频列表
    url = "https://www.bilibili.com/v/popular/rank/all"
    r = requests.get(url)
    # 网页解析
    soup = BeautifulSoup(r.content.decode(), 'html.parser')
    body = soup.body
    json_text = body.script.string
    json_text = re.sub('window\\.__INITIAL_STATE__=','',json_text)
    json_text = re.sub('\\,\\"rankNote.*$', '}', json_text)
    data =json.loads(json_text)
    rank_list=data['rankList']

    for rl in rank_list:
        print(rl)
        aid=rl['aid']
        title=rl['title']
        dynamic=rl['dynamic']
        bvid=rl['bvid']
        view=rl['stat']['view']
        danmaku=rl['stat']['danmaku']
        reply=rl['stat']['reply']
        favorite=rl['stat']['favorite']
        coin=rl['stat']['coin']
        share=rl['stat']['share']
        like=rl['stat']['like']
        dislike=rl['stat']['dislike']
        score=rl['score']
        his_rank=rl['stat']['his_rank']
        duration=rl['duration']
        desc=rl['desc']
        tid=rl['tid']
        tname=rl['tname']
        owner_mid=rl['owner']['mid']
        owner_name=rl['owner']['name']
        #写入本地数据库中
        sql.insert_aids(aid,title,dynamic,bvid,view,danmaku,reply,favorite,coin,share,like,dislike,score,his_rank,duration,desc,tid,tname,owner_mid,owner_name)


def saveCidByAid(aid_bvid):
    for aid_bv in aid_bvid:
        aid=aid_bv['aid']
        bvid=aid_bv['bvid']
        url="http://api.bilibili.com/x/web-interface/view?aid=%s&bvid=%s" % (aid,bvid)
        r = requests.get(url)
        numtext = r.text
        json_text = json.loads(numtext)
        cid=json_text['data']['cid']
        sql.insert_cids(aid,bvid,cid)

# 获取一个AV号视频下所有评论
def getAllCommentList(item):
    url = 'https://api.bilibili.com/x/v1/dm/list.so'
    params = {'oid': item}
    resp = requests.get(url,params)
    data = resp.content.decode()
    data = BeautifulSoup(data, "lxml")
    d=data.find_all('d')
    for d_txt in d:
        sql.insert_cid_comment(item,d_txt.get_text())
        print(item,d_txt.get_text())
    time.sleep(5)


if __name__ == "__main__":
    # 爬取全站排行榜TOP100  需要做什么依次打开注释即可
    #第一步把全站排行榜TOP100先拿下,
    saveIndexAVList()

    #第二步获取视频的aid和bvid 就是视频id和视频编码
    aid_bvid=sql.get_aid_bvid()

    #第三步通过aid+bvid获取cid 就是视频的弹幕id
    saveCidByAid(aid_bvid)

    #下面是通过视频的cid获取具体的弹幕内容
    cids=sql.get_cids()
    for cid in cids:
        # print()
        getAllCommentList(cid['cid'])
    print("The End.")
