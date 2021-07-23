#!/usr/bin/env python
# coding: utf-8

# In[120]:


import tweepy  # api package handler
import pandas as pd
import time
import datetime

# In[121]:


""" Api Consumer Class"""


class TweeterApiSearch:
    #'count how many rows received from api'
    total_found = 0
    # start chronometer
    start_time = 0  # start chronometer
    end_time = 0  # end chronometer

    # storing api result in array
    tweets_array = []
    # collect all posts trends
    hashtags_collection = []

    def __init__(self, api, keyword_array, nb_record=''):
        self.api = api
        self.keyword_array = keyword_array
        self.nb_records = nb_record

    def __consumeApi(self):
        self.start_time = time.time()

        for key in self.keyword_array:
            for tweet in tweepy.Cursor(self.api.search, q=key).items(self.nb_records):
                # check if post has hashtag
                is_hashtag = len(tweet.entities['hashtags'])
                # get first hashtag only if there is an hashtag
                hashtag = tweet.entities['hashtags'][0]['text'] if is_hashtag != 0 else ''

                created_at = tweet.created_at
                text = tweet.text
                username = tweet.user.screen_name

                # store tweet record
                TweeterApiSearch.tweets_array.append(
                    [key, created_at, text, username, hashtag])
                # store tweet tag
                TweeterApiSearch.hashtags_collection.append(hashtag)

                # track records got as an api resonse total++
                self.total_found = self.total_found + 1

        self.end_time = time.time()  # chrono ends

    def getTweets(self):
        self.__consumeApi()
        return TweeterApiSearch.tweets_array

    def getHashtags(self):
        return TweeterApiSearch.hashtags_collection

    def getTotalRows(self):
        return self.total_found

    def getChronoRecord(self):
        record = self.end_time - self.start_time
        return record


# In[122]:


""" Connect to Api"""


def ApiConnection(api_key, api_key_secret):
    # send OAuth request
    auth = tweepy.AppAuthHandler(api_key, api_key_secret)
    # create API object
    api = tweepy.API(auth)

    return api


# In[123]:


""" Conver input to List"""


def inputToList(text):
    # prepare input to convert it into array
    text = text.replace(', ', ',').replace(' ,', ',')
    # conver input to array
    array = text.split(',')

    return array


# In[124]:


""" list to string """
# array to string


def listToString(L):
    return ", ".join(str(x) for x in L)


# In[125]:


""" Remove empty elements from list """


def removeEmptyFromList(list):
    return [string for string in list if string != ""]


# In[126]:


""" Get array with occurence, and with no duplications"""


def arrayOccurences(array):
    array_occurence = []
    no_duplications = list(set(array))
    for item in no_duplications:
        array_occurence.append([item, array.count(item)])

    return {'without_duplications': no_duplications, 'array_occurence': array_occurence}


# In[127]:


""" Tweeter array with occurences of registered hashtags """


def TweetWithHashtagOccurence(input_array, hashtags_array, target_column_index):
    final_array = []
    columns = len(input_array[0])
    target_column = arrayOccurences(hashtags_array)
    target_no_duplication = target_column['without_duplications']
    target_occurence = target_column['array_occurence']

    for item in input_array:
        name = item[target_column_index]
        index = target_no_duplication.index(name)
        occurence = target_occurence[index][1]

        final_array.append(
            [item[0], item[1], item[2], item[3], item[4], occurence])
    return final_array


# In[128]:


""" create csv file from twitter's given array"""


def createTweetCsv(array, filename, display_message=False):
    fieldnames = ["keyword", "created_at", "text",
                  "username", "hashtag", "hashtag_occurence"]
    df = pd.DataFrame(array, columns=fieldnames)
    df.to_csv(filename, index=False)

    if display_message:
        print('file ', end=" ")
        print('\033[4m' + filename + '\033[0m', end=" ")
        print(' has been successfully created')


# In[129]:


""" sort tweeter's array by column """


def TweetSortedByColumn(input_array, column_index=5, desc=True):
    # sorted on descandant
    sorted_array = sorted(input_array, key=lambda x: x[column_index])
    return sorted_array


# In[175]:


""" get day start, get day end """


def getDayInerval(date):
    date_start = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    date_end = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)
    return {'start': date_start, 'end': date_end}


# In[176]:


""" get hour start, get day end """


def getHourInerval(date):
    date_start = datetime.datetime(
        date.year, date.month, date.day, date.hour, 0, 0)
    date_end = datetime.datetime(
        date.year, date.month, date.day, date.hour, 59, 0)
    return {'start': date_start, 'end': date_end}


# In[215]:


""" get top 10 hashtag of precise date, or ( by default ) of a week excepts it requires an array input of all hashtags """


