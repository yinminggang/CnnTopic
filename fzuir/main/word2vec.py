# -*- coding:utf-8
from gensim.models import Word2Vec, Doc2Vec
from gensim.models.word2vec import LineSentence
from gensim.models.doc2vec import TaggedLineDocument
import logging
import multiprocessing

def trainWord2Vector(splitedword_path, sentence_count, vector_dimension, train_count):
    model_out, vector_out = "word2vec/BOW_word2vec.model", "word2vec/BOW_word2vec.txt"
    logging.info("start word2vector training data")
    sentences = LineSentence(splitedword_path)

    # 注意min_count=3表示词频小于3的词 不做计算，，也不会保存到word2vec.vector中
    # workers是训练的进程数，一般等于CPU核数  默认是3
    # sg=1 表示用skip-gram算法，sg=0表示用BOW算法
    model = Word2Vec(sentences, sg=0, size=vector_dimension, window=8,
                     min_count=0, workers=multiprocessing.cpu_count())
    # 多训练几次  使得效果更好
    for i in range(train_count):
        model.train(sentences=sentences, total_examples=sentence_count, epochs=model.iter)

    # trim unneeded model memory = use(much) less RAM
    # model.init_sims(replace=True)
    model.save(model_out)
    model.wv.save_word2vec_format(fname=vector_out)
    logging.info("end word2vector")

def trainDoc2Vector(splitedword_path, sentence_count, vector_dimension, train_count):
    logging.info("start doc2vector training data")
    sentences = TaggedLineDocument(splitedword_path)
    model = Doc2Vec(sentences, size=vector_dimension, dm=0,
                    window=8, min_count=2, workers=multiprocessing.cpu_count())

    for i in range(train_count):
        model.train(sentences, total_examples=sentence_count, epochs=model.iter)

    model.save('word2vec/PV-DBOW_doc2vec.model')
    # save vectors
    out = open('word2vec/PV-DBOW_doc2vec.vector', mode='w+', encoding='utf-8')
    for index in range(0, sentence_count, 1):
        docvec = model.docvecs[index]
        out.write(' '.join(str(f) for f in docvec) + "\n")
    out.close()
    # with open('', mode='w', encoding='utf-8') as f:
    #     f.write(model.docvecs)
    logging.info("end doc2vector")

if __name__ == '__main__':
    logging.basicConfig(filename="logs/word2vector.log", format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    trainWord2Vector(splitedword_path='sources/new_all_splited.txt',
                     sentence_count=16041, vector_dimension=100, train_count=30)
    logging.info("\n===============================\n")
    trainDoc2Vector(splitedword_path='sources/new_all_splited.txt',
                    sentence_count=16041, vector_dimension=100, train_count=30)