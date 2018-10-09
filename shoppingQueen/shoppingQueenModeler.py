import json
import os, sys
import re
import random

import numpy as np
from pydoc import locate
import pandas as pd
from fbprophet import Prophet

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

sys.path.append(os.getcwd()+'/../lib')
from collector import Collector
from logger import Logger

import defs

class ShoppingQueenModeler:

    logger = None

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
        forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
        #%matplotlib inline
        fig1 = m.plot(forecast, ax=None, uncertainty=True, plot_cap=True, xlabel=defs.COL_DS_LABEL, ylabel=defs.COL_Y_LABEL)
        fig2 = m.plot_components(forecast)
        fig3 = m.plot(forecast, ax=None, uncertainty=True, plot_cap=True, xlabel=defs.COL_DS_LABEL, ylabel=defs.COL_Y_LABEL)
        #self.logger.log("fig1 is a "+fig1.__class__.__name__)  ->  fig1 is a Figure
        fig1.savefig(os.path.join(self.datadir, self.source + '.plot.png')) #matplotlib.pyplot.savefig
        #fig3.savefig(os.path.join(self.datadir, self.source + '.plot.certain.png')) #matplotlib.pyplot.savefig
        fig2.savefig(os.path.join(self.datadir, self.source + '.plot_components.png'))

        #self.render3d(fig3, collector)

    def render3d(self, fig, collector):
        ax = fig.add_subplot(111, projection='3d')
        #X, Y, Z = axes3d.get_test_data(0.1)    #TODO: get data out of .df
        #//TODO: //WIP
        ax.plot_wireframe(collector.df[defs.COL_DS], collector.df[defs.COL_Y], collector.df, rstride=5, cstride=5)

        # rotate the axes and update
        #for angle in range(0, 360):
        #    ax.view_init(30, angle)
        #    plt.draw()
        #    plt.pause(.001)

        fig.savefig(os.path.join(self.datadir, self.source + '.plot3d.png'))
