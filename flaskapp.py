#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys

import sqlite3
from flask import Flask, g, jsonify, render_template, request

app = Flask(__name__)

DATABASE = 'observations.db'
N_ROWS = 1000

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


@app.route('/')
def index():
    ret = {
        'Usage': 'Do stuff.',
        '/observations?rows=N': f'return N rows. default is most recent {N_ROWS}. Negative N for all.',
    }
    return jsonify(ret)


@app.route('/observations')
def observations():
    n_rows = request.args.get('rows', N_ROWS, type=int)
    if n_rows is None:
        n_rows = str(N_ROWS)
    elif n_rows < 0:
        query = 'SELECT * FROM observations'
        n_rows = None
    else:
        query = 'SELECT * FROM observations ORDER BY Valid DESC LIMIT ?'
        n_rows = str(n_rows)
    return jsonify(query_db(query, (n_rows,)))

@app.route('/plot')
def plot():
    return render_template('plot.html')

if __name__ == '__main__':
    app.run(debug=True)
