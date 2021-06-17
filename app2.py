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


import pickle

from flask import Flask,render_template,request
import pandas as pd
app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def homepage():
    if request.method=='POST':
        stock_name=request.form['stock']
        from datetime import datetime
        print(datetime.min.time())          
        print(date.today())
        LastDay= datetime.combine(date.today(), datetime.min.time())
        print(LastDay)
        stock = web.DataReader(stock_name+".ns","yahoo",LastDay,LastDay)
        
       # stock_data=updateStockPrice(stock_name)
        #prediction=updateStockPrediction(stock_name,stock_data)
        #news=updateSentiment(stock_name)
        #sentiment_score=updateSentimentScore(stock_name,news)
                
        
    stocklist=['RELIANCE','HDFCBANK','INFY','HDFC','ICICIBANK','TCS','KOTAKBANK','HINDUNILVR','ITC','AXISBANK']
    
  #  return render_template('page3.html',stock_name=stock_name,prediction=prediction,news=news,sentiment_score=sentiment_score)
    return render_template('home.html', stocklist=stocklist)

@app.route('/page3')
def page3(value):
    return render_template('page3.html',value=value)


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
    lastDayWindow=lastDayWindow.to_numpy()
    
    lastDayWindow=lastDayWindow.drop(['Date'],axis=1)
    numerical = ['Open', 'Close', 'Volume']
    lastDayWindow[numerical] = sc.fit_transform(lastDayWindow[numerical])
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

