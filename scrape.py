#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import sqlite3
import re

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def most_recent_observation(driver):
    tr_sel = 'div#observations>table>tbody>tr'
    try:
        tr = driver.find_element_by_css_selector(tr_sel)
        elements = tr.find_elements_by_css_selector('td')
    except:
        elements = []
    return elements


class we_has_observation(object):
    def __call__(self, driver):
        return len(most_recent_observation(driver)) > 0


def fix_date(datestr):
    now = datetime.today()
    dt = datetime.strptime(datestr, '%m/%d %H:%M%p %Z')
    # strptime not smart enough to do the right thing with '%p (am/pm)'.
    if re.search('pm ', datestr) and dt.hour != 12:
        dt = dt.replace(hour = dt.hour + 12)
    org_year = dt.year
    dt = dt.replace(year = now.year)
    if abs((now - dt).days) > 180:
        dt = dt.replace(year = now.year - 1)
    if abs((now - dt).days) > 180:
        # Give up.
        dt = dt.replace(year = org.year)
    return dt.astimezone(tz=None).isoformat()


def save_observation(me, observation, dbfile):
    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    table = 'observations'
    columns = ', '.join(observation.keys())
    constraint = f'UNIQUE(Valid, station) ON CONFLICT IGNORE'
    placeholders = ':'+', :'.join(observation.keys())
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    cur.execute(f'CREATE TABLE IF NOT EXISTS {table} ({columns}, {constraint})')
    cur.execute(sql, observation)
    con.commit()

def get_observations(me, station, dbfile, verbose):
    if verbose:
        print(station)
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
    WebDriverWait(driver, wait).until(we_has_observation())

    # This should be able to be done w/o bs but seems maybe not.
    source = driver.page_source
    soup = BeautifulSoup(source, 'lxml')
    observation = soup.find('div', id='observations')
    ths = observation.find('thead').find_all('th')
    columns = [col.find('a').get_text().replace('*', '') for col in ths]
    trs = observation.find('tbody').find_all('tr')
    # Make the headers more descriptive.
    replacement_keys = {
        'Winds': 'Winds_MPH',
        'Gusts': 'Gusts_MPH',
        'Temp': 'Temp_F',
        'Humidity': 'Humidity_PCT',
    }
    columns = [replacement_keys[c] if c in replacement_keys else c for c in columns]
    regex = re.compile(r'\D+')
    for tr in trs:
        tds = tr.find_all('td')
        observation = {c:d for c,d in zip(columns, [col.get_text() for col in tds])}
        # Change the data from string to number.
        for k in replacement_keys.values():
            observation[k] = regex.sub('', observation[k])
        observation['station'] = station
        observation['Valid'] = fix_date(observation['Valid'])
        if verbose:
            print(observation)
        save_observation(me, observation, dbfile)
    return


if __name__ == "__main__":
    stations= ['LCK', 'WCV',]
    dbfile = 'observations.db'
    me = os.path.basename(sys.argv[0])
    p = argparse.ArgumentParser(description='Do something')
    p.add_argument('--verbose', action='store_true', help='Verbose')
    #p.add_argument('--stations', default=stations, action="extend", nargs="+", type=str,
    p.add_argument('--stations', default=stations, nargs="*", type=str,
            help=f'stations to query. default: "{stations}"')
    p.add_argument('--dbfile', default=dbfile,
            help=f'sqlite3 db file to store observerations. default: "{dbfile}"')
    args = p.parse_args()

    errors = 0
    for station in args.stations:
        get_observations(me, station, args.dbfile, args.verbose)
    sys.exit(errors)
