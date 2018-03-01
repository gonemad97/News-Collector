import requests
from bs4 import BeautifulSoup as bs
import simplejson as json
from jsonschema import validate
import time
import MySQLdb
'''This script deals with scraping a site focusing on science news. It has the functionality for searching through it's
contents and displaying the respective titles that a user can refer to. This is given in processing.py with the use of
a shared dictionary and also has its data stored in a database.'''

def getScienceNews(num, returnVals):
    print ("\nScience News\n")

    start_time = time.time()
    url = "https://www.sciencenews.org/"
    requestSource = requests.get(url) # or "html.parser"
    beautifiedSource = bs(requestSource.content, "html.parser")

    news_links = []

    for h in beautifiedSource.findAll('h2', {'class' :'node-title'}):
        links = h.findAll('a')
        for result in links:
            news_links.append(result.attrs["href"])

    LINKS = news_links
    for i in range(len(LINKS)):
        LINKS[i] = LINKS[i] or "null"

    TITLES = []

    for h in beautifiedSource.findAll('h2', {'class' :'node-title'}):
        news_links_title = h.find('a')
        TITLES.append(news_links_title.text.strip())

    for i in range(len(TITLES)):
        TITLES[i] = TITLES[i] or "null"

    print ("\nFetching Science News...")
    CONTENT =[]
    for link in LINKS:
        requestSource = requests.get(url + link) # or "html.parser"
        beautifiedSource = bs(requestSource.content, "html.parser")
        content_links = beautifiedSource.findAll('p')
        content1 = ''
        for i in range(len(content_links)):
            content1 = beautifiedSource.findAll('p')[i].get_text() + content1
        CONTENT.append(content1)

    schema = {
        "type":"object" ,
        "properties": {
        "title": {"type":"string"},
        "url": {"type":"string"},
        "content": {"type":"string"}
        }
    }


    SCIENCE = {}
    for i in range(len(LINKS)):
        SCIENCE[i] = {"title":TITLES[i],"url": "https://www.sciencenews.org" + LINKS[i],"content":CONTENT[i]}
        title = SCIENCE[i]["title"]
        url = SCIENCE[i]["url"]
        content = SCIENCE[i]["content"]
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="science")
        cursor = db.cursor()
        db.set_character_set('utf8')
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        try:
            cursor.execute('''INSERT IGNORE INTO science VALUES (%s, %s, %s)''',(title,url,content))
            db.commit()
        except:
            db.rollback()
        cursor.execute('''SELECT * FROM `science`; WHERE 1''')
        result = cursor.fetchall()
        final_result = [element for tup in result for element in tup]
        for i in range(len(final_result)):
            if final_result[i] == "\x00":
                final_result[i] = ''
        final_result1 = ''.join(str(final_result[i]))
        final_result2 = final_result1.split('   ')
        db.close()


    print("\n\nValidating Science News...")
    for i in range(len(SCIENCE)):
        validate(SCIENCE[i],schema)

    with open("scienceNews.json", "w") as f:
        jsonfile = json.dumps(SCIENCE, indent = 4)
        f.write(jsonfile)

    print ("\nScience news data stored in scienceNews.json")

    print("\nTime taken to fetch Science data:\n")
    print("--- %s seconds ---" % (time.time() - start_time))


    returnVals[num] = SCIENCE


if __name__ == "__main__":
    #num=0
    #returnVals={}
    getScienceNews()#(num,returnVals)
