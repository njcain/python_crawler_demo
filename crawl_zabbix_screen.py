#异步爬取（同时爬取50张）zabbix图片并放到excel表中，爬虫使用socks5代理
import asyncio
import os
import sys
import re
import shutil
import socket
from datetime import datetime

import aiohttp
import requests
import socks
import xlsxwriter
from bs4 import BeautifulSoup

# execute command example:
# python crawler.py "2019-08-08 00:00:00" "2019-08-09 10:10:47"

now = datetime.now()




xlsx_file_name = "zabbix_images.xlsx"

from_time = sys.argv[1]
end_time = sys.argv[2]
xlsx_file_name = sys.argv[3]

picture_directory = "zabbix_image"
if os.path.exists(picture_directory):
    shutil.rmtree(picture_directory)
    os.mkdir(picture_directory)
else:
    os.mkdir(picture_directory)
loop = asyncio.get_event_loop()

#使用本地socks代理
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1081)
socket.socket = socks.socksocket

session = requests.Session()

payload = {'name': 'username', 'password': 'password', "enter": "Sign in", "autologin": 1}
r = session.post('http://zabbix_host_ip/zabbix/index.php', data=payload)
cookies = r.cookies
html = session.get("http://zabbix_host_ip/zabbix/screenconf.php").text
html_test = session.get("http://zabbix_host_ip/zabbix/screens.php?elementid=87").text
soup = BeautifulSoup(html, features="lxml")
screen_urls = soup.find_all("a", {"href": re.compile('^screens.php.elementid.*')})
base_url = "http://zabbix_host_ip/zabbix/"

all_graph = dict()


def get_all_graph():
    global all_graph
    for screen_url in screen_urls:
        html_2 = session.get(base_url + screen_url['href'], ).text
        graphs = re.findall(r'"src":"chart2.php.*', html_2)
        tmpgraph_list = []
        for graph in graphs:
            tmpgraph_list.append(graph)
        all_graph[screen_url.text] = tuple(tmpgraph_list)


get_all_graph()


async def download_session(graph_url, cookies_2, semaphore):
    async with semaphore:
        try:
            async with aiohttp.ClientSession(cookies=cookies_2) as session_2:
                async with session_2.get(graph_url) as response_2:
                    return await response_2.content.read()
        except Exception:
            exit()


async def download_img(screen, graph_url, num, semaphore):
    global cookies
    graph_url = base_url + graph_url[7:-4]
    tmp = graph_url.split("&")
    tmp[-2] = "from=%s" % (from_time,)
    tmp[-1] = "to=%s" % (end_time,)
    graph_url = "&".join(tmp)
    #    print("downloading screen %s num %s ,graph_url is %s" % (screen, num, graph_url))
    r2 = await download_session(graph_url, cookies, semaphore)
    with open(picture_directory + '/' + screen + str(num) + '.png', 'wb') as f:
        f.write(r2)
    print("%s%s.png downloaded" % (screen, str(num)))


async def main(loop):
    tasks = []
    semaphore = asyncio.Semaphore(50)
    for screen in all_graph.keys():
        num = 0
        for graph_url in all_graph[screen]:
            tasks.append(loop.create_task(download_img(screen, graph_url, num, semaphore)))
            num += 1
    await asyncio.wait(tasks)


try:
    loop.run_until_complete(main(loop))
    loop.close()
except Exception:
    exit()
finally:
    loop.close()


def archive_img(all_graph):
    workbook = xlsxwriter.Workbook(xlsx_file_name)
    for screen in all_graph.keys():
        num = 0
        worksheet = workbook.add_worksheet(screen)
        print("add sheet %s" % (screen,))
        for graph_url in all_graph[screen]:
            for i in range(15):
                worksheet.set_row(i, 300)
            worksheet.set_column('A:C', 88)

            if num % 3 == 0:
                worksheet.insert_image("A%s" % (num // 3 + 1), picture_directory + "/" + screen + str(num) + '.png',
                                       {'x_offset': 1, 'y_offset': 1})
            elif num % 3 == 1:
                worksheet.insert_image("B%s" % (num // 3 + 1), picture_directory + "/" + screen + str(num) + '.png',
                                       {'x_offset': 1, 'y_offset': 1})
            elif num % 3 == 2:
                worksheet.insert_image("C%s" % (num // 3 + 1), picture_directory + "/" + screen + str(num) + '.png',
                                       {'x_offset': 1, 'y_offset': 1})
            num += 1
            print("write in %s" % (screen + str(num) + '.png',))
    workbook.close()


archive_img(all_graph)
now_1 = datetime.now()
print(now_1 - now)
