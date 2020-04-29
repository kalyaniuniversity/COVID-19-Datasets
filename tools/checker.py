import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import urllib, json
import pprint
pp = pprint.PrettyPrinter(width=41, compact=True)


scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('cred_sheet.json',scope)
client = gspread.authorize(creds)
sheet_list=['COVID19_INDIA_STATEWISE_TIME_SERIES_CONFIRMED','COVID19_INDIA_STATEWISE_TIME_SERIES_RECOVERY',
            'COVID19_INDIA_STATEWISE_TIME_SERIES_DEATH']
#json_url = urllib.request.urlopen('https://api.covid19india.org/v2/state_district_wise.json')
#data_district=json.loads(json_url.read())

def checker(dataset_api,dataset_sheet,tag):
    flag=0
    change_dict={}
    for i in dataset_api.index:
        for j in dataset_api.columns[:-1]:
            date='{d.month}/{d.day}/{d.year}'.format(d=datetime.strptime(j,"%d-%b-%y"))
            #date=datetime.strftime(datetime.strptime(j,"%d-%b-%y"),'%m/%d/%Y')
            if dataset_api.loc[i,j] != dataset_sheet[dataset_sheet['CODE']==i][date].values[0]:
                flag=1
                change_dict[(date,dataset_sheet[dataset_sheet['CODE']==i]['STATE/UT'].values[0])]={'api_sheet':dataset_api.loc[i,j],
                                                                                            'google_sheet':dataset_sheet[dataset_sheet['CODE']==i][date].values[0]}
    if flag == 0:
        print(f'All values are ok for {tag}')
    return change_dict

def pull_api_dataset(url,of):
    json_url = urllib.request.urlopen(url)
    data = json.loads(json_url.read())
    states_daily=data['states_daily']
    df=pd.DataFrame(states_daily)
    df.index=df['date'].drop(columns=['date'])
    df=df.drop(columns=['date'])
    df=df.replace(to_replace = '', value = 0)
    for i in df.columns:
        try:
            df[i]=df[i].astype(int)
        except:
            continue
    cum=df[df['status']==of.title()].drop(columns=['status']).cumsum()
    cum_1=cum.drop(columns='tt').T
    return cum_1

def pull_sheet_dataset(of):
    sheet = client.open(of).sheet1
    result = sheet.get_all_records()
    dataset=pd.DataFrame(result)
    return dataset
                
if __name__ =='__main__':
    for name in sheet_list:
        if 'CONFIRMED' in name.split('_'):
            dataset_conf_api=pull_api_dataset('https://api.covid19india.org/states_daily.json','confirmed')
            dataset_conf_sheet=pull_sheet_dataset(of=name)
            change_conf_dict=checker(dataset_conf_api, dataset_conf_sheet, tag='confirmed')
            print('#################################################################')
            print('\tConfirmed changes')
            print('#################################################################')
            pp.pprint(change_conf_dict)
        elif 'RECOVERY' in name.split('_'):
            dataset_recover_api=pull_api_dataset('https://api.covid19india.org/states_daily.json','recovered')
            dataset_recover_sheet=pull_sheet_dataset(of=name)
            change_recover_dict=checker(dataset_recover_api, dataset_recover_sheet, tag='recovered')
            print('#################################################################')
            print('\tRecovery changes')
            print('#################################################################')
            pp.pprint(change_recover_dict)
        else:
            dataset_death_api=pull_api_dataset('https://api.covid19india.org/states_daily.json','Deceased')
            dataset_death_sheet=pull_sheet_dataset(of=name)
            change_death_dict=checker(dataset_death_api, dataset_death_sheet, tag='deceased')
            print('#################################################################')
            print('\tDeath changes')
            print('#################################################################')
            pp.pprint(change_death_dict)