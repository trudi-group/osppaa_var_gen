
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

def _wma_weighting_func_linear(self,
                        steps):
    weights = [1*i for i in steps] #steps to be given in range
    return weights

def _peg_1usd(self,
               time):
    peg = 1
    return peg

def _peg_default(self,
                  time):
    peg = np.nan
    return peg

def _peg_1eur(self,
              time):
    prices = self.yfinancedata["EURUSD=X"]["cp"] # cp means closing price
    dates  = self.yfinancedata["EURUSD=X"]["time"]
    peg = prices[dates == time.strftime('%Y-%m-%d %H:%M')] # time same for all coins
    if len(peg) > 1:
        raise TypeError("Issue in Yahoo Finance data!")
    elif len(peg) == 0:
        pegout = np.nan
    else:
        pegout = peg.values[0] 
    return pegout


def _peg_1gbp(self,
              time):
    prices = self.yfinancedata["EURGBP=X"]["cp"] # cp means closing price
    dates  = self.yfinancedata["EURGBP=X"]["time"]
    peg = prices[dates == time.strftime('%Y-%m-%d %H:%M')] # time same for all coins
    if len(peg) > 1:
        raise TypeError("Issue in Yahoo Finance data!")
    elif len(peg) == 0:
        pegout = np.nan
    else:
        pegout = peg.values[0] 
    return pegout


def _peg_1nzusd(self,
              time):
    prices = self.yfinancedata["NZDUSD=X"]["cp"] # cp means closing price
    dates  = self.yfinancedata["NZDUSD=X"]["time"]
    peg = prices[dates == time.strftime('%Y-%m-%d %H:%M')] # time same for all coins
    if len(peg) > 1:
        raise TypeError("Issue in Yahoo Finance data!")
    elif len(peg) == 0:
        pegout = np.nan
    else:
        pegout = peg.values[0] 
    return pegout


# def _peg_1cny(self,
#               time):
#     prices = self.yfinancedata["CNYUSD=X"]["cp"] # cp means closing price
#     dates  = self.yfinancedata["CNYUSD=X"]["time"]
#     peg = prices[dates == time.strftime('%Y-%m-%d %H:%M')] # time same for all coins
#     if len(peg) > 1:
#         raise TypeError("Issue in Yahoo Finance data!")
#     elif len(peg) == 0:
#         pegout = np.nan
#     else:
#         pegout = peg.values[0] 
#     return pegout

def _peg_gold1ounce(self,
                    time):
    prices = self.yfinancedata["GC=F"]["cp"] # cp means closing price
    dates  = self.yfinancedata["GC=F"]["time"]
    peg = prices[dates == time.strftime('%Y-%m-%d %H:%M')] # time same for all coins
    if len(peg) > 1:
        raise TypeError("Issue in Yahoo Finance data!")
    elif len(peg) == 0:
        pegout = np.nan
    else:
        pegout = peg.values[0] 
    return pegout

def _peg_gold1gramm(self,
                    time):
    prices = self.yfinancedata["GC=F"]["cp"] # cp means closing price
    dates  = self.yfinancedata["GC=F"]["time"]
    peg = prices[dates == time.strftime('%Y-%m-%d %H:%M')] # time same for all coins
    if len(peg) > 1:
        raise TypeError("Issue in Yahoo Finance data!")
    elif len(peg) == 0:
        pegout = np.nan
    else:
        pegout = peg.values[0] * 28.3495 
    return pegout


def _getStabelcoinPeg(self,
                      cname):
    # 1. Get the right function to apply to daily data
    # -- Known cases
    switcher = {
        # broken "nubits"     :self._peg_1usd,
        # broken "bitusd"     :self._peg_1usd,
        "tether"     :self._peg_1usd,
        "tether-gold":self._peg_gold1ounce,
        "perth-mint-gold-token":self._peg_gold1ounce,
        "gold-bcr"   :self._peg_gold1ounce,
        # broken "usd-bancor"     :self._peg_1usd,
        "sdusd"      :self._peg_1usd,
        "stasis-eurs":self._peg_1eur,
        "gemini-dollar"   :self._peg_1usd,
        "dai"        :self._peg_1usd,
        # broken "trustusd"   :self._peg_1usd,
        "aave-tusd"  :self._peg_1usd,
        "digitalusd" :self._peg_1usd,
        "neutrino"   :self._peg_1usd,
        "musd"       :self._peg_1usd,
        "stableusd"  :self._peg_1usd,
        "true-usd"   :self._peg_1usd,
        "etoro-euro" :self._peg_1eur,
        "equilibrium-eosdt" :self._peg_1usd,
        "digix-gold" :self._peg_gold1gramm,
        "pax-gold"   :self._peg_gold1ounce,
        "binance-usd":self._peg_1usd,
        "usdx"       :self._peg_1usd,
        "nusd"       :self._peg_1usd,
        "usdk"       :self._peg_1usd,
        "usd-coin"   :self._peg_1usd,
        "husd"       :self._peg_1usd,
        "usdq"       :self._peg_1usd,
        "paxos-standard" :self._peg_1usd,
        # pegged to world economy "anchor":self._peg_1usd,
        "binance-gbp":self._peg_1gbp,
        #"bitCNY"     :self._peg_1cny,
        "etoro-new-zealand-dollar":self._peg_1nzusd,
    }
    # -- Unknown cases
    self.get_peg_for_day = switcher.get(cname, self._peg_default)

    # 2. Apply this function to daily data
    datevec = self.coindata[cname]["time"]

    peg = []
    for d in datevec:
        peg.append(self.get_peg_for_day(time = d))
    peg_fact = { 'V_fact_fval_coll': peg} 
    peg_fact = pd.DataFrame(peg_fact)

    self.coindata[cname] = pd.concat([self.coindata[cname], peg_fact], axis=1)

