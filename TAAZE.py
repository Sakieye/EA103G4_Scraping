# coding=UTF-8
import json
import traceback
import sys,os
import requests
import shutil
import re
import time
import pymysql
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs2json import bs2json
from urllib.request import urlopen
from bs4 import BeautifulSoup

def setupDriver(driverPath):
    # Setup selenium
    opts = Options()
    opts.add_argument("--incognito")
    opts.add_argument("user-agent={}".format("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"))
    driver = webdriver.Chrome(executable_path=driverPath, options=opts)
    # https://blog.csdn.net/anguuan/article/details/104685099
    driver.set_page_load_timeout(20)
    print('Driver start!')
    return driver

# Setup mysql connection
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='taaze', charset='utf8')
cur = conn.cursor()
cur.execute('USE taaze')

def getAllClass2Links(class0page):
    # 由於爬行蒐集耗時，僅執行一次並儲存結果，之後的爬行都直接取用儲存結果
    try:
        # class0最大類別中文書
        driver.get(class0page)
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'list-group')))
        pageSource = driver.page_source
        bs = BeautifulSoup(pageSource, 'html.parser')
        # 取得所有中文書下第一層主類別
        class1Tags = bs.findAll('a', class_='list-group-item', href=re.compile('^(rwd_list.html\?).*'))
        # for tag in class1Tags:
        #     class1Links.append(tag.attrs['href'])
        # print(class1Links)

        # 取得第一層主類別下所有第二層類別的url
        class2Links = []
        class2Names = []
        sql = 'INSERT INTO class2links (url, name) VALUES (%s, %s)'
        for tag in class1Tags:
            print('Crawling class 2 links in a class1...')
            class1Link = 'https://www.taaze.tw/' + tag.attrs['href']
            class1Name = tag.find('span').get_text()
            driver.get(class1Link)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'list-group')))
            pageSource = driver.page_source
            bs = BeautifulSoup(pageSource, 'html.parser')
            class2TagsInThisClass1 = bs.find('div', id='mlistProdCat').findAll('a')
            for class2Tag in class2TagsInThisClass1:
                url = class2Tag.attrs['href']
                class2Name = class2Tag.find('span').get_text()
                class2Name = '中文書,' + class1Name + ',' + class2Name
                if url not in class2Links:
                    class2Links.append(url)
                    class2Names.append(class2Name)
                    cur.execute(sql, (url, class2Name))
                    conn.commit()
        print(class2Links)
        print(class2Names)
        print(len(class2Links)) # 20200809時共有201個class2
        print(len(class2Names))

    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

def getLinksInClass2Page(class2pageURL):
    try:
        driver.get(class2pageURL)
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'listView')))
        pageSource = driver.page_source
        bs = BeautifulSoup(pageSource, 'html.parser')
        links = bs.findAll('a', href=re.compile('^(\/goods\/)[\d]{11}\.html'))
        nextPage = bs.find('a', class_='arrowForRightImg_s')
        bookLinkSet = set()
        for link in links:
            bookLinkSet.add(link.attrs['href'])
        print('get {} links in a class2 page!'.format(len(bookLinkSet)))
        return (bookLinkSet, nextPage)

    except Exception as exc:
        # https://docs.python.org/3/library/traceback.html
        print(traceback.format_exc())
        print(exc)

def getBookInfo(bookLink, class2id):
    try:
        global driver
        driver.get('https://www.taaze.tw' + bookLink)
        time.sleep(3)
        pageSource = driver.page_source
        bs = BeautifulSoup(pageSource, 'html.parser')

        # 網頁中的script Tag提供json，取出其中['script']['text']資訊後轉為字典型別
        converter = bs2json()
        j = converter.convert(bs.find('script', type='application/ld+json'))
        j = json.loads(j['script']['text'])

        bookName = j['name']
        images = j['image']
        if len(images) >= 1: # 只取一張
            images = [images[0]]
        publisherName = j['brand']['name']
        author = j['review']['author']['name']
        author = author.replace('、',',')
        listPrice = j['offers']['price']
        listPrice = int(float(listPrice))

        # https://stackoverflow.com/questions/31958637/beautifulsoup-search-by-text-inside-a-tag
        publishDateTag = bs.find(lambda tag:tag.name=='span' and "出版日期：" in tag.text).find('span')
        if publishDateTag != None:
            publishDate = publishDateTag.get_text()
        else:
            publishDate = None

        languageTag = bs.find(lambda tag:tag.name=='span' and "語言：" in tag.text)
        if languageTag != None:
            language = languageTag.find('span').get_text()
        else:
            language = None

        # 漫畫類別之類的經常沒有isbn，但仍希望收入資料庫
        isbnTag = bs.find(lambda tag:tag.name=='span' and "ISBN/ISSN：" in tag.text)
        if isbnTag != None:
            isbn = isbnTag.find('span').get_text()
        else:
            isbn = None

        # 儲存多個類別中的a標籤，並一一取出其中的文字，放到categoryList
        category = bs.find(lambda tag:tag.name=='span' and "類別：" in tag.text).findAll('a')
        categoryStr = ''
        for c in category:
            categoryStr += (c.get_text()+',')
        categoryStr = categoryStr[:-1]

        bookURL = bookLink.strip('/goods/').strip('.html')
        bookInfo = [isbn, bookName, listPrice, author, categoryStr, class2id, publisherName, publishDate, language, bookURL, images]
        print('isbn:', isbn)
        return bookInfo
    except selenium.common.exceptions.TimeoutException as e:
        print(traceback.format_exc())
        print(e)
        driver.close()
        time.sleep(3)
        driver = setupDriver(driverPath)
        return False

    except Exception as exc:
        print(traceback.format_exc())
        print(exc)
        return False

