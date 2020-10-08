import cx_Oracle
import time, datetime
import traceback
import re
import sys,os
import random
import datetime
import json 
from os import listdir
from os.path import isfile, join
import shutil

def insertBookPicToOracle(PicRootFolderPath, start):
    try:
        conn = cx_Oracle.connect("BOOKSHOP", "123456", "localhost:1521/xe")
        cur = conn.cursor()
        insertSQL = "INSERT INTO BOOK_PICTURES (BOOK_ID, BOOK_PIC_NAME, BOOK_PIC) VALUES (:1,:2,:3)"
        selectSQL = "SELECT BOOK_ID FROM BOOKS WHERE URL=:url"

        for folderName in os.listdir(PicRootFolderPath):
            folder = r'C:/Users/User/Desktop/images/' + folderName
            bookID = cur.execute(selectSQL, {'url':folderName}).fetchone()
            bookID = bookID[0]
            # if bookID == None:
            #     shutil.rmtree(folder)
            #     continue
            print('folderName:', folderName)
            print('bookID:', bookID)

            bookIsExisted = cur.execute("SELECT BOOK_ID FROM BOOK_PICTURES WHERE BOOK_ID=:bookID", {'bookID':bookID}).fetchone()
            if bookIsExisted:
                print('existed!')
                continue
            
            for pic in os.listdir(folder):
                with open(os.path.join(folder, pic), 'rb') as f: # open in readonly mode
                    picNum = f.name[f.name.rindex("\\") + 1:]
                    picBytes = f.read()
                    if picBytes == b'':
                        print('None File!')
                        continue
                    print(picNum)
                    # print(f.read())
                    # print([bookID, picNum, picBytes])
                    cur.execute(insertSQL, [bookID, picNum, picBytes])
                    conn.commit()

    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

insertBookPicToOracle(r'C:/Users/User/Desktop/images', 0)

# def test():
#     filePath = r'C:\Users\User\Desktop\images\11100850644\1.jpg'
#     with open(filePath, 'rb') as f:
#         print(f.read())
#         print(f.read() == b'')
# test()
 