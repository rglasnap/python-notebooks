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

bloom_req = requests.get('https://www.data.jma.go.jp/sakura/data/sakura003_06.html')

bloom_content = BeautifulSoup(bloom_req.content, 'lxml')

#print(bloom_content.find(id='main').pre.text)
bloom_string = StringIO(bloom_content.find(id='main').pre.text)
print(bloom_string.getvalue())
#derp = pd.read_csv(bloom_string,sep=r"[ ]{2,}", engine='c')
unparsed_data = pd.read_csv(bloom_string,header=None)

unparsed_data[unparsed_data.duplicated()]

unparsed_data = unparsed_data.drop_duplicates()

raw_headers = StringIO(unparsed_data.loc[:1,0].to_string(index=False))
raw_data = StringIO(unparsed_data.loc[2:,0].to_string(index=False))
test_data = pd.read_fwf(raw_data,header=None)

test_data.head()


