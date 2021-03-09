![](https://img.shields.io/badge/Python-3.5.2-blue.svg)

这是一个爬取bilibili的全站热门排行榜的视频和弹幕。

以下为主要思路：

1. 爬取把全站排行榜TOP100先拿下,得到全站热门排行榜的视频信息；
2. 根据上一步获取视频的aid和bvid 就是视频id和视频编码；
3. 第三步通过aid+bvid获取cid 就是视频的弹幕id
4. 通过视频的cid获取具体的弹幕内容
5. The End.
