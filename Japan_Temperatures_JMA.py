# %% markdown
# # Japanese Temperature Data Collection
# This is a companion to the other Japanese Meteorological Agency notebook on Sakura Data processing.
#
#
# Sources:
# * https://www.data.jma.go.jp/obd/stats/data/mdrr/man/kansoku_gaiyou.html  (smater.index file)
# * https://www.data.jma.go.jp/gmd/risk/obsdl/index.php Temperature Request site
#
# Notes:
# I'm really hoping this smaster file has the data I need. Well not so much the data as it is the station identifiers that get used in the POST requests to the other link.
#
# Notes2:
# This data file has the data I need! HOORAY! Well at least part of it, the station numbers match up with the last 3 digits of the requests I manually put in for Kyoto, Nara, and Osaka
# %% codecell
import sys
import pandas as pd
import numpy as np
import requests as req
# %% codecell
with open('Japan Temp Data/smaster.index', encoding='shift_jis') as file:
    for i in range(5):
        line = file.readline()
        print(line)

# %% codecell
col_widths = [3 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,2 ,1 ,1 ,8 ,12 ,6 ,7,5 ,5 ,3 ,1 ,1 ,8 ,8 ,12 ,18 ,8 ,5 ,12 ,1 ,1 ,1 ,1 ,1 ,1 ,5]

with open('Japan Temp Data/smaster.index', encoding='shift_jis') as file:
    smaster = pd.read_fwf(file,header=None,widths=col_widths,dtype='object')
# %% codecell
np.unique(smaster.loc[smaster[14] == 'SAPPORO'][[0,14]])
# %% codecell
site_list = smaster[[0,14]].drop_duplicates()
site_list.rename(columns={0:'Site Id',14:'Site Name'},inplace=True)

site_list['Site Id'] = 's47' + site_list['Site Id']
site_list['Site Name'] = site_list['Site Name'].str.title()
# %% codecell
site_list.loc[site_list['Site Name'] == 'Kyoto']
# %% codecell
site_list.shape

# %% codecell
site = 'https://www.data.jma.go.jp/gmd/risk/obsdl/show/table'
site2 = 'https://www.data.jma.go.jp/gmd/risk/obsdl/index.php'
data = {'stationNumList': ["s47759"],
    'aggrgPeriod': 1,
    'elementNumList': [["201",""]],
    'interAnnualFlag': 1,
    'ymdList': ["2020","2021","1","1","1","1"],
    'optionNumList': [],
    'downloadFlag': True,
    'rmkFlag': 1,
    'disconnectFlag': 1,
    'youbiFlag': 0,
    'fukenFlag': 0,
    'kijiFlag': 0,
    'huukouFlag': 0,
    'csvFlag': 1,
    'jikantaiFlag': 0,
    'jikantaiList': [],
    'ymdLiteral': 1,
    'PHPSESSID': 'b1mththn5adl374iv59udc0976'}

headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding': 'gzip, deflate, br',
'Content-Type': "application/x-www-form/urlencoded",
'Host': 'www.data.jma.go.jp',
'Origin': 'https://www.data.jma.go.jp',
'Referer': 'https://www.data.jma.go.jp/gmd/risk/obsdl/index.php'}

response = req.post(site,data=data, headers=headers)
response.headers

print(response.url)

print(response.text)
from bs4 import BeautifulSoup

testcase = BeautifulSoup(response.content)

testcase
