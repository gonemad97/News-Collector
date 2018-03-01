import requests
from bs4 import BeautifulSoup as bs
import simplejson as json
from jsonschema import validate
import time
import MySQLdb
'''This script deals with scraping a site focusing on history news. It has the functionality for searching through it's
contents and displaying the respective titles that a user can refer to. This is given in processing.py with the use of
a shared dictionary and also has its data stored in a database.'''



def getHistoryNews(num, returnVals):
    print ("\nHistory News\n")

    start_time = time.time()
    url = "http://www.history.com/news"
    requestSource = requests.get(url) # or "html.parser"
    beautifiedSource = bs(requestSource.content, "html.parser")

    news_links = []

    for strong in beautifiedSource.findAll('strong', {'class' :'title'},{'itemprop':'name'}):
        links = strong.findAll('a')
        for result in links:
            news_links.append(result.attrs["href"])

    LINKS = news_links
    for i in range(len(LINKS)):
        LINKS[i] = LINKS[i] or "null"

    TITLES =[]

    for strong in beautifiedSource.findAll('strong', {'class' :'title'},{'itemprop':'name'}):
        news_links_title = strong.find('a')
        TITLES.append(news_links_title.text.strip())

    for i in range(len(TITLES)):
        TITLES[i] = TITLES[i] or "null"

    DATES = []

    for div in beautifiedSource.findAll('div', {'class' :'meta'}):
        news_links_date = div.find('span',{'class':'date'})
        DATES.append(news_links_date.text.strip())

    for i in range(len(DATES)):
        DATES[i] = DATES[i] or "null"

    AUTHORS = []

    for div in beautifiedSource.findAll('div', {'class' :'meta'}):
        news_links_author = div.find('strong')
        AUTHORS.append(news_links_author.text.strip())

    for i in range(len(AUTHORS)):
        AUTHORS[i] = AUTHORS[i] or "null"

    print ("\nFetching History News...\n")
    CONTENT =[]
    for link in LINKS:
        requestSource = requests.get("http://www.history.com" + link) # or "html.parser"
        beautifiedSource = bs(requestSource.content, "html.parser")
        content_links = beautifiedSource.findAll('p')
        content1 = ''
        for i in range(len(content_links)):
            content1 = beautifiedSource.findAll('p')[i].get_text() + content1
        CONTENT.append(content1)

    for i in range(len(CONTENT)):
        CONTENT[i] = CONTENT[i] or "null"

    schema = {
        "type":"object",
        "properties": {
        "title":{"type":"string"},
        "date":{"type":"string"},
        "url":{"type":"string"},
        "author":{"type":"string"},
        "content":{"type":"string"}
        }
    }


    HISTORY = {}
    for i in range(len(LINKS)):
        HISTORY[i] = {"title":TITLES[i],"date": DATES[i], "url": "http://www.history.com" + LINKS[i],"author":AUTHORS[i],"content":CONTENT[i]}
        title = HISTORY[i]["title"]
        date = HISTORY[i]["date"]
        url = HISTORY[i]["url"]
        author = HISTORY[i]["author"]
        content = HISTORY[i]["content"]
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="history")
        cursor = db.cursor()
        db.set_character_set('utf8')
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        try:
            cursor.execute('''INSERT IGNORE INTO his VALUES (%s, %s, %s, %s, %s)''',(title,date,url,author,content))
            db.commit()
        except:
            db.rollback()
        cursor.execute('''SELECT * FROM `his`; WHERE 1''')
        result = cursor.fetchall()
        final_result = [element for tup in result for element in tup]
        for i in range(len(final_result)):
            if final_result[i] == "\x00":
                final_result[i] = ''
        final_result1 = ''.join(str(final_result[i]))
        final_result2 = final_result1.split('   ')
        db.close()

    print("\n\nValidating History News...")
    for i in range(len(HISTORY)):
        validate(HISTORY[i],schema)

    with open("historyNews.json", "w") as f:
        jsonfile = json.dumps(HISTORY, indent = 4)
        f.write(jsonfile)

    print ("\nHistory news data stored in historyNews.json")
    print("\nTime taken to fetch History data:\n")
    print("--- %s seconds ---" % (time.time() - start_time))


    returnVals[num] = HISTORY

if __name__ == "__main__":
    #num = 0
    #returnVals ={}
    getHistoryNews()#(num,returnVals)
