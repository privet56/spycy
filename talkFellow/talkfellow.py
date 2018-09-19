#!/usr/bin/env python
import argparse
from pydoc import locate

import os, sys
import argparse
from talkFellowModeler import TalkFellowModeler
sys.path.append(os.getcwd()+'/../lib')
from collector_gutenberg import CollectorGutenberg
from logger import Logger

logger = None

MODE_TRAIN = 'train'
MODE_TEST  = 'test'
MODE_TRAIN_AND_TEST = 'train_and_test'

def getCollector(source, datadir):
        return CollectorGutenberg(source, datadir)

def train(datadir, source, bookids):
    collector = getCollector(source, datadir)
    logger.log("train-step.1: collecting...("+bookids+")", False)
    len_converations, downloaded_books, download_book_failed = collector.collect(source, -1, map(int, bookids.split(',')))
    logger.log("train-step.1: collected len_converations:"+str(len_converations)+" downloaded_books:"+str(downloaded_books)+" download_book_failed:"+str(download_book_failed), True)
    talkFellowModeler = TalkFellowModeler(source, datadir)
    logger.log("train-step.2: fitting...", True)
    talkFellowModeler.fit(collector)
    logger.log("FINISHED TRAIN", True)

def test(datadir, source):
    collector = getCollector(source, datadir)
    logger.log("test-step.1: load serialized data...")
    collector.loadCollectedData()
    talkFellowModeler = TalkFellowModeler(source, datadir)
    logger.log("test-step.2: load model...", True)
    talkFellowModeler.load(datadir)
    logger.log("test-step.2: start talking to fellow... (exit with 'q')", True)
    talkFellowModeler.discuss()
    #question = 'Hallo'
    #logger.log("test-step.3: start talking...(question:'"+question+"')", True)
    #answer = talkFellowModeler.talk('Hallo')
    #logger.log("test-step.4: answer:'"+answer+"'", True)
    logger.log("FINISHED TEST", True)

if __name__ == '__main__':
    #python talkfellow.py --mode=train --datadir=data --source=gutenberg --bookids=2229,12108,23134,53689,22517,52856
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode'            , type=str, default='test',    help='specify mode: {0} or {1} or {2}'.format(MODE_TRAIN, MODE_TEST, MODE_TRAIN_AND_TEST), choices=[MODE_TRAIN,MODE_TEST, MODE_TRAIN_AND_TEST])
    parser.add_argument('--datadir'         , type=str,                    help='specify dir of data-model')
    parser.add_argument('--source'          , type=str,                    help='specify dir(?) of source data')
    parser.add_argument('--bookids'         , type=str,                    help='specify gutenberg bookid´s')
    args = parser.parse_args()

    logger = Logger(args.source, args.datadir)
    logger.log("START "+args.mode+"ing "+str(sys.argv))

    if((args.mode == MODE_TRAIN) or (args.mode == MODE_TRAIN_AND_TEST)):
        train(args.datadir, args.source, args.bookids)
    if((args.mode == MODE_TEST) or (args.mode == MODE_TRAIN_AND_TEST)):
        test(args.datadir, args.source)
