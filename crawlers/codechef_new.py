from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

import psycopg2
from psycopg2 import Error

from datetime import datetime
import time
import re

# web Driver path
PATH = "C:\Program Files (x86)\chromedriver.exe"

chrome_options = Options()  
chrome_options.headless = True 
chrome_options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

driver = webdriver.Chrome(executable_path=PATH, options=chrome_options) 


# url to crawl
url = 'https://www.codechef.com/'


# create tables in database
def create_table(conn, create_table_sql):
    
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


# insert records in table
def insert_future_data(conn, future_contests):
    
    cursor = conn.cursor()
    try:
        for items in future_contests:
            cursor.execute('INSERT INTO future_contests VALUES (%s,%s,%s,%s,%s,0)', items)

        conn.commit()

        cursor.execute('DELETE FROM future_contests WHERE endTime < timestamp("now", "localtime")')
        conn.commit()
    except:
        conn.rollback()


def insert_present_data(conn, present_contests):
    
    cursor = conn.cursor()
    try:
        for items in present_contests:
                cursor.execute('INSERT INTO present_contests VALUES (%s,%s,%s,%s,%s,0)', items)
        conn.commit()

    # Delete record if the contest has ended.
    cursor.execute('DELETE FROM present_contests WHERE endTime < timestamp("now", "localtime")')
    conn.commit()
    except:
        conn.rollback()

#######################################################  PRESENT CONTESTS ########################################################
def extract_present_data():
    
    WebDriverWait(driver, 10).until( 
        EC.presence_of_all_elements_located((By.XPATH, "//*[@id='primary-content']/div/div[3]/table/tbody/tr")) 
    )

    rows = driver.find_elements_by_xpath("//*[@id='primary-content']/div/div[3]/table/tbody/tr")
    
    rowsize = len(rows)
        
    codes = []
    for i in range(0, rowsize):
        WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="primary-content"]/div/div[3]/table/tbody/tr["+i+"]/td[1]')) 
        )
        codes.append(driver.find_elements_by_xpath('//*[@id="primary-content"]/div/div[3]/table/tbody/tr["+i+"]/td[1]')[i].text)


    names = []
    for i in range(0, rowsize):
        WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="primary-content"]/div/div[3]/table/tbody/tr["+i+"]/td[2]')) 
        )
        names.append(driver.find_elements_by_xpath('//*[@id="primary-content"]/div/div[3]/table/tbody/tr["+i+"]/td[2]')[i].text)

    startTime = []
    for i in range(0, rowsize):
        WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="primary-content"]/div/div[3]/table/tbody/tr["+i+"]/td[3]')) 
        )
        startTime.append(driver.find_elements_by_xpath('//*[@id="primary-content"]/div/div[3]/table/tbody/tr["+i+"]/td[3]')[i].text)
    

    ends = []
    for i in range(0, rowsize):
        WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="primary-content"]/div/div[3]/table/tbody/tr["+i+"]/td[4]')) 
        )
        ends.append(driver.find_elements_by_xpath('//*[@id="primary-content"]/div/div[3]/table/tbody/tr["+i+"]/td[4]')[i].text)

    endTime = []
    for i in ends:
        datetime_object = datetime.strptime(i, '%d %b %Y %H:%M:%S')
        endTime.append(datetime_object)

    lists = [codes, names, startTime, ends, endTime]

    present_contests = list(zip(*lists))

    return (present_contests)


