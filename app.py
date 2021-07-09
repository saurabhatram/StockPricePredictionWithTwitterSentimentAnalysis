from datetime import datetime, timedelta
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like #For solving import pandas_datareader issue
import numpy as np
import datetime
import csv
import requests
import pandas_datareader.data as web
import pandas_datareader as pdr
from pandas_datareader import data, wb
from datetime import date
from nsepy import get_history
from datetime import date
import h5py
import yfinance as yf
from tensorflow.keras.models import load_model
from sklearn.externals import joblib

import pandas as pd


from flask import Flask,request,render_template,redirect,url_for
import os
import sqlite3

currentlocation = os.path.dirname(os.path.abspath(__file__))

import matplotlib.pyplot as plt
plt.style.use('ggplot')
import math, random
import tweepy
import re
from textblob import TextBlob
import preprocessor as p
import nltk
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


myapp= Flask(__name__)
stocklist=['RELIANCE','ADANIPORTS','GRASIM','M&M','COALINDIA','HDFCBANK','HDFC','INDUSINDBK','KOTAKBANK','JSWSTEEL']
wishlist1=[]
Email=""

@myapp.route("/")
def homepage():
 print("inside homepage")
 return render_template("index.html")

@myapp.route("/index.html")
def index():
 print("inside index")
 return render_template("index.html")

@myapp.route("/inner-page.html")
def innerpage():
    print("inside innerpage")
    return render_template("inner-page.html")

@myapp.route("/signup.html",methods=["GET","POST"])
def registerpage():
    print("inside registerpage")
    if request.method=="POST":
        dUN= request.form["Fname"]
        dPW= request.form["pass"]
        dCPW= request.form['cpass']
        Uemail= request.form["email"]
        if(dPW!=dCPW):
            return render_template("signup.html")
        print(dUN+" "+dPW+" "+Uemail)

        sqlconnection= sqlite3.Connection(currentlocation+"\Login.db")
        cursor = sqlconnection.cursor()
        queryCheck="SELECT  Username, Email From Users WHERE Username='{un}' AND Email='{em}' ".format(un=dUN,em=Uemail)
        rows=cursor.execute(queryCheck)
        rows=rows.fetchall()
        if len(rows) ==0:
            query1="INSERT INTO Users VALUES('{u}','{p}','{e}')".format(u=dUN,p=dPW,e=Uemail)
            cursor.execute(query1)
            sqlconnection.commit()
            return redirect("/inner-page.html")
        return render_template("signup.html")
    
@myapp.route("/inner-page.html",methods=["POST"])
def checklogin():
    print("inside checklogin")
    em=request.form['email']
    PW=request.form["pass"]
    print(em+" " +PW)
    sqlconnection=sqlite3.Connection(currentlocation + "\Login.db")
    cursor=sqlconnection.cursor()
    query1="SELECT  Email, Password From Users WHERE Email='{em}' AND Password='{pw}' ".format(em=em,pw=PW)
    rows=cursor.execute(query1)
    rows=rows.fetchall()
    if len(rows) ==1:
        email=em
        global Email
        Email=email
        global wishlist1
        wishlist1=showWishList(em)
        return render_template("middlepage1.html",stocklist=stocklist,wishlist=wishlist1)
    else:
        print("No user found")
        return redirect("/signup.html")
'''
@myapp.route('/choicelist.html')
def choicelist1():
    print("inside choicelist1")
    return render_template('choicelist.html', stocklist=stocklist)"
'''
@myapp.route('/choicelist.html', methods=['GET','POST'])
def choicelist2():
    print("inside choicelist2")
    if request.method=='POST':
        if request.form.get("stock"):
            stock_name=request.form['stock']
            print(stock_name)
        if request.form.get("wstock"):
            stock_name=request.form['wstock']
            print(stock_name)
            
        lastDayPrediction,df=historyandprediction(stock_name)
        print('THE last day prediction is'+ str(lastDayPrediction))
        #graph(lastDayPrediction,df,stock_name)//the function itself shows the graph 
        df=df.tail(300)
        maxvalue=lastDayPrediction
        minvalue=df.iloc[0]['Close']
        df['Date'] = df['Date'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))
        labels=df['Date'].tolist()
        #labels.append(df['Date'].tail(1)+timedelta(1))
        #print(labels)
        values=df['Close'].tolist()
        values.append(lastDayPrediction)
        print('len of labels is : ') 
        print(len(labels))
        print('len of values is : ')
        print(len(values))
        print(stock_name)
        print(lastDayPrediction)
        maxvalue=values[-1]
        minvalue=values[0]
        print(minvalue)
        print(maxvalue)
        stock_name1=stock_name+'.NS'
        gp,tw,twp,pos,neg,neut=retrieving_tweets_polarity(stock_name1)
        print("GLOBAL Polarity :"+ str(gp))
        #print("tw_list :"+str(tw))
        print("tw_pol :"+ str(twp))
        print("positive :"+str(pos))
        print("negative :"+str(neg))
        print("neutral :"+str(neut))
        return render_template("chart.html", labels=labels,values=values,value=lastDayPrediction,stock_name=stock_name,minvalue=minvalue,maxvalue=maxvalue,tw_pol=twp,positive=pos,negative=neg,neutral=neut)

        
