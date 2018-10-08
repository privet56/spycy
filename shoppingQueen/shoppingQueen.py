import os, sys
import argparse
sys.path.append(os.getcwd()+'/../lib')
from shoppingQueenModeler import ShoppingQueenModeler
from collector_excel import Collector_Excel
from logger import Logger

logger = None

def getCollector(datadir, source):
    #//TODO: support xlsx, xls, csv
    #//TODO: choose class based on prefix with __import__('Collector_'+prefix)
    return Collector_Excel(source, datadir, logger)

def predict(datadir, source):
    collector = getCollector(datadir, source)
    logger.log("step.0: load data source...")
    collector.collect(os.path.join(datadir, source))
    logger.log("step.0: fit data source...", True)
    shoppingQueenModeler = ShoppingQueenModeler(source, datadir, logger)
    shoppingQueenModeler.fit()
    logger.log("FINISH: fit data source...", True)

if __name__ == '__main__':
    #python autoCoder.py --source=amazon_order_history.xlsx --datadir=data
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir' , type=str, help='specify dir of data-model')
    parser.add_argument('--source', type=str, help='specify dir of source data')
    args = parser.parse_args()

    logger = Logger(args.source, args.datadir)
    logger.log("START prophesy: "+str(sys.argv))

    predict(args.datadir, args.source)
