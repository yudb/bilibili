# -*- coding: utf-8 -*-
# @Time    : 2021/3/9 14:32
# @Author  : YuDongbo
# @Email   : jayyudb@126.com
# @File    : sql.py
# @Software: PyCharm

"""
一般 Python 用于连接 MySQL 的工具：pymysql
"""
import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123456',
                             db='metadata',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
'''
初始化本地db和建表
create table aid_detail(
        aid int,
        title varchar(255),
        dynamic varchar(255),
        bvid varchar(64),
        view int,
        danmaku int,
        reply int,
        favorite int,
        coin int,
        share int,
        `like` int,
        dislike int,
        score int,
        his_rank int,
        duration int,
        `desc` varchar(1024),
        tid int,
        tname varchar(255),
        owner_mid int,
        owner_name varchar(255),
        UNIQUE index(aid)
    )ENGINE=INNODB character set utf8mb4
;

create table cid(
aid int,
bvid varchar(64),
cid int,
UNIQUE index(aid)
)ENGINE=INNODB character set utf8mb4
;

create table cid_comment(
cid int,
comment text,
index(cid)
)ENGINE=INNODB character set utf8mb4
;

'''
# 保存视频AID
def insert_aids(aid,title,dynamic,bvid,view,danmaku,reply,favorite,coin,share,like,dislike,score,his_rank,duration,desc,tid,tname,owner_mid,owner_name):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `aid_detail` (aid,title,dynamic,bvid,view,danmaku,reply,favorite,coin,share,`like`,dislike,score,his_rank,duration,`desc`,tid,tname,owner_mid,owner_name) " \
              "VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s) ON DUPLICATE KEY UPDATE " \
              "`title`=%s,`dynamic`=%s,bvid=%s,view=%s,danmaku=%s,reply=%s,favorite=%s,coin=%s,share=%s,`like`=%s,dislike=%s,score=%s,his_rank=%s,duration=%s,`desc`=%s,tid=%s,tname=%s,owner_mid=%s,owner_name=%s"
        cursor.execute(sql, (aid,title,dynamic,bvid,view,danmaku,reply,favorite,coin,share,like,dislike,score,his_rank,duration,desc,tid,tname,owner_mid,owner_name,title,dynamic,bvid,view,danmaku,reply,favorite,coin,share,like,dislike,score,his_rank,duration,desc,tid,tname,owner_mid,owner_name))
    connection.commit()

# 获取AID和BVID
def get_aid_bvid():
    with connection.cursor() as cursor:
        sql = "select aid,bvid from aid_detail"
        cursor.execute(sql, ())
        return cursor.fetchall()

# 保存视频CID
def insert_cids(aid,bvid,cid):
    with connection.cursor() as cursor:
        sql="INSERT INTO `cid` (aid,bvid,cid) values (%s,%s,%s) ON DUPLICATE KEY UPDATE bvid=%s,cid=%s "
        cursor.execute(sql,(aid,bvid,cid,bvid,cid))
    connection.commit()

# 保存视频CID+弹幕
def insert_cid_comment(cid,comment):
    with connection.cursor() as cursor:
        sql="INSERT INTO `cid_comment` (cid,comment) values (%s,%s)"
        cursor.execute(sql,(cid,comment))
    connection.commit()


# 获取视频库的弹幕ID
def get_cids():
    with connection.cursor() as cursor:
        sql = "select DISTINCT cid from cid"
        cursor.execute(sql, ())
        return cursor.fetchall()

def get_comment():
    with connection.cursor() as cursor:
        sql = "select comment,count(comment) as cnt from cid_comment group by comment"
        cursor.execute(sql, ())
        return cursor.fetchall()


def dis_connect():
    connection.close()
