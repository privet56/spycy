import json
import os, sys
import re
import random

import numpy as np
import tensorflow as tf
from pydoc import locate
from seq2seq import models
from seq2seq.training import utils as training_utils
from seq2seq.tasks.inference_task import InferenceTask, unbatch_dict

sys.path.append(os.getcwd()+'/../lib')
from collector import Collector
from logger import Logger
from reflector import Reflector

class DecodeOnce(InferenceTask):
  '''
  Similar to tasks.DecodeText, but for one input only.
  Source fed via features.source_tokens and features.source_len
  '''
  def __init__(self, params, callback_func):
    super(DecodeOnce, self).__init__(params)
    self.callback_func=callback_func

  @staticmethod
  def default_params():
    return {}

  def before_run(self, _run_context):
    fetches = {}
    fetches["predicted_tokens"] = self._predictions["predicted_tokens"]
    fetches["features.source_tokens"] = self._predictions["features.source_tokens"]
    return tf.train.SessionRunArgs(fetches)

  def after_run(self, _run_context, run_values):
    fetches_batch = run_values.results
    for fetches in unbatch_dict(fetches_batch):
      # Convert to unicode
      fetches["predicted_tokens"] = np.char.decode(
          fetches["predicted_tokens"].astype("S"), "utf-8")
      predicted_tokens = fetches["predicted_tokens"]

      # If we're using beam search we take the first beam
      # TODO: beam search top k
      if np.ndim(predicted_tokens) > 1:
        predicted_tokens = predicted_tokens[:, 0]

      fetches["features.source_tokens"] = np.char.decode(
          fetches["features.source_tokens"].astype("S"), "utf-8")
      source_tokens = fetches["features.source_tokens"]

      self.callback_func(source_tokens, predicted_tokens)

######################################### class DecodeOnce END

class TalkFellowModeler:

    logger = None

    session = None
    source_tokens_ph = None
    source_len_ph = None

    def __init__(self, source, datadir, logger=None):
        self.source = source
        self.datadir = datadir
        self.logger = logger if logger else Logger(source, datadir)

    def fit(self, collector):
        self.logger.err("NOTIMPL:"+str(self.__class__)+":"+Reflector.get_function_name())

        '''
        cd ../../3rdparty_libs/seq2seq

        python -m bin.train ^
        --batch_size 1024 --eval_every_n_steps 5000 ^
        --train_steps 5000000 ^
        --output_dir ../../spycy/talkFellow/data/model ^
        --config_paths="./example_configs/nmt_large.yml,./example_configs/train_seq2seq.yml,../../spycy/talkFellow/data/gutenberg_train_config.yml"
        '''

        '''
        model_params:
        vocab_source: ../../spycy/talkFellow/data/gutenberg.tok
        vocab_target: ../../spycy/talkFellow/data/gutenberg.tok

        input_pipeline_train:
        class: ParallelTextInputPipeline
        params:
            source_files:
            - ../../spycy/talkFellow/data/train/sources.txt
            target_files:
            - ../../spycy/talkFellow/data/train/targets.txt

        input_pipeline_dev:
        class: ParallelTextInputPipeline
        params:
            source_files:
            - ../../spycy/talkFellow/data/dev/sources.txt
            target_files:
            - ../../spycy/talkFellow/data/dev/targets.txt
        '''

    def _tokens_to_str(self, tokens):
        return " ".join(tokens).split("SEQUENCE_END")[0].strip()

    # A hacky way to retrieve prediction result from the task hook...
    prediction_dict = {}
    def _save_prediction_to_dict(self, source_tokens, predicted_tokens):
        self.prediction_dict[self._tokens_to_str(source_tokens)] = self._tokens_to_str(predicted_tokens)

    def load(self, datadir):
        return self._load(os.path.join(self.datadir,'model'))

    def _load(self, model_path):
        checkpoint_path = tf.train.latest_checkpoint(model_path)
        train_options = training_utils.TrainOptions.load(model_path)

        # Create the model
        model_cls = locate(train_options.model_class) or \
            getattr(models, train_options.model_class)
        model_params = train_options.model_params

        model = model_cls(
            params=model_params,
            mode=tf.contrib.learn.ModeKeys.INFER)

        # first dim is batch size
        self.source_tokens_ph = tf.placeholder(dtype=tf.string, shape=(1, None))
        self.source_len_ph = tf.placeholder(dtype=tf.int32, shape=(1,))

        model(
            features={
            "source_tokens": self.source_tokens_ph,
            "source_len": self.source_len_ph
            },
            labels=None,
            params={
            }
        )

        saver = tf.train.Saver()

        def _session_init_op(_scaffold, sess):
            saver.restore(sess, checkpoint_path)
            tf.logging.info("Restored model from %s", checkpoint_path)

        scaffold = tf.train.Scaffold(init_fn=_session_init_op)
        session_creator = tf.train.ChiefSessionCreator(scaffold=scaffold)

        self.session = tf.train.MonitoredSession(
            session_creator=session_creator,
            hooks=[DecodeOnce({}, callback_func=self._save_prediction_to_dict)])

        return self.session, self.source_tokens_ph, self.source_len_ph

    def talk(self, input):
        if input:
            tf.reset_default_graph()
            source_tokens = input.split() + ["SEQUENCE_END"]
            self.session.run([], {
                self.source_tokens_ph: [source_tokens],
                self.source_len_ph: [len(source_tokens)]
            })
            return self.prediction_dict.pop(self._tokens_to_str(source_tokens))
        else:
            return "no question, no answer!"
