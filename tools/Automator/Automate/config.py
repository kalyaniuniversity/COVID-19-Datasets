# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 21:35:07 2021

@author: dript
"""

import yaml
import os

class Config:
    path = os.path.dirname(os.path.abspath(__file__))
    conf_name = "config.yml"
    
    def __getConf__(self):
        with open(os.path.join(self.path,self.conf_name), 'r') as stream:
            try:
                conf = yaml.safe_load(stream)
                return conf
            except yaml.YAMLError as exc:
                raise Exception(exc)