def getTopHashtag(array, date, type, nb_display, allHashtags=[]):
    collection_temp = []
    collection = []

    if type == 'day':
        date_start = getDayInerval(date)['start']
        date_end = getDayInerval(date)['end']
    elif type == 'hour':
        date_start = getHourInerval(date)['start']
        date_end = getHourInerval(date)['end']

    else:
        # top of the week
        collection = sorted(set(allHashtags), key=lambda ele: allHashtags.count(
            ele), reverse=True)  # sort hashtags by occurence, descendant
        collection.remove('')  # to remove the no hashtag case

        return collection[:nb_display]

    # sweep the array
    for item in array:
        if item[1] >= date_start and item[1] < date_end:
            collection_temp.append(item[4])  # store item's hashtag

    # sort array by occurences decendant
    collection = sorted(set(collection_temp), key=lambda ele: collection_temp.count(
        ele), reverse=True)  # sort resulted hashtags by occurence descendant

    # remove empty hashtag
    collection = removeEmptyFromList(collection)

    return collection[:nb_display]


# In[231]:


def displayTopOfWeek(array, nb_display=10):
    result = getTopHashtag(array, datetime.datetime.now(),
                           'week', nb_display, hashtags_array)
    print(listToString(result))

    return ''


# In[232]:


def displayTopOfDays(array, n_days, nb_display=10):
    for i in range(n_days + 1):
        # set a day of the 7 days (1 week)
        askedDay = datetime.date.today() - datetime.timedelta(days=i)

        result = getTopHashtag(array, askedDay, 'day',
                               nb_display, hashtags_array)
        print(askedDay, end=" ")
        print(':', end=" ")
        print(listToString(result))

    return ''


# In[233]:


def displayTopPerHour(array, n_days, nb_display=10):
    for i in range(n_days + 1):
        askedDay = datetime.datetime.today() - datetime.timedelta(days=i)
        resultDay = getTopHashtag(
            array, askedDay, 'day', nb_display, hashtags_array)

        # check if the day has top hashtag
        print('\033[4m' + str(askedDay.year) + '-' + str(askedDay.month) +
              '-' + str(askedDay.day) + '\033[0m')  # display the date found
        for i in range(24):
            # set an hour of the current day
            askedHour = askedDay - datetime.timedelta(hours=i)
            resultHour = getTopHashtag(
                tweets_array, askedHour, 'hour', nb_display, hashtags_array)
            if len(resultHour) != 0:
                print(askedHour.hour, end=" ")
                print('to', end=" ")
                print((askedHour.hour + 1) % 24, end=" ")
                print(':', end=" ")
                print(listToString(resultHour))

    return ''


# In[229]:


#######################################################################################


# In[235]:


# Setup API object, NOTE:: api_keys are preferably getting asked through console
api_key = ''
api_key_secret = ''
api = ApiConnection(api_key, api_key_secret)

# User input must be: word1, word2, .....
print('Enter keywords as folling: word1, word2, ....')
userInput = input()
# turn input into List structure
keywordsArray = inputToList(userInput)

# ask limit for queries sent to twitter api for one keyword
print('Set limit of records needed for one keyword, Note::prefirably limit must not be above 250 due to twitter\'s api policy')
limit = int(input())

print('please wait...')
# create tweeter search object,
tweets = TweeterApiSearch(api, keywordsArray, limit)
# get tweets
tweets_array = tweets.getTweets()
# get all hashtags found even if cases without hashtags
hashtags_array = tweets.getHashtags()
# get each hashtag's occurence
hashtag_occurence = arrayOccurences(hashtags_array)['array_occurence']

# create array of tweets with hashtag occurence
tweets_with_occurence = TweetWithHashtagOccurence(
    tweets_array, hashtags_array, 4)

# save tweets to csv
# setted to true, in order to display message of success
createTweetCsv(tweets_with_occurence, 'tweetsResult.csv', True)

# sort tweets array by occurence column
tweet_sorted = TweetSortedByColumn(tweets_with_occurence)

# save sorted tweets to csv
createTweetCsv(tweet_sorted, 'sortedTweets.csv', True)


# In[242]:


#----- DISPLAY RESULT --------#
""" Display Results """
print('\nTop n hashtags you want to display, n = ? : ')
top_number = int(input())

# keywods
print('\nKeywords used in search : ')
print(userInput + '\n')

# top 10 hashtags of the week
print('Top 10 Hashtags of the week : ')
print(displayTopOfWeek(tweets_array, top_number))

# top 10 hashtags for each latest 7 days
print('Top 10 Hashtags for each latest 7 days : ')
print(displayTopOfDays(tweets_array, 7, top_number))

# Top10 hashtags per hours
print('Top 10 Hashtags for each hour of today')
print(displayTopPerHour(tweets_array, 7, top_number))

# General Details
print('Benchmarking')

# chorometer counts
print('\033[4m' + 'Total time spent to get results' + '\033[0m' + ':', end=" ")
print(str(tweets.getChronoRecord()) + ' seconds')
# total rows caught from api
print('\033[4m' + 'Total rows found from api' + '\033[0m' + ':', end=" ")
print(str(tweets.getTotalRows()) + ' rows')


# In[ ]:
