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
# 注: Until 1994 the observations at Kutchan were Sargent Cherries. From 1995 to 2006 they were Yoshino Cherries.
#

# +
import pandas as pd
import numpy as np
import urllib
import requests
from bs4 import BeautifulSoup
import lxml
import time
import re
from io import StringIO

from googletrans import Translator
# -

# Workaround because I'm on an old version of pandas
pd.set_option("display.max_colwidth", 10000)


def batch_translation(df, column_src, batch_size=100):
    idx = 0
    while idx < df[column_src].size:
        # Spawn a new translator session to see if that gets past the 429 code from Google.
        translator = Translator()
        translator.raise_Exception = True
        df.loc[idx:idx+batch_size,column_src] = df.loc[idx:idx+batch_size,column_src].apply(translator.translate, src='ja').apply(getattr, args=('text',))
        idx = idx+batch_size
        print(f"Current index: {idx} of {df[column_src].size}")
        time.sleep(10)


# +
def extract_sakura_data(url,batch=False,pause_length=2):    
    #colspecs = [(0,5),(5,9),(9,16),(16,23),(23,30),(30,37),(37,44),(44,51),(51,58),(58,65),(65,72),(72,78),(78,86),(86,None)]

    # Be nice to the endpoint and wait a bit if we're doing batch processing of multiple function calls. 
    if batch:
        time.sleep(pause_length)
    bloom_req = requests.get(url)
    bloom_content = BeautifulSoup(bloom_req.content, 'lxml')

    print(f"Processing: {bloom_content.title.text}")
    # Convert the text table to a string IO so that pandas can read it in.
    #print(bloom_content.find(id='main').pre.text)
    bloom_string = StringIO(bloom_content.find(id='main').pre.text)

    #Find the first real line so we can dynmiacally determine the column spacings
    for line in bloom_string:
        if line.isspace() == False:
            break;

    #Find all of the character locations of each year
    year_iter = re.finditer("\d{4}", line)
    year_indices = [(m.start(0),m.end(0)+3) for m in year_iter]

    #Pick the ending character of the last year so we can add the last two columns.
    end_char = year_indices[-1][1]

    dynamic_colspecs = [(0,5),(5,9)]
    end_colspecs = [(end_char,end_char+8),(end_char+8,None)]

    # Put everything together in the same list
    dynamic_colspecs.extend(year_indices)
    dynamic_colspecs.extend(end_colspecs)

    # Reset the string stream so we can re-parse the entire thing.
    bloom_string.seek(0)
    
    
    if debug_print:
        print(bloom_string.getvalue())

    bloom_df = pd.read_fwf(bloom_string,header=0,colspecs=dynamic_colspecs,true_values=['*'])

    # Get rid of the extra headers that showed up for readability on a web page.
    bloom_df.columns = bloom_df.columns.str.strip()

    bloom_df[bloom_df.duplicated()]
    bloom_df = bloom_df.drop_duplicates()
    
    bloom_df.drop(bloom_df.loc[bloom_df['地点名'].isna()].index, inplace=True)
    bloom_df.drop(bloom_df[bloom_df['地点名'].str.contains('地点名')].index, inplace=True)

    #Parse the year columns into datetime format.
    for col in bloom_df:
        if str.isnumeric(col):
            # Account for the # entries (which are usually dates measured in december)
            if bloom_df[col].str.contains('#').any():
                last_year = bloom_df[col].str.contains('#',na=False)
                this_year = ~bloom_df[col].str.contains('#',na=False)
                
                bloom_df.loc[last_year,col] = bloom_df.loc[last_year,col] + f' {int(col)-1}'
                bloom_df.loc[this_year,col] = bloom_df.loc[this_year,col] + f' {col}'
                bloom_df[col] = bloom_df[col].str.replace("#","")
            else:
                bloom_df[col] = bloom_df[col] + f' {col}'
            bloom_df[col] = pd.to_datetime(bloom_df[col],errors='coerce',exact=False,format="%m %d %Y")
            
            #   Data Assertion: No dates should exist in the current year after October. If they exist, they should be in the previous year.
            if bloom_df.loc[bloom_df[col] > f'{col}-10-01',col].any():
                bloom_df.loc[bloom_df[col] > f'{col}-10-01',col] = bloom_df.loc[bloom_df[col] > f'{col}-10-01',col] - pd.DateOffset(years=1)

    # Translate the non date columns
    bloom_df.rename(columns={bloom_df.columns[0]: 'Site Name',
                          'Unnamed: 1': 'Currently Being Observed',
                          bloom_df.columns[-2]: '30 Year Average 1981-2010',
                          bloom_df.columns[-1]: 'Notes' }, inplace=True)
    
    bloom_df.set_index('Site Name',inplace=True)
    
    #Fix stray #'s
    # Note: There's probably a better way of doing this, but I haven't found it yet.
    bloom_df['30 Year Average 1981-2010'] = bloom_df['30 Year Average 1981-2010'].str.replace("#","")
    
    # Fix the boolean data.
    # There were set values for True, blank got converted into NaN.
    bloom_df['Currently Being Observed'].fillna(False,inplace=True)
    
    with pd.option_context('display.max_rows', None):
        if debug_print:
            display(bloom_df)
            
    return bloom_df

#TODO: Come up with a more descriptive title that isn't super long.
def combine_sakura_data(bloom_dfs):
    
    concated = pd.concat(bloom_dfs,axis=1)
    concated.drop_duplicates(inplace=True)
    
    # Translations
    concated = concated.reset_index()
    batch_translation(concated,'Site Name')
    concated.set_index('Site Name',inplace=True)

    # Google translate doesn't properly translate the notes column, so I'm doing that manually.
    notes_dict = {'えぞやまざくら': 'Sargent cherry (Prunus sargentii)',
                  'ちしまざくら': 'Kurile Island Cherry (Cerasus nipponica var. kurilensis)',
                 'ひかんざくら': 'Taiwan cherry (Prunus campanulata)',
                  '（注）': 'Until 1994 Sargent Cherry, from 1995 to 2006 they were Yoshino Cherry.'}
    
    observed_col = concated['Currently Being Observed'].iloc[:,0]
    transposed = concated.T.drop_duplicates(keep='last')
    transposed.drop('Currently Being Observed',inplace=True)

    combined_blooms = transposed.T
    combined_blooms.insert(0,'Currently Being Observed',observed_col);

    combined_blooms.Notes = combined_blooms.Notes.map(notes_dict)
    
    return combined_blooms


# +
debug_print = False
bloom_urls = ['https://www.data.jma.go.jp/sakura/data/sakura003_00.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura003_01.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura003_02.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura003_03.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura003_04.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura003_05.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura003_06.html']

bloom_dfs = [extract_sakura_data(x,batch=True) for x in bloom_urls]
bloom_start = combine_sakura_data(bloom_dfs)
# +
debug_print = False
full_bloom_urls = ['https://www.data.jma.go.jp/sakura/data/sakura004_00.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura004_01.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura004_02.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura004_03.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura004_04.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura004_05.html',
                     'https://www.data.jma.go.jp/sakura/data/sakura004_06.html']

full_bloom_dfs = [extract_sakura_data(x,batch=True) for x in full_bloom_urls]
full_bloom = combine_sakura_data(full_bloom_dfs)

# +
# Sanity checks
#    Full bloom is *ALWAYS* after the initial bloom. If it's not something somewhere is wrong.

date_cols = [col for col in bloom_start.columns if str.isnumeric(col)]
broken_dates = full_bloom[date_cols].fillna(pd.Timestamp('2021-01-01')) < bloom_start[date_cols].fillna(pd.Timestamp('1950-01-01'))

broken_dates.any().any()
# -

# Translations Final Fixes
bloom_start = bloom_start.rename(index={"Iriomotei sand": "Iriomote Island"},errors="raise")
full_bloom = full_bloom.rename(index={"Iriomotei sand": "Iriomote Island"},errors="raise")

bloom_start.to_csv('sakura_first_bloom_dates.csv')
full_bloom.to_csv('sakura_full_bloom_dates.csv')

# # Troubleshooting
# This is my area for misc troubleshooting. Fully working code is above this.

bloom_start = bloom_start.rename(index={"Iriomotei sand": "Iriomote Island"},errors="raise")

full_bloom

full_bloom[full_bloom[date_cols].fillna(pd.Timestamp('2020-01-02')) < bloom_start[date_cols].fillna(pd.Timestamp('2020-01-01'))]

# +
debug_print = True
test_url = 'https://www.data.jma.go.jp/sakura/data/sakura004_00.html'

test_df = extract_sakura_data(test_url)
# -

test_df['Currently Being Observed'].fillna(False,inplace=True)
test_df.head()

