from bs4 import BeautifulSoup
import urllib.request
import aiohttp
import asyncio
from collections import OrderedDict
import time
import jieba
import jieba.analyse
from collections import Counter

# IT类工作地址
listTypes = ['5480', '5484']
jobsNum = []
jobList = ["c#","vb","python","c++","sql","swift","go","java", "php","ruby","js","javascript","css"]
urls = []

content = ""

# 伪装浏览器头部
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/81.0.4044.138 Safari/537.36'
}

# 获取网页（文本信息）


async def fetch(session, url):
    try:
        async with session.get(url, headers=headers) as response:
            return await response.text()
    except aiohttp.ServerDisconnectedError:
        # 由于异步的关系，有时候seesion会被提前关闭，这里捕捉异常，用标准库请求
        request = urllib.request.Request(url=url_prefix + '1', headers=headers)
        return urllib.request.urlopen(request)


async def getData(page, session):
    soup = BeautifulSoup(page, 'lxml')
    searchResultPage = soup.find_all(name='div', attrs='rlOne')
    for job in searchResultPage:
        tag_a = job.find('a')
        href = tag_a.get('href')
        company = job.find('li', 'w2').text
        salary = job.find('li', 'w3').text
        jobName = tag_a.text.lower()
        if href not in jobsNum:
            jobsNum.append(href)
            print(company + " " + jobName + ":" + salary + " " + href)
            # 打开详情页
            detailPage = await fetch(session, "https:" + href)
            jobDetail = BeautifulSoup(detailPage, 'lxml').find(
                "pre")
            global content
            content += str(jobDetail)


# 处理网页
async def download(url):
    async with aiohttp.ClientSession() as session:
        page = await fetch(session, url)
        await getData(page, session)

time_start = time.time()

for type_number in listTypes:
    url_prefix = 'https://s.gxrc.com/sJob?schType=1&expend=1&PosType=' + \
        type_number + '&page='

    # Request类的实例，构造时需要传入Url,Data，headers等等的内容
    request = urllib.request.Request(url=url_prefix + '1', headers=headers)
    first_page = urllib.request.urlopen(request)
    soup = BeautifulSoup(first_page, 'lxml')
    intLastPageNumber = int(soup.find('i', {"id": "pgInfo_last"}).text)
    urls.extend([url_prefix + str(i) for i in range(1, intLastPageNumber + 1)])


async def main():
    tasks = []
    for url in urls:
        tasks.append(asyncio.create_task(download(url)))

    await asyncio.gather(*tasks)

    time_end = time.time()
    counter = Counter()
    words = jieba.cut(content, cut_all=False)
    for word in words:
        wordCommn = word.lower()
        if wordCommn in jobList:
            counter[wordCommn] += 1

    print('广西人才网IT岗统计结果(词频)')
    print('总岗位数量:' + str(len(jobsNum)))
    common = counter.most_common(len(jobList))
    for k, v in common:
        print(f"{k}  {v}次")

    print('time cost', time_end-time_start, 's')

asyncio.run(main())