def historyandprediction(stock_name):
        print("inside historyandprediction")
        
        from datetime import datetime,timedelta
        LastDay= datetime.combine(date.today(), datetime.min.time())
        StartDay = LastDay - timedelta(days=331)
        
        '''
        stock = web.DataReader(stock_name+".ns","yahoo",StartDay,LastDay)        
        
        '''
        stock = yf.download(tickers=stock_name+".ns", period="2y", interval="1d",auto_adjust=True)
        
        stock.reset_index(inplace=True,drop=False)
        res = stock.copy(deep=True)
        
        model = load_model(stock_name+'.h5')
        sc= joblib.load(stock_name+'.save')
        
        
        
        #print(stock)
        stock = stock.drop(['High','Low'],axis=1)
        lastDayWindow=stock.drop(['Date'],axis=1)
        numerical = ['Open', 'Close', 'Volume']
        lastDayWindow[numerical] = sc.fit_transform(lastDayWindow[numerical])
        #print(lastDayWindow)
       
        lastDayWindow=lastDayWindow.to_numpy()
        lastDayWindow=lastDayWindow.reshape((1,lastDayWindow.shape[0], lastDayWindow.shape[1]))
        ''' predicting last 331 days data'''
        predictions=model.predict(lastDayWindow)
        
        ''' denormalising last 331 days data'''
        df2 = pd.DataFrame(predictions, columns = [0])
        df2
        df2[1]=df2[0]
        df2[2]=df2[1]
        Y_test = sc.inverse_transform(df2)
        df2 = pd.DataFrame(Y_test, columns = ['Close','Column_B','Column_C'])
        df2=df2['Close']
        #print(df2[0])
        return(df2[0],res)

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

@myapp.route("/editwishlist.html")
def editwishlist():
    print("inside editwishlist")
    global wishlist1
    return render_template("editwishlist.html",stocklist=stocklist,wishlist=wishlist1)
@myapp.route("/editwishlist.html", methods=['GET','POST'])
def editwishlist1():
    print("inside editwishlist1")
    global wishlist1
    if request.method=='POST':
        if request.form.get("update_button"):
            stock_name=request.form['stock']
            create(Email, stock_name)
            print(Email)
            print("in Update")
            print(stock_name)
        if request.form.get("delete_button"):
            stock_name=request.form['stock']
            delete(Email,stock_name)
            print(Email)
            print('In delete')
            print(stock_name)
    return render_template("/editwishlist.html",stocklist=stocklist,wishlist=wishlist1)
        
    return render_template("editwishlist.html")

@myapp.route("/middlepage1.html")
def middlepage1():
    print("inside middlepage1")
    global wishlist1
    return render_template("middlepage1.html",stocklist=stocklist,wishlist=wishlist1)


def create(email,stock_name):
        print("inside create wishlist")
        if(checkBeforeCreate(email, stock_name)):
            sqlconnection= sqlite3.Connection(currentlocation+"\wishlist.db")
            cursor = sqlconnection.cursor()
            query1="INSERT INTO wishlist VALUES('{e}','{s}')".format(e=email,s=stock_name)
            cursor.execute(query1)
            sqlconnection.commit()
            global wishlist1
            wishlist1=showWishList(email)

def delete(email,stock_name):
        print("inside delete wishlist")
        if(checkBeforeDelete(email, stock_name)):
            sqlconnection= sqlite3.Connection(currentlocation+"\wishlist.db")
            cursor = sqlconnection.cursor()
            cursor.execute("delete from wishlist where email=? AND stockname=?", (email,stock_name))
            sqlconnection.commit()
            global wishlist1
            wishlist1=showWishList(email)
        
def showWishList(email):
        print("inside showWishlist")
        sqlconnection= sqlite3.Connection(currentlocation+"\wishlist.db")
        cursor = sqlconnection.cursor()
        query1="SELECT stockname from wishlist where email='{e}' ".format(e=email)
        cursor.execute(query1)
        rows=cursor.fetchall()
        a=[datum[0] for datum in rows]
        print(a)
        sqlconnection.commit()
        return a

def findEmail(UN):
        print("inside findEmail")
        sqlconnection=sqlite3.Connection(currentlocation + "\Login.db")
        cursor=sqlconnection.cursor()
        query1="SELECT  Email From Users WHERE Username='{un}' ".format(un=UN)
        cursor.execute(query1)
        rows=cursor.fetchall()
        a=[datum[0] for datum in rows]
        sqlconnection.commit()
        print(a[0])
        return a[0]

def checkBeforeCreate(email,stock_name):
        print("inside checkBeforeCreate")
        sqlconnection= sqlite3.Connection(currentlocation+"\wishlist.db")
        cursor = sqlconnection.cursor()
        query1="SELECT stockname From wishlist WHERE email='{em}'AND stockname='{sn}' ".format(em=email,sn=stock_name)
        rows=cursor.execute(query1)
        rows=rows.fetchall()
        if len(rows) ==0:#if there is no stock added earlier with the same name then only you can add itt
            return True
        else:
            return False
    
def checkBeforeDelete(email,stock_name):
        print("inside checkBeforeCreate")
        sqlconnection= sqlite3.Connection(currentlocation+"\wishlist.db")
        cursor = sqlconnection.cursor()
        query1="SELECT stockname From wishlist WHERE email='{em}' AND stockname='{sn}'".format(em=email,sn=stock_name)
        rows=cursor.execute(query1)
        rows=rows.fetchall()
        if len(rows) !=0: #if there is an element there then only you can deleteit
            return True
        else:
            return False 
if __name__=="__main__":
    myapp.run()
