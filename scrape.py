#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import sqlite3
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def most_recent_data(driver):
    tr_sel = 'div#observations>table>tbody>tr'
    try:
        tr = driver.find_element_by_css_selector(tr_sel)
        elements = tr.find_elements_by_css_selector('td')
    except:
        elements = []
    return elements

class we_has_data(object):
    def __call__(self, driver):
        return len(most_recent_data(driver)) > 0


def get_data(me, station):
    url = 'https://weather.sdgeweather.com/station/' + station
    wait = 5 # seconds
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get(url)

    # Wait until the 'observations' link is ready to be clicked.
    observation_link = WebDriverWait(driver, wait).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="#observations"]'))
        )
    # Wait until the observation data is loaded.
    WebDriverWait(driver, wait).until(we_has_data())

    # This should be able to be done w/o bs but seems maybe not.
    source = driver.page_source
    soup = BeautifulSoup(source, 'lxml')
    observation_data = soup.find('div', id='observations')
    ths = observation_data.find('thead').find_all('th')
    tds = observation_data.find('tbody').find('tr').find_all('td')
    columns = [col.find('a').get_text().replace('*', '') for col in ths]
    # Make the headers more descriptive.
    replacement_keys = {
        'Winds': 'Winds_MPH',
        'Gusts': 'Gusts_MPH',
        'Temp': 'Temp_F',
        'Humidity': 'Humidity_PCT',
    }
    columns = [replacement_keys[c] if c in replacement_keys else c for c in columns]
    data = [col.get_text() for col in tds]
    ret = {c:d for c,d in zip(columns, data) }
    # Change the data from string to number.
    regex = re.compile(r'\D+')
    for k in replacement_keys.values():
        ret[k] = regex.sub('', ret[k])
    ret['station'] = station
    return ret

def save_data(me, data, dbfile):
    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    table = 'observations'
    columns = ', '.join(my_dict.keys())
    constraint = f'UNIQUE(Valid, station) ON CONFLICT IGNORE'
    placeholders = ':'+', :'.join(my_dict.keys())
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    cur.execute(f'CREATE TABLE IF NOT EXISTS {table} ({columns}, {constraint})')
    cur.execute(sql, data)
    con.commit()


if __name__ == "__main__":
    stations= ['LCK', 'WCV',]
    dbfile = 'observations.db'
    me = os.path.basename(sys.argv[0])
    p = argparse.ArgumentParser(description='Do something')
    p.add_argument('--verbose', action='store_true', help='Verbose')
    p.add_argument('--stations', default=stations, action="extend", nargs="+", type=str,
            help=f'stations to query. default: "{stations}"')
    p.add_argument('--dbfile', default=dbfile,
            help=f'sqlite3 db file to store observerations. default: "{dbfile}"')
    args = p.parse_args()

    errors = 0
    for station in args.stations:
        if args.verbose:
            print(station)
        data = get_data(me, station)
        if data:
            save_data(me, data, args.dbfile)
            if args.verbose:
                print(data)
                print()
        else:
            print(f'ERROR: no data for station "{station}".')
            errors += 1
    sys.exit(errors)
