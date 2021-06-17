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

import pandas as pd


from flask import Flask,request,render_template,redirect,url_for
import os
import sqlite3

currentlocation = os.path.dirname(os.path.abspath(__file__))

myapp= Flask(__name__)
stocklist=['RELIANCE','ADANIPORTS','GRASIM','M&M','COALINDIA','HDFCBANK','HDFC','INDUSINDBK','KOTAKBANK','JSWSTEEL']


@myapp.route("/")
def homepage():
 return render_template("index.html")

@myapp.route("/index.html")
def index():
 return render_template("index.html")

@myapp.route("/inner-page.html")
def innerpage():
    print("inside innerpage")
    return render_template("inner-page.html")

@myapp.route("/signup.html",methods=["GET","POST"])
def registerpage():
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
        query1="INSERT INTO Users VALUES('{u}','{p}','{e}')".format(u=dUN,p=dPW,e=Uemail)
        cursor.execute(query1)
        sqlconnection.commit()
        return redirect("/inner-page.html")
    return render_template("signup.html")

@myapp.route("/inner-page.html",methods=["POST"])
def checklogin():
    em=request.form['email']
    PW=request.form["pass"]
    print(em+" " +PW)
    sqlconnection=sqlite3.Connection(currentlocation + "\Login.db")
    cursor=sqlconnection.cursor()
    query1="SELECT  Email, Password From Users WHERE Email='{em}' AND Password='{pw}' ".format(em=em,pw=PW)
    rows=cursor.execute(query1)
    rows=rows.fetchall()
    if len(rows) ==1:
        stocklist=['RELIANCE','ADANIPORTS','GRASIM','M&M','COALINDIA','HDFCBANK','HDFC','INDUSINDBK','KOTAKBANK','JSWSTEEL']
        return render_template('choicelist.html',stocklist=stocklist)
    else:
        print("No user found")
        return redirect("/signup.html")

@myapp.route('/choicelist.html')
def choicelist1():
    return render_template('choicelist.html', stocklist=stocklist)
@myapp.route('/choicelist.html', methods=['GET','POST'])
def choicelist2():
    if request.method=='POST':
        stock_name=request.form['stock']
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
        return render_template("chart.html", labels=labels,values=values,value=lastDayPrediction,stock_name=stock_name,minvalue=minvalue,maxvalue=maxvalue)

        stocklist=['RELIANCE','ADANIPORTS','GRASIM','M&M','COALINDIA','HDFCBANK','HDFC','INDUSINDBK','KOTAKBANK','JSWSTEEL']    
        return render_template('choicelist.html', stocklist=stocklist,labels=labels,values=values,value=lastDayPrediction,stock_name=stock_name,minvalue=minvalue,maxvalue=maxvalue)

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


if __name__=="__main__":
    myapp.run()