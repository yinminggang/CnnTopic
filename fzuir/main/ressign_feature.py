# -*- coding: utf-8 -*-

import logging
def constrcutNewFeature(model_name):
    """
    根据doc2vector模型，求得各个话题的特征向量，
    现在需要将这些特征加到以前的特征上，以便于matlab训练预测
    model_name为模型名称：PV-DM  或者PV-DBOW
    :return: 
    """
    doc2vec_read = open("word2vec/"+model_name+"_doc2vec.vector", mode='r', encoding='utf-8')
    traindata_write = open("sources/train/"+model_name+"_traindata.txt", mode='w+', encoding='utf-8')
    hottopic_read = open("sources/train/hottopic_feature.txt", mode='r', encoding='utf-8')
    negative_read = open("sources/train/negative_feature.txt", mode='r', encoding='utf-8')
    line_num = 0
    # 热点话题特征
    hot_line = hottopic_read.readline()
    while hot_line:
        line_num += 1
        # 得到8个特征
        write_line = "1 "+hot_line.replace("\t", " ").strip()[-71:]
        doc2vec_line = doc2vec_read.readline()
        vec_split = doc2vec_line.strip().split(" ")
        # 拼接doc向量到特征后面，并加上序号
        i = 9
        for vec in vec_split:
            write_line += " " + str(i) + ":"+vec
            i += 1
        traindata_write.write(write_line.strip()+"\n")
        hot_line = hottopic_read.readline()
    hottopic_read.close()
    logging.info("=========热点话题特征数目为：%s" % line_num)

    # 非热点话题特征
    negative_line = negative_read.readline()
    while negative_line:
        line_num += 1
        write_line = negative_line.replace("\t", " ").strip()[-74:]
        doc2vec_line = doc2vec_read.readline()
        vec_split = doc2vec_line.strip().split(" ")
        # 拼接doc向量到特征后面，并加上序号
        i = 9
        for vec in vec_split:
            write_line += " " + str(i) + ":" + vec
            i += 1
        traindata_write.write(write_line.strip()+"\n")
        negative_line = negative_read.readline()
    negative_read.close()
    traindata_write.close()
    logging.info("==========热点话题与非热点话题总条数为：%s" % line_num)

    # 开始写测试集的特征
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
            feature_read = open("sources/new_test/" + str(file_name) + "_feature.txt", mode='r', encoding='utf-8')
            new_feature_write = open("sources/new_test/" + model_name + str(file_name) + "_newfeature.txt", mode='w+', encoding='utf-8')
            write_line = feature_read.readline().strip()
            while write_line:
                line_num += 1
                doc2vec_line = doc2vec_read.readline()
                vec_split = doc2vec_line.strip().split(" ")
                # 拼接doc向量到特征后面，并加上序号
                num = 9
                for vec in vec_split:
                    write_line += "\t" + str(num) + ":" + vec
                    num += 1
                new_feature_write.write(write_line.strip() + "\n")
                write_line = feature_read.readline().strip()
            feature_read.close()
            new_feature_write.close()
            file_name += 100
    doc2vec_read.close()
    logging.info("所有的数据条数为：%s" % line_num)

if __name__ == '__main__':
    logging.basicConfig(filename="logs/newfeature.log", format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    # PV-DM(分布记忆模型)  或者PV-DBOW(分布词袋模型)
    constrcutNewFeature("PV-DM")