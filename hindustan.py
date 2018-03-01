import requests
from bs4 import BeautifulSoup as bs
import simplejson as json
from jsonschema import validate
import time
import MySQLdb
'''This script deals with scraping a site focusing on music news. It has the functionality for searching through it's
contents and displaying the respective titles that a user can refer to. This is given in processing.py with the use of
a shared dictionary and also has its data stored in a database.'''

def getMusicNews(num, returnVals):

    print ("\nMusic News\n")
    start_time = time.time()
    url = "http://www.hindustantimes.com/music/"
    requestSource = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}) # or "html.parser"
    beautifiedSource = bs(requestSource.content, "html.parser")

    top_three_links = []
    top_two_links = []
    recent_news_links = []

    for div in beautifiedSource.findAll('div', {'class' :'media-heading headingfive'}):
        top_three = div.findAll('a')
        for result in top_three:
            top_three_links.append(result.attrs["href"])

    for div in beautifiedSource.findAll('div', {'class':'col-sm-4 col-md-4 col-lg-3 border-right'}):
        top_two = div.find('a')
        top_two_links.append(top_two.attrs["href"])

    for div in beautifiedSource.findAll('div', {'class':'media-heading headingfour'}):
        recent_news = div.findAll('a')
        for result in recent_news:
            recent_news_links.append(result.attrs["href"])

    LINKS = top_three_links + top_two_links + recent_news_links

    for i in range(len(LINKS)):
        LINKS[i] = LINKS[i] or "null"

    TITLES =[]

    for div in beautifiedSource.findAll('div', {'class' :'media-heading headingfive'}):
        top_three_title = div.find('a')
        TITLES.append(top_three_title.text.strip())

    for div in beautifiedSource.findAll('div', {'class':'col-sm-4 col-md-4 col-lg-3 border-right'}):
        top_two_title = div.find('a')
        TITLES.append(top_two_title.text.strip())


    for div in beautifiedSource.findAll('div', {'class':'media-heading headingfour'}):
        recent_news_title = div.find('a')
        TITLES.append(recent_news_title.text.strip())

    for i in range(len(TITLES)):
        TITLES[i] = TITLES[i] or "null"

    DATES = []
    for div in beautifiedSource.findAll('div', {'class' :'col-sm-12 col-lg-3 col-lg-push-3'}):
        top_three_date = div.find('span',{'class':'time-dt mb-5'})
        DATES.append(top_three_date.text.strip())

    for div in beautifiedSource.findAll('div', {'class':'clearfix top-news-sec'}):
        top_two_date = div.find('span',{'class':'time-dt mb-5'})
        DATES.append(top_two_date.text.strip())

    for div in beautifiedSource.findAll('div', {'class':'media-body'}):
        recent_news_date = div.find('span', {'class':'time-dt'})
        DATES.append(recent_news_date.text.strip())

    for i in range(len(DATES)):
        DATES[i] = DATES[i] or "null"


    CONTENT = []
    for link in LINKS:
        #added headers because this website has auto bot detection, and will reset the connection if multiple pings from the same IP is detected.
        #if connection reset by peer error happens, usage of headers solves the problem
        requestSource = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}) # or "html.parser"
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
        "content":{"type":"string"}
        }
    }

    print ("\nFetching Music News...\n")
    HINDUSTAN = {}
    for i in range(len(LINKS)):
        if i == 0:
            HINDUSTAN[i] = {"title":TITLES[i],"date": "null" ,"url" : LINKS[i],"content":CONTENT[i]}
        else:
            HINDUSTAN[i] = {"title":TITLES[i],"date": DATES[i-1], "url": LINKS[i],"content":CONTENT[i]}
        title = HINDUSTAN[i]["title"]
        date = HINDUSTAN[i]["date"]
        url = HINDUSTAN[i]["url"]
        content = HINDUSTAN[i]["content"]
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="music")
        cursor = db.cursor()
        db.set_character_set('utf8')
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        try:
            cursor.execute('''INSERT IGNORE INTO music VALUES (%s, %s, %s, %s)''',(title,date,url,content))
            db.commit()
        except:
            db.rollback()
        cursor.execute('''SELECT * FROM `music`; WHERE 1''')
        result = cursor.fetchall()
        final_result = [element for tup in result for element in tup]
        for i in range(len(final_result)):
            if final_result[i] == "\x00":
                final_result[i] = ''
        final_result1 = ''.join(str(final_result[i]))
        final_result2 = final_result1.split('   ')
        db.close()



    print("\n\nValidating Music News..")
    for i in range(len(HINDUSTAN)):
        validate(HINDUSTAN[i],schema)

    with open("musicNews.json", "w") as f:
        jsonfile = json.dumps(HINDUSTAN, indent = 4)
        f.write(jsonfile)

    print ("\nMusic news data stored in musicNews.json")
    print("\nTime taken to fetch Music data:\n")
    print("--- %s seconds ---" % (time.time() - start_time))

    returnVals[num] = HINDUSTAN

if __name__ == "__main__":
    #num = 0
    #returnVals = {}
    getMusicNews()#(num,returnVals)
