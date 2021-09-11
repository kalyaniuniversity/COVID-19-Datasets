# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 22:43:06 2021

@author: dript
"""

from .config import Config
from gspread_pandas import Spread,conf

class getSheetData():
    # This Class pull data from our google sheets 

    def __init__(self):
        self.__conf__ = Config().__getConf__()
    
    def pull_data_sheet(self,config_auth):
        spread_dict = self.__conf__["sheet_url"]
        spread_obj = {}
        sheet_dict = {}
        for j in spread_dict:
            spread = Spread(spread = spread_dict[j],sheet="Sheet1",
                config=conf.get_config(config_auth))
            data_frame = spread.sheet_to_df()
            sheet_dict[j] = data_frame.reset_index()
            spread_obj[j] = spread
        return sheet_dict,spread_dict
                