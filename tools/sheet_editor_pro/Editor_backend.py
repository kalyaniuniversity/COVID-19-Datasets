# -*- coding: utf-8 -*-
"""
Created on Wed May 20 10:21:09 2020

@author: Dripta
"""

import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import urllib
import json
import pprint
from utils import DateChecker, WriteonSheet, resolveData
pp = pprint.PrettyPrinter(width=41, compact=True)


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'cred_sheet.json', scope)
client = gspread.authorize(creds)
sheet_data_list = ['COVID19_INDIA_STATEWISE_TIME_SERIES_CONFIRMED', 'COVID19_INDIA_STATEWISE_TIME_SERIES_RECOVERY',
              'COVID19_INDIA_STATEWISE_TIME_SERIES_DEATH']


def pull_api_data(url='https://api.covid19india.org/states_daily.json'):
    print('Scraping API data...')
    json_url = urllib.request.urlopen(url)
    data = json.loads(json_url.read())
    states_daily = data['states_daily']
    df = pd.DataFrame(states_daily)
    df.index = df['date'].drop(columns=['date'])
    df = df.drop(columns=['date'])
    df = df.replace(to_replace='', value=0)
    for i in df.columns:
        try:
            df[i] = df[i].astype(int)
        except:
            continue
    cum_conf = df[df['status'] == 'Confirmed'].drop(
        columns=['status']).cumsum()
    cum_recovered = df[df['status'] == 'Recovered'].drop(
        columns=['status']).cumsum()
    cum_death = df[df['status'] == 'Deceased'].drop(
        columns=['status']).cumsum()
    cum_conf = cum_conf.drop(columns='tt').T
    cum_recovered = cum_recovered.drop(columns='tt').T
    cum_death = cum_death.drop(columns='tt').T
    return DateChecker(cum_conf, cum_recovered, cum_death)




def pull_sheet_data():
    print('Scraping Google Sheet data....')
    for i in sheet_data_list:
        sheet = client.open(i).sheet1
        result = sheet.get_all_records()
        if 'CONFIRMED' in i.split('_'):
            sheet_confirmed = pd.DataFrame(result)
        elif 'RECOVERY' in i.split('_'):
            sheet_recovered = pd.DataFrame(result)
        elif 'DEATH' in i.split('_'):
            sheet_death = pd.DataFrame(result)
    return sheet_confirmed, sheet_recovered, sheet_death




def checker(api_list, sheet_list, resolve=True):
    error = False
    tag = ['Confirmed', 'Recovered', 'Death']
    k = 0
    for x, y in zip(api_list, sheet_list):
        print(f'Checking errors for {tag[k]}')
        flag = 0
        column_index_api = {}
        for i, j in enumerate(x.columns):
            column_index_api[j] = i
        sheet_last_date = datetime.strftime(
            datetime.strptime(y.columns[-1], '%m/%d/%Y'), '%d-%b-%y')
        change_dict_list = []
        for i in x.index:
            for j in x.columns[:column_index_api[sheet_last_date]+1]:
                date = '{d.month}/{d.day}/{d.year}'.format(
                    d=datetime.strptime(j, "%d-%b-%y"))
                if i in list(y['CODE']):
                    if y[y['CODE'] == i][date].values[0] != "":
                        if (date != '3/14/2020') & (y[y['CODE'] == i]['STATE/UT'].values[0] != 'Kerala'):
                            if (date != '3/14/2020') & (y[y['CODE'] == i]['STATE/UT'].values[0] != 'Maharashtra'):
                                if x.loc[i, j] != y[y['CODE'] == i][date].values[0]:
                                    flag = 1
                                    error = True
                                    change_dict_list.append({'api_sheet': x.loc[i, j],
                                                         'google_sheet': y[y['CODE'] == i][date].values[0].item(),
                                                         'position': {
                                        'api': (i, j),
                                        'gsheet': (y['CODE'][y['CODE'] == i].index.tolist()[0]+2, list(y.columns).index(date)+1)
                                    },
                                        'State': y[y['CODE'] == i]['STATE/UT'].values[0],
                                        'Date':date})
        if flag == 1:
            print('Printing in a file...')
            with open(f'{tag[k]}_error.json', 'w') as f:
                json.dump(change_dict_list, f, indent=4)
        else:
            print(f'All values are ok for {tag[k]}')

        if resolve and flag==1:
            resolveData(dictionary=change_dict_list,name = sheet_data_list[k], api_client = client)
        k = k+1
    return error


