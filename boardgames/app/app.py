#!/usr/local/bin/python3

from flask import Flask, redirect, request, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import xml.etree.ElementTree as ET

app = Flask(
    __name__, template_folder='ui/templates', static_folder='ui/static')

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
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        conn = psycopg2.connect(**connparams)
        headers = None
        data = None

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(request.form['Query'])
                    if cur.description:
                        headers = [
                            description[0] for description in cur.description
                        ]
                        data = cur.fetchall()
        except psycopg2.Error as e:
            return render_template('index.html', error=e)
        finally:
            conn.close()

        return render_template('index.html', headers=headers, data=data)


@app.route('/import', methods=['GET', 'POST'])
def import_data():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        if request.method == 'POST':
            datafiles = request.files.getlist('file[]')

            for datafile in datafiles:
                tree = ET.parse(datafile)
                root = tree.getroot()

                a = ()

                item = root.find('item')
                if item == None:
                    continue

                if item.get('type') == 'boardgame' or item.get(
                        'type') == 'boardgameexpansion':
                    a = (item.get('id'), )
                else:
                    continue

                name = item.find('name')
                if name != None:
                    a = a + (name.get('value'), )
                else:
                    a = a + (None, )

                description = item.find('description')
                if description.text != None:
                    a = a + (description.text, )
                else:
                    a = a + (None, )

                yearpublished = item.find('yearpublished')
                if yearpublished != None:
                    a = a + (yearpublished.get('value'), )
                else:
                    a = a + (None, )

                statistics = item.find('statistics')
                if statistics != None:
                    ratings = statistics.find('ratings')
                    rating = ratings.find('average')
                    a = a + (rating.get('value'), )
                    num_ratings = ratings.find('usersrated')
                    a = a + (num_ratings.get('value'), )
                else:
                    a = a + (
                        None,
                        None,
                    )

                minplaytime = item.find('minplaytime')
                if minplaytime != None:
                    a = a + (minplaytime.get('value'), )
                else:
                    a = a + (None, )

                maxplaytime = item.find('maxplaytime')
                if maxplaytime != None:
                    a = a + (maxplaytime.get('value'), )
                else:
                    a = a + (None, )

                minplayers = item.find('minplayers')
                if minplayers != None:
                    a = a + (minplayers.get('value'), )
                else:
                    a = a + (None, )

                maxplayers = item.find('maxplayers')
                if maxplayers != None:
                    a = a + (maxplayers.get('value'), )
                else:
                    a = a + (None, )

                conn = psycopg2.connect(**connparams)

                try:
                    with conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                "INSERT INTO bg(bg_id, title, description, released, rating, num_ratings, min_playtime, max_playtime, min_players, max_players) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                                a)

                    for trait in root.iter('link'):
                        if trait.get('type') == 'boardgamecategory':
                            with conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        "INSERT INTO categories(cat_id, category) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            trait.get('id'),
                                            trait.get('value'),
                                        ))
                                    cur.execute(
                                        "INSERT INTO categoriesrel(bg_id, cat_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            item.get('id'),
                                            trait.get('id'),
                                        ))
                        elif trait.get('type') == 'boardgamemechanic':
                            with conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        "INSERT INTO mechanics(mech_id, mechanic) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            trait.get('id'),
                                            trait.get('value'),
                                        ))
                                    cur.execute(
                                        "INSERT INTO mechanicsrel(bg_id, mech_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            item.get('id'),
                                            trait.get('id'),
                                        ))
                        elif trait.get('type') == 'boardgamefamily':
                            with conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        "INSERT INTO families(fam_id, family) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            trait.get('id'),
                                            trait.get('value'),
                                        ))
                                    cur.execute(
                                        "INSERT INTO familiesrel(bg_id, fam_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            item.get('id'),
                                            trait.get('id'),
                                        ))
                        elif trait.get('type') == 'boardgamedesigner':
                            with conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        "INSERT INTO people(p_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            trait.get('id'),
                                            trait.get('value'),
                                        ))
                                    cur.execute(
                                        "INSERT INTO designerrel(bg_id, p_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            item.get('id'),
                                            trait.get('id'),
                                        ))
                        elif trait.get('type') == 'boardgameartist':
                            with conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        "INSERT INTO people(p_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            trait.get('id'),
                                            trait.get('value'),
                                        ))
                                    cur.execute(
                                        "INSERT INTO artistrel(bg_id, p_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            item.get('id'),
                                            trait.get('id'),
                                        ))
                        elif trait.get('type') == 'boardgamepublisher':
                            with conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        "INSERT INTO publishers(pub_id, publisher) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            trait.get('id'),
                                            trait.get('value'),
                                        ))
                                    cur.execute(
                                        "INSERT INTO publishersrel(bg_id, pub_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                        (
                                            item.get('id'),
                                            trait.get('id'),
                                        ))
                        elif trait.get(
                                'type') == 'boardgameexpansion' and trait.get(
                                    'inbound') != None:
                            with conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        "SELECT * FROM bg WHERE bg_id=%s",
                                        (trait.get('id'), ))
                                    if cur.fetchone() != None:
                                        cur.execute(
                                            "UPDATE bg SET expansion_of = %s WHERE bg_id = %s;",
                                            (
                                                trait.get('id'),
                                                item.get('id'),
                                            ))
                finally:
                    conn.close()
            return render_template('index.html', error="Data imported")

        else:
            return render_template('import.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        conn = psycopg2.connect(**connparams)
        result = None

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT get_hashed_pw(%s);", (username, ))
                    result = cur.fetchone()
        except psycopg2.DataError:
            conn.close()

        if result != None:
            if result[0] != None:
                if check_password_hash(result[0], password):
                    session['logged_in'] = True
                    session['user_id'] = username
                    return redirect('/')

        message = 'Invalid Username/Password combo'
        category = 'alert-danger'
        return render_template(
            'login.html', message=message, category=category)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.form['firstName'] == "" or request.form['lastName'] == "":
            error = 'Enter your name'
            category = 'alert-danger'
            return render_template(
                'signup.html', error=error, category=category)
        elif request.form['email'] == "":
            error = 'Enter an email'
            category = 'alert-danger'
            return render_template(
                'signup.html', error=error, category=category)
        elif request.form['password'] == "":
            error = 'Enter a password'
            category = 'alert-danger'
            return render_template(
                'signup.html', error=error, category=category)
        elif request.form['password'] != request.form['confirmPassword']:
            error = 'Passwords must match'
            category = 'alert-danger'
            return render_template(
                'signup.html', error=error, category=category)
        else:
            conn = psycopg2.connect(**connparams)
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO users(email, password, name) VALUES (%s, %s, %s);",
                            (request.form['email'],
                             generate_password_hash(request.form['password']),
                             request.form['firstName'] + ' ' +
                             request.form['lastName']))
                flash('Account Created', 'alert-success')
            except psycopg2.IntegrityError:
                flash('An account already exists for that email',
                      'alert-danger')
                conn.close()
            return redirect('/')
    else:
        return render_template('signup.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        headers = None
        data = None
        query = None
        conditions = None
        errors = None
        if request.method == 'POST':
            conn = psycopg2.connect(**connparams)

            try:
                with conn:
                    with conn.cursor() as cur:
                        query = "SELECT DISTINCT bg_id, title, rating FROM bg"
                        from_tables = ""
                        where = []
                        conditions = ()
                        if request.form['Title'] != "":
                            where += ["title=placeholder"]
                            conditions += (request.form['Title'], )
                        if request.form['Release Year'] != "":
                            where += ["released=placeholder"]
                            conditions += (request.form['Release Year'], )
                        if request.form['Rating'] != "":
                            where += ["rating=placeholder"]
                            conditions += (request.form['Rating'], )
                        if request.form['Minimum Length'] != "":
                            where += ["min_playtime=placeholder"]
                            conditions += (request.form['Minimum Length'], )
                        if request.form['Maximum Length'] != "":
                            where += ["max_playtime=placeholder"]
                            conditions += (request.form['Maximum Length'], )
                        if request.form['Minimum Players'] != "":
                            where += ["min_players=placeholder"]
                            conditions += (request.form['Minimum Players'], )
                        if request.form['Maximum Players'] != "":
                            where += ["max_players=placeholder"]
                            conditions += (request.form['Maximum Players'], )
                        if request.form['Publisher'] != "":
                            from_tables += " NATURAL JOIN publishersrel INNER JOIN publishers ON publishers.pub_id = publishersrel.pub_id"
                            where += ["publisher=placeholder"]
                            conditions += (request.form['Publisher'], )
                        if request.form['Mechanic'] != "":
                            from_tables += " NATURAL JOIN mechanicsrel INNER JOIN mechanics ON mechanics.mech_id = mechanicsrel.mech_id"
                            where += ["mechanic=placeholder"]
                            conditions += (request.form['Mechanic'], )
                        if request.form['Family'] != "":
                            from_tables += " NATURAL JOIN familiesrel INNER JOIN families ON families.fam_id = familiesrel.fam_id"
                            where += ["family=placeholder"]
                            conditions += (request.form['Family'], )
                        if request.form['Category'] != "":
                            from_tables += " NATURAL JOIN categoriesrel INNER JOIN categories ON categories.cat_id = categoriesrel.cat_id"
                            where += ["category=placeholder"]
                            conditions += (request.form['Category'], )
                        if request.form['Designer'] != "":
                            where += [
                                "bg_id IN (SELECT DISTINCT bg_id FROM designerrel NATURAL JOIN people WHERE name=placeholder)"
                            ]
                            conditions += (request.form['Designer'], )
                        if request.form['Artist'] != "":
                            where += [
                                "bg_id IN (SELECT DISTINCT bg_id FROM artistrel NATURAL JOIN people WHERE name=placeholder)"
                            ]
                            conditions += (request.form['Artist'], )

                        if where:
                            query += from_tables
                            query += ' WHERE ' + ' AND '.join(where)
                            query = query.replace('placeholder', '%s')
                            query += ' ORDER BY rating DESC'

                        cur.execute(query, conditions)
                        if cur.description:
                            headers = [
                                description[0]
                                for description in cur.description
                            ]
                            data = cur.fetchall()
            except psycopg2.Error as e:
                return render_template('index.html', error=e)
            finally:
                conn.close()

        conn = psycopg2.connect(**connparams)
        bgheaders = [
            'Title', 'Release Year', 'Rating', "Number of Ratings",
            'Minimum Length', 'Maximum Length', 'Minimum Players',
            'Maximum Players'
        ]
        bgdata = None
        table = []

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT title, released, rating, num_ratings, min_playtime, max_playtime, min_players, max_players FROM bg;"
                    )
                    bgdata = cur.fetchall()
                    for idx, column in enumerate(bgheaders):
                        table += [
                            [column] + list(set([row[idx] for row in bgdata]))
                        ]

                    cur.execute("SELECT publisher FROM publishers")
                    table += [['Publisher'] + list(
                        set([item[0] for item in cur.fetchall()]))]

                    cur.execute("SELECT mechanic FROM mechanics")
                    table += [['Mechanic'] + list(
                        set([item[0] for item in cur.fetchall()]))]

                    cur.execute("SELECT family FROM families")
                    table += [['Family'] + list(
                        set([item[0] for item in cur.fetchall()]))]

                    cur.execute("SELECT category FROM categories")
                    table += [['Category'] + list(
                        set([item[0] for item in cur.fetchall()]))]

                    cur.execute(
                        "SELECT name FROM people NATURAL JOIN designerrel")
                    table += [['Designer'] + list(
                        set([item[0] for item in cur.fetchall()]))]

                    cur.execute(
                        "SELECT name FROM people NATURAL JOIN artistrel")
                    table += [['Artist'] + list(
                        set([item[0] for item in cur.fetchall()]))]

        except psycopg2.Error as e:
            return render_template('search.html', error=e)
        finally:
            conn.close()

        if request.form.get('show') != None:
            errors = (query, conditions)

        return render_template(
            'search.html',
            table=table,
            data=data,
            headers=headers,
            error=errors)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['user_id'] = None
    return redirect('/')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
