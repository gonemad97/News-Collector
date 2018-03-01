import requests
from bs4 import BeautifulSoup as bs
import simplejson as json
from jsonschema import validate
import time
import MySQLdb
'''This script deals with scraping a site focusing on child development news. It has the functionality for searching through it's
contents and displaying the respective titles that a user can refer to. This is given in processing.py with the use of
a shared dictionary and also has its data stored in a database.'''

def getChildNews(num, returnVals):
    print ("\nChild Development News\n")
    start_time = time.time()
    url = "https://childdevelopmentinfo.com/"
    requestSource = requests.get(url) # or "html.parser"
    beautifiedSource = bs(requestSource.content, "html.parser")

    news_links = []

    for h in beautifiedSource.findAll('h2', {'class' :'title entry-title'}):
        links = h.findAll('a')
        for result in links:
            news_links.append(result.attrs["href"])


    LINKS = news_links
    for i in range(len(LINKS)):
        LINKS[i] = LINKS[i] or "null"

    TITLES = []

    for h in beautifiedSource.findAll('h2', {'class' :'title entry-title'}):
        news_links_title = h.find('a')
        TITLES.append(news_links_title.text.strip())

    for i in range(len(TITLES)):
        TITLES[i] = TITLES[i] or "null"

    DATES = []

    for div in beautifiedSource.findAll('div', {'class' :'post-meta'}):
        news_links_date = div.find('abbr')
        DATES.append(news_links_date.text.strip())

    for i in range(len(DATES)):
        DATES[i] = DATES[i] or "null"

    AUTHORS = []

    for span in beautifiedSource.findAll('span', {'class' :'fn'}):
        news_links_author = div.find('a')
        AUTHORS.append(news_links_author.text.strip())

    for i in range(len(AUTHORS)):
        AUTHORS[i] = AUTHORS[i] or "null"

    print ("\nFetching Child Development News...\n")
    CONTENT =[]
    for link in LINKS:
        requestSource = requests.get(link) # or "html.parser"
        beautifiedSource = bs(requestSource.content, "html.parser")
        content_links = beautifiedSource.findAll('p')
        content1 = ''
        for i in range(len(content_links)):
            content1 = beautifiedSource.findAll('p')[i].get_text() + content1
        CONTENT.append(content1)

    for i in range(len(CONTENT)):
        CONTENT[i] = CONTENT[i] or "null"



    schema ={
        "type":"object" ,
        "properties": {
        "title":{"type":"string"},
        "date":{"type":"string"},
        "url":{"type":"string"},
        "author":{"type":"string"},
        "content":{"type":"string"}
        }
    }


    CHILD = {}
    for i in range(len(LINKS)):
        CHILD[i] = {"title":TITLES[i],"date": DATES[i], "url": LINKS[i],"author":AUTHORS[i],"content":CONTENT[i]}
        title = CHILD[i]["title"]
        date = CHILD[i]["date"]
        url = CHILD[i]["url"]
        author = CHILD[i]["author"]
        content = CHILD[i]["content"]
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="child")
        cursor = db.cursor()
        db.set_character_set('utf8')
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        try:
            cursor.execute('''INSERT IGNORE INTO child VALUES (%s, %s, %s, %s, %s)''',(title,date,url,author,content))
            db.commit()
        except:
            db.rollback()
        cursor.execute('''SELECT * FROM `child`; WHERE 1''')
        result = cursor.fetchall()
        final_result = [element for tup in result for element in tup]
        for i in range(len(final_result)):
            if final_result[i] == "\x00":
                final_result[i] = ''
        final_result1 = ''.join(str(final_result[i]))
        final_result2 = final_result1.split('   ')
        db.close()


    print("\n\nValidating Child Development News...")
    for i in range(len(CHILD)):
        validate(CHILD[i],schema)

    with open("childNews.json", "w") as f:
        jsonfile = json.dumps(CHILD, indent = 4)
        f.write(jsonfile)

    print ("\nChild Development news data stored in childNews.json")
    print("\nTime taken to fetch Child data:\n")
    print("--- %s seconds ---" % (time.time() - start_time))

    returnVals[num] = CHILD

if __name__ == "__main__":
    #num = 0
    #returnVals = {}
    getChildNews()#(num,returnVals)
