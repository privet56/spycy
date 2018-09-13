import os, sys
import argparse
sys.path.append(os.getcwd()+'/../lib')
from autoCoderModeler import AutoCoderModeler
from collector_py import Collector_py
from collector_java import Collector_java
from logger import Logger

logger = None

def getCollector(prefix, source, datadir):
    if(prefix == 'py'):
        return Collector_py(source, datadir)   #//TODO: choose class based on prefix with __import__('Collector_'+prefix)
    if(prefix == 'java'):
        return Collector_java(source, datadir)
    raise ValueError("invalid prefix:'"+prefix+"'")

def train(prefix, epochs, datadir, source, max_file_count):
    collector = getCollector(prefix, source, datadir)
    logger.log("train-step.1: collecting...", False)
    collector.collect(source, max_file_count)
    collector.writeCollectedData()
    autoCoderModeler = AutoCoderModeler(prefix, source, datadir)
    logger.log("train-step.2: fitting model (found files:{0})".format(len(collector.aSRCs)), True)
    autoCoderModeler.fit(collector, batch_size=256, epochs=epochs)
    logger.log("train-step.1: save model...", True)
    autoCoderModeler.save()
    logger.log("FINISH!!!", True)

def test(prefix, datadir):
    source = datadir
    collector = getCollector(prefix, source, datadir)
    logger.log("test-step.1: load serialized data...")
    collector.loadCollectedData()
    autoCoderModeler = AutoCoderModeler(prefix, source, datadir)
    logger.log("test-step.2: load model...", True)
    autoCoderModeler.load()
    logger.log("test-step.3: generating code...", True)
    autoCoderModeler.generateCode(collector, 3, prefix, stdout=True)
    logger.log("FINISH!!!", True)

MODE_TRAIN = 'train'
MODE_TEST  = 'test'

if __name__ == '__main__':
    #python autoCoder.py --mode=train prefix=py epochs=2 datadir=data source=../ max_file_count=99
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode'            , type=str, default='test',    help='specify mode: {0} or {1}'.format(MODE_TRAIN, MODE_TEST), choices=[MODE_TRAIN,MODE_TEST])
    parser.add_argument('--prefix'          , type=str,                    help='specify prefix of which files should be read, eg py or java', choices=['py','java'])
    parser.add_argument('--epochs'          , type=int, default=40,        help='specify train epochs')
    parser.add_argument('--datadir'         , type=str,                    help='specify dir of data-model')
    parser.add_argument('--source'          , type=str,                    help='specify dir of source data')
    parser.add_argument('--max_file_count'  , type=int, default=999999999, help='specify max file count to be used to train the model')
    args = parser.parse_args()

    logger = Logger(args.prefix, args.datadir)
    logger.log("START "+args.mode+"ing "+str(sys.argv))

    if(args.mode == MODE_TRAIN):
        train(args.prefix, args.epochs, args.datadir, args.source, args.max_file_count)
    elif(args.mode == MODE_TEST):
        test(args.prefix, args.datadir)
    else:
        logger.log("ERR: unknown mode!")
