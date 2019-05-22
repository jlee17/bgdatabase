#!/usr/local/bin/python3

from flask import Flask, redirect, request, render_template, session, flash
import psycopg2
app = Flask(__name__, template_folder='ui/templates')

# Temporary Secret Key
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
connparams = {
    'host': 'db',
    'port': '5432',
    'dbname': 'gamelist',
    'user': 'admin',
    'password': 'password'
}


@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')

    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    conn = psycopg2.connect(**connparams)

    conn = psycopg2.connect(**connparams)
    headers = None
    data = None

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(request.form['Query'])
                if cur.description:
                    headers = [description[0]
                               for description in cur.description]
                    data = cur.fetchall()

    except psycopg2.Error as e:
        return render_template('index.html', error=e)
    finally:
        conn.close()

    return render_template('index.html', headers=headers, data=data)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['User']
    password = request.form['Password']

    conn = psycopg2.connect(**connparams)

    # try:
    # with conn:
    # with conn.cursor() as cur:
    # cur.execute(
    # "SELECT * FROM users WHERE name=%s AND age=%s;", (username, password))
    #result = cur.fetchone()
    # except psycopg2.DataError:
    # conn.close()
    result = 1

    if result:
        session['logged_in'] = True
        return index()
    else:
        errors = 'Invalid Username/Password combo'
        return render_template('login.html', errors=errors)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
