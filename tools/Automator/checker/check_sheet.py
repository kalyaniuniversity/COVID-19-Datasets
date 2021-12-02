# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 13:59:42 2021

@author: dript
"""

import pandas as pd
from Automate.api_data_parser import getApiData
from Automate.sheet_data_parser import getSheetData 
from datetime import datetime,timedelta
import logging

class SheetChecker():
    def __init__(self,auth_token,days = 10):
        self.auth = auth_token
        self.days = days
        
    def logger(self, massage):
        logging.basicConfig(filename="stdOut_Checker.log",
                            format='%(asctime)s %(message)s',
                            filemode='a',
                            level=logging.INFO)

        logging.info(massage)
        
    def CollectApiData(self):
        print("Fetching API data..",end="")
        data = getApiData()
        api_data = data()
        print("done.")
        return api_data
    
    def CollectSheetData(self):
        print("Fetching Sheet data..",end="")
        data, spread_obj = getSheetData().pull_data_sheet(self.auth)
        print("done.")
        return data, spread_obj
    
    def CollectLastDaysData(self,data_sheet,last_base = None):
        base = data_sheet.columns[-1]
        if last_base != None:
            base = last_base
        
        last_days = [base - timedelta(days = x) for x in range(self.days)]
        
        last_days.reverse()
        #print(data_sheet['12/01/2021'])
        
        last_days_data = data_sheet[last_days]
        last_days_data.index = data_sheet["CODE"]
        return last_days_data
    
    
    #helper function to change the dates of sheet data in datetime format
    def ConvertDatesSheet(self,sheet_data):
        cols = []
        for i in sheet_data.columns:
            try:
                d_col = datetime.strptime(i,"%m/%d/%Y")
                cols.append(d_col)
            except:
                cols.append(i)
        sheet_data.columns = cols
        return sheet_data
    
    #helper function to change the dates of sheet data in string format
    def ConvertDatesSheetString(self,sheet_data):
        cols = []
        for i in sheet_data.columns:
            try:
                d_col = datetime.strftime(i,"%m/%d/%Y")
                cols.append(d_col)
            except:
                cols.append(i)
        sheet_data.columns = cols
        return sheet_data
            
    
    def CompareData(self,api,sheet,key):
        last_day_api = self.CollectLastDaysData(api,
                                                last_base=sheet.columns[-1])
        last_day_api_temp = last_day_api.sort_index()
        last_day_sheet = self.CollectLastDaysData(sheet)
        last_day_sheet_temp = last_day_sheet.sort_index()
        
        #last_day_sheet_temp.columns = [datetime.strptime(x,"%m/%d/%Y") for x in last_day_sheet_temp.columns]
        compare_bool = last_day_sheet_temp.astype(int) == last_day_api_temp
        hasChange = False
        for x in compare_bool.columns:
            if (compare_bool[x] == True).all() == False:
                hasChange = True
                print("Value Mismatch Found. Please refer `stdOut_Checker.log` file.")
                states = list(compare_bool[x][compare_bool[x] == False].index)
                if 'tt' in states:
                    states.remove('tt')
                self.logger(f"Values mismatched while checking for state {','.join(states)} at {x.strftime('%m/%d/%Y')} while updating {key}")
                last_day_sheet[x] = last_day_api[x]
                
        if hasChange:
            print(f"Value mismatch found. Patching it for {key}..")
        else:
            print(f"No Value mismatch found in {key}..")
                
        return last_day_sheet,hasChange
                
        
        
    
    def CompareDataLoop(self):
        api_data = self.CollectApiData()
        sheet_data,objs = self.CollectSheetData()
        
        return_sheets = {}
        for tag_api,tag_sheet in zip(api_data,sheet_data):
            print(f"Checking data for {tag_sheet} for last {self.days} days...")
            compare_last,hasChange = self.CompareData(api_data[tag_api],self.ConvertDatesSheet(sheet_data[tag_sheet]),key = tag_sheet)
            tag_sheet_data = sheet_data[tag_sheet]
            if hasChange:
                tag_sheet_data[list(compare_last.columns)] = compare_last.values.astype(int)
                objs[tag_sheet].df_to_sheet(self.ConvertDatesSheetString(tag_sheet_data), index=False, replace=True)
            return_sheets[tag_sheet] = tag_sheet_data
        print("All Checks Done..")
        return return_sheets
            
        
        
        
        
        
        
        
        
