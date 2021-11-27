# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 21:04:56 2021

@author: dript
"""

from Automate.updater import Updater
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import json

gcp_auth = os.environ["API_KEY"]
print(gcp_auth)


if __name__ == "__main__":
    cwd = os.getcwd()
    update_obj = Updater(json.loads(gcp_auth))
    updated_data = update_obj()
    for j in updated_data:
        if j == "confirmed":
            frame = updated_data[j]
            frame.to_csv("COVID19_INDIA_STATEWISE_TIME_SERIES_CONFIRMED.csv",index=False)
        elif j == "deceased":
            frame = updated_data[j]
            frame.to_csv("COVID19_INDIA_STATEWISE_TIME_SERIES_DEATH.csv",index=False)
        elif j == "recovered":
            frame = updated_data[j]
            frame.to_csv("COVID19_INDIA_STATEWISE_TIME_SERIES_RECOVERY.csv",index=False)
    print("All data are saved...")
    
    
    
