import cx_Oracle
import time, datetime
import traceback
import re
import sys,os
import random
import datetime
import json 

languageDict = {'繁體中文':'LAN0000001', '簡體中文':'LAN0000002', '英文':'LAN0000003', '日文':'LAN0000004', '韓文':'LAN0000005'}

def insertBookToOracle(BookFilePath, start):
    try:
        conn = cx_Oracle.connect("BOOKSHOP", "123456", "localhost:1521/xe")
        cur = conn.cursor()
        sql = "INSERT INTO BOOKS (BOOK_ID, PUBLISHER_ID, LANGUAGE_ID, CATEGORY_ID, BOOK_NAME, ISBN, AUTHOR, LIST_PRICE, SALE_PRICE, BOOK_BP, IS_SOLD, PUBLICATION_DATE, PROMO_END_TIME, STOCK, SAFETY_STOCK, BOOK_INTRO, BOOK_NAME_ORIGINAL, URL) VALUES ('B' || lpad(BOOK_ID_SEQ.NEXTVAL, 11, '0'),:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18)"
        
        with open(BookFilePath, encoding='utf-8') as jsonFile:
            j = json.load(jsonFile) 
            count = 0
            for book in j:
                count += 1
                print(count)
                if count < start:
                    continue
                # print(book)
                publisherID = book['PUBLISHER_ID']
                language = book['LANGUAGE']
                languageID = None
                if language != None:
                    languageID = languageDict[language]
                categoryID = 'CAT' + book['CLASS2ID'] + '000'
                bookName = book['BOOKNAME']
                isbn = book['ISBN']
                author = book['AUTHOR']
                listPrice = book['LIST_PRICE']
                salePrice = int(listPrice*random.randint(90, 95)/100)
                bookBP = int(listPrice*random.randint(0, 5)/100)
                isSold = 1
                if random.randint(0, 100) < 1:
                    isSold = 0
                publicationDate = None
                pDate = book['PUBLICATION_DATE']
                if pDate != None:
                    try:
                        publicationDate = datetime.datetime(int(pDate[:4]), int(pDate[5:7]), int(pDate[-2:]))
                    except Exception as exc:
                        publicationDate = None
                        print('Fucking TAAZE')
                stock = random.randint(0, 1000)
                safetyStock = random.randint(0, 100)
                bookIntro = '測試書籍簡介'
                bookNameOriginal = None
                url = book['BOOKURL']
                
                bookdata = [publisherID, languageID, categoryID, bookName, isbn, author, listPrice, salePrice, bookBP, isSold, publicationDate, None, stock, safetyStock, bookIntro, bookNameOriginal, url]
                # print(bookdata)

                cur.execute(sql, bookdata)
                conn.commit()
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

BookFilePath = os.path.realpath('..') + r'\Python\python-scraping-master\TAAZE-scraping\Results\20200913result.json'
insertBookToOracle(BookFilePath, 0)