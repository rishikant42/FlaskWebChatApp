from flask import Flask, render_template, request, url_for, redirect,session
import sqlite3
import jinja2
import time
import simplejson as json
import requests
from microsofttranslator import Translator
import os

app = Flask(__name__)
app.secret_key = 'my precious'

@app.route('/')
def file():
    if session.get('logged_in_user', False):
        return redirect(url_for('chat'))
    else:
        return render_template("login.html",error="welcome to open chat")


@app.route('/user')
def user():
    with sqlite3.connect("sample.db") as connection:
        c = connection.cursor()
        y = c.execute("select name from currentusers")
    return json.dumps(y.fetchall())

@app.route('/chat')
def chat():
    if session.get('logged_in_user', False):
        with sqlite3.connect("sample.db") as connection:
            c = connection.cursor()
            chats = []
            y = c.execute("select * from chats order by datetime(time) desc limit 10")
        return json.dumps(y.fetchall())
    else:
        return render_template('login.html', error="you need to login first")

@app.route('/send', methods=['POST'])
def send():
    with sqlite3.connect("sample.db") as connection:
        c = connection.cursor()
        cht = request.form['msg']
        translator = Translator('rk', os.environ['CLIENT_KEY'])
        p = translator.translate(cht, "hi")
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO chats(chat, time, name) VALUES(?, ?, ?)", (p, t,session.get('logged_in_user')))
    return "Ok"

@app.route('/logout')
def logout():
    if session.get('logged_in_user'):
        with sqlite3.connect("sample.db") as connection:
            c = connection.cursor()
            uname =  session.get('logged_in_user')
            c.execute("delete from currentusers where name=?", (uname,))
        session.pop('logged_in_user', None)
        return render_template("login.html",error="you are logged out")
    else:
        return "you were already logged out"
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        with sqlite3.connect("sample.db") as connection:
            c = connection.cursor()
            y = c.execute("select * from users where name=?", (request.form['username'], ))

            y = y.fetchall()
            if y == []:
                error = "user does not exist"
            elif (request.form['username'] != y[0][0]) or request.form['password'] != y[0][1]:
                error = 'Invalid Credentials. Please try again.'
            else:
                c.execute("INSERT INTO currentusers VALUES(?)", (request.form['username'], ))
                session['logged_in_user'] = request.form['username']
                return redirect(url_for('chats'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        with sqlite3.connect("sample.db") as connection:
            c = connection.cursor()
            name = request.form['username']
            password = request.form['password']
            passwrd = request.form['passwrd']
            if password != passwrd:
                return render_template('register.html',error="password is not matching")
            try:
                c.execute("INSERT INTO users VALUES(?, ?)", (name, password))
                return render_template("login.html",error="welcome to open chat")
            except sqlite3.IntegrityError as e: 
                return e.message
    return render_template('register.html')


@app.route('/chats')
def chats():
    if session.get('logged_in_user', False):
        return render_template('chat.html')
    else:
        return render_template('login.html', error="you need to login first")
        
if __name__ == '__main__':
    app.run(debug=True)


