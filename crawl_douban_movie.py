#python练习 爬取豆瓣正在播的电影，按照投票人数排序

from urllib import request
from bs4 import BeautifulSoup

req = request.Request("https://movie.douban.com/cinema/nowplaying/shanghai/")
req.add_header("User-Agent", 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
html = request.urlopen(req)
movie_list = []
bs = BeautifulSoup(html, 'lxml')
for movie in bs.find(id='nowplaying').find_all(class_='list-item'):
    movie_list.append(
        {'data-title': movie.attrs['data-title'],
         'data-score': movie.attrs['data-score'],
         'data-actors': movie.attrs['data-actors'],
         'data-votecount': movie.attrs['data-votecount']
         }
    )

for movie in sorted(movie_list, key=lambda x: int(x['data-votecount']),reverse=True):
    print(movie)