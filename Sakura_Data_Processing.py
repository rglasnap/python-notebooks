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

import pandas as pd
import numpy as np


pd.read_csv('sample_sakura_pref/biz_sakura_yosou_20190207_01.csv', encoding='SHIFT_JIS')


