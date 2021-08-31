#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This has been superseded by an update to `scrape.py`. It now trys to import all the
the observations it finds instead of just the latest. sqlite3 "unique" prevents
duplicate observations.

<strike>
This is a one-time only (or if your importer's not been running for a while) script.
Instead of scraping you do a manual grab of the data and put it in a csv file.
Now that I think about it, it makes more sense for the scraper to just try and put
in all the data it finds and let sql worry about duplicates.
</strike>
'''

import argparse
import csv
import os
import re
import sqlite3
import sys

sys.exit(255)

from pathlib import Path

def save_data(me, data, dbfile):
    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    table = 'observations'
    columns = ', '.join(data.keys())
    constraint = f'UNIQUE(Valid, station) ON CONFLICT IGNORE'
    placeholders = ':'+', :'.join(data.keys())
    create = f'CREATE TABLE IF NOT EXISTS {table} ({columns}, {constraint})'
    insert = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    cur.execute(create, data)
    cur.execute(insert, data)
    con.commit()
    return


def main(me, file):
    station = Path(file).stem
    with open(file, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        columns = [col.replace('*', '') for col in reader.fieldnames]
        # Make the headers more descriptive.
        replacement_keys = {
            'Winds': 'Winds_MPH',
            'Gusts': 'Gusts_MPH',
            'Temp': 'Temp_F',
            'Humidity': 'Humidity_PCT',
        }
        columns = [replacement_keys[c] if c in replacement_keys else c for c in columns]
        reader.fieldnames = columns
        regex = re.compile(r'\D+')
        for row in reader:
            for k in replacement_keys.values():
                row[k] = regex.sub('', row[k])
            row['station'] = station
            print(row)
            save_data(me, row, 'observations.db')
    return

if __name__ == "__main__":
    me = os.path.basename(sys.argv[0])
    p = argparse.ArgumentParser(description='Do something')
    p.add_argument('files', nargs='+')
    args = p.parse_args()
    [main(me, file) for file in args.files]

