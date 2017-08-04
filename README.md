# CnnTopic
Using CNN for prediction of Emerging Hot Topic. Moreover, using word2vec and doc2vec for word embedding

数据：新浪微博
参照：文章Convolutional Neural Networks for Sentences Classification(EMNLP2014)
forked called cnn-text-classificatin-tf in github
其实更想用原作者kim的theano版本
（1）根据dl_hottopic.txt文件，来构造新兴热点话题的数据集
聚类结果xml文件命名，比如201606220100.xml表示比如201606220000-201606220100这段时间内的微博聚类结果。
所以在dl_hottopic.txt文件中读取的话题特征时间戳，应该要在后一个xml文件中读取相应话题信息
（2）根据select_negative.txt文件来构建非新兴热点话题的特征数据集，negative中特征是什么时间就加载哪一个xml文件

（3）训练模型，给遍历赋值好相应路径，python3 train.py