import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import statsmodels.api as sm
from datetime import datetime as dt
import numpy as np
from time import mktime

def DataConstructor(c, temp, precip, t_sens, p_sens, time_low = None, time_up = None, list_of_blocks = None):
    '''
    DOC
    '''
    where = ' WHERE DailyWeather.Precip <= ? AND DailyWeather.Precip >= ? '+\
    'AND DailyWeather.AverageTemp <= ? AND DailyWeather.AverageTemp >= ?'
    params = [precip + p_sens, precip - p_sens, temp + t_sens, temp - t_sens]
    if list_of_blocks:
        select = 'SELECT CrimeData1.Day, CrimeData1.Primary_Type, CrimeData1.Block FROM DailyWeather '+\
        'JOIN CrimeData1 ON DailyWeather.Date = CrimeData1.Day'
        where += ' AND (' +('CrimeData1.Block = ? OR '*len(list_of_blocks))[:-3]+') '
        params += list_of_blocks
        where += 'AND CrimeData1.Hour >= ? AND CrimeData1.Hour <= ?'
        params += [time_low, time_up]
    else:
        select = 'SELECT Date FROM DailyWeather'
    return pd.read_sql(select + where, c, params = params)

SAFETY_DICT = {'BATTERY': 8, 'ROBBERY': 7, 'THEFT': 2, 'BURGLARY': 6,
       'ASSAULT': 6, 'CRIM SEXUAL ASSAULT': 10, 'KIDNAPPING': 9, 
               'SEX OFFENSE': 5, 'HOMICIDE': 10, 'INTIMIDATION': 3}

def Regression(weather, crimes, date):
    '''
    DOC
    '''
    weather['Score'] = crimes.groupby('Day').sum()['Primary_Type']
    weather['Score'] = weather['Score'].fillna(0)
    X = sm.add_constant(weather.Date)
    model = sm.OLS(weather.Score, X)
    results = model.fit()
    date = mktime(dt.strptime(date, '%Y-%m-%d').timetuple())
    return results.params[0] + results.params[1]*date


def Regression_List(list_of_blocks, temp, precip, t_sens, p_sens, date, time_low, time_up):
    '''
    DOC
    '''
    c = sqlite3.connect("Crime.db")
    weather = DataConstructor(c, temp, precip, t_sens, p_sens).set_index('Date')
    crimes = DataConstructor(c, temp, precip, t_sens, p_sens, time_low, time_up, list_of_blocks)
    c.close()
    crimes['Primary_Type'] = crimes['Primary_Type'].map(SAFETY_DICT)
    weather = weather.sort_index()
    weather['Date'] = pd.to_datetime(weather.index).astype(np.int64) // 10**9
    ret_dic = {}
    for block in list_of_blocks: 
        crime = crimes[crimes['Block'] == block]
        ret_dic[block] = Regression(weather, crime, date)
    return ret_dic


