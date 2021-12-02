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
from checker.check_sheet import SheetChecker
import argparse

gcp_auth = os.environ["API_KEY"]


def Update(token):
    update_obj = Updater(token)
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
    
    
def Validate(token,days = None):
    if days != None:
        chk_obj = SheetChecker(auth_token = token,days = days)  
    else:
        chk_obj = SheetChecker(auth_token = token)
    chk_data = chk_obj.CompareDataLoop()
    for j in chk_data:
        if j == "confirmed":
            frame = chk_data[j]
            frame.to_csv("COVID19_INDIA_STATEWISE_TIME_SERIES_CONFIRMED.csv",index=False)
        elif j == "deceased":
            frame = chk_data[j]
            frame.to_csv("COVID19_INDIA_STATEWISE_TIME_SERIES_DEATH.csv",index=False)
        elif j == "recovered":
            frame = chk_data[j]
            frame.to_csv("COVID19_INDIA_STATEWISE_TIME_SERIES_RECOVERY.csv",index=False)
    print("All data are saved...")
    
    


parser = argparse.ArgumentParser(description='To Update datasets and validate the data')
parser.add_argument('-m','--mode', type = str,choices = ["Update","Validate"],default="Update",
                    help = "Run Script to Update or Validate")

parser.add_argument('-c','--checkdays', type = int,default=10,
                    help = "How many last days to be validated. Use only when mode is set to Validate.")

args = parser.parse_args()


if args.mode == "Update":
    print("Starting Updating Service..")  
    Update(json.loads(gcp_auth))
elif args.mode == "Validate":
    print("Starting Validate Service..")
    if args.checkdays != None:
        Validate(json.loads(gcp_auth),args.checkdays)
    else:
        Validate(json.loads(gcp_auth))
    
    
    
