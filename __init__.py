
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

class data:

    # Konstruktor
    def __init__(self,
                 config_obj):
        # Attribute
        self.config         = config_obj
        self.coindata_dir   = config_obj["dataloading"]["market_raw_data_dir"]
        self.coindata_files = [x for x in os.listdir(self.coindata_dir) if x.endswith('.csv')]
        self.coindata_names_original = [w.join(w.split("_")[:(w.count("_")-2+1)]) for w in self.coindata_files]
        self.coindata       = self.load_data(self.coindata_dir)
        self.coindata       = self.coindata_list_to_dictonary()
        self.yfinance_path  = self.config["yfinance"]["path"]
        self.yfinance_name  = self.config["yfinance"]["obj_name"]
        self.yfinancedata   = self.load_yfinance_data(path = self.yfinance_path,
                                                      name = self.yfinance_name)
        self.crixdata       = self.load_crix_data(path = self.config["crix"]["loadpath"],
                                                  name = self.config["crix"]["loadname"])
        self.cmi10data      = self.load_cmi10_data(path = self.config["crix"]["loadpath"],
                                                  name = self.config["crix"]["loadname"])
        self.price_var      = config_obj["dataloading"]["price_var"]
        self.vol_var        = config_obj["dataloading"]["vol_var"]
        self.source_sc_ids  = config_obj["dataloading"]["source_of_stablecoin_ids"]
        
    # Methoden
    from ._cleaning           import coindata_list_to_dictonary, clean_date, _zscore_for_pd, truncate_outliers, remove_nan_lines, _return_missing_val_percentage, drop_dta_with_many_nas, drop_dta_with_few_obs, drop_dta_with_low_volume, _norm_for_pd, normalize_data_by_col, drop_dta_with_low_mcap
    from ._loaddata           import load_data, load_yfinance_data, load_crix_data, load_cmi10_data
    from ._adding_basicvars   import add_returns, add_stablecoin_identifier, add_supply
    from ._adding_resistance  import add_resistance
    from ._adding_timedummies import add_timedummy
    from ._adding_volume      import add_volume_ratio
    from ._adding_trends      import _make_tuples, add_trend_shortterm, add_trend_longterm
    from ._adding_volatility  import add_volatility_squaredreturns, add_volatility_windowSD, add_volatility_ratio
    from ._adding_fvaluevars  import _peg_1usd, _peg_default, _peg_1eur, _peg_gold1ounce, _peg_gold1gramm, _peg_1nzusd, _peg_1gbp
    from ._adding_fvaluevars  import _getStabelcoinPeg
    from ._adding_fvaluevars  import _wma_weighting_func_linear, add_fvalue_coll, add_fvalue_zero, add_fvalue_network, add_fvalue_anchored, add_fvalue_property, add_fvalue_txcosts, add_fvalue_hacks, add_fvalue_lineartrend, reduce_to_single_fv_choice
    from ._utils              import get_current_cols, na_check, empty_check
    from ._merge_other        import mergeCRIX, mergeCMI10
