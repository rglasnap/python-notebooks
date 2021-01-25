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

# # Sakura Data Processing
# I obtained this data from the Japan Meterological Corporation from this page: https://ods.n-kishou.co.jp/detail?pid=2407
#
# My intent is to process the data (and likely translate) the data into a CSV that I can then load in a separate notebook for analysis and prediction.
#

# +
import pandas as pd
import numpy as np

from googletrans import Translator
# -

# # Information from the specification file
#
#
# Table 1 Specifications of cherry blossom blooming forecast data (by prefecture)
#
# File name: biz_sakura_yosou_yyyymmdd_pp.csv
# * Yyyymmdd: Date
# * Pp: Prefecture number (01-46: * 3.2 Refer to the target point list)
# file format: CSV format (comma separated)
# Character code: Shift-JIS
# Data element: Point number, point name, latitude, longitude, expected flowering date, expected full bloom dateTarget point
#
# Famous spots for cherry blossoms in prefectures
# * Limited to the location where Yoshino cherry tree is located.
# * The distribution map of the target points is as shown in Fig. 1 .
# * Target points are subject to change every year, so a separate list of target points
#
# Please refer to (biz_sakura_spotinfo_yyyy.csv).
#
# file size: About 60KB
# Data provision period: February-April
# * Please refer to the list of expected creation dates (biz_sakura_schedule_yyyy.csv).
# I.
# File modification date: Around 9 o'clock on the forecast creation date
# * Please refer to the list of expected creation dates for the delivery schedule.
#

# +

pref_codes = pd.read_csv('specification_sakura_pref/pref_code.csv', encoding='SHIFT_JIS',names =['Code', 'Prefecture'])
sakura_schedule = pd.read_csv('specification_sakura_pref/biz_sakura_schedule_2020.csv', encoding='SHIFT_JIS', header=None)
sakura_spotinfo = pd.read_csv('specification_sakura_pref/biz_sakura_spotinfo_2020.csv', encoding='SHIFT_JIS', 
                              names = ['Point number', 'Point name', 'Unknown', 'Prefecture', 'Latitude', 'Longitude'])
sakura_spotinfo_remove = pd.read_csv('specification_sakura_pref/biz_sakura_spotinfo_2020.csv', encoding='SHIFT_JIS', header=None)

# +
translator = Translator()

pref_map = pd.DataFrame(sakura_spotinfo['Prefecture'].unique(), columns=['jp'])

pref_map['en'] = pref_map['jp'].apply(translator.translate).apply(getattr, args=('text',))

# +
prefectures = pref_map.set_index('jp').to_dict()['en']

sakura_spotinfo.Prefecture = sakura_spotinfo['Prefecture'].map(prefectures)
# -

# Commenting out the code below for now. It's not so much an issue with the code, but an issue with trying to run too much data thru google translate. 
#
# I need to either figure out a way to get the google translate extension to translate batches slower, or do some sort of batch processing myself on the data frame (i.e. break it up into chunks of applies, if that's possible).
#

#pref_codes['Prefecture'] = pref_codes['Prefecture'].apply(translator.translate).apply(getattr, args=('text',))
#sakura_spotinfo['Point name'] = sakura_spotinfo['Point name'].apply(translator.translate).apply(getattr, args=('text',))
#sakura_spotinfo['Prefecture'] = sakura_spotinfo['Prefecture'].apply(translator.translate).apply(getattr, args=('text',))


pref_codes.head()
sakura_spotinfo.head()

# ## Sample testing

sample = pd.read_csv('sample_sakura_pref/biz_sakura_yosou_20190207_01.csv', encoding='SHIFT_JIS', header=None)

sample

sample[1][0]

sample['Location'] = sample[1].apply(translator.translate).apply(getattr, args=('text',))


sample