#######################################################  FUTURE CONTESTS ########################################################
def extract_future_data():

    WebDriverWait(driver, 10).until( 
        EC.presence_of_all_elements_located((By.XPATH, "//*[@id='primary-content']/div/div[4]/table/tbody/tr")) 
    )

    rows = driver.find_elements_by_xpath("//*[@id='primary-content']/div/div[4]/table/tbody/tr")
    
    rowsize = len(rows)
        
    codes = []
    for i in range(0, rowsize):
        WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="primary-content"]/div/div[4]/table/tbody/tr["+i+"]/td[1]')) 
        )
        codes.append(driver.find_elements_by_xpath('//*[@id="primary-content"]/div/div[4]/table/tbody/tr["+i+"]/td[1]')[i].text)


    names = []
    for i in range(0, rowsize):
        WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="primary-content"]/div/div[4]/table/tbody/tr["+i+"]/td[2]')) 
        )
        names.append(driver.find_elements_by_xpath('//*[@id="primary-content"]/div/div[4]/table/tbody/tr["+i+"]/td[2]')[i].text)

    starts = []
    for i in range(0, rowsize):
        WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="primary-content"]/div/div[4]/table/tbody/tr["+i+"]/td[3]')) 
        )
        starts.append(driver.find_elements_by_xpath('//*[@id="primary-content"]/div/div[4]/table/tbody/tr["+i+"]/td[3]')[i].text)
    

    ends = []
    for i in range(0, rowsize):
        WebDriverWait(driver, 10).until( 
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="primary-content"]/div/div[4]/table/tbody/tr["+i+"]/td[4]')) 
        )
        ends.append(driver.find_elements_by_xpath('//*[@id="primary-content"]/div/div[4]/table/tbody/tr["+i+"]/td[4]')[i].text)
    
    '''convert the endtime of a contest from "24 Oct 2020 12:30:00" format to "2020-10-24 12:30:00" format '''

    endTime = []
    for i in ends:
        datetime_object = datetime.strptime(i, '%d %b %Y %H:%M:%S')
        endTime.append(datetime_object)

    driver.quit()
    
    lists = [codes, names, starts, ends, endTime]

    future_contests = list(zip(*lists)) 

    return (future_contests)


def get_present_data(conn):
    
    cursor = conn.cursor()
    cursor.execute('SELECT code,name,start,endt FROM present_contests WHERE is_added = 0')
    list_p=cursor.fetchall()
    for item in list_p:
        list_present.append(item)
        

    cursor.execute('UPDATE present_contests SET is_added = 1 ')
    conn.commit()

def get_future_data(conn):
    
    cursor = conn.cursor()
    cursor.execute('SELECT code,name,start,endt FROM future_contests WHERE is_added = 0')
    list_f=cursor.fetchall()
    for item in list_f:
        list_future.append(item)

    cursor.execute('UPDATE future_contests SET is_added = 1 ')
    conn.commit()
     
def print_present_data(list_present):

    print("\nPresent Data")
    for item in list_present:
        print(item)

def print_future_data(list_future):

    print("\nFuture Data")
    for item in list_future:
        print(item)


def main():
    
    # database connection
    conn = None
    try:
        conn = psycopg2.connect("dbname=codechef_new.db host=localhost port=5432 user=postgres password=Samarth@1729")

    except Error as e:
        print(e)

    
    create_table_future = '''CREATE TABLE future_contests(
                    CODE text UNIQUE, NAME text,
                    START text, ENDt text, endTime timestamp, 
                    is_added INTEGER NOT NULL CHECK(is_added IN (0,1)));'''

    create_table_present = '''CREATE TABLE present_contests(
                    CODE text UNIQUE, NAME text,
                    START text, ENDt text, endTime timestamp, 
                    is_added INTEGER NOT NULL CHECK(is_added IN (0,1)));'''

    

    if conn is not None:
        create_table(conn, create_table_present)
        create_table(conn, create_table_future)
    else:
        print("Error! cannot create tha database connection.")

    
    driver.get(url)

    # finds a element with id "menu-309"
    # contests = driver.find_element_by_id("menu-309")
    contests = WebDriverWait(driver, 10).until( 
        EC.presence_of_element_located((By.ID, "menu-309")) 
    )

    contests.click()

    ''' Extract the records from the website and store it in a database table'''
    present_contests = extract_present_data()
    insert_present_data(conn, present_contests)

    future_contests = extract_future_data()
    insert_future_data(conn, future_contests)

    # get data from the tables
    get_present_data(conn)
    get_future_data(conn)

    #print data presents in the table
    print_present_data(list_present)
    print_future_data(list_future)


if __name__ == "__main__":
     
    '''Lists to store records which were not included already''' 
    list_present = []   
    list_future = []    

    main()
