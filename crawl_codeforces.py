from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

import sqlite3
from sqlite3 import Error

from datetime import datetime
import datetime as dt
import time
import re

# web Driver path
PATH = "C:\Program Files (x86)\chromedriver.exe"

chrome_options = Options()  
chrome_options.headless = True 
chrome_options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

driver = webdriver.Chrome(executable_path=PATH, chrome_options=chrome_options) 


# url to crawl
url = 'https://codeforces.com/'


# create a database connection
def create_connection(db_file):
    
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

# create tables in database
def create_table(conn, create_table_sql):
    
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


# insert records in table
def insert_present_data(conn, present_contests):
    
    cursor = conn.cursor()
    for items in present_contests:
        cursor.execute('INSERT OR IGNORE INTO `Present Contests` VALUES (?,?,?,?,0)', items)

    conn.commit()


    # Delete record if the contest has ended.
    # cursor.execute('DELETE FROM `Present Contests` WHERE endTime < datetime("now", "localtime")')
    # conn.commit()


#######################################################  PRESENT CONTESTS ########################################################
def extract_present_data():
    
    WebDriverWait(driver, 20).until( 
        EC.presence_of_all_elements_located((By.XPATH, "//div[@id='pageContent']/div[1]/div[1]/div[6]/table/tbody/tr")) #//div[@id='pageContent']/div[1]/div[1]/div[6]/table/tbody/tr
    )

    rows = driver.find_elements_by_xpath("//div[@id='pageContent']/div[1]/div[1]/div[6]/table/tbody/tr")
    
    rowsize = len(rows)

    names = []
    for i in range(1, rowsize):
        WebDriverWait(driver, 20).until( 
            EC.presence_of_all_elements_located((By.XPATH, "//div[@id='pageContent']/div[1]/div[1]/div[6]/table/tbody/tr['+i+']/td[1]")) 
        )
        x=driver.find_elements_by_xpath("//div[@id='pageContent']/div[1]/div[1]/div[6]/table/tbody/tr['+i+']/td[1]")
        names.append(driver.find_elements_by_xpath('//div[@id="pageContent"]/div[1]/div[1]/div[6]/table/tbody/tr["+i+"]/td[1]')[i-1].text)
    
    # print(names)

    startTime = []
    for i in range(1, rowsize):
        WebDriverWait(driver, 20).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="pageContent"]/div[1]/div[1]/div[6]/table/tbody/tr["+i+"]/td[3]/a')) 
        )
        # print(('//div[@id="pageContent"]/div[1]/div[1]/div[6]/table/tbody/tr["+i+"]/td[3]/a')[i].text)
        startTime.append(driver.find_elements_by_xpath('//div[@id="pageContent"]/div[1]/div[1]/div[6]/table/tbody/tr["+i+"]/td[3]/a')[i-1].text)

    for start in range(1, rowsize):
        i = startTime[start-1]
        j = i[7:11] + '-' + i[0:3] + '-' + i[4:6] + ' ' + i[13:17] + ':00'
        datetime_object = datetime.strptime(j, '%Y-%b-%d %H:%M:%S')
        startTime[start-1] = datetime_object


    duration = []
    for i in range(1, rowsize):
        WebDriverWait(driver, 20).until( 
            EC.presence_of_all_elements_located((By.XPATH, "//div[@id='pageContent']/div[1]/div[1]/div[6]/table/tbody/tr['+i+']/td[4]")) 
        )
        duration.append(driver.find_elements_by_xpath("//div[@id='pageContent']/div[1]/div[1]/div[6]/table/tbody/tr['+i+']/td[4]")[i-1].text)

    for i in range(1, rowsize):
        d = duration[i-1]
        if d[1] == ':':
            d= '0'+d
        duration[i-1] = d
        

    endTime = []
    for i in range(1, rowsize):
        start = startTime[i-1]
        delta = dt.timedelta(hours=int(duration[i-1][0:2]), minutes=int(duration[i-1][3:5]))
        end = start + delta
        endTime.append(end)

    lists = [names, startTime, duration, endTime]

    present_contests = list(zip(*lists)) 

    return (present_contests)


def get_present_data(conn):
    
    cursor = conn.cursor()
    for item in cursor.execute('SELECT name,start,duration FROM `Present Contests`WHERE is_added = 0').fetchall():
        list_present.append(item)

    cursor.execute('UPDATE `Present Contests` SET is_added = 1 ')
    conn.commit()
     
def print_present_data(list_present):

    print("\nPresent Data")
    for item in list_present:
        print(item)

def main():
    
    # database location
    database = 'codeforces_new.db'
    create_table_present = '''CREATE TABLE IF NOT EXISTS `Present Contests`(
                    NAME text UNIQUE,
                    START text, DURATION text, END text,
                    is_added INTEGER NOT NULL CHECK(is_added IN (0,1)));'''

    
    conn = create_connection(database)

    if conn is not None:
        create_table(conn, create_table_present)
    else:
        print("Error! cannot create tha database connection.")

    
    driver.get(url)
    contests = WebDriverWait(driver, 10).until( 
        EC.presence_of_element_located((By.XPATH , "//div[@id='body']/div[3]/div[5]//ul/li[3]/a"))   #//div[@id='body']/div[3]/div[5]/ul/li[3]/a
    )



    contests.click()

    ''' Extract the records from the website and store it in a database table'''
    present_contests = extract_present_data()
    insert_present_data(conn, present_contests)

    # get data from the tables
    get_present_data(conn)

    #print data presents in the table
    print_present_data(list_present)


if __name__ == "__main__":
     
    '''Lists to store records which were not included already''' 
    list_present = []   

    main()