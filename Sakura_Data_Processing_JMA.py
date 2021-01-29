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
colspecs = [(0,5),(5,9),(9,16),(16,23),(23,30),(30,37),(37,44),(44,51),(51,58),(58,65),(65,72),(72,80),(80,87),(87,None)]
#print(bloom_content.find(id='main').pre.text)
bloom_string = StringIO(bloom_content.find(id='main').pre.text)
#print(bloom_string.getvalue())
#derp = pd.read_csv(bloom_string,sep=r"[ ]{2,}", engine='c')
unparsed_data = pd.read_fwf(bloom_string,header=0,colspecs=colspecs,
                           parse_dates=['2011','2012'],infer_datetime_format=True,
                           true_values=['*'])

unparsed_data.head()
# -

unparsed_data[unparsed_data.duplicated()]

unparsed_data = unparsed_data.drop_duplicates()
#print(unparsed_data.iloc[5:8].apply(lambda x: x.to_string(index=False)))

raw_headers = StringIO(unparsed_data.loc[:1,0].to_string(index=False))
raw_data = StringIO(unparsed_data.loc[2:,0].to_string(index=False))
print(raw_data.getvalue())
test_data = pd.read_fwf(raw_data,header=None,colspecs=colspecs)

test_data.head(10)


