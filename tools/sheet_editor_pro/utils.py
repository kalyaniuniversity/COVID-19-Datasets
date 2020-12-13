from datetime import datetime
import time
from dateutil import parser
from tqdm import tqdm

def DateChecker(*args, **kwargs):
    sheet_list = []
    for sheet in args:
        col_dates = list(sheet.columns)
        for date in col_dates:
            newdate = parser.parse(date)
            col_dates[col_dates.index(date)] = newdate.strftime("%d-%b-%y")
        sheet.columns = col_dates
        sheet_list.append(sheet)
    return sheet_list


def blankChecker(func):
    def inner(*args, **kwargs):
        target_data = kwargs['target_data']
        api_data = kwargs['api_data']
        target_sheet = kwargs['target_sheet']
        code_list = kwargs['code_list']
        k = kwargs['diff'].days
        if '' in list(target_data[target_data.columns[-1]]):
            print(
                f'All fields are not filled for {kwargs["tag"]} filling that up')
            val = []
            i = 0
            while i < target_data.shape[0] + 1:
                try:
                    if i == 0:
                        value = datetime.strftime(datetime.strptime(
                            api_data.columns[-(k+1)], '%d-%b-%y'), '%m/%d/%Y')
                        target_sheet.update_cell(
                            i+1, target_data.shape[1], value)
                    else:
                        if i != target_data.shape[0]:
                            value = int(
                                api_data[api_data.columns[-(k+1)]][code_list[i-1]])
                            target_sheet.update_cell(
                                i+1, target_data.shape[1], value)
                            val.append(value)
                        else:
                            value = sum(val)
                            target_sheet.update_cell(
                                i + 1, target_data.shape[1], value)
                    i = i+1
                except:
                    for x in tqdm(range(100)):
                        time.sleep(1)
        if k > 0:
            func(api_data, target_data, target_sheet, kwargs['diff'], code_list, kwargs["tag"])
        else:
            print(f"{kwargs['tag']} google sheet is up to date")
    return inner


@blankChecker
def WriteonSheet(api_data, target_data, target_sheet, diff, code_list,tag):
    api_updated_date = datetime.strftime(datetime.strptime(
        api_data.columns[-1], '%d-%b-%y'), '%m/%d/%Y')
    sheet_updated_date = target_data.columns[-1]
    if api_updated_date != sheet_updated_date:
        print(
            f'{tag} Google Sheet will be updated till {api_updated_date}')
        target_sheet.add_cols(diff.days)
        k = diff.days
        for j in range(diff.days):
            val = []
            i=0
            while i < target_data.shape[0] + 1:
                try:
                    if i == 0:
                        value = datetime.strftime(datetime.strptime(
                            api_data.columns[-(k-j)], '%d-%b-%y'), '%m/%d/%Y')
                        target_sheet.update_cell(
                            i+1, target_data.shape[1]+(j+1), value)
                    else:
                        if i != target_data.shape[0]:
                            value = int(
                                api_data[api_data.columns[-(k-j)]][code_list[i-1]])
                            target_sheet.update_cell(
                                i+1, target_data.shape[1]+j+1, value)
                            val.append(value)
                        else:
                            value = sum(val)
                            target_sheet.update_cell(
                                i + 1, target_data.shape[1] + j + 1, value)
                    i = i + 1
                except:
                    for x in tqdm(range(100)):
                        time.sleep(1)
        print(f'{tag} Google Sheet is updated till {api_updated_date}')



def resolveData(dictionary, name, api_client):
    print(f'Resolving {name}')
    sheet = api_client.open(name).sheet1
    i = 0
    while i < len(dictionary):
        value = dictionary[i]['api_sheet']
        sheet_row = dictionary[i]['position']['gsheet'][0]
        sheet_col = dictionary[i]['position']['gsheet'][1]
        try:
            sheet.update_cell(sheet_row, sheet_col, value)
            i = i + 1
        except:
            for x in tqdm(range(100)):
                time.sleep(1)
    print(f'Resolving of {name} is done.')


