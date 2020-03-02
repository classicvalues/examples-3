# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Text classification demo code of Model Maker for TFLite."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from absl import app
from absl import flags
from absl import logging

import tensorflow as tf # TF2
from tensorflow_examples.lite.model_maker.core.data_util.text_dataloader import TextClassifierDataLoader
from tensorflow_examples.lite.model_maker.core.task import text_classifier
from tensorflow_examples.lite.model_maker.core.task.model_spec import BertModelSpec

flags.DEFINE_string('tflite_filename', None, 'File name to save tflite model.')
flags.DEFINE_string('label_filename', None, 'File name to save labels.')
flags.DEFINE_string('vocab_filename', None, 'File name to save vocabulary.')
FLAGS = flags.FLAGS


def main(_):
  logging.set_verbosity(logging.INFO)

  data_path = tf.keras.utils.get_file(
      fname='sst.tar.gz',
      origin='https://firebasestorage.googleapis.com/v0/b/mtl-sentence-representations.appspot.com/o/data%2FSST-2.zip?alt=media&token=aabc5f6b-e466-44a2-b9b4-cf6337f84ac8',
      extract=True)
  data_path = os.path.join(os.path.dirname(data_path), 'SST-2')

  # Chooses model specification that represents model.
  model_spec = BertModelSpec()

  # Gets training data and validation data.
  train_data = TextClassifierDataLoader.from_csv(
      filename=os.path.join(os.path.join(data_path, 'train.tsv')),
      text_column='sentence',
      label_column='label',
      model_spec=model_spec,
      delimiter='\t')
  validation_data = TextClassifierDataLoader.from_csv(
      filename=os.path.join(os.path.join(data_path, 'dev.tsv')),
      text_column='sentence',
      label_column='label',
      model_spec=model_spec,
      delimiter='\t')

  # Fine-tunes the model.
  model = text_classifier.create(
      train_data, model_spec=model_spec, validation_data=validation_data)

  # Gets evaluation results.
  _, acc = model.evaluate(validation_data)
  print('Eval accuracy: %f' % acc)

  # Exports to TFLite format.
  model.export(FLAGS.tflite_filename, FLAGS.label_filename,
               FLAGS.vocab_filename)


if __name__ == '__main__':
  assert tf.__version__.startswith('2')
  flags.mark_flag_as_required('tflite_filename')
  flags.mark_flag_as_required('label_filename')
  flags.mark_flag_as_required('vocab_filename')
  app.run(main)