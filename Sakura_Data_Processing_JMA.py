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

import pandas as pd
import numpy as np
import urllib
import requests
from bs4 import BeautifulSoup
import lxml
from io import StringIO

# Workaround because I'm on an old version of pandas
pd.set_option("display.max_colwidth", 10000)


bloom_req = requests.get('https://www.data.jma.go.jp/sakura/data/sakura003_06.html')

bloom_content = BeautifulSoup(bloom_req.content, 'lxml')

# +
colspecs = [(0,5),(5,9),(9,16),(16,23),(23,30),(30,37),(37,44),(44,51),(51,58),(58,65),(65,72),(72,78),(78,86),(86,None)]
#print(bloom_content.find(id='main').pre.text)
bloom_string = StringIO(bloom_content.find(id='main').pre.text)
print(bloom_string.getvalue())

unparsed_data = pd.read_fwf(bloom_string,header=0,colspecs=colspecs,true_values=['*'])

unparsed_data[unparsed_data.duplicated()]
unparsed_data = unparsed_data.drop_duplicates()

for col in unparsed_data:
    if str.isnumeric(col):
        unparsed_data[col] = unparsed_data[col] + f' {col}'
        unparsed_data[col] = pd.to_datetime(unparsed_data[col],errors='coerce',format="%m %d %Y")
# -

with pd.option_context('display.max_rows', None):
    display(unparsed_data)