def downloadImgs(bookInfo):
    # https://towardsdatascience.com/how-to-download-an-image-using-python-38a75cfa21c
    try:
        imgLinks = bookInfo[-1]
        bookLink = bookInfo[-2]

        # mkdir
        folderName = bookLink.strip('/goods/').strip('.html')
        path = r'C:\Users\User\Desktop\images\\' + folderName
        print('download imgs to:', path)
        os.makedirs(path)
        count = 0

        # download images
        for url in imgLinks:
            filename = str(count) + '.jpg'
            count += 1
            r = requests.get(url, stream = True)
            if r.status_code == 200:
                # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                r.raw.decode_content = True
                # Open a local file with wb ( write binary ) permission.
                with open(path + '\\' + filename,'wb') as f:
                    shutil.copyfileobj(r.raw, f)
        return True

    except Exception as exc:
        # https://docs.python.org/3/library/traceback.html
        print(traceback.format_exc())
        print(exc)

def insertToSQL(bookInfo):
    try:
        # https://stackoverflow.com/questions/5785154/python-mysqldb-issues-typeerror-d-format-a-number-is-required-not-str
        sql = 'INSERT INTO books (ISBN, BOOKNAME, LIST_PRICE, AUTHOR, CATEGORY, CLASS2ID, PUBLISHER_NAME, PUBLICATION_DATE, LANGUAGE, BOOKURL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cur.execute(sql, (bookInfo[0], bookInfo[1], bookInfo[2], bookInfo[3], bookInfo[4], bookInfo[5], bookInfo[6], bookInfo[7], bookInfo[8], bookInfo[9]))
        conn.commit()
        return True
    except pymysql.err.IntegrityError as e:
        print('Duplicate entry {}-{}'.format(bookInfo[0], bookInfo[1]))
        return False
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)
        return False

def mainThread(class2LinkFilePath, previousClass2ID):
    try:
        f = open(class2LinkFilePath)
        class2Links = []
        for line in f:
            class2Links.append(line[:-1]) # 去除換行符號
        f.close()

        # 爬行class2pages，class2Links後的[]可以填開始爬行的小類別，可以爬完n類別後中斷，改天繼續爬n類別或n+1類別
        previousClass2Link = 'rwd_listView.html?t=11&k=01&d=00&a=00&c=' + previousClass2ID + '00000000&l=2'
        startFrom = class2Links.index(previousClass2Link)
        class2Links = class2Links[startFrom:]
        for class2Link in class2Links:
            class2id = class2Link[-16:-12] # 取網址的這四碼作為class2id

            # 初始化
            pageNum = 0
            nextPage = True
            crawlingAllpages(pageNum, nextPage, class2Link, class2id)

    except Exception as exc:
        # https://docs.python.org/3/library/traceback.html
        print(traceback.format_exc())
        print(exc)

def crawlingAllpages(pageNum, nextPage, class2Link, class2id):
    try:
        while nextPage:
            pageNum += 1
            # 限制爬行頁數
            # if pageNum > 20:
            #     print('over 20 pages!')
            #     return

            print('crawling class2id: {}, pageNum: {}...'.format(class2id, pageNum))
            duplicateNumInOnePage = 0
            class2pageURL = 'https://www.taaze.tw/' + class2Link + '#' + str(pageNum) + '$1$2'
            bookLinkSet, nextPage = getLinksInClass2Page(class2pageURL)
            for bookLink in bookLinkSet:
                bookInfo = getBookInfo(bookLink, class2id)
                # 取得bookInfo才嘗試insertToSQL
                if bookInfo != False:
                    insertFlag = insertToSQL(bookInfo)
                    # insertToSQL成功才嘗試downloadImgs
                    if insertFlag != False:
                        downloadImgs(bookInfo)
                    else:
                        duplicateNumInOnePage += 1
                        if duplicateNumInOnePage >= 5:
                            print('too much duplicate books in this page, jump to next page!')
                            break;
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)
        pageNum += 1
        nextPage = True
        crawlingAllpages(pageNum, nextPage, class2Link, class2id)

driverPath = os.path.realpath('..') + r'\Python\python-scraping-master\chromedriver.exe'
driver = setupDriver(driverPath)
# 必須先取得所有class2 url和name才有class2LinkFilePath
# getAllClass2Links('https://www.taaze.tw/rwd_list.html?t=11&k=01&d=00')
class2LinkFilePath = os.path.realpath('..') + r'\Python\python-scraping-master\TAAZE-scraping\class2links.txt'

# getBookInfo('/goods/11100897359.html')
# print('='*50)
# getBookInfo('/goods/11100911993.html')
# print('='*50)
# insertToSQL(getBookInfo('/goods/11100914173.html'))
# downloadImgs(getBookInfo('/goods/11100914173.html'))
# getAllClass2Link('https://www.taaze.tw/rwd_list.html?t=11&k=01&d=00')

mainThread(class2LinkFilePath, '0907')
cur.close()
conn.close()
driver.close()
