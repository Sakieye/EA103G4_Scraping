# coding=UTF-8
import traceback
import re
import pymysql
import sys,os

# Setup mysql connection
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='taaze', charset='utf8')
cur = conn.cursor()
cur.execute('USE taaze')

def updateSQL(class2idDict):
    try:
        for key in class2idDict:
            category = key
            class2id = class2idDict[key]
            # https://stackoverflow.com/questions/5785154/python-mysqldb-issues-typeerror-d-format-a-number-is-required-not-str
            sql = "UPDATE books SET CLASS2ID = %s WHERE CATEGORY= %s;"
            val = (class2id, category)
            cur.execute(sql, val)
            conn.commit()
            print(cur.rowcount, "record(s) affected")
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

def buildClass2idDict(Class2idFilePath):
    try:
        f = open(Class2idFilePath, encoding='utf-8')
        class2idDict = dict()
        for line in f:
            url, name = line.split('\t')
            url = url[-16:-12]
            name = name[:-1]
            class2idDict[name] = url
        return class2idDict
        f.close()
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

Class2idFilePath = os.path.realpath('..') + r'\Python\python-scraping-master\TAAZE-scraping\class2links2.txt'

class2idDict = buildClass2idDict(Class2idFilePath)
# for key in class2idDict:
#     print(key, class2idDict[key])
updateSQL(class2idDict)
cur.close()
conn.close()