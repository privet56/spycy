import json
import os, sys
import re
import random

import numpy as np
from pydoc import locate
import pandas as pd
from fbprophet import Prophet

sys.path.append(os.getcwd()+'/../lib')
from collector import Collector
from logger import Logger

class ShoppingQueenModeler:

    logger = None

    def __init__(self, source, datadir, logger=None):
        self.source = source
        self.datadir = datadir
        self.logger = logger if logger else Logger(source, datadir)

    def fit(self, collector):
        self.logger.err(""+self.__class__.__name__+":collect: yet NOTIMPL")
        m = Prophet(daily_seasonality=False)
        m.fit(collector.df)
        future = m.make_future_dataframe(periods=365)
        print(future.tail())
        forecast = m.predict(future)
        forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
        #%matplotlib inline
        fig1 = m.plot(forecast)
        fig2 = m.plot_components(forecast)

        fig1.savefig(os.path.join(self.datadir, self.source, '.plot.png'))
        fig2.savefig(os.path.join(self.datadir, self.source, '.plot_components.png'))
