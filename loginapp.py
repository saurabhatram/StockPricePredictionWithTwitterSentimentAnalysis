from flask import Flask,request,render_template,redirect
import os
import sqlite3

currentlocation = os.path.dirname(os.path.abspath(__file__))

myapp= Flask(__name__)


@myapp.route("/",methods=["POST"])
def checklogin():
    em=request.form['email']
    PW=request.form["pass"]
    print(em+" " +PW)
    sqlconnection=sqlite3.Connection(currentlocation + "\Login.db")
    cursor=sqlconnection.cursor()
    query1="SELECT  Email, Password From Users WHERE Username='{em}' AND Password='{pw}' ".format(em=em,pw=PW)
    
    rows=cursor.execute(query1)
    rows=rows.fetchall()
    if len(rows) ==1:
        return render_template("loggedin.html",uname=em)
    else:
        return redirect("/register")

@myapp.route("/register",methods=["GET","POST"])
def registerpage():
    if request.method=="POST":
        dUN= request.form["Fname"]
        dPW= request.form["pass"]
        Uemail= request.form["email"]
        print(dUN+" "+dPW+" "+Uemail)
        sqlconnection= sqlite3.Connection(currentlocation+"\Login.db")
        cursor = sqlconnection.cursor()
        query1="INSERT INTO Users VALUES('{u}','{p}','{e}')".format(u=dUN,p=dPW,e=Uemail)
        cursor.execute(query1)
        sqlconnection.commit()
        return redirect("/")
    return render_template("signup.html")


if __name__=="__main__":
    myapp.run()