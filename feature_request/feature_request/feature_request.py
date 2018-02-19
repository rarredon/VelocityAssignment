#!/bin/python
# -----------------------------------------------------------------------------
# Purpose: A features request application
# Author: Ryan Arredondo
# Date: 2/18/2018
# -----------------------------------------------------------------------------
"""This module contains code for running the feature requests application


To run: TODO

"""
# Module imports
import os
import sqlite3
from flask import (Flask, request, session, g, redirect, url_for, abort,
                   render_template, flash)

# Initialize application
app = Flask(__name__)

# App configuration
app.config.from_object(__name__)  # load configuration from this file
config = dict(DATABASE=os.path.join(app.root_path, 'feature_request.db'),
              SECRET_KEY='supersecret')
app.config.update(config)


def connect_db():
    """Returns a new connection to the feature requests database"""
    connection = sqlite3.connect(app.config['DATABASE'])
    connection.row_factory = sqlite3.Row
    return connection

def get_db():
    """Returns connection to db, creating new connection if necessary"""
    try:
        return g.sqlite_db
    except AttributeError:
        g.sqlite_db = connect_db()
        return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes db connection at app teardown"""
    try:
        g.sqlite_db.close()
    except AttributeError:
        pass


def init_db():
    """Uses schema to initialize application database"""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Command for CLI to initialize the database"""
    init_db()
    print('Initialized the database.')


@app.route('/')
def list_requests():
    """List view of the feature requests"""
    db = get_db()
    query = ('SELECT title, client.name, target_date, priority '
             'FROM request JOIN client ON request.client = client.id '
             ' ORDER BY client, priority')
    requests = db.execute(query).fetchall()
    return render_template('list_requests.html', requests=requests)


@app.route('/detail/')
def detail_request():
    """Detail view of a feature request"""
    pass


@app.route('/create', methods=['GET', 'POST'])
def create_request():
    """Handles GET and POST to create a new features request
    """
    db = get_db()

    # Return form, if request was a 'GET'
    if request.method == 'GET':
        # Get client names and previous priorities for form drop downs
        clients = db.execute('SELECT id, name FROM client').fetchall()
        priors = dict()
        for client in clients:
            prior_query = ('SELECT priority, title FROM request '
                           'JOIN client ON client.id = request.client '
                           'WHERE client.name = "%s"' % client[1])
            
            priors[client[0]] = db.execute(prior_query).fetchall()
        return render_template(
            'create_request.html', clients=clients, priors=priors)

    # Otherwise, handle 'POST'
    else:
        insert = ('INSERT INTO request '
                  '(title, description, client, '
                  'priority, target_date, product_area) '
                  'VALUES (?, ?, ?, ?, ?, ?)')
        update_priors(request.form['client'], request.form['priority'])
        data = [request.form['title'], request.form['description'],
                request.form['client'], request.form['priority'],
                request.form['date'], request.form['area']]
    db.execute(insert, data)
    db.commit()
    flash('New feature request was successfully created!')
    return redirect(url_for('list_requests'))


def update_priors(client, new_prior):
    """Updates priorities if new_prior is already used by client"""
    db = get_db()
    update = ('UPDATE request SET priority = priority + 1 '
              'WHERE client = ? AND priority >= ?')
    db.execute(update, [client, new_prior])
    db.commit()
