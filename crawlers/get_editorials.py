from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

import psycopg2
from psycopg2 import Error

PATH = "C:\\Program Files (x86)\\chromedriver.exe"

chrome_options = Options()
chrome_options.headless = True
chrome_options.binary_location = "C:\\Program Files (x86)\\Google\Chrome\\Application\\chrome.exe"

driver = webdriver.Chrome(PATH)

driver.get("https://www.codechef.com/contests/?itm_medium=navmenu&itm_campaign=allcontests#past-contests")

import os
from dotenv import load_dotenv
load_dotenv()
PASS = os.getenv("PASSWORD")
PORT = os.getenv("PORT")
DB_NAME_EDIT = os.getenv("DB_NAME_EDIT")

# create tables in database
def create_table(conn, create_table_sql):

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        conn.rollback()
        print(e)


# insert records in table
def insert_edit_data(conn, present_contests):

    cursor = conn.cursor()
    cursor.execute('DELETE FROM editorial_info')
    for items in present_contests:
        try:
            cursor.execute('INSERT INTO editorial_info VALUES (%s,%s,0)', items)
        except Error as e:
            conn.rollback()
            print(e)

    conn.commit()

# text to be found in webpages
find_text = 'the editorials can be found here'
events = driver.find_elements_by_xpath("//*[@id='past-contests-data']/tr['+i+']/td[2]")

# lists to store names of contest and url whose editorial is available
editorial_contests = []
editorial_urls = []

# loop to extract all recent contests whose editorials are available
for i in range(1, len(events)+1):
    cont = "//*[@id='past-contests-data']/tr[" + str(i) + "]/td[2]/a"
    cont_link = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, cont))
        )
    print(cont_link.text)
    current_contest_name = cont_link.text
    try:
        cont_link.click()
    except ElementClickInterceptedException:
        driver.execute_script("window.scrollBy(0,925)", "")
        cont_link.click()
    contest_current_url = driver.current_url
    main = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'main'))
        )
    if find_text in main.text.lower():
        editorial_contests.append(current_contest_name)
        editorial_urls.append(contest_current_url)
        print('yes')
    driver.back()


lists = [editorial_contests, editorial_urls]
editorials = list(zip(*lists))

# establishing connections
conn = None
try:
    conn = psycopg2.connect("dbname=DB_NAME host=localhost port=PORT user=postgres password=PASS")
except Error as e:
    conn.rollback()
    print(e)

create_table_edit = '''CREATE TABLE editorial_info(
                NAME text UNIQUE,
                URL text, 
                is_added INTEGER NOT NULL CHECK(is_added IN (0,1)));'''

if conn is not None:
    create_table(conn, create_table_edit)
else:
    print("Error! cannot create tha database connection.")

insert_edit_data(conn, editorials)


print(editorial_contests)
driver.close()
