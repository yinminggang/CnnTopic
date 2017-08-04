#! /usr/bin/python3
# -*- coding:utf-8 -*-

import os
import time
import datetime
from cnn import TextCNN
import sys
# sys.path.append("/home/fzuir/ymg/CnnTopic/fzuir/util")
sys.path.append("E:/DLTopicWorkspace/CnnTopic/fzuir/util")
import deal_traindata
import tensorflow as tf
import numpy as np
from tensorflow.contrib import learn
import csv
import logging

# Parameters
# ==================================================

# Data Parameters
tf.flags.DEFINE_string("positive_data_file", "sources/train/hottopic_text.txt", "Data source for the positive data.")
tf.flags.DEFINE_string("negative_data_file", "sources/train/negative_text.txt", "Data source for the positive data.")

# Eval Parameters
tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_string("checkpoint_dir", "", "Checkpoint directory from training run")
tf.flags.DEFINE_boolean("eval_train", False, "Evaluate on all training data")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")

logging.basicConfig(filename="logs/predict.log", format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)

FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
logging.info("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
    logging.info("{}={}".format(attr.upper(), value))
logging.info("")

test_date = [201606290000, 201606300000, 201607010000, 201607020000,
             201607030000, 201607040000, 201607050000, 201607060000]
j = 0
is_end = False
while j < 8 and is_end is False:
    file_name = test_date[j]
    i = 0
    j += 1
    while i < 24 and is_end is False:
        # 最后一天0706，只读一个文件即可
        if j == 8:
            is_end = True
        i += 1
        real_file_name = str(file_name)
        file_name += 100

        y_test = None
        # CHANGE THIS: Load data. Load your own data here
        if FLAGS.eval_train:
            x_raw, y_test = deal_traindata.loadDataAndLabels(FLAGS.positive_data_file, FLAGS.negative_data_file)
            y_test = np.argmax(y_test, axis=1)
        else:
            x_raw = deal_traindata.loadTestData("sources/new_test/"+real_file_name+"_text.txt")
            # x_raw = ["a masterpiece four years in the making", "everything is off."]
            # y_test = [1, 0]

        # Map data into vocabulary
        vocab_path = os.path.join(FLAGS.checkpoint_dir, "..", "vocab")
        vocab_processor = learn.preprocessing.VocabularyProcessor.restore(vocab_path)
        x_test = np.array(list(vocab_processor.transform(x_raw)))

        logging.info("\nEvaluating...\n")

        # Evaluation
        # ==================================================
        checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
        # tensorflow中的计算以图数据流的方式表示一个图,包含一系列表示计算单元的操作对象
        # 以及在图中流动的数据单元以tensor对象表现
        graph = tf.Graph()
        # 一个将某图设置为默认图，并返回一个上下文管理器
        # 如果不显式添加一个默认图，系统会自动设置一个全局的默认图。
        with graph.as_default():
            session_conf = tf.ConfigProto(
                allow_soft_placement=FLAGS.allow_soft_placement,
                log_device_placement=FLAGS.log_device_placement)
            sess = tf.Session(config=session_conf)
            with sess.as_default():
                # Load the saved meta graph and restore variables
                # 加载训练好的网络图结构
                saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
                saver.restore(sess, checkpoint_file)

                # Get the placeholders from the graph by name
                # 根据名称返回操作节点
                input_x = graph.get_operation_by_name("input_x").outputs[0]
                # input_y = graph.get_operation_by_name("input_y").outputs[0]
                dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

                features = graph.get_tensor_by_name("features").outputs[0]

                # Tensors we want to evaluate
                predictions = graph.get_operation_by_name("output/predictions").outputs[0]

                # Generate batches for one epoch
                batches = deal_traindata.batchIter(list(x_test), FLAGS.batch_size, 1, shuffle=False)

                # Collect the predictions here
                all_predictions = []

                for x_test_batch in batches:
                    batch_predictions, final_features = sess.run([predictions, features], {input_x: x_test_batch, dropout_keep_prob: 1.0})
                    logging.error(type(final_features))
                    logging.error(final_features)
                    all_predictions = np.concatenate([all_predictions, batch_predictions])

        # Print accuracy if y_test is defined
        if y_test is not None:
            correct_predictions = float(sum(all_predictions == y_test))
            logging.info("Total number of test examples: {}".format(len(y_test)))
            logging.info("Accuracy: {:g}".format(correct_predictions/float(len(y_test))))

        # Save the evaluation to a csv
        predictions_human_readable = np.column_stack((np.array(x_raw), all_predictions))
        out_path = os.path.join(FLAGS.checkpoint_dir, "../predict/", real_file_name+"prediction.txt")
        logging.info("Saving evaluation to {0}".format(out_path))
        with open(out_path, mode='w', encoding='utf-8') as f:
            csv.writer(f).writerows(predictions_human_readable)

