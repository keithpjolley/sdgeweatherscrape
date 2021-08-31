#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import sqlite3

import pandas as pd
import seaborn as sns

def main(me):

    # %matplotlib
    con =  sqlite3.connect('observations.db')
    df = pd.read_sql_query("SELECT * from observations", con)
    con.close()

    df.Temp_F = df.Temp_F.astype(int)
    df.Valid = pd.to_datetime(df.Valid)

    sns.scatterplot(data=df, x='Valid', y='Temp_F', hue='station')
    sns.lineplot(data=df, x='Valid', y='Temp_F', hue='station')

    return

if __name__ == "__main__":
    me = os.path.basename(sys.argv[0])
    p = argparse.ArgumentParser(description='Do something')
    p.add_argument('--verbose', action='store_true', help='Verbose')
    args = p.parse_args()
    main(me)