def updater(skip=False, check_error=True):
    Confirmed, Recovered, Death = pull_api_data()
    sheet_confirmed, sheet_recovered, sheet_death = pull_sheet_data()
    api_data = [Confirmed, Recovered, Death]
    sheet_data = [sheet_confirmed, sheet_recovered, sheet_death]
    if check_error and skip:
        error = checker(api_data, sheet_data)
        for name in sheet_data_list:
            if 'CONFIRMED' in name.split('_'):
                sheet = client.open(name).sheet1
                code_list = list(sheet_confirmed['CODE'])
                days_diff = datetime.strptime(
                    Confirmed.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_confirmed.columns[-1], '%m/%d/%Y')
                if days_diff.days >= 0:
                    WriteonSheet(api_data=Confirmed, target_data=sheet_confirmed,
                                 target_sheet=sheet, diff=days_diff, code_list=code_list, tag='Confirmed')

            else:
                if 'RECOVERY' in name:
                    sheet = client.open(name).sheet1
                    code_list = list(sheet_recovered['CODE'])
                    days_diff = datetime.strptime(
                        Recovered.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_recovered.columns[-1], '%m/%d/%Y')
                    if days_diff.days >= 0:
                        WriteonSheet(api_data=Recovered, target_data=sheet_recovered,
                                     target_sheet=sheet, diff=days_diff, code_list=code_list, tag='Recovered')
                else:
                    sheet = client.open(name).sheet1
                    code_list = list(sheet_death['CODE'])
                    days_diff = datetime.strptime(
                        Death.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_death.columns[-1], '%m/%d/%Y')
                    if days_diff.days >= 0:
                        WriteonSheet(api_data=Death, target_data=sheet_death,
                                     target_sheet=sheet, diff=days_diff, code_list=code_list, tag='Deceased')
    elif check_error and skip == False:
        error = checker(api_data, sheet_data)
    elif check_error == False:
        api_data = [Confirmed, Recovered, Death]
        sheet_data = [sheet_confirmed, sheet_recovered, sheet_death]
        for name in sheet_data_list:
            if 'CONFIRMED' in name.split('_'):
                sheet = client.open(name).sheet1
                code_list = list(sheet_confirmed['CODE'])
                days_diff = datetime.strptime(
                    Confirmed.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_confirmed.columns[-1], '%m/%d/%Y')
                if days_diff.days >= 0:
                    WriteonSheet(api_data=Confirmed, target_data=sheet_confirmed,
                                 target_sheet=sheet, diff=days_diff, code_list=code_list, tag='Confirmed')
            else:
                if 'RECOVERY' in name:
                    sheet = client.open(name).sheet1
                    code_list = list(sheet_recovered['CODE'])
                    days_diff = datetime.strptime(
                        Recovered.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_recovered.columns[-1], '%m/%d/%Y')
                    if days_diff.days >= 0:
                        WriteonSheet(api_data=Recovered, target_data=sheet_recovered,
                                     target_sheet=sheet, diff=days_diff, code_list=code_list, tag='Recovered')
                else:
                    sheet = client.open(name).sheet1
                    code_list = list(sheet_death['CODE'])
                    days_diff = datetime.strptime(
                        Death.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_death.columns[-1], '%m/%d/%Y')
                    if days_diff.days >= 0:
                        WriteonSheet(api_data=Death, target_data=sheet_death,
                                     target_sheet=sheet, diff=days_diff, code_list=code_list, tag='Deceased')


def sheet_save():
    for name in sheet_data_list:
        sheet = client.open(name).sheet1
        result = sheet.get_all_records()
        df = pd.DataFrame(result)
        df.to_csv(f'{name}.csv', index=False)
    print('All google sheets are saved')


