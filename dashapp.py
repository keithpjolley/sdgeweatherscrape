#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import sqlite3
#from flask import Flask, g, jsonify, render_template, request
#import json

DATABASE = 'observations.db'
N_ROWS = 1000

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    db = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    db.close()
    return (rv[0] if rv else None) if one else rv

def observations():
    #n_rows = request.args.get('rows', N_ROWS, type=int)
    #if n_rows is None:
    #    n_rows = str(N_ROWS)
    #elif n_rows < 0:
    #    query = 'SELECT * FROM observations'
    #    n_rows = None
    #else:
    #    query = 'SELECT * FROM observations ORDER BY Valid DESC LIMIT ?'
    #    n_rows = str(n_rows)
    query = 'SELECT Valid, Temp_F, station FROM observations'
    return query_db(query)



data = observations() 
#print(data)

fig = px.scatter(data, x="Valid", y="Temp_F", color="station")

app.layout = html.Div([
    dcc.Graph(
        id='theid',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
