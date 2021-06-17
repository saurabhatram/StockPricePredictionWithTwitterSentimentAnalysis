import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import math, random
from datetime import datetime
import datetime as dt
import tweepy
import re
from textblob import TextBlob
import preprocessor as p
import nltk
#nltk.download('punkt')

# Ignore Warnings
import warnings
warnings.filterwarnings("ignore")
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class Tweet(object):
    def __init__(self, content, polarity):
        self.content = content
        self.polarity = polarity  
consumer_key= '7x7w8Ti8GmMtuhvj7IXBuvZmP'
consumer_secret= 'kpFGcKiGxP9dJtlQzZ99p2OK9HM0IjA1I8n23N40VJyctOzvkG'

access_token='1365544389498474497-97lzyZE9lroLNDzLhvW1dLS3MDKfV5'
access_token_secret='8mF9CrBt4SvmewPZaapgL7kkh2iJus824SvhBJOvDpXlw'

num_of_tweets = int(300)

def retrieving_tweets_polarity(symbol):
        stock_ticker_map = pd.read_csv('Yahoo-Finance-Ticker-Symbols.csv')
        stock_full_form = stock_ticker_map[stock_ticker_map['Ticker']==symbol]
        symbol = stock_full_form['Name'].to_list()[0][0:12]

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        user = tweepy.API(auth)
        
        tweets = tweepy.Cursor(user.search, q=symbol, tweet_mode='extended', lang='en',exclude_replies=True).items(num_of_tweets)
        
        tweet_list = [] #List of tweets alongside polarity
        global_polarity = 0 #Polarity of all tweets === Sum of polarities of individual tweets
        tw_list=[] #List of tweets only => to be displayed on web page
        #Count Positive, Negative to plot pie chart
        pos=0 #Num of pos tweets
        neg=1 #Num of negative tweets
        for tweet in tweets:
            count=20 #Num of tweets to be displayed on web page
            #Convert to Textblob format for assigning polarity
            tw2 = tweet.full_text
            tw = tweet.full_text
            #Clean
            tw=p.clean(tw)
            #print("-------------------------------CLEANED TWEET-----------------------------")
            #print(tw)
            #Replace &amp; by &
            tw=re.sub('&amp;','&',tw)
            #Remove :
            tw=re.sub(':','',tw)
            #print("-------------------------------TWEET AFTER REGEX MATCHING-----------------------------")
            #print(tw)
            #Remove Emojis and Hindi Characters
            tw=tw.encode('ascii', 'ignore').decode('ascii')

            #print("-------------------------------TWEET AFTER REMOVING NON ASCII CHARS-----------------------------")
            #print(tw)
            blob = TextBlob(tw)
            polarity = 0 #Polarity of single individual tweet
            for sentence in blob.sentences:
                   
                polarity += sentence.sentiment.polarity
                if polarity>0:
                    pos=pos+1
                if polarity<0:
                    neg=neg+1
                
                global_polarity += sentence.sentiment.polarity
            if count > 0:
                tw_list.append(tw2)
                
            tweet_list.append(Tweet(tw, polarity))
            count=count-1
        if len(tweet_list) != 0:
            global_polarity = global_polarity / len(tweet_list)
        else:
            global_polarity = global_polarity
        neutral=num_of_tweets-pos-neg
        if neutral<0:
        	neg=neg+neutral
        	neutral=20
        print()
        print("##############################################################################")
        print("Positive Tweets :",pos,"Negative Tweets :",neg,"Neutral Tweets :",neutral)
        print("##############################################################################")
        labels=['Positive','Negative','Neutral']
        sizes = [pos,neg,neutral]
        explode = (0, 0, 0)
        fig = plt.figure(figsize=(7.2,4.8),dpi=65)
        fig1, ax1 = plt.subplots(figsize=(7.2,4.8),dpi=65)
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax1.axis('equal')  
        plt.tight_layout()
        plt.savefig('static/SA.png')
        plt.close(fig)
        #plt.show()
        if global_polarity>0:
            print()
            print("##############################################################################")
            print("Tweets Polarity: Overall Positive")
            print("##############################################################################")
            tw_pol="Overall Positive"
        else:
            print()
            print("##############################################################################")
            print("Tweets Polarity: Overall Negative")
            print("##############################################################################")
            tw_pol="Overall Negative"
        return global_polarity,tw_list,tw_pol,pos,neg,neutral

if __name__ == "__main__":
    #stock_name1=stock_name+'.NS'
    gp,tw,twp,pos,neg,neut=retrieving_tweets_polarity('RELIANCE.NS')
    print("GLOBAL Polarity :"+ str(gp))
    print("tw_list :"+str(tw))
    print("tw_pol :"+ str(twp))
    print("positive :"+str(pos))
    print("negative :"+str(neg))
    print("neutral :"+str(neut))
    