# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 16:48:16 2021

@author: dript
"""

'''
This file will be triggered to pull API data and Google Sheet data
and check if any new date there or not. Then merge new date if 
available.

'''




import pandas as pd
from .api_data_parser import getApiData
from .sheet_data_parser import getSheetData
from datetime import datetime
import logging


class Updater():
    def __init__(self, config_path):
        self.config = config_path

    def apiData(self):
        """This pull the API data from https://data.covid19bharat.org/v4/min/timeseries.min.json

        Returns:
            dict: Gives a Dict in following format
            '{
              "confirmed":DataFrame,
              "recovered":DataFrame,
              "deceased":DataFrame  
            }'
        """
        data = getApiData()
        return data()

    def sheetData(self):
        """This pull the Google Sheet data

        Returns:
            dict: Gives a Dict in following format
            '{
              "confirmed":DataFrame,
              "recovered":DataFrame,
              "deceased":DataFrame  
            }'
        """
        data, spread_obj = getSheetData().pull_data_sheet(self.config)
        return data, spread_obj

    def logger(self, massage):
        """Helper function to log any massage

        Args:
            massage (str): The massage that has to be logged
        """
        logging.basicConfig(filename="stdOut.log",
                            format='%(asctime)s %(message)s',
                            filemode='a',
                            level=logging.INFO)

        logging.info(massage)

    def Validator(self, new_frame, key):
        """Validate the data whether current date values 
            are greater than previous data values or not

        Args:
            new_frame (DataFrame): The new data with new dates
            key (str): A value among ["confirmed","deceased","recovered"]

        Returns:
            bool: If any new date value less than previous data returns False.
        """
        new_frame = new_frame.set_index("CODE")
        new_frame = new_frame.astype(int)

        def getName(d1, d2):
            tally = new_frame[d1] <= new_frame[d2]
            name = tally[tally == False].index[0]
            return name
        haserror = False
        col_list = new_frame.columns
        for idx, val in enumerate(col_list):
            if idx > 0:
                if (new_frame[col_list[idx - 1]] <= new_frame[col_list[idx]]).all() != True:
                    haserror = True
                    print(f"Data integrity error found for {key} check 'stdOut.log' file.")
                    self.logger(
                        f"Data Integrity Error b/w {col_list[idx - 1]} and {col_list[idx]} at {getName(col_list[idx - 1],col_list[idx])} for updating {key}")
        if haserror == True:
            return True    # Toggle this to False if don't want to update when value is less than previous day
        return True

    def prepare_for_merge(self, api_data, sheet_data, key):
        """Prepare the new data for merging with old data.

        Args:
            api_data (DataFrame): The data pull from API    
            sheet_data (DataFrame): The data pulled from Google Sheet
            key (str): A value among ["confirmed","deceased","recovered"]

        Raises:
            Exception: If last updated date is not specified in API data then
            it raises an exception.

        Returns:
            DataFrame: If new date is available the new merged data will be returned.
            Otherwise old data is returned.
        """
        sheet_cols_last = sheet_data.columns[-1]
        sheet_cols_last = datetime.strptime(sheet_cols_last, "%m/%d/%Y")
        #print(api_data.columns)
        if sheet_cols_last in api_data.columns:
            idx = list(api_data.columns).index(sheet_cols_last)
            if len(list(api_data.columns)[idx:]) > 1:
                new_col = api_data.iloc[:, idx+1:].astype(int)
                new_col.columns = [i.strftime("%m/%d/%Y")
                                   for i in new_col.columns]
                new_col["CODE"] = api_data["CODE"]
                mer = pd.merge(sheet_data[["CODE",sheet_data.columns[-1]]], new_col, on="CODE", how='left')
                if self.Validator(mer, key):
                    mer = pd.merge(sheet_data, new_col, on="CODE", how='left')
                    return mer.dropna(axis=0)
                else:
                    return sheet_data
            else:
                return sheet_data
        else:
            raise Exception("Something Wrong Happended!!")

    def __call__(self):
        print("Fetching API data....")
        api = self.apiData()
        print("Fetching API data done.")
        print("Fetching Google Sheet data....")
        sheet, objs = self.sheetData()
        print("Fetching Google Sheet data done.")

        print("Performing Update of Google Sheet...")
        res_dict = {}
        for api_data, sheet_data in zip(api, sheet):
            final_data = self.prepare_for_merge(
                api[api_data], sheet[sheet_data], key=api_data)
            if final_data.shape[1] > sheet[sheet_data].shape[1]:
                res_dict[api_data] = final_data
                obj = objs[api_data]
                print(f"Updating {api_data} Google Sheet...")
                obj.df_to_sheet(final_data, index=False, replace=True)
            else:
                print(
                    f"Updating {api_data} Google Sheet is not required(already up-to-date)...")
            res_dict[api_data] = final_data
        print("Google Sheet Updating Done..")
        return res_dict
