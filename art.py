import requests
from bs4 import BeautifulSoup as bs
import simplejson as json
from jsonschema import validate
import time
import MySQLdb
'''This script deals with scraping a site focusing on art news. It has the functionality for searching through it's
contents and displaying the respective titles that a user can refer to. This is given in processing.py with the use of
a shared dictionary and also has its data stored in a database.'''

#we pass the corresponding news number and the shared variable. This fucntion will
#make the news dict, save it to a json file, and writes the dict to the shared variable
#called returnVals

#similar change to all getNews functions

def getArtNews(num, returnVals):
    print ("\nArt News\n")
    start_time = time.time() #this is for keeping track of the time it takes to fetch the data
    url = "http://artindiamag.com/Volume21-Issue-2/index.html"
    requestSource = requests.get(url) # or "html.parser"
    beautifiedSource = bs(requestSource.content, "html.parser")
    news_links = []

    for div in beautifiedSource.findAll('div', {'class':'titleContent'}):
        links = div.findAll('a')
        for result in links:
            news_links.append(result.attrs["href"])#taking the parts of the<a> tag that only contain the links ie,href

    LINKS = news_links
    for i in range(len(LINKS)):
        LINKS[i] = LINKS[i] or "null" #if incase a particular LINK doesn't exist,it will be replaced by 'null'

    TITLES =[]

    for div in beautifiedSource.findAll('div', {'class' :'titleContent'}):
        news_links_title = div.find('a')
        TITLES.append(news_links_title.text.strip())#Like we took the link part separately from the whole <a> tag,
                                                    #here we strip the textual part of it alone
    for i in range(len(TITLES)):
        TITLES[i] = TITLES[i] or "null" #same as why we used this for LINKS


    CONTENT =[]
    AUTHORS = []
    print ("\nFetching Art News...\n")
    for link in LINKS:
        requestSource = requests.get("http://artindiamag.com/Volume21-Issue-2/" + link) # or "html.parser"
        beautifiedSource = bs(requestSource.content, "html.parser")
        content_links = beautifiedSource.findAll('p')#This is for going into each of the links and fetching the
                                                     #content from all of them,from <p> tag
        content1 = '' #without this,content1 will be undefined
        for i in range(len(content_links)):
            content1 = beautifiedSource.findAll('p')[i].get_text() + content1 #we need content1 so that it adds the new content
                                                                              # with the previous one without overwriting
        CONTENT.append(content1)
        author_links = beautifiedSource.find("strong")
        AUTHORS.append(author_links.text.strip())

    for i in range(len(AUTHORS)):
        AUTHORS[i] = AUTHORS[i] or "null"


    schema ={
        "type":"object" ,
        "properties": {
        "title":{"type":"string"},
        "url":{"type":"string"},
        "author":{"type":"string"},
        "content":{"type":"string"}
        }
    }
    #schema for the json files we make.
    #some fields differ from script to script


    ART = {}
    for i in range(len(LINKS)):
        ART[i] = {"title":TITLES[i],"url": "http://artindiamag.com/Volume21-Issue-2/" + LINKS[i],"author":AUTHORS[i],"content":CONTENT[i]}
        #dictionary for art,will appear in json format
        #the code that now follows is purely for storing the contents in the database
        title = ART[i]["title"]
        url = ART[i]["url"]
        author = ART[i]["author"]
        content = ART[i]["content"]
        db = MySQLdb.connect(host="localhost", user="root", passwd="", db="art")
        cursor = db.cursor()
        db.set_character_set('utf8')
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        try:
            cursor.execute('''INSERT IGNORE INTO art VALUES (%s, %s, %s, %s)''',(title,url,author,content))
            #ignore is given to ignore the duplicate errors that occur,no duplicates will be added in the databases
            db.commit()
        except:
            db.rollback()
        cursor.execute('''SELECT * FROM `art`; WHERE 1''')
        result = cursor.fetchall() #used for fetching data from the database
        final_result = [element for tup in result for element in tup] #used to change a tuple of tuples into a single list
        #the code shown below is for dealing with unicode errors that occured in the resultant list
        for i in range(len(final_result)):
            if final_result[i] == "\x00":
                final_result[i] = ''
        final_result1 = ''.join(str(final_result[i]))
        final_result2 = final_result1.split('   ')
        db.close()

    print("\n\nValidating Art News...")
    for i in range(len(ART)):
        validate(ART[i],schema) #this validate is to cross check between the final json output and the given schema

    with open("artNews.json", "w") as f:
        jsonfile = json.dumps(ART, indent = 4)
        f.write(jsonfile) #writes into a json file

    print ("\nArt news data stored in artNews.json")
    print("\nTime taken to fetch Art data:\n")
    print("--- %s seconds ---" % (time.time() - start_time))

    #at the num index of returnVals, we put the corresponding news dict
    #similar change in other getNews functions
    returnVals[num] = ART


#the function now searches for something, given the news dict


if __name__ == "__main__":
    #num=0 ==> These default values are to be given if and only if you run this script separately
    #returnVals={}
    getArtNews()#(num,returnVals)
