#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import sqlite3

DATABASE = 'observations.db'
N_ROWS = 1000

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


sql = 'SELECT Valid, Temp_F, station FROM observations ORDER BY Valid DESC'
con = sqlite3.connect(DATABASE)
data = pd.read_sql_query(sql, con, parse_dates=['Valid'], dtype={'Temp_F': int})
con.close()
data['fake'] = data['Valid'].apply(lambda x:x.replace(year=2020,month=10,day=20))
data['date'] = data['Valid'].dt.date
data = data.sort_values(by=['Valid'])
fig1 = px.line(data, x="Valid", y="Temp_F", color="station", markers=True)
fig2 = px.line(data, x="fake", y="Temp_F", color="station", symbol="date", markers=True)
fig2.show()

print('observe.')
app.layout = html.Div([
    dcc.Graph(
        id='g1',
        figure=fig1
    ),
    dcc.Graph(
        id='g2',
        figure=fig2
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
