 from multiprocessing import Process, Manager
#importing manager also
from science import getScienceNews
from child import getChildNews
from hindustan import getMusicNews
from history import getHistoryNews
from art import getArtNews
'''In this script,we incorporate all the other scripts,history.py,science.pt,child.py,art.py and music.py
and make them fetch all the data from their respective sites at once. This script makes use of the multiprocessing
module so that all the scripts are run at the same time,thereby reducing time delay. We also make use of a shared
dictionary caled returnVals, so that we can make use of the effective search function,search_proc(). All the data fetched
will also be put into each of the scripts' respective databases.NOTE:All referential comments can be viewed from art.py.
Lots of changes can be made to this program and many additions can be made as well. Some things were avoided due to time
contraints and difficulty,so please feel free to change anything :)'''

# Initiate workers for the functions
if __name__ == '__main__':
    #making a shared variable(dictionary) called returnVals
    manager = Manager() #inbuilt python function from multiprocessing module to help create shared variable
    returnVals = manager.dict()

    #0 corresponds to science news
    #1   "          "   child news and so on
    #passing arguments to the news fetching functions (num, returnVals)
    workerSCIENCE = Process(target=getScienceNews, args = (0, returnVals))
    workerCHILD = Process(target=getChildNews, args = (1, returnVals))
    workerHINDUSTAN = Process(target=getMusicNews, args = (2, returnVals))
    workerHISTORY = Process(target=getHistoryNews, args = (3, returnVals))
    workerART = Process(target=getArtNews, args = (4, returnVals))


    # Start the workers
    workerSCIENCE.start()
    workerCHILD.start()
    workerHINDUSTAN.start()
    workerHISTORY.start()
    workerART.start()

    # Wait until the functions have finished
    workerSCIENCE.join()
    workerCHILD.join()
    workerHINDUSTAN.join()
    workerHISTORY.join()
    workerART.join()

#returnVals is a dict, with the news dicts at the corresponding indices. Basically a dict of dicts
#could use a list also, but since we use threading the order of the dicts returned might be messed up
    SCIENCE = returnVals[0]
    CHILD = returnVals[1]
    HINDUSTAN = returnVals[2]
    HISTORY = returnVals[3]
    ART = returnVals[4]



    def search_proc():
        while True:
            search_topic = input("Enter which topic you'd like to search about...\nEnter science,history,art,music or child: ")
            if search_topic == 'exit':
                break
            elif search_topic == 'history':
                search(HISTORY, "history")  #the news dicts we returned from the getNews functions.
                                 #we say, search  in HISTORY dict, using a universal 'search' function
            elif search_topic == 'science':
                search(SCIENCE, "science")
            elif search_topic == 'art':
                search(ART, "art")
            elif search_topic == 'music':
                search(HINDUSTAN, "music")
            elif search_topic == 'child':
                search(CHILD, "child development")
            else:
                print("No such topic")




#universal search function, no need of separate search functions for each kind of news
    def search(newsDict, newstype):
        while True:
            search = input("Search for something in {} news: ".format(newstype))
            #if the search item does not exit it will ask input to the user again
            if search == "exit":
                break
            for i in range(len(newsDict)):
                search_title = newsDict[i]["title"]
                search_content = newsDict[i]["content"]
                if search not in search_content:
                    continue
                elif search in search_content:
                    print("\nFound!Try this article: ")
                    print(search_title)

    print("Is there anything you want to search for?")
    search_proc()