# +
translator = Translator()

notes_map = pd.DataFrame(bloom_start['Notes'].unique(), columns=['jp'])

notes_map['en'] = notes_map['jp'].apply(translator.translate).apply(getattr, args=('text',))
# -

notes_map

notes_dict = {'えぞやまざくら': 'Sargent cherry (Prunus sargentii)',
              'ちしまざくら': 'Kurile Island Cherry (Cerasus nipponica var. kurilensis)',
             'ひかんざくら': 'Taiwan cherry (Prunus campanulata)',
              '（注）': 'Note: Translation pending'}

concated['Currently Being Observed'].iloc[:,0]

trans = Translator()
trans.translate('山形').src

with pd.option_context('display.max_rows', None):
    display(transposed.T['30 Year Average 1981-2010'])

with pd.option_context('display.max_rows', None):
    print(concated.loc[['津']].T)

debug_print=True
process_sakura_url('https://www.data.jma.go.jp/sakura/data/sakura003_03.html')

# +
import re
debug_print = True

bloom_req = requests.get('https://www.data.jma.go.jp/sakura/data/sakura003_03.html')
bloom_content = BeautifulSoup(bloom_req.content, 'lxml')

# Convert the text table to a string IO so that pandas can read it in.
#print(bloom_content.find(id='main').pre.text)
bloom_string = StringIO(bloom_content.find(id='main').pre.text)

String = '地点名　     1953   1954   1955   1956   1957   1958   1959   1960   平年値   代替種目'
String2 = '地点名　     2011   2012   2013   2014   2015   2016   2017   2018   2019   2020   平年値   代替種目'

#Find the first real line so we can dynmiacally determine the column spacings
for line in bloom_string:
    if line.isspace() == False:
        break;

#Find all of the character locations of each year
year_iter = re.finditer("\d{4}", line)
year_indices = [(m.start(0),m.end(0)+3) for m in year_iter]

#Pick the ending character of the last year so we can add the last two columns.
end_char = year_indices[-1][1]

dynamic_colspecs = [(0,5),(5,9)]
end_colspecs = [(end_char,end_char+8),(end_char+8,None)]

# Put everything together in the same list
dynamic_colspecs.extend(year_indices)
dynamic_colspecs.extend(end_colspecs)

print(dynamic_colspecs)
# Reset the string stream so we can re-parse the entire thing.
bloom_string.seek(0)

if debug_print:
    print(bloom_string.getvalue())

tst_names = ['地点名', 'Unnamed: 1', '1953', '1954', '1955','1956','1957','1958','1959','1960','平年値','代替種目']
unparsed_data = pd.read_fwf(bloom_string,header=0,colspecs=dynamic_colspecs,true_values=['*'])
with pd.option_context('display.max_rows', None):
    if debug_print:
        display(unparsed_data)
# +
debug_print = False
testing = process_sakura_url('https://www.data.jma.go.jp/sakura/data/sakura003_03.html')

print(testing.iloc[1])
# -
testing.loc[testing['1989'] > '1989-10-01','1989']


testing.loc[testing['1989'] < '1989-01-01','1989']

concated.T.loc[concated.T.duplicated()]



# +
with pd.option_context('display.max_rows', None):
    display(concated.loc['名護','30 Year Average 1981-2010'])
    
concated.loc['名護','30 Year Average 1981-2010'].str.contains('#').any()

derp = '2019'

for entry in concated.loc['名護','30 Year Average 1981-2010']:
    if '#' in entry:
         print(entry)

# +
untransposed = transposed.T

with pd.option_context('display.max_rows', None):
    display(untransposed['30 Year Average 1981-2010'])
# -

debug_print = True
#process_sakura_url('https://www.data.jma.go.jp/sakura/data/sakura003_01.html')

# +
col = '1990'

has_stuff = unparsed_data[col].str.contains('#',na=False)
no_stuff = ~unparsed_data[col].str.contains('#',na=False)
#unparsed_data.loc[~unparsed_data[col].str.contains('#',na=False),col] = unparsed_data.loc[~unparsed_data[col].str.contains('#',na=False),col] + f' {int(col)-1}'
# -

unparsed_data.loc[has_stuff,col] = unparsed_data.loc[has_stuff,col].str.strip('#') + f' {int(col)-1}'

unparsed_data.loc[has_stuff,'1989'].str.replace("#","")

bloom_content.title.text


