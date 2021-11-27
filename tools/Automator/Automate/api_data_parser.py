# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 20:39:24 2021

@author: dript
"""
from .config import Config
import json
import urllib
import pandas as pd
from datetime import datetime


class getApiData():
    # This class is for pulling and preparing api data from https://www.covid19india.org/
    # and prepare that data to use in our database.
    
    
    # read config file
    __conf__ = Config().__getConf__()
    
    def pull_data(self):
        url = self.__conf__["api_url"]["timeseries"]
        with urllib.request.urlopen(url) as url:
            try:
                data_state = json.loads(url.read().decode())
                return data_state
            except Exception as e:
                raise Exception(e)
                
    
    def prepare_data(self,pulled_data):
        '''
        Prepare the pulled data for storing and updating our database

        Returns
        -------
        dict. A Dictionary Object containing all dataframes

        '''
        dict_frame = {
            "confirmed":pd.DataFrame(),
            "deceased":pd.DataFrame(),
            "recovered":pd.DataFrame()
        }
        for st in pulled_data:
            if st != "UN":
                st_date = pulled_data[st]["dates"]
                st_date_list = list(st_date.keys())
                for i in ["confirmed","recovered","deceased"]:
                    temp_dict = {}
                    temp_dict[st] = [st_date[d]['total'].get(i,0) for d in st_date]
                    t = pd.DataFrame(temp_dict,index=st_date_list)
                    dict_frame[i] = pd.concat([dict_frame[i],t],axis=1)
                    dict_frame[i] = dict_frame[i].fillna(0)
                    
                    
        for df in dict_frame:
            df_temp = dict_frame[df]
            df_temp.index = pd.to_datetime(df_temp.index)
            df_temp.sort_index(inplace=True)
            #df_temp.index = df_temp.index.strftime("%m/%d/%Y")
            df_temp_t = df_temp.T
            df_temp_t = df_temp_t.reset_index()
            df_temp_t = df_temp_t.rename(columns = {"index":"CODE"})
            df_temp_t.CODE = df_temp_t.CODE.str.lower()
            dict_frame[df] = df_temp_t
        return dict_frame
    
    def __call__(self):
        pulled_data = self.pull_data()
        prepared_data = self.prepare_data(pulled_data)
        for j in prepared_data:
            date_today = datetime.now().date()
            fr = prepared_data[j]
            if fr.columns[-1].date() == date_today:
                prepared_data[j] = fr.drop(columns = [fr.columns[-1]])
        return prepared_data
            
        

