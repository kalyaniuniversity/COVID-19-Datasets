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
pp = pprint.PrettyPrinter(width=41, compact=True)


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'cred_sheet.json', scope)
client = gspread.authorize(creds)
sheet_list = ['COVID19_INDIA_STATEWISE_TIME_SERIES_CONFIRMED', 'COVID19_INDIA_STATEWISE_TIME_SERIES_RECOVERY',
              'COVID19_INDIA_STATEWISE_TIME_SERIES_DEATH']


def pull_api_data(url='https://api.covid19india.org/states_daily.json'):
    global pull_counter
    pull_counter = 0
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
    return cum_conf, cum_recovered, cum_death

# Confirmed,Recovered,Death=pull_api_data()


def pull_sheet_data():
    global pull_counter
    for i in sheet_list:
        sheet = client.open(i).sheet1
        result = sheet.get_all_records()
        pull_counter = pull_counter+1
        if 'CONFIRMED' in i.split('_'):
            sheet_confirmed = pd.DataFrame(result)
        elif 'RECOVERY' in i.split('_'):
            sheet_recovered = pd.DataFrame(result)
        elif 'DEATH' in i.split('_'):
            sheet_death = pd.DataFrame(result)
    return sheet_confirmed, sheet_recovered, sheet_death

# sheet_confirmed,sheet_recovered,sheet_death=pull_sheet_data()


def checker(api_list, sheet_list):
    global pull_counter
    error = False
    tag = ['Confirmed', 'Recovered', 'Death']
    k = 0
    for x, y in zip(api_list, sheet_list):
        flag = 0
        column_index_api = {}
        for i, j in enumerate(x.columns):
            column_index_api[j] = i
        sheet_last_date = datetime.strftime(
            datetime.strptime(y.columns[-1], '%m/%d/%Y'), '%d-%b-%y')
        change_dict = {}
        for i in x.index:
            for j in x.columns[:column_index_api[sheet_last_date]+1]:
                # print(i)
                date = '{d.month}/{d.day}/{d.year}'.format(
                    d=datetime.strptime(j, "%d-%b-%y"))
                # date=datetime.strftime(datetime.strptime(j,"%d-%b-%y"),'%m/%d/%Y')
                if (date != '3/14/2020') & (y[y['CODE'] == i]['STATE/UT'].values[0] != 'Kerala'):
                    if (date != '3/14/2020') & (y[y['CODE'] == i]['STATE/UT'].values[0] != 'Maharashtra'):
                        if x.loc[i, j] != y[y['CODE'] == i][date].values[0]:
                            flag = 1
                            error = True
                            change_dict[(date, y[y['CODE'] == i]['STATE/UT'].values[0])] = {'api_sheet': x.loc[i, j],
                                                                                            'google_sheet': y[y['CODE'] == i][date].values[0]}
        if flag == 1:
            print('#################################################################')
            print(f'\t{tag[k]} changes')

            print('#################################################################')
            pp.pprint(change_dict)
            print('#################################################################\n')
        else:
            print(f'All values are ok for {tag[k]}')
        k = k+1
    return error


