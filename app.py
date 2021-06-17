from flask import Flask,render_template,request
import pandas as pd
app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def home():
    df=pd.read_csv('static/RELIANCE.csv')
    print(df.head())
    df=df.tail(300)
    labels=df['Date'].tolist()
    values=df['Close'].tolist()
    return render_template("chart.html", labels=labels,values=values)

if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)