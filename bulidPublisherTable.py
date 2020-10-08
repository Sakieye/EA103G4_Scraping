import cx_Oracle
import time, datetime
import traceback
import re
import sys,os
import pymysql

def insertPublisherToOracle(PublisherFilePath):
    try:
        conn = cx_Oracle.connect("BOOKSHOP", "123456", "localhost:1521/xe")
        cur = conn.cursor()
        #https://stackoverflow.com/questions/61248730/cx-oracle-databaseerror-ora-01036-illegal-variable-name-number
        sql = "INSERT INTO PUBLISHERS (PUBLISHER_ID, PUBLISHER_NAME, PUBLISHER_PHONE, PUBLISHER_ADDRESS, PUBLISHER_EMAIL) VALUES ('P' || lpad(PUBLISHERS_ID_SEQ.NEXTVAL, 9, '0'),:2,:3,:4,:5)"
        data = [None, '091234TEST', '測試出版社地址', '測試出版社@EMAIL.COM']
        
        f = open(PublisherFilePath, encoding='utf-8')
        for line in f:
            data[0] = line.strip()
            cur.execute(sql, data)
            conn.commit()
            print(cur.rowcount, "record(s) affected")
        f.close()
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

def insertPublisherIDToMySQL(PublisherFilePath):
    try:
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='taaze', charset='utf8')
        cur = conn.cursor()
        cur.execute('USE taaze')
        sql = "UPDATE books SET PUBLISHER_ID = %s WHERE PUBLISHER_NAME = %s;"

        f = open(PublisherFilePath, encoding='utf-8')
        initID = 2
        for line in f:
            name = line.strip()
            publisherID = 'P' + str(initID).zfill(9)
            val = (publisherID, name)
            cur.execute(sql, val)
            conn.commit()
            initID += 1
            print(cur.rowcount, "record(s) affected")
        f.close()
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

        

PublisherFilePath = os.path.realpath('..') + r'\Python\python-scraping-master\TAAZE-scraping\publishers.txt'
# insertPublisherToOracle(PublisherFilePath)
insertPublisherIDToMySQL(PublisherFilePath)