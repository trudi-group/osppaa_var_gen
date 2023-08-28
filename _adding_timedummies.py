# TO BE CLEANED -----------------------------

# Modules
import pandas as pd
import os as os
import statistics as stcs
import numpy as np
import itertools as itr
import pandas as pd
import statsmodels.formula.api as sm
import datetime
import yaml
import importlib
#temp
import matplotlib.pyplot as plt

# Import SETTINGS-file
with open("./SETTINGS.yml", 'r') as stream:
    try:
        SETTINGS = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# Import helpers
spec    = importlib.util.spec_from_file_location("noname", "./gen_helpers.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

# ----------------------------------

# Thanks to https://stackoverflow.com/questions/40923820/pandas-timedelta-in-months
def month_diff(a, b):
    return 12 * (a.year - b.year) + (a.month - b.month)

def add_timedummy(self):

    for coin_name in self.coindata.keys():

        dates = self.coindata[coin_name]["time"]
        referencedate = pd.Timestamp("2000-01-01")
        timedummy = [month_diff(d, referencedate) for d in dates]
        timedummy = {'V_timedummy': timedummy} 
        timedummy = pd.DataFrame(timedummy)    

        self.coindata[coin_name] = pd.concat([self.coindata[coin_name], timedummy], axis=1)

        print("|---| Added timedummy for: |---|" + coin_name )

