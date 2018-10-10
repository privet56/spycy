import json
import os, sys
import re
import random

import numpy as np
from pydoc import locate
import pandas as pd
from fbprophet import Prophet

from datetime import datetime

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

sys.path.append(os.getcwd()+'/../lib')
from collector import Collector
from logger import Logger

import defs

class ShoppingQueenModeler:

    logger = None
    trisurf = True

    def __init__(self, source, datadir, logger=None):
        self.source = source
        self.datadir = datadir
        self.logger = logger if logger else Logger(source, datadir)

    def fit(self, collector):
        m = Prophet(daily_seasonality=False)
        m.fit(collector.df)
        future = m.make_future_dataframe(periods=365)
        #print(future.tail())
        forecast = m.predict(future)
        forecast[[defs.COL_DS, defs.COL_YHAT, defs.COL_YHAT+'_lower', defs.COL_YHAT+'_upper']].tail()
        fig1 = m.plot(forecast, ax=None, uncertainty=True, plot_cap=True, xlabel=defs.COL_DS_LABEL, ylabel=defs.COL_Y_LABEL)
        fig2 = m.plot_components(forecast)
        fig3 = m.plot(forecast, ax=None, uncertainty=True, plot_cap=True, xlabel=defs.COL_DS_LABEL, ylabel=defs.COL_Y_LABEL)#magic, influencing the generated 3d plot
        self.render3d(forecast, collector)
        #self.logger.log("fig1 is a "+fig1.__class__.__name__)  ->  fig1 is a Figure
        fig1.savefig(os.path.join(self.datadir, self.source + '.plot.png')) #matplotlib.pyplot.savefig
        fig2.savefig(os.path.join(self.datadir, self.source + '.plot_components.png'))

    def render3d(self, forecast, collector):

        #%matplotlib inline
        #forecast is a pd.DataFrame
        #print(forecast.columns)
        #Index(['ds', 'trend', 'yhat_lower', 'yhat_upper', 'trend_lower', 'trend_upper',
        #    'additive_terms', 'additive_terms_lower', 'additive_terms_upper',
        #    'weekly', 'weekly_lower', 'weekly_upper', 'yearly', 'yearly_lower',
        #    'yearly_upper', 'multiplicative_terms', 'multiplicative_terms_lower',
        #    'multiplicative_terms_upper', 'yhat'],
        #    dtype='object')

        #print(type(forecast['ds'][0])) = <class 'pandas._libs.tslibs.timestamps.Timestamp'>    #too big numbers!
        forecast['date'] = forecast[defs.COL_DS].dt.year

        fig = plt.figure(3,figsize=(6, 6))
        ax3 = axes3d.Axes3D(fig)
        #ax3.view_init(elev=40, azim=5) #sets 3D rotation
        ax3.set_color_cycle('b')

        if(self.trisurf):
            #ax3.scatter3D would create dots at the data points
            ax3.plot_trisurf(
                    forecast['date']    ,
                    forecast['trend']   ,
                    forecast[defs.COL_YHAT]    )
            ax3.set_proj_type('persp')
        else:
            t, = ax3.plot(
                    forecast['date']    ,
                    forecast['trend']   ,
                    forecast[defs.COL_YHAT]    )
            t.set_linewidth(2)

        ax3.set_xlabel('X: data point (index)')
        ax3.set_ylabel('Y: Trend')
        ax3.set_zlabel('Z: forecast deviation ('+defs.COL_YHAT+')')
        #ax3.legend()
        plt.savefig(os.path.join(self.datadir, self.source + '.plot3d.png'))

    def explode(self, data):
        size = np.array(data.shape)*2
        data_e = np.zeros(size - 1, dtype=data.dtype)
        data_e[::2, ::2, ::2] = data
        return data_e
