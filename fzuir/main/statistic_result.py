# -*- coding:utf-8 -*-

import logging
from fzuir.util import database_util

def readPredict(predict_dir, cluster_id_dir):
    predict_date = [201606290000, 201606300000, 201607010000, 201607020000,
                    201607030000, 201607040000, 201607050000, 201607060000]
    j = 0
    # 定义一个字典，存储话题簇id和时间
    clusterIdTime = {}
    is_end = False
    while j < 8 and is_end is False:
        file_name = predict_date[j]
        i = 0
        j += 1
        while i < 24 and is_end is False:
            # 最后一天0706，只读一个文件即可
            if j == 8:
                is_end = True
            i += 1
            real_file_name = str(file_name)
            predict_read = open(predict_dir+real_file_name+"prediction.txt", mode='r', encoding='utf-8')
            clusterid_read = open(cluster_id_dir+real_file_name+"_clusterid.txt", mode='r', encoding='utf-8')
            id_line = clusterid_read.readline().strip()
            while id_line:
                predict_line = str(predict_read.readline()).strip()
                if len(predict_line) < 5:
                    continue
                # 如果已经存在该话题簇id,则不需要再记录，因为已经记录下了最早时间
                if id_line in clusterIdTime:
                    id_line = clusterid_read.readline().strip()
                    continue
                # 表示预测为新兴话题。取predict_line最后4个字符
                if predict_line[-4:] == ",0.0":
                    # 存储整数类型，方便后面比较大小
                    clusterIdTime[id_line] = file_name
                id_line = clusterid_read.readline().strip()
            file_name += 100
            predict_read.close()
            clusterid_read.close()

    logging.warning("*********算法共预测到"+str(len(clusterIdTime))+"个话题簇****************\n")
    logging.info("现在要将话题簇转换为话题id，去数据库表中匹配")

    predict_topic = []  # 算法预测的新兴话题
    len_not_topic = 0  # 预测的话题在标注的话题中不存在
    not_emerging_topic = []  # 预测的新兴话题在数据库中不是新兴话题
    emerging_topic = []  # 预测的新兴话题，在数据库中也是新兴话题
    mid_topic = []    # 预测的新兴话题，时间比tmid提早
    hot_topic = []  # 预测的新兴话题，时间比thot提早
    out_mid_date_topic = []  # 预测的新兴话题，对tmid是过时的话题
    out_hot_date_topic = []  # 预测的新兴话题，对thot是过时的话题
    conn = database_util.ConnMysql("59.77.233.198", 3306, "root", "mysql_fzu_118", "HotTopic")
    conn.connectMysql()
    for clusterid in clusterIdTime:
        topic = list(conn.queryData("select a.id,a.topicStatus,a.tmid,a.thot from topicmanual a,topicmanual_topic b "
                                    "where a.id=b.topicid and b.childTopicid=" + clusterid))
        if len(topic) < 1:
            len_not_topic += 1
        continue
        topic_id = topic[0][0]
        if topic_id in predict_topic:
            continue
        status = int(topic[0][1])
        # 2016-06-29 10:10:10 --> 201606291010
        tmid = int(str(topic[0][2]).replace("-", "").replace(":", "").replace(" ", "").strip()[0:10])
        thot = int(str(topic[0][3]).replace("-", "").replace(":", "").replace(" ", "").strip()[0:10])
        predict_time = clusterIdTime[clusterid]

        predict_topic.append(topic_id)
        if status == 0:
            not_emerging_topic.append(topic_id)
        elif status == 1:
            emerging_topic.append(topic_id)
            if tmid >= predict_time:
                mid_topic.append(topic_id)
                hot_topic.append(topic_id)
            elif thot >= predict_time:
                out_mid_date_topic.append(topic_id)
                hot_topic.append(topic_id)
            else:
                out_hot_date_topic.append(topic_id)


    conn.closeMysql()
    len_predict_topic = len(predict_topic)
    len_not_emerging_topic = len(not_emerging_topic)
    len_emerging_topic = len(emerging_topic)
    len_mid_topic = len(mid_topic)
    len_out_mid_date_topic = len(out_mid_date_topic)
    len_hot_topic = len(hot_topic)
    len_out_hot_date_topic = len(out_hot_date_topic)
    logging.warning("***********分析结果如下**************\n")
    logging.info("预测到的话题个数为：" + str(len_predict_topic))
    logging.info("人工标注中，后7天的话题个数为：65")
    logging.info("预测的话题不在人工标注话题中的个数为：" + str(len_not_topic))
    logging.info("预测为新兴话题，而人工为非新兴话题，个数为：" + str(len_not_emerging_topic))
    logging.info("预测为新兴话题，人工也为新兴话题，个数为：" + str(len_emerging_topic))
    logging.info("预测的话题比中间时刻tmid话题要早，个数为：" + str(len_mid_topic))
    logging.info("预测的话题比中间时刻tmid话题要晚(相当于预测失败)，个数为：" + str(len_out_mid_date_topic))
    logging.info("预测的话题比热门时刻thot话题要早，个数为：" + str(len_hot_topic))
    logging.info("预测的话题比中间时刻thot话题要晚(相当于预测失败)，个数为：" + str(len_out_hot_date_topic))
    logging.warning("***************************************\n")
    logging.warning("***********计算结果如下**************\n")
    logging.warning("*******tmid******\n")
    mid_precision = len_mid_topic / (len_mid_topic+len_not_topic+len_not_emerging_topic)
    mid_recall = len_mid_topic / 65
    logging.info("准确率：%s / %s+%s+%s " % (len_mid_topic, len_mid_topic, len_not_topic,len_not_emerging_topic) +
                 "=" + str(mid_precision))
    logging.info("召回率：%s / 65 " % len_mid_topic + "=" + str(mid_recall))
    logging.info("F1值：" + str((2*mid_precision*mid_recall)/(mid_precision+mid_recall)))
    logging.warning("***************************************\n")
    logging.warning("*******thot******\n")
    hot_precision = len_hot_topic / (len_hot_topic + len_not_topic + len_not_emerging_topic)
    hot_recall = len_hot_topic / 65
    logging.info("准确率：%s / %s+%s+%s " % (len_hot_topic, len_hot_topic, len_not_topic, len_not_emerging_topic) +
                 "=" + str(hot_precision))
    logging.info("召回率：%s / 65 " % len_hot_topic + "=" + str(hot_recall))
    logging.info("F1值：" + str((2 * hot_precision * hot_recall) / (hot_precision + hot_recall)))
    logging.warning("***************************************\n")

if __name__ == '__main__':
    logging.basicConfig(filename="logs/result1.txt", format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    predict_dir = "runs/1500087757/predict/"
    cluster_id_dir = "sources/new_test/"
    readPredict(predict_dir=predict_dir, cluster_id_dir=cluster_id_dir)