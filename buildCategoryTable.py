import cx_Oracle
import time, datetime
import traceback
import re
import sys,os

# parentCategoryDict = {
# '華文文學':'CAT0100000',
# '世界文學':'CAT0200000',
# '類型文學':'CAT0300000',
# '歷史地理':'CAT0400000',
# '哲學宗教':'CAT0500000',
# '社會科學':'CAT0600000',
# '藝術':'CAT0700000',
# '建築設計':'CAT0800000',
# '商業':'CAT0900000',
# '語言':'CAT1000000',
# '電腦':'CAT1100000',
# '生活風格':'CAT1200000',
# '醫學保健':'CAT1300000',
# '旅遊':'CAT1400000',
# '漫畫':'CAT1500000',
# '政府考用':'CAT1600000',
# '少兒親子':'CAT1700000',
# '教育':'CAT1800000',
# '科學':'CAT1900000',
# '心理勵志':'CAT2000000',
# '傳記':'CAT2100000'}

def insertCategoryToOracle(CategoryFilePath):
    try:
        conn = cx_Oracle.connect("BOOKSHOP", "123456", "localhost:1521/xe")
        cur = conn.cursor()
        sql = "INSERT INTO CATEGORIES (CATEGORY_ID, CATEGORY_NAME, PARENT_CATEGORY_ID) VALUES (:1,:2,:3)"
        
        f = open(CategoryFilePath, encoding='utf-8')
        for line in f:
            categoryID, name = line.split('\t')
            categoryID = 'CAT' + categoryID[-16:-12] + '000'
            name = name[4:].strip()
            parentCategoryID = categoryID[:5] + '00000'
            print(categoryID, name, parentCategoryID)
            cur.execute(sql, [categoryID, name, parentCategoryID])
            conn.commit()
            print(cur.rowcount, "record(s) affected")
        f.close()
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

CategoryFilePath = os.path.realpath('..') + r'\Python\python-scraping-master\TAAZE-scraping\class2links2.txt'
insertCategoryToOracle(CategoryFilePath)