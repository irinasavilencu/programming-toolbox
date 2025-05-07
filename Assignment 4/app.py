from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import pandas as pd
import pickle
import sklearn
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Important for session

def getDBConnection():
    return psycopg2.connect(
        dbname="programming_toolbox",
        user="dcm_user",
        password="dcm",
        host="localhost",
        port="5432"  # default PostgreSQL port
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None #the error will be passed to HTML
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = getDBConnection()
        cursor = connection.cursor()
        cursor.execute('select * from users where username = %s and password=%s', (username, password))
        user=cursor.fetchone()
        connection.close()
        if user :
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error="Invalid username or password"
    return render_template('login.html', error=error)

@app.route('/home', methods=['GET'])
def home():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

df=pd.read_csv('Salary_dataset.csv', index_col=0)

@app.route('/shape')
def shape():
    if 'username' not in session:
        return redirect(url_for('login'))

    rows, columns = df.shape
    return render_template('shape.html',rows=rows, columns=columns)
@app.route('/dtypes')
def dtypes():
    if 'username' not in session:
        return redirect(url_for('login'))
    columns=df.dtypes.to_dict()
    return render_template('columns.html',columns=columns)

@app.route('/head', methods=['POST','GET'])
def head():
    if 'username' not in session:
        return redirect(url_for('login'))
    rows=None
    if request.method == 'POST':
        try:
            n=int(request.form['n'])
            rows=df.head(n)
        except:
            rows = None
    return render_template('head.html',rows=rows)
@app.route('/tail', methods=['POST','GET'])
def tail():
    if 'username' not in session:
        return redirect(url_for('login'))
    rows=None
    if request.method == 'POST':
        try:
            n=int(request.form['n'])
            rows=df.tail(n)
        except:
            rows = None
    return render_template('tail.html', rows=rows)

@app.route('/describe', methods=['GET'])
def describe():
    if 'username' not in session:
        return redirect(url_for('login'))
    statistics = df.describe()
    print(statistics)
    return render_template('describe.html', statistics=statistics)


with open('regression_predictions.pkl', 'rb') as f:
     model = pickle.load(f)# Load the trained model
@app.route('/predict', methods=['GET','POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))
    prediction =None
    if request.method == 'POST':
        try:
            years=float(request.form['years'])
            prediction = model.predict([[years]])[0]
        except:
            prediction = None
    return render_template('prediction.html', prediction=prediction)
if __name__ == '__main__':
    app.run(host='localhost', port=9874)



