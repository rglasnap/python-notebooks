# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Sakura Data Processing (Japan Meteorological Agency)
# The Japan Meteorological Agency (JMA) has a lot more data than JMC does so I'm using their data for processing. Hopefully they have accompanything temperature data that I can use once I get to the modeling stage, otherwise I might 
#
# Notes:
# * When I get to the modeling stage, I will probably have to weight recent weather/temperature data higher than old temperature data because of global climate change impacts.
# * Bloom URL's are sakura003_00.html up to sakura003_06.html
# * Full Bloom URL's are sakura004_00.html up to sakura004_06.html
#
# The bottom of the pages have some definitions and notes on the data. I'm using those to determine column names and do some of the translations manually. 
#
# For posterity (said notes):
#
#  「*」が現在観測中の地点です。<br>
#  代替種目が空欄の地点はそめいよしのを観測しています。<br>
#  「-」は観測値なしを表しています。<br>
#  平年値は、1981-2010年の平均値です。<br>
#  「#」は、前年に観測したことを表します。<br>
#  (注）倶知安は1994年までえぞやまざくらを、1995年から2006年までそめいよしのを観測していました。
#  
# Which rougly translates to
#
# \*: The asteric denotes locations that are currently being observed. <br>
# \-: The dash represents no observation value. <br>
# 平年値: This column is the normal year average from 1981 to 2010. <br>
# \#: This represents that the observation was made in the previous year. <br>
# 注: This denotes some sort of change in observation. I'm still working on the translation.
#

import pandas as pd
import numpy as np
import urllib
import requests
from bs4 import BeautifulSoup
import lxml
from io import StringIO

# Workaround because I'm on an old version of pandas
pd.set_option("display.max_colwidth", 10000)


##TODO: Fix up some of the variable names (most notable unparsed_data)
def process_sakura_url(url):
    colspecs = [(0,5),(5,9),(9,16),(16,23),(23,30),(30,37),(37,44),(44,51),(51,58),(58,65),(65,72),(72,78),(78,86),(86,None)]

    # 
    bloom_req = requests.get(url)
    bloom_content = BeautifulSoup(bloom_req.content, 'lxml')

    # Convert the text table to a string IO so that pandas can read it in.
    #print(bloom_content.find(id='main').pre.text)
    bloom_string = StringIO(bloom_content.find(id='main').pre.text)
    
    if debug_print:
        print(bloom_string.getvalue())

    unparsed_data = pd.read_fwf(bloom_string,header=0,colspecs=colspecs,true_values=['*'])

    # Get rid of the extra headers that showed up for readability on a web page.
    unparsed_data.columns = unparsed_data.columns.str.strip()

    unparsed_data[unparsed_data.duplicated()]
    unparsed_data = unparsed_data.drop_duplicates()
    
    unparsed_data.drop(unparsed_data.loc[unparsed_data['地点名'].isna()].index, inplace=True)
    unparsed_data.drop(unparsed_data[unparsed_data['地点名'].str.contains('地点名')].index, inplace=True)

    #Parse the year columns into datetime format.
    for col in unparsed_data:
        if str.isnumeric(col):
            unparsed_data[col] = unparsed_data[col] + f' {col}'
            unparsed_data[col] = pd.to_datetime(unparsed_data[col],errors='coerce',format="%m %d %Y")

    # Translate the non date columns
    unparsed_data.rename(columns={unparsed_data.columns[0]: 'Site Name',
                          'Unnamed: 1': 'Currently Being Observed',
                          unparsed_data.columns[-2]: '30 Year Average 1981-2010',
                          unparsed_data.columns[-1]: 'Notes' }, inplace=True)
    
    with pd.option_context('display.max_rows', None):
        if debug_print:
            display(unparsed_data)
            
    return unparsed_data


# +
debug_print = True

latest_df = process_sakura_url('https://www.data.jma.go.jp/sakura/data/sakura003_06.html')
# -


