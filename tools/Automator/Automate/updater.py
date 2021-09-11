# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 16:48:16 2021

@author: dript
"""

import pandas as pd
from .api_data_parser import getApiData
from .sheet_data_parser import getSheetData
from datetime import datetime

class Updater():
    def __init__(self,config_path):
        self.config = config_path
        
    def apiData(self):
        data = getApiData()
        return data()
    
    def sheetData(self):
        data,spread_obj = getSheetData().pull_data_sheet(self.config)
        return data,spread_obj
    
    def prepare_for_merge(self,api_data,sheet_data):
        sheet_cols_last = sheet_data.columns[-1]
        sheet_cols_last = datetime.strptime(sheet_cols_last,"%m/%d/%Y")
        if sheet_cols_last in api_data.columns:
            idx = list(api_data.columns).index(sheet_cols_last)
            if len(list(api_data.columns)[idx:]) > 1:
                new_col = api_data.iloc[:,idx+1:]
                new_col.columns = [i.strftime("%m/%d/%Y") for i in new_col.columns]
                new_col["CODE"] = api_data["CODE"]
                mer = pd.merge(sheet_data,new_col,on = "CODE",how='left')
                return mer.dropna(axis=0)
            else:
                return sheet_data
        else:
            raise Exception("Something Wrong Happended!!")                
        
    def __call__(self):
        print("Fetching API data....")
        api = self.apiData()
        print("Fetching API data done.")
        print("Fetching Google Sheet data....")
        sheet,objs = self.sheetData()
        print("Fetching Google Sheet data done.")
        
        print("Performing Update of Google Sheet...")
        res_dict = {}
        for api_data,sheet_data in zip(api,sheet):
            final_data = self.prepare_for_merge(api[api_data],sheet[sheet_data])
            if final_data.shape[1] > sheet[sheet_data].shape[1]:
                res_dict[api_data] = final_data
                obj = objs[api_data]
                print(f"Updating {api_data} Google Sheet...")
                obj.df_to_sheet(final_data,index = False,replace=True)
            else:
                print(f"Updating {api_data} Google Sheet is not required(already up-to-date)...")
            res_dict[api_data] = final_data
        print("Google Sheet Updating Done..")
        return res_dict
            
        
        
        