def updater(skip=False):
    global pull_counter
    Confirmed, Recovered, Death = pull_api_data()
    sheet_confirmed, sheet_recovered, sheet_death = pull_sheet_data()
    api_data = [Confirmed, Recovered, Death]
    sheet_data = [sheet_confirmed, sheet_recovered, sheet_death]
    error = checker(api_data, sheet_data)
    if skip == True:
        for name in sheet_list:
            if 'CONFIRMED' in name.split('_'):
                sheet = client.open(name).sheet1
                code_list = list(sheet_confirmed['CODE'])
                days_diff = datetime.strptime(
                    Confirmed.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_confirmed.columns[-1], '%m/%d/%Y')
                if days_diff.days > 0:
                    api_updated_date = datetime.strftime(datetime.strptime(
                        Confirmed.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                    sheet_updated_date = sheet_confirmed.columns[-1]
                    if api_updated_date != sheet_updated_date:
                        print(
                            f'Confirmed Google Sheet will be updated till {api_updated_date}')
                        sheet.add_cols(days_diff.days)
                        k = days_diff.days
                        for j in range(days_diff.days):
                            val = []
                            for i in range(sheet_confirmed.shape[0]+1):
                                if i == 0:
                                    value = datetime.strftime(datetime.strptime(
                                        Confirmed.columns[-k], '%d-%b-%y'), '%m/%d/%Y')
                                    sheet.update_cell(
                                        i+1, sheet_confirmed.shape[1]+j+1, value)
                                    pull_counter = pull_counter+1

                                else:
                                    if i != sheet_confirmed.shape[0]:
                                        value = int(
                                            Confirmed[Confirmed.columns[-k]][code_list[i-1]])
                                        sheet.update_cell(
                                            i+1, sheet_confirmed.shape[1]+j+1, value)
                                        val.append(value)
                                        pull_counter = pull_counter+1
                                    else:
                                        value = sum(val)
                                        sheet.update_cell(
                                            i+1, sheet_confirmed.shape[1]+j+1, value)
                                        pull_counter = pull_counter+1
                            if j != days_diff.days-1:
                                if pull_counter+38 >= 100:
                                    for x in range(100):
                                        b = f"Wait for 100s: {x}"
                                        print(b, end="\r")
                                        time.sleep(1)
                                    pull_counter = 0
                            if k != 0:
                                k = k-1
                            else:
                                break
                        print(f'Update done for {name}')
                        if pull_counter+39 >= 100:
                            for x in range(100):
                                b = f"Wait for 100s: {x}"
                                print(b, end="\r")
                                time.sleep(1)
                            pull_counter = 0
                else:
                    if '' in list(sheet_confirmed[sheet_confirmed.columns[-1]]):
                        print(
                            f'Dates are up-to-date but all fields are not filled... filling that up')
                        val = []
                        for i in range(sheet_confirmed.shape[0]+1):
                            if i == 0:
                                value = datetime.strftime(datetime.strptime(
                                    Confirmed.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                                sheet.update_cell(
                                    i+1, sheet_confirmed.shape[1], value)
                                pull_counter = pull_counter+1
                            else:
                                if i != sheet_confirmed.shape[0]:
                                    value = int(
                                        Confirmed[Confirmed.columns[-1]][code_list[i-1]])
                                    sheet.update_cell(
                                        i+1, sheet_confirmed.shape[1], value)
                                    val.append(value)
                                    pull_counter = pull_counter+1
                                else:
                                    value = sum(val)
                                    sheet.update_cell(
                                        i+1, sheet_confirmed.shape[1], value)
                                    pull_counter = pull_counter+1
                        print(f'Update done for {name}')
                        if pull_counter+39 >= 100:
                            for x in range(100):
                                b = f"Wait for 100s: {x}"
                                print(b, end="\r")
                                time.sleep(1)
                            pull_counter = 0
                    else:
                        print(f'No update Required for {name}')

            else:
                # r_pull_counter=pull_counter
                if 'RECOVERY' in name:
                    # print(pull_counter)
                    sheet = client.open(name).sheet1
                    code_list = list(sheet_recovered['CODE'])
                    days_diff = datetime.strptime(
                        Recovered.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_recovered.columns[-1], '%m/%d/%Y')
                    if days_diff.days > 0:
                        api_updated_date = datetime.strftime(datetime.strptime(
                            Recovered.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                        sheet_updated_date = sheet_recovered.columns[-1]
                        if api_updated_date != sheet_updated_date:
                            print(
                                f'Recovery Google Sheet will be updated till {api_updated_date}')
                            sheet.add_cols(days_diff.days)
                            k = days_diff.days

                            for j in range(days_diff.days):
                                val = []
                                for i in range(sheet_recovered.shape[0]+1):
                                    if i == 0:
                                        value = datetime.strftime(datetime.strptime(
                                            Recovered.columns[-k], '%d-%b-%y'), '%m/%d/%Y')
                                        sheet.update_cell(
                                            i+1, sheet_recovered.shape[1]+j+1, value)
                                        pull_counter = pull_counter+1
                                    else:
                                        if i != sheet_recovered.shape[0]:
                                            value = int(
                                                Recovered[Recovered.columns[-k]][code_list[i-1]])
                                            sheet.update_cell(
                                                i+1, sheet_recovered.shape[1]+j+1, value)
                                            val.append(value)
                                            pull_counter = pull_counter+1
                                        else:
                                            value = sum(val)
                                            sheet.update_cell(
                                                i+1, sheet_recovered.shape[1]+j+1, value)
                                            pull_counter = pull_counter+1
                                if j != days_diff.days-1:
                                    if pull_counter+38 >= 100:
                                        for x in range(100):
                                            b = f"Wait for 100s: {x}"
                                            print(b, end="\r")
                                            time.sleep(1)
                                        pull_counter = 0
                                if k != 0:
                                    k = k-1
                                else:
                                    break
                            print(f'Update done for {name}')
                            if pull_counter+38 >= 100:
                                for x in range(100):
                                    b = f"Wait for 100s: {x}"
                                    print(b, end="\r")
                                    time.sleep(1)
                                pull_counter = 0
                    else:
                        if '' in list(sheet_recovered[sheet_recovered.columns[-1]]):
                            print(
                                f'Dates are up-to-date but all fields are not filled... filling that up')
                            val = []
                            for i in range(sheet_recovered.shape[0]+1):
                                if i == 0:
                                    value = datetime.strftime(datetime.strptime(
                                        Recovered.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                                    sheet.update_cell(
                                        i+1, sheet_recovered.shape[1], value)
                                    pull_counter = pull_counter+1
                                else:
                                    if i != sheet_recovered.shape[0]:
                                        value = int(
                                            Recovered[Recovered.columns[-1]][code_list[i-1]])
                                        sheet.update_cell(
                                            i+1, sheet_recovered.shape[1], value)
                                        val.append(value)
                                        pull_counter = pull_counter+1
                                    else:
                                        value = sum(val)
                                        sheet.update_cell(
                                            i+1, sheet_recovered.shape[1], value)
                                        pull_counter = pull_counter+1
                            print(f'Update done for {name}')
                            if pull_counter+38 >= 100:
                                for x in range(100):
                                    b = f"Wait for 100s: {x}"
                                    print(b, end="\r")
                                    time.sleep(1)
                                pull_counter = 0
                        else:
                            print(f'No update Required for {name}')
                else:
                    # d_pull_counter=pull_counter
                    sheet = client.open(name).sheet1
                    code_list = list(sheet_death['CODE'])
                    days_diff = datetime.strptime(
                        Death.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_death.columns[-1], '%m/%d/%Y')
                    if days_diff.days > 0:
                        api_updated_date = datetime.strftime(
                            datetime.strptime(Death.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                        sheet_updated_date = sheet_death.columns[-1]
                        if api_updated_date != sheet_updated_date:
                            print(
                                f'Deceased Google Sheet will be updated till {api_updated_date}')
                            sheet.add_cols(days_diff.days)
                            k = days_diff.days
                            for j in range(days_diff.days):
                                val = []
                                for i in range(sheet_death.shape[0]+1):
                                    if i == 0:
                                        value = datetime.strftime(datetime.strptime(
                                            Death.columns[-k], '%d-%b-%y'), '%m/%d/%Y')
                                        sheet.update_cell(
                                            i+1, sheet_death.shape[1]+j+1, value)
                                        pull_counter = pull_counter+1
                                    else:
                                        if i != sheet_death.shape[0]:
                                            value = int(
                                                Death[Death.columns[-k]][code_list[i-1]])
                                            sheet.update_cell(
                                                i+1, sheet_death.shape[1]+j+1, value)
                                            val.append(value)
                                            pull_counter = pull_counter+1
                                        else:
                                            value = sum(val)
                                            sheet.update_cell(
                                                i+1, sheet_death.shape[1]+j+1, value)
                                            pull_counter = pull_counter+1
                                if j != days_diff.days-1:
                                    if pull_counter+38 >= 100:
                                        for x in range(100):
                                            b = f"Wait for 100s: {x}"
                                            print(b, end="\r")
                                            time.sleep(1)
                                        pull_counter = 0
                                if k != 0:
                                    k = k-1
                                else:
                                    break
                            print(f'Update done for {name}')

                    else:
                        if '' in list(sheet_death[sheet_death.columns[-1]]):
                            print(
                                f'Dates are up-to-date but all fields are not filled... filling that up')
                            val = []
                            for i in range(sheet_death.shape[0]+1):
                                if i == 0:
                                    value = datetime.strftime(datetime.strptime(
                                        Death.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                                    sheet.update_cell(
                                        i+1, sheet_death.shape[1], value)
                                    pull_counter = pull_counter+1
                                else:
                                    if i != sheet_death.shape[0]:
                                        value = int(
                                            Death[Death.columns[-1]][code_list[i-1]])
                                        sheet.update_cell(
                                            i+1, sheet_death.shape[1], value)
                                        val.append(value)
                                        pull_counter = pull_counter+1
                                    else:
                                        value = sum(val)
                                        sheet.update_cell(
                                            i+1, sheet_death.shape[1], value)
                                        pull_counter = pull_counter+1
                            print(f'Update done for {name}')

                        else:
                            print(f'No update Required for {name}')

    else:
        if error == False:
            for name in sheet_list:
                if 'CONFIRMED' in name.split('_'):
                    sheet = client.open(name).sheet1
                    code_list = list(sheet_confirmed['CODE'])
                    days_diff = datetime.strptime(
                        Confirmed.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_confirmed.columns[-1], '%m/%d/%Y')
                    if days_diff.days > 0:
                        api_updated_date = datetime.strftime(datetime.strptime(
                            Confirmed.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                        sheet_updated_date = sheet_confirmed.columns[-1]
                        if api_updated_date != sheet_updated_date:
                            print(
                                f'Google Sheet will be updated till {api_updated_date}')
                            sheet.add_cols(days_diff.days)
                            k = days_diff.days
                            for j in range(days_diff.days):
                                val = []
                                for i in range(sheet_confirmed.shape[0]+1):
                                    if i == 0:
                                        value = datetime.strftime(datetime.strptime(
                                            Confirmed.columns[-k], '%d-%b-%y'), '%m/%d/%Y')
                                        sheet.update_cell(
                                            i+1, sheet_confirmed.shape[1]+j+1, value)
                                        pull_counter = pull_counter+1
                                    else:
                                        if i != sheet_confirmed.shape[0]:
                                            value = int(
                                                Confirmed[Confirmed.columns[-k]][code_list[i-1]])
                                            sheet.update_cell(
                                                i+1, sheet_confirmed.shape[1]+j+1, value)
                                            val.append(value)
                                            pull_counter = pull_counter+1
                                        else:
                                            value = sum(val)
                                            sheet.update_cell(
                                                i+1, sheet_confirmed.shape[1]+j+1, value)
                                            pull_counter = pull_counter+1
                                if j != days_diff.days-1:
                                    if pull_counter+38 >= 100:
                                        for x in range(100):
                                            b = f"Wait for 100s: {x}"
                                            print(b, end="\r")
                                            time.sleep(1)
                                        pull_counter = 0
                                if k != 0:
                                    k = k-1
                                else:
                                    break
                            print(f'Update done for {name}')
                            if pull_counter+38 >= 100:
                                for x in range(100):
                                    b = f"Wait for 100s: {x}"
                                    print(b, end="\r")
                                    time.sleep(1)
                                pull_counter = 0
                    else:
                        if '' in list(sheet_confirmed[sheet_confirmed.columns[-1]]):
                            print(
                                f'Dates are up-to-date but all fields are not filled... filling that up')
                            val = []
                            for i in range(sheet_confirmed.shape[0]+1):
                                if i == 0:
                                    value = datetime.strftime(datetime.strptime(
                                        Confirmed.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                                    sheet.update_cell(
                                        i+1, sheet_confirmed.shape[1], value)
                                    pull_counter = pull_counter+1
                                else:
                                    if i != sheet_confirmed.shape[0]:
                                        value = int(
                                            Confirmed[Confirmed.columns[-1]][code_list[i-1]])
                                        sheet.update_cell(
                                            i+1, sheet_confirmed.shape[1], value)
                                        val.append(value)
                                        pull_counter = pull_counter+1
                                    else:
                                        value = sum(val)
                                        sheet.update_cell(
                                            i+1, sheet_confirmed.shape[1], value)
                                        pull_counter = pull_counter+1
                            print(f'Update done for {name}')
                            if pull_counter+38 >= 100:
                                for x in range(100):
                                    b = f"Wait for 100s: {x}"
                                    print(b, end="\r")
                                    time.sleep(1)
                                pull_counter = 0
                        else:
                            print(f'No update Required for {name}')

                else:
                    if 'RECOVERY' in name:
                        # r_pull_counter=pull_counter
                        sheet = client.open(name).sheet1
                        code_list = list(sheet_recovered['CODE'])
                        days_diff = datetime.strptime(
                            Recovered.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_recovered.columns[-1], '%m/%d/%Y')
                        if days_diff.days > 0:
                            api_updated_date = datetime.strftime(datetime.strptime(
                                Recovered.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                            sheet_updated_date = sheet_recovered.columns[-1]
                            if api_updated_date != sheet_updated_date:
                                print(
                                    f'Recovery Google Sheet will be updated till {api_updated_date}')
                                sheet.add_cols(days_diff.days)
                                k = days_diff.days
                                for j in range(days_diff.days):
                                    val = []
                                    for i in range(sheet_recovered.shape[0]+1):
                                        if i == 0:
                                            value = datetime.strftime(datetime.strptime(
                                                Recovered.columns[-k], '%d-%b-%y'), '%m/%d/%Y')
                                            sheet.update_cell(
                                                i+1, sheet_recovered.shape[1]+j+1, value)
                                            pull_counter = pull_counter+1
                                        else:
                                            if i != sheet_recovered.shape[0]:
                                                value = int(
                                                    Recovered[Recovered.columns[-k]][code_list[i-1]])
                                                sheet.update_cell(
                                                    i+1, sheet_recovered.shape[1]+j+1, value)
                                                val.append(value)
                                                pull_counter = pull_counter+1
                                            else:
                                                value = sum(val)
                                                sheet.update_cell(
                                                    i+1, sheet_recovered.shape[1]+j+1, value)
                                                pull_counter = pull_counter+1
                                    if j != days_diff.days-1:
                                        if pull_counter+38 >= 100:
                                            for x in range(100):
                                                b = f"Wait for 100s: {x}"
                                                print(b, end="\r")
                                                time.sleep(1)
                                            pull_counter = 0
                                    if k != 0:
                                        k = k-1
                                    else:
                                        break
                                print(f'Update done for {name}')
                                if pull_counter+38 >= 100:
                                    for x in range(100):
                                        b = f"Wait for 100s: {x}"
                                        print(b, end="\r")
                                        time.sleep(1)
                                    pull_counter = 0
                        else:
                            if '' in list(sheet_recovered[sheet_recovered.columns[-1]]):
                                print(
                                    f'Dates are up-to-date but all fields are not filled... filling that up')
                                val = []
                                for i in range(sheet_recovered.shape[0]+1):
                                    if i == 0:
                                        value = datetime.strftime(datetime.strptime(
                                            Recovered.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                                        sheet.update_cell(
                                            i+1, sheet_recovered.shape[1], value)
                                        pull_counter = pull_counter+1
                                    else:
                                        if i != sheet_recovered.shape[0]:
                                            value = int(
                                                Recovered[Recovered.columns[-1]][code_list[i-1]])
                                            sheet.update_cell(
                                                i+1, sheet_recovered.shape[1], value)
                                            val.append(value)
                                            pull_counter = pull_counter+1
                                        else:
                                            value = sum(val)
                                            sheet.update_cell(
                                                i+1, sheet_recovered.shape[1], value)
                                            pull_counter = pull_counter+1
                                print(f'Update done for {name}')
                                if pull_counter+38 >= 100:
                                    for x in range(100):
                                        b = f"Wait for 100s: {x}"
                                        print(b, end="\r")
                                        time.sleep(1)
                                    pull_counter = 0
                            else:
                                print(f'No update Required for {name}')
                    else:
                        # d_pull_counter=pull_counter
                        sheet = client.open(name).sheet1
                        code_list = list(sheet_death['CODE'])
                        days_diff = datetime.strptime(
                            Death.columns[-1], '%d-%b-%y')-datetime.strptime(sheet_death.columns[-1], '%m/%d/%Y')
                        if days_diff.days > 0:
                            api_updated_date = datetime.strftime(
                                datetime.strptime(Death.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                            sheet_updated_date = sheet_death.columns[-1]
                            if api_updated_date != sheet_updated_date:
                                print(
                                    f'Google Sheet will be updated till {api_updated_date}')
                                sheet.add_cols(days_diff.days)
                                k = days_diff.days
                                for j in range(days_diff.days):
                                    val = []
                                    for i in range(sheet_death.shape[0]+1):
                                        if i == 0:
                                            value = datetime.strftime(datetime.strptime(
                                                Death.columns[-k], '%d-%b-%y'), '%m/%d/%Y')
                                            sheet.update_cell(
                                                i+1, sheet_death.shape[1]+j+1, value)
                                            pull_counter = pull_counter+1
                                        else:
                                            if i != sheet_death.shape[0]:
                                                value = int(
                                                    Death[Death.columns[-k]][code_list[i-1]])
                                                sheet.update_cell(
                                                    i+1, sheet_death.shape[1]+j+1, value)
                                                val.append(value)
                                                pull_counter = pull_counter+1
                                            else:
                                                value = sum(val)
                                                sheet.update_cell(
                                                    i+1, sheet_death.shape[1]+j+1, value)
                                                pull_counter = pull_counter+1
                                    if j != days_diff.days-1:
                                        if pull_counter+38 >= 100:
                                            for x in range(100):
                                                b = f"Wait for 100s: {x}"
                                                print(b, end="\r")
                                                time.sleep(1)
                                            pull_counter = 0
                                    if k != 0:
                                        k = k-1
                                    else:
                                        break
                                print(f'Update done for {name}')

                        else:
                            if '' in list(sheet_death[sheet_death.columns[-1]]):
                                print(
                                    f'Dates are up-to-date but all fields are not filled... filling that up')
                                val = []
                                for i in range(sheet_death.shape[0]+1):
                                    if i == 0:
                                        value = datetime.strftime(datetime.strptime(
                                            Death.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
                                        sheet.update_cell(
                                            i+1, sheet_death.shape[1], value)
                                        pull_counter = pull_counter+1
                                    else:
                                        if i != sheet_death.shape[0]:
                                            value = int(
                                                Death[Death.columns[-1]][code_list[i-1]])
                                            sheet.update_cell(
                                                i+1, sheet_death.shape[1], value)
                                            val.append(value)
                                            pull_counter = pull_counter+1
                                        else:
                                            value = sum(val)
                                            sheet.update_cell(
                                                i+1, sheet_death.shape[1], value)
                                            pull_counter = pull_counter+1
                                print(f'Update done for {name}')

                            else:
                                print(f'No update Required for {name}')

        else:
            pass


def sheet_save():
    for name in sheet_list:
        sheet = client.open(name).sheet1
        result = sheet.get_all_records()
        df = pd.DataFrame(result)
        df.to_csv(f'{name}.csv', index=False)
    print('All google sheets are saved')

