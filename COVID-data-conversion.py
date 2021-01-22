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

# # Notes for posterity
# The COVID data seems to change format on the following dates:
# * 03/01/2020
# * 03/22/2020 (Add FIPS and Admin2)
# * 05/29/2020 (Add Incident Rate and Fatality Rate)
#
# FIPS stands for Federal Information Processing Standard, there appear to be entries for cities and counties. At this time I do not konw if the data for cities is counted in a county. I'm going to assume that it does, but there's all sorts of consequences from that assumption.
#
# Additional note: Officially from the JHU readme they started using county level data on the 26th of March.
#
# Note: I ended up using a dataset I found on Kaggle based on the NYT data instead of JHUs data. There ended up being some oddiites in the dataset that I wasn't sure how to reconcile. 
#

# +
import pandas as pd
import numpy as np
import os
from glob import glob
import sys
from datetime import datetime


filepath = "./COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"

daily_report_files = [file for file in glob(os.path.join(filepath,'*.csv'))]

#base_covid = pd.concat(map(pd.read_csv, daily_report_files),axis=0,sort=True)



# +
daily_reports = pd.DataFrame()

for file in daily_report_files:
    try:
        file_date, file_ext = file.split('/')[-1].split('.')
        temp_df = pd.read_csv(file)
        temp_df['date_str'] = file_date
        temp_df['Date'] = temp_df['date_str'].apply(lambda x: datetime.strptime(x, "%m-%d-%Y"))
        temp_df.rename(columns = {'Province/State':'Province_State',
                                  'Country/Region':'Country_Region',
                                  'Lat':'Latitude',
                                  'Long_':'Longitude',
                                  'Last Update':'Last_Update'}, inplace = True)
        daily_reports = daily_reports.append(temp_df)
    except Exception as ex:
        print(repr(ex))
        pass

# daily_reports = [pd.read_csv(file) for file in daily_report_files]

# TODO: Remove non US entries.

# +
us_daily_reports = daily_reports.loc[daily_reports['Country_Region'] == 'US']

us_daily_reports.loc[us_daily_reports.Admin2.notna()].tail(10)
# -

daily_reports.loc[daily_reports.Admin2.isna()].tail(5)

daily_reports.query('FIPS != FIPS and Country_Region == "US"').Admin2.unique()

# +
#db_source = filepath
#
#data_df = pd.DataFrame()
#for file in os.listdir(db_source):
#    try:
#        crt_date, crt_ext = crt_file = file.split(".")
#        if(crt_ext == "csv"):
#            crt_date_df = pd.read_csv(os.path.join(db_source, file))
#            crt_date_df['date_str'] = crt_date
#            crt_date_df['date'] = crt_date_df['date_str'].apply(lambda x: datetime.strptime(x, "%m-%d-%Y"))
#            data_df = data_df.append(crt_date_df)
#            print(data_df.columns())
#    except:
#        pass


# -

#province_state = data_df['Province/State'].unique()
#
#for ps in province_state:
#
#    data_df.loc[(data_df['Province/State']==ps) & (data_df['Latitude'].isna()), 'Latitude'] =\
 #               data_df.loc[(~data_df['Latitude'].isna()) & \
 #                           (data_df['Province/State']==ps), 'Latitude'].median()
#
#    data_df.loc[(data_df['Province/State']==ps) & (data_df['Longitude'].isna()), 'Longitude'] =\
#            data_df.loc[(~data_df['Longitude'].isna()) & \
#                        (data_df['Province/State']==ps), 'Longitude'].median() 
#
#country_region = data_df['Country/Region'].unique()
#
#for cr in country_region:
#
#    data_df.loc[(data_df['Country/Region']==cr) & (data_df['Latitude'].isna()), 'Latitude'] =\
#                data_df.loc[(~data_df['Latitude'].isna()) & \
#                            (data_df['Country/Region']==cr), 'Latitude'].median()
#
#    data_df.loc[(data_df['Country/Region']==cr) & (data_df['Longitude'].isna()), 'Longitude'] =\
#            data_df.loc[(~data_df['Longitude'].isna()) & \
#                        (data_df['Country/Region']==cr), 'Longitude'].median() 