def add_fvalue_coll(self):
    for coin_name in self.coindata.keys():
        self._getStabelcoinPeg(cname = coin_name)
        print("|---| Added fundamental value estimate ('Collateral') for: |---|" + coin_name)

def add_fvalue_zero(self):
    for coin_name in self.coindata.keys():
        self.coindata[coin_name]["V_fact_fval_zero"] = 0
        print("|---| Added fundamental value estimate ('ZeroValue') for: |---|" + coin_name )

def add_fvalue_lineartrend(self,
                           wlength    = "from_config",
                           ols_minobs = "from_config"):

    # Input either from config file or specified in arguments
    if wlength == "from_config":
        wlength = self.config["dataloading"]["fvalue_lineartrend_windowlength"]
    elif not type(wlength) == int:
        raise TypeError("Input has to be an integer.")
    
    if ols_minobs == "from_config":
        ols_minobs = self.config["dataloading"]["fvalue_lineartrend_ols_minobs"]
    elif not type(wlength) == int:
        raise TypeError("Input has to be an integer.")
        
    for coin_name in self.coindata.keys():

        # Inputs required for longterm trend
        prices       = self.coindata[coin_name][self.price_var]
        prices.index = self.coindata[coin_name]["time"]

        # Loop over timeseries to apply rolling functionality (OLS here)
        fv_est = list()
        for i in range(len(prices)): # loop to satisfy ols_minobs 

            # Determine cut to apply functionality to
            index_from = i
            index_to   = wlength + i

            # Extract data for regression
            regressiondata_endog_var = prices.shift(-1)[index_from:index_to]
            regressiondata_exog_var  = prices[index_from:index_to]
            regressiondata           = pd.concat([regressiondata_endog_var,
                                                  regressiondata_exog_var],
                                       axis = 1)
            regressiondata.columns = ["prices","lagged_prices"]

            # Performance of regression on data extract if sufficient observ.
            cond_many_nans_data_exog   = regressiondata_exog_var.isna().sum()
            cond_many_nans_data_endog  = regressiondata_endog_var.isna().sum()
            cond_to_little_observatios = regressiondata.shape[0] < ols_minobs 
            if (cond_many_nans_data_endog or
                cond_many_nans_data_exog or
                cond_to_little_observatios):
                intercept = np.nan
                slope     = np.nan
            else:
                ols_obj = sm.ols(formula = "prices ~ lagged_prices", 
                                 data    = regressiondata,
                                 missing = 'drop').fit()
                intercept = ols_obj.params[0]
                slope     = ols_obj.params[1]
                
            base_price = regressiondata_endog_var[0]
            est_price  = intercept + slope * base_price
            fv_est.append(est_price)

        fv_est = { 'V_fvalue_ols_'+ str(wlength): fv_est} 
        fv_est = pd.DataFrame(fv_est)
            
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name],
                                              fv_est], axis=1)
            
        print("|---| Added fundamental value estimate ('OLS trend') (wlength = "
              + str(wlength)
              +") for: |---| "
              + coin_name)

def add_fvalue_anchored(self,
                        halflife  = "from_config",
                        minobs    = "from_config",
                        anchortyp = "from_config",
                        wlength   = "from_config"):

    # Input either from config file or specified in arguments
    if halflife == "from_config":
        halflife = self.config["dataloading"]["fvalue_anchor_emwa_halflife"]
    elif not type(halflife) == int and not type(halflife) == float:
        raise TypeError("Input has to be an integer or float.")

    if wlength == "from_config":
        wlength = self.config["dataloading"]["fvalue_anchor_wa_wlength"]
    elif not type(wlength) == int:
        raise TypeError("Input has to be an integer.")

    if minobs == "from_config":
        minobs = self.config["dataloading"]["fvalue_anchor_minobs"]
    elif not type(minobs) == int:
        raise TypeError("Input has to be an integer.")

    if anchortyp == "from_config":
        anchortyp = self.config["dataloading"]["fvalue_anchor_anchortyp"]
    elif anchortyp not in ["emwa", "lma", "sma"]:
        raise TypeError("Input has to be 'emwa', 'lma' or 'sma'.")

    # Calculate EMWA per coin
    for coin_name in self.coindata.keys():

        # Inputs required for longterm trend
        prices            = self.coindata[coin_name][self.price_var]
        center_left_shift = (-minobs+1 if anchortyp == "emwa" else -wlength+1) # as pandas is stupid and does not support center = "left". minobs for emwa as wlength infinite and minobs determining position of first emwa-value
        if anchortyp == "emwa":
            # Calculate Exponentially Weighted Moving average
            fv_est = (prices
                      .ewm(halflife    = halflife,
                           adjust      = False,
                           min_periods = minobs)
                      .mean()
                      .shift(center_left_shift)
            )
        elif anchortyp == "sma":
            # Calculate Equally Weighted Moving average
            fv_est = (prices
                      .rolling(window      = wlength,
                               min_periods = minobs)
                      .mean()
                      .shift(center_left_shift)
            )
        elif anchortyp == "lma":
            # Calculate general moving average with custom weight vector
            steps       = range(wlength,0,-1)
            weights     = self._wma_weighting_func_linear(steps)
            sum_weights = np.sum(weights)
            
            fv_est = (prices
                      .rolling(window=len(weights), center=False)
                      .apply(lambda x: np.sum(weights*x) / sum_weights, raw=False)
                      .shift(center_left_shift)
            )
                   
        # rename column and append to coindata
        fv_est = { 'V_fvalue_'
                   + anchortyp
                   + '_'
                   +(str(halflife)
                     if anchortyp == "emwa"
                     else str(wlength)): fv_est
        } 
        fv_est = pd.DataFrame(fv_est)
            
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name],
                                              fv_est], axis=1)
            
        print("|---| Added fundamental value estimate ('Anchoring (EMWA)') (halflife = "
              + str(halflife)
              +") for: |---| "
              + coin_name)


def reduce_to_single_fv_choice(self,
                               choice_tradcoins = "from_config",
                               choice_stabcoins = "from_config"):

    if choice_tradcoins == "from_config":
        choice_tradcoins = self.config["dataloading"]["fvalue_choice_tradcoins"]
    elif not type(choice_tradcoins) not in self.coindata.keys():
        raise TypeError("Inputs have to be a valid variable names.")

    if choice_stabcoins == "from_config":
        choice_stabcoins = self.config["dataloading"]["fvalue_choice_stabcoins"]
    elif choice_stabcoins not in self.coindata.keys():
        raise TypeError("Inputs have to be a valid variable names.")

    for coin_name in self.coindata.keys():
        if all(self.coindata[coin_name].loc[:,"is_stablecoin"]) == True:
            choice = choice_stabcoins
        elif all(self.coindata[coin_name].loc[:,"is_stablecoin"]) == False:
            choice = choice_tradcoins
            
        dist_to_fv = (self.coindata[coin_name].loc[:,"prices"] - self.coindata[coin_name].loc[:,choice])
        dist_to_fv = { 'V_fv': dist_to_fv} 
        dist_to_fv = pd.DataFrame(dist_to_fv)
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name],
                                              dist_to_fv], axis=1)
        
        print("|---| Added combined fv estimate depending on type: |---| " + coin_name)        


def add_fvalue_network(self):
    for coin_name in self.coindata.keys():
        print("Something's missing here.")
    print("|---| Added fundamental value estimate ('Network Estimate') for: |---|" + coin_name )

def add_fvalue_hedge(self):
    for coin_name in self.coindata.keys():
        print("Something's missing here.")
    print("|---| Added fundamental value estimate ('Save Harbour') for: |---|" + coin_name )

def add_fvalue_property(self):
    for coin_name in self.coindata.keys():
        print("Something's missing here.")
    print("|---| Added fundamental value estimate ('Property Protection') for: |---|" + coin_name )

def add_fvalue_txcosts(self):
    for coin_name in self.coindata.keys():
        print("Something's missing here.")
    print("|---| Added fundamental value estimate ('TX Costs') for: |---|" + coin_name )

def add_fvalue_hacks(self):
    for coin_name in self.coindata.keys():
        print("Something's missing here.")
    print("|---| Added fundamental value estimate ('Hacks') for: |---|" + coin_name )

