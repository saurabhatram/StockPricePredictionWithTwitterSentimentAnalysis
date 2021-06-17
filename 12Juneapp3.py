# -*- coding: utf-8 -*-
"""
Created on Sat Jun 12 12:02:45 2021

@author: saura
"""


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

from tensorflow.keras.models import load_model
from sklearn.externals import joblib

from flask import Flask,render_template,request
import pandas as pd
app = Flask(__name__)


@app.route('/')
def choicepage():
        stocklist=['RELIANCE','ADANIPORTS','GRASIM','M&M','COALINDIA','HDFCBANK','HDFC','INDUSINDBK','KOTAKBANK','JSWSTEEL']
        print('IN Choicepage function')
  #  return render_template('page3.html',stock_name=stock_name,prediction=prediction,news=news,sentiment_score=sentiment_score)
        return render_template('choicelist.html', stocklist=stocklist)

    
@app.route('/', methods=['GET','POST'])
def homepage():
    if request.method=='POST':
        stock_name=request.form['stock']
        lastDayPrediction,df=historyandprediction(stock_name)
        print('THE last day prediction is'+ str(lastDayPrediction))
        graph(lastDayPrediction,df,stock_name)
        df=df.tail(300)
        labels=df['Date'].tolist()
        #labels.append(df['Date'].tail(1)+timedelta(1))
        #print(labels)
        values=df['Close'].tolist()
        #values.append(lastDayPrediction)
        print('len of labels is : ') 
        print(len(labels))
        print('len of values is : ')
        print(len(values))
        print(stock_name)
        print(lastDayPrediction)
        print('IN homepage function')
        return render_template("chart.html", labels=labels,values=values,value=lastDayPrediction,stock_name=stock_name)
            
        
      #  print("The next day prediction is "+ historyandprediction(stock_name))
        #print(datetime.min.time())          
        #print(date.today())
       #LastDay= datetime.combine(date.today(), datetime.min.time())
       # print(LastDay)
        #stock = web.DataReader(stock_name+".ns","yahoo",LastDay,LastDay)
        #print(stock)
       # stock_data=updateStockPrice(stock_name)
        #prediction=updateStockPrediction(stock_name,stock_data)
        #news=updateSentiment(stock_name)
        #sentiment_score=updateSentimentScore(stock_name,news)
                
        
        stocklist=['RELIANCE','ADANIPORTS','GRASIM','M&M','COALINDIA','HDFCBANK','HDFC','INDUSINDBK','KOTAKBANK','JSWSTEEL']
    
  #  return render_template('page3.html',stock_name=stock_name,prediction=prediction,news=news,sentiment_score=sentiment_score)
        return render_template('choicelist.html', stocklist=stocklist,value=lastDayPrediction,stock_name=stock_name)

@app.route('/graph',methods=['GET','POST'])
def graph(value,df,stock_name):
    #df=pd.read_csv('static/RELIANCE.csv')
    #print(df.head())
    print(df.dtypes)
    df['Date'] = df['Date'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))
    df=df.tail(300)
    labels=df['Date'].tolist()
    values=df['Close'].tolist()
    print("HIIII")
    print(stock_name)
    print(value)
    print('len of labels is : ') 
    print((labels))
    print('len of values is : ')
    print((values))
    return render_template("chart.html", labels=labels,values=values,value=value,stock_name=stock_name)

def historyandprediction(stock_name):
        from datetime import datetime,timedelta
        LastDay= datetime.combine(date.today(), datetime.min.time())
        StartDay = LastDay - timedelta(days=331)
        stock = web.DataReader(stock_name+".ns","yahoo",StartDay,LastDay)        
        stock.reset_index(inplace=True,drop=False)
        res = stock.copy(deep=True)
        
        model = load_model(stock_name+'.h5')
        sc= joblib.load(stock_name+'.save')
        
        

        #print(stock)
        stock = stock.drop(['High','Low','Adj Close'],axis=1)
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
        
def updateStockPrice(stock_name):
    from datetime import datetime
    LastDay= datetime.combine(date.today(), datetime.min.time())
    stock = web.DataReader(stock_name+".ns","yahoo",LastDay,LastDay)
    stock_final = pd.DataFrame()
    stock_final = pd.DataFrame.append(stock_final,stock)
    stock_final.to_csv( 'static/csvfiles/'+ stock_name +".csv",mode='a', header=False)
    return stock


def updateStockPrediction(stock_name,stock_data):
    '''unloading starts'''
    model = pickle.load(open('static/h5files/'+stock_name+'.pkl', 'rb'))
    sc =    pickle.load(open('static/scalerfiles/'+stock_name+'.pkl', 'rb'))
    df=pd.read_csv('static/csvfiles/'+ stock_name +".csv")
   
    '''normalising last 331 days data 331 is y_test'''
    lastDayWindow=df.tail(331)       #take last 30 days into account
    #lastDayWindow=lastDayWindow.to_numpy()
    
    lastDayWindow=lastDayWindow.drop(['Date'],axis=1)
    numerical = ['Open', 'Close', 'Volume']
    lastDayWindow[numerical] = sc.fit_transform(lastDayWindow[numerical])
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
    lastDayPrediction=float(df['Close'].tail(1).values)
    return lastDayPrediction
    
def updateSentiment(stock_name):
    a=1
def updateSentimentScore(stock_name):
    a=1

if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)

