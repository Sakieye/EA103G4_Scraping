import cx_Oracle
import time, datetime
import traceback
import sys,os
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def randomSelectBookIDFromOracle():
    try:
        conn = cx_Oracle.connect("BOOKSHOP", "123456", "localhost:1521/xe")
        cur = conn.cursor()
        # 隨機選取1%的資料
        sql = "SELECT BOOK_ID FROM BOOKS SAMPLE(1)"
        
        bookIDs = cur.execute(sql)
        bookIDList = []
        for bookID in bookIDs:
            bookIDList.append(bookID[0])
        conn.close
        return bookIDList

    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

    finally:
        if conn is not None:
            conn.close()

def setupWebDriver(driverPath):
    # Setup selenium
    opts = Options()
    opts.add_argument("--incognito")
    opts.add_argument("user-agent={}".format("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"))
    driver = webdriver.Chrome(executable_path=driverPath, options=opts)
    # https://blog.csdn.net/anguuan/article/details/104685099
    driver.set_page_load_timeout(20)
    print('Driver start!')
    return driver

def visitBook(bookIDs, driver):
    try:
        for bookID in bookIDs:
            driver.get('http://localhost:8081/EA103G4/Product/' + bookID)
            time.sleep(3)

    except selenium.common.exceptions.TimeoutException as e:
        print(traceback.format_exc())
        print(e)
        driver.close()
        time.sleep(3)
        driver = setupWebDriver(driverPath)
        return False

    except Exception as exc:
        print(traceback.format_exc())
        print(exc)
        return False



driverPath = os.path.realpath('..') + r'\Python\python-scraping-master\chromedriver.exe'
driver = setupWebDriver(driverPath)

while(True):
    bookIDs = randomSelectBookIDFromOracle()
    visitBook(bookIDs, driver)