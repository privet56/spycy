from keras.models import Input, Model, model_from_json
from keras.layers import Dense, Dropout
from keras.layers import LSTM
from keras.layers.wrappers import TimeDistributed
import keras.callbacks
import keras.backend as K
import scipy.misc
import json

import os, sys
import re
import PIL
from PIL import ImageDraw

from keras.optimizers import RMSprop
import random
import numpy as np
import tensorflow as tf
from keras.utils import get_file

sys.path.append(os.getcwd()+'/../lib')
from collector import Collector

class AutoCoderModeler:
    def __init__(self, prefix, source, datadir):
        self.source = source
        self.datadir = datadir
        self.prefix = prefix
        self.model = None

    def generate_code(self, model, collector, end_with=Collector.SRC_SEPARATOR, diversity=1.0):
        generated = collector.startWith()
        yield generated
        for i in range(2000):
            x = np.zeros((1, len(generated), len(collector.lChars)))
            for t, char in enumerate(generated):
                x[0, t, collector.dChars2idx[char]] = 1.
            preds = model.predict(x, verbose=0)[0]
            
            preds = np.asarray(preds[len(generated) - 1]).astype('float64')
            preds = np.log(preds) / diversity
            exp_preds = np.exp(preds)
            preds = exp_preds / np.sum(exp_preds)
            probas = np.random.multinomial(1, preds, 1)
            next_index = np.argmax(probas)        
            next_char = collector.lChars[next_index]
            yield next_char

            generated += next_char
            if generated.endswith(end_with):
                break

    def data_generator(self, collector, batch_size, chunk_size):
        X = np.zeros((batch_size, chunk_size, len(collector.dChars2idx)))
        y = np.zeros((batch_size, chunk_size, len(collector.dChars2idx)))
        while True:
            for row in range(batch_size):
                idx = random.randrange(len(collector.sCode) - chunk_size - 1)
                chunk = np.zeros((chunk_size + 1, len(collector.dChars2idx)))
                for i in range(chunk_size + 1):
                    chunk[i, collector.dChars2idx[collector.sCode[idx + i]]] = 1
                X[row, :, :] = chunk[:chunk_size]
                y[row, :, :] = chunk[1:]
            yield X, y

    def char_rnn_model(self, collector, num_layers, num_nodes=512, dropout=0.1):
        input = Input(shape=(None, len(collector.lChars)), name='input')
        prev = input
        for i in range(num_layers):
            lstm = LSTM(num_nodes, return_sequences=True, name='lstm_layer_%d' % (i + 1))(prev)
            if dropout:
                prev = Dropout(dropout)(lstm)
            else:
                prev = lstm
        dense = TimeDistributed(Dense(len(collector.lChars), name='dense', activation='softmax'))(prev)
        self.model = Model(inputs=[input], outputs=[dense])
        optimizer = RMSprop(lr=0.01)
        self.model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
        return self.model

    def fit(self, collector, batch_size, epochs=40):
        self.model = self.char_rnn_model(collector, num_layers=2, num_nodes=640, dropout=0)

        early = keras.callbacks.EarlyStopping(monitor='loss',
                                    min_delta=0.03,
                                    patience=3,
                                    verbose=0, mode='auto')

        self.model.fit_generator(
            self.data_generator(collector, batch_size=batch_size, chunk_size=160),
            epochs=epochs,
            callbacks=[early,],
            steps_per_epoch=2 * len(collector.sCode) / (batch_size * 160),
            verbose=2
        )

    def getModelPathName(self):
        assert self.datadir != None
        assert self.prefix  != None

        #the .h5 HDF5 file contains the model 
        # - architecture
        # - weiths
        # - training config (loss, optimizer)
        # - state of the optimizer (allows to resume)

        return os.path.join(self.datadir,'{0}.kerasmodel.h5'.format(self.prefix))

    def save(self):

        assert self.model   != None
        assert self.datadir != None
        assert self.prefix  != None

        # save a Keras model into a single HDF5 file
        self.model.save(self.getModelPathName())

        # saves train options / config:
        with open(self.getModelPathName()+".json", "w") as json_file:
            json_file.write(self.model.to_json())   #//TODO: pretty_format|pretty_print|indent=2 & encoding='utf-8'

        #//alternative saving of train options
        #model_config = self.model.get_config()
        #model_config_json = json.loads(model_config.decode('utf-8'))

    def load(self):
        
        self.model = keras.models.load_model(self.getModelPathName())

        assert self.model   != None

        # alternatives:
        #self.model = Model.from_config(config)
        #self.model = model_from_json(json_string)

    def generateCode(self, collector, count, prefix, stdout):
        for i in range(count):
            generatedCode = ''
            for ch in self.generate_code(self.model, collector):
                generatedCode += ch
            generatedCode = generatedCode.strip()

            with open(os.path.join(self.datadir, prefix + Collector.AUTOGENERATED_CODE_PREFIX + "{0}.{1}".format(i, prefix)), 'w', ) as codefile:       # 'w' overwrites
                codefile.write(generatedCode)

            if(stdout):
                print("------------------- GENERATED CODE START",(i+1),"/",count,"\n",generatedCode,"\n------------------- GENERATED CODE END")

        if(stdout):
            print("END")
