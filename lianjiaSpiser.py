# -*- coding:utf-8 -*-
'''
@Author  : minwei
@File    : lianjiaSpider.py
'''

import requests
import lxml
from lxml import etree
import json
import time
import threading

time.clock()
rlock = threading.RLock()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
}


def getArea(url, cityList):
    '''
    获取城市分区
    :param url: 城市url
    :return: 分区字典
    '''
    response = requests.get(url, headers=headers)

    mytree = lxml.etree.HTML(response.text)
    # 区域列表
    areaList = mytree.xpath('//div[@data-role="ershoufang"]/div[1]/a')

    areaDict = {}

    for area in areaList:
        areaName = area.xpath('./text()')[0]
        areaurl = "http://" + cityList + ".lianjia.com" + area.xpath('./@href')[0]
        print(areaName, areaurl)
        areaDict[areaName] = areaurl

    return areaDict


def getPage(url):
    '''
    获取页数
    :param url: 分区url
    :return: 页数
    '''

    response = requests.get(url, headers=headers)

    mytree = lxml.etree.HTML(response.text)
    # 页数
    page = mytree.xpath('//div[@class="page-box house-lst-page-box"]/@page-data')[0]
    totalPage = int(json.loads(page)['totalPage'])
    return totalPage


def getHouseInfo(urlList, city):
    '''
    获取房子信息
    :param urlList :区+页 url列表
    :return:
    '''

    for url in urlList:
        response = requests.get(url[1], headers=headers)

        mytree = lxml.etree.HTML(response.text)

        # 房子列表
        houseList = mytree.xpath('//ul[@class="sellListContent"]/li')

        for house in houseList:
            # 图片
            houseImg = house.xpath('./a/img/@data-original')[0]

            # 标题
            houseAlt = house.xpath('./a/img/@alt')[0]

            # 位置
            houseAddress = house.xpath('.//div[@class="houseInfo"]/a/text()')[0] + \
                           house.xpath('.//div[@class="houseInfo"]/text()')[0]
            # 楼层 小区
            positionInfo = house.xpath('.//div[@class="positionInfo"]/text()')[0] + \
                           house.xpath('.//div[@class="positionInfo"]/a/text()')[0]

            # 总价
            totalPrice = house.xpath('.//div[@class="totalPrice"]/span/text()')[0] + "万"

            # 单价
            unitPrice = house.xpath('.//div[@class="unitPrice"]/span/text()')[0]
            print(houseImg, houseAlt, houseAddress, positionInfo, totalPrice, unitPrice)
            with rlock:
                with open('./data/' + city + url[0] + '.csv', 'a+', encoding='utf-8', errors='ignore') as f:
                    # print(houseImg, houseAlt, houseAddress, positionInfo, totalPrice, unitPrice)
                    f.write(str((houseImg, houseAlt, houseAddress, positionInfo, totalPrice, unitPrice)) + '\n')
                    f.flush()


if __name__ == '__main__':
    '''
    'hf',
    '''
    cityList = ['bj', 'cq', 'xm', 'dg', 'fs', 'gz', 'hui',
                'sz', 'zh', 'zs', 'wh', 'lf', 'sjz', 'hk', 'zz',
                'nj', 'su', 'wx', 'dl', 'sy', 'sh', 'cd', 'jn',
                'qd', 'yt', 'xa', 'tj', 'hz']
    urlList = ["http://%s.lianjia.com/ershoufang/pg1/" % (i) for i in cityList]
    for url, city in zip(urlList, cityList):
        areaDict = getArea(url, city)
        # 全部区+url
        newUrl = []
        for areaName, areaUrl in areaDict.items():
            try:
                totalPage = getPage(areaUrl)
            except Exception as e:
                totalPage = 0
            for i in range(1, totalPage + 1):
                url = areaUrl + "pg%d" % i
                print(url)
                newUrl.append((areaName, url))

        print(newUrl)

        # 20 条线程
        # 二维列表
        cityAndAreaList = [[] for _ in range(20)]

        print(cityAndAreaList)

        for i in range(len(newUrl)):
            cityAndAreaList[i % 20].append(newUrl[i])

        # 开线程
        tList = []
        for urlList in cityAndAreaList:
            print(urlList)
            print('*************************')

            t = threading.Thread(target=getHouseInfo, args=(urlList, city))
            tList.append(t)
            t.start()

        for t in tList:
            t.join()

        print(time.clock())
