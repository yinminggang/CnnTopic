# -*- coding:utf-8 -*-

import numpy as np
import re
import itertools
from collections import Counter

def cleanStr(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

def loadTestData(test_data_file):
    data_read = open(test_data_file, mode='r', encoding='utf-8')
    line_data = []
    line = data_read.readline()
    while line:
        line_data.append(line.strip())
        line = data_read.readline()
    data_read.close()
    return line_data

def loadDataAndLabels(positive_data_file, negative_data_file):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    # Load data from files
    positive_examples = list(open(positive_data_file, "r", encoding='utf-8').readlines())
    positive_examples = [s.strip() for s in positive_examples]
    negative_examples = list(open(negative_data_file, "r", encoding='utf-8').readlines())
    negative_examples = [s.strip() for s in negative_examples]
    # Split by words
    x_text = positive_examples + negative_examples
    x_text = [cleanStr(sent) for sent in x_text]
    # Generate labels
    positive_labels = [[0, 1] for _ in positive_examples]
    negative_labels = [[1, 0] for _ in negative_examples]
    y = np.concatenate([positive_labels, negative_labels], 0)
    # data_labels = open("./data/rt-polaritydata/data_labes.txt", mode='w+', encoding='utf-8')
    # i = 0
    # for line in x_text:
    #     data_labels.write(str(y[i])+"\t"+str(line)+"\n")
    #     i += 1
    #
    # data_labels.close()
    return [x_text, y]


def batchIter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            # 一个带有 yield 的函数就是一个 generator，它和普通函数不同，
            # 生成一个 generator 看起来像函数调用，但不会执行任何函数代码，
            # 直到对其调用 next()（在 for 循环中会自动调用 next()）才开始执行。
            yield shuffled_data[start_index:end_index]

if __name__ == '__main__':
    loadDataAndLabels("./data/rt-polaritydata/rt-polarity.pos", "./data/rt-polaritydata/rt-polarity.neg")