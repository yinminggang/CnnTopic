#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os.path
import os
import sys
sys.path.append("/home/fzuir/ymg/CnnTopic/fzuir/util")
import deal_weibo, database_util
import jieba
import jieba.posseg as pseg
import logging
from xml.etree import ElementTree as ET
import time

def constructTestTextAndSplitedWord(conn):
    # 加载过滤词
    filter_read = open("sources/filter_words.dic", mode='r', encoding='utf-8')
    filter_words = set()
    write_flag = 0
    for words in filter_read:
        words = words.strip("\n")
        if words in filter_words:
            write_flag = 1
            logging.info("过滤词典中有重复词:%s" % words)
        filter_words.add(words)
    filter_read.close()
    # 出现了重复词 则要更新过滤词表
    if write_flag == 1:
        filter_write = open("sources/filter_words.dic", mode='w+', encoding='utf-8')
        for word in filter_words:
            filter_write.write(word + "\n")
        filter_write.close()

    jieba.load_userdict("sources/jieba_dict.txt")
    word_attribute = ['n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf', 'nt', 'nz', 'nl', 'ng', 'v', 'vd', 'vn',
                      'vf', 'vx', 'vi', 'vl', 'vg', 'a', 'an', 'ad', 'ag', 'al', 'mg']

    # 从数据库中读表情符号
    expression_list = deal_weibo.readExpression(conn)

    test_date = [201606290000, 201606300000, 201607010000, 201607020000, 201607030000, 201607040000, 201607050000]
    j = 0
    all_splited_write = open("sources/test/all_splited.txt", mode='w+', encoding='utf-8')
    all_text_write = open("sources/test/all_text.txt", mode='w+', encoding='utf-8')
    all_clusterid_write = open("sources/test/all_clusterid.txt", mode='w+', encoding='utf-8')
    while j < 7:
        file_name = test_date[j]
        i = 0
        j += 1
        while i < 24:
            i += 1
            real_file_name = str(file_name)
            file_name += 100
            xml_path = "E:/DLTopicWorkspace/RnnTopic/initTopics/" + real_file_name + ".xml"
            logging.info(xml_path)
            cluster_write = open("sources/test/" + real_file_name + "_clusterid.txt", mode='w+', encoding='utf-8')
            text_write = open("sources/test/" + real_file_name + "_text.txt", mode='w+', encoding='utf-8')
            words_write = open("sources/test/" + real_file_name + "_splited.txt", mode='w+', encoding='utf-8')
            xml = ET.parse(xml_path)
            xml_topics = xml.findall("topic")
            for xml_topic in xml_topics:
                clusterid = xml_topic.find("clusterid").text
                cluster_write.write(clusterid+"\n")
                all_clusterid_write.write(clusterid+"\n")
                docs = xml_topic.find("DocMembers")
                for doc in docs.getchildren():
                    title = doc.text
                    title = deal_weibo.removeExpression(title=title, expression_list=expression_list)
                    title = deal_weibo.dealWeiboContent(title=title)
                    text_write.write(title + "。")
                    all_text_write.write(title + "。")
                    title = deal_weibo.removePunctuation(title=title)
                    seg_list = pseg.cut(title)  # seg_list是生成器generator类型
                    # 去掉过滤词
                    words = ""
                    for seg in seg_list:
                        if seg.flag not in word_attribute:
                            continue
                        w = seg.word.strip()
                        words += " " + w
                    words = words.strip()
                    words_write.write(words + " ")
                    all_splited_write.write(words + " ")
                words_write.write("\n")
                all_splited_write.write("\n")
                text_write.write("\n")
                all_text_write.write("\n")
            text_write.close()
            words_write.close()
            cluster_write.close()
    all_text_write.close()
    all_splited_write.close()
    all_clusterid_write.close()

def newConstructTestTextAndSplitedWord(conn):
    """
    这个修改了一点，主要是对话题微博做了限制，之前是不做限制
    这次限制了微博的时间只能在当前1小时时间段内
    :param conn: 
    :return: 
    """
    # 加载过滤词
    filter_read = open("sources/filter_words.dic", mode='r', encoding='utf-8')
    filter_words = set()
    write_flag = 0
    for words in filter_read:
        words = words.strip("\n")
        if words in filter_words:
            write_flag = 1
            logging.info("过滤词典中有重复词:%s" % words)
        filter_words.add(words)
    filter_read.close()
    # 出现了重复词 则要更新过滤词表
    if write_flag == 1:
        filter_write = open("sources/filter_words.dic", mode='w+', encoding='utf-8')
        for word in filter_words:
            filter_write.write(word + "\n")
        filter_write.close()

    jieba.load_userdict("sources/jieba_dict.txt")
    word_attribute = ['n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf', 'nt', 'nz', 'nl', 'ng', 'v', 'vd', 'vn',
                      'vf', 'vx', 'vi', 'vl', 'vg', 'a', 'an', 'ad', 'ag', 'al', 'mg']

    # 从数据库中读表情符号
    expression_list = deal_weibo.readExpression(conn)

    test_date = [201606290000, 201606300000, 201607010000, 201607020000,
                 201607030000, 201607040000, 201607050000, 201607060000]
    j = 0
    all_splited_write = open("sources/test/all_splited.txt", mode='w+', encoding='utf-8')
    all_text_write = open("sources/test/all_text.txt", mode='w+', encoding='utf-8')
    all_clusterid_write = open("sources/test/all_clusterid.txt", mode='w+', encoding='utf-8')
    is_end = False
    while j < 8 and is_end is False:
        file_name = test_date[j]
        i = 0
        j += 1
        while i < 24 and is_end is False:
            # 最后一天0706，只读一个xml文件即可
            if j == 8:
                is_end = True
            i += 1
            real_file_name = str(file_name)
            file_name += 100
            threshold = 100
            if real_file_name.find("0000") != -1 or real_file_name.find("0100") != -1:
                threshold = 7700
                if real_file_name.find("07010000") != -1 or real_file_name.find("07010100") != -1:
                    threshold = 707700
            xml_path = "initTopics/" + str(real_file_name) + ".xml"
            logging.info(xml_path)
            cluster_write = open("sources/test/" + real_file_name + "_clusterid.txt", mode='w+', encoding='utf-8')
            text_write = open("sources/test/" + real_file_name + "_text.txt", mode='w+', encoding='utf-8')
            words_write = open("sources/test/" + real_file_name + "_splited.txt", mode='w+', encoding='utf-8')
            xml = ET.parse(xml_path)
            xml_topics = xml.findall("topic")
            for xml_topic in xml_topics:
                clusterid = xml_topic.find("clusterid").text
                docs = xml_topic.find("DocMembers")
                no_doc = 1
                for doc in docs.getchildren():
                    title = doc.text
                    doc_time = int(str(doc.get("day")).replace(":", "").replace("-", "").replace(" ", "")[0:12])
                    # 如果微博时间不在当前1个小时时间段内，则不予加入计算
                    if file_name - doc_time - 100 > threshold or doc_time > file_name - 100:
                        continue
                    no_doc = 0
                    title = deal_weibo.removeExpression(title=title, expression_list=expression_list)
                    title = deal_weibo.dealWeiboContent(title=title)
                    text_write.write(title + "。")
                    all_text_write.write(title + "。")
                    title = deal_weibo.removePunctuation(title=title)
                    seg_list = pseg.cut(title)  # seg_list是生成器generator类型
                    # 去掉过滤词
                    words = ""
                    for seg in seg_list:
                        if seg.flag not in word_attribute:
                            continue
                        w = seg.word.strip()
                        words += " " + w
                    words = words.strip()
                    words_write.write(words + " ")
                    all_splited_write.write(words + " ")
                # no_doc=1表示没有一篇微博符合时间限制，这一行不添加
                if no_doc == 1:
                    continue
                cluster_write.write(clusterid + "\n")
                all_clusterid_write.write(clusterid + "\n")
                words_write.write("\n")
                all_splited_write.write("\n")
                text_write.write("\n")
                all_text_write.write("\n")
            text_write.close()
            words_write.close()
            cluster_write.close()
    all_text_write.close()
    all_splited_write.close()
    all_clusterid_write.close()

def newestConstructTestTextAndSplistedWord(conn):
    """
    最新的构建测试集代码，修改以前的读xml文件来构建测试集，
    修改为直接读predict文件夹下的特征.txt文件，
    :param conn: 
    :return: 
    """
    # 加载过滤词
    filter_read = open("sources/filter_words.dic", mode='r', encoding='utf-8')
    filter_words = set()
    write_flag = 0
    for words in filter_read:
        words = words.strip("\n")
        if words in filter_words:
            write_flag = 1
            logging.info("过滤词典中有重复词:%s" % words)
        filter_words.add(words)
    filter_read.close()
    # 出现了重复词 则要更新过滤词表
    if write_flag == 1:
        filter_write = open("sources/filter_words.dic", mode='w+', encoding='utf-8')
        for word in filter_words:
            filter_write.write(word + "\n")
        filter_write.close()

    jieba.load_userdict("sources/jieba_dict.txt")
    word_attribute = ['n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf', 'nt', 'nz', 'nl', 'ng', 'v', 'vd', 'vn',
                      'vf', 'vx', 'vi', 'vl', 'vg', 'a', 'an', 'ad', 'ag', 'al', 'mg']

    # 从数据库中读表情符号
    expression_list = deal_weibo.readExpression(conn)

    test_date = [201606290000, 201606300000, 201607010000, 201607020000,
                 201607030000, 201607040000, 201607050000, 201607060000]
    j = 0
    all_splited_write = open("sources/new_test/all_splited.txt", mode='w+', encoding='utf-8')
    all_text_write = open("sources/new_test/all_text.txt", mode='w+', encoding='utf-8')
    all_clusterid_write = open("sources/new_test/all_clusterid.txt", mode='w+', encoding='utf-8')
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
            # 3小时作为限制
            threshold = 300
            if real_file_name.find("0000") != -1 or real_file_name.find("0100") != -1:
                threshold = 9700
                if real_file_name.find("07010000") != -1 or real_file_name.find("07010100") != -1:
                    threshold = 709700

            xml_path = "initTopics/" + str(real_file_name) + ".xml"
            logging.info(xml_path)
            xml = ET.parse(xml_path)
            xml_topics = xml.findall("topic")
            feature_read = open("predict_feature/" + str(real_file_name) + "trainnew.txt", mode='r', encoding='utf-8')
            id_read = open("predict_feature/" + str(real_file_name) + ".txt", mode='r', encoding='utf-8')
            cluster_write = open("sources/new_test/" + real_file_name + "_clusterid.txt", mode='w+', encoding='utf-8')
            text_write = open("sources/new_test/" + real_file_name + "_text.txt", mode='w+', encoding='utf-8')
            words_write = open("sources/new_test/" + real_file_name + "_splited.txt", mode='w+', encoding='utf-8')
            feature_write = open("sources/new_test/" + real_file_name + "_feature.txt", mode='w+', encoding='utf-8')

            id_line = id_read.readline()
            while id_line:
                if len(id_line) < 2:
                    continue
                cluster_id = str(id_line.split("\t")[0])

                no_cluster = 1
                no_doc = 2
                for xml_topic in xml_topics:
                    clusterid = xml_topic.find("clusterid").text
                    if cluster_id != clusterid:
                        continue
                    no_cluster = 0
                    docs = xml_topic.find("DocMembers")
                    no_doc = 1
                    for doc in docs.getchildren():
                        title = doc.text
                        doc_time = int(str(doc.get("day")).replace(":", "").replace("-", "").replace(" ", "")[0:12])
                        # 如果微博时间不在当前1个小时时间段内，则不予加入计算
                        if file_name - doc_time - 100 > threshold or doc_time > file_name - 100:
                            continue
                        no_doc = 0
                        title = deal_weibo.removeExpression(title=title, expression_list=expression_list)
                        title = deal_weibo.dealWeiboContent(title=title)
                        text_write.write(title + "。")
                        all_text_write.write(title + "。")
                        title = deal_weibo.removePunctuation(title=title)
                        seg_list = pseg.cut(title)  # seg_list是生成器generator类型
                        # 去掉过滤词
                        words = ""
                        for seg in seg_list:
                            if seg.flag not in word_attribute:
                                continue
                            w = seg.word.strip()
                            words += " " + w
                        words = words.strip()
                        words_write.write(words + " ")
                        all_splited_write.write(words + " ")
                    break

                feature_line = feature_read.readline()
                # no_doc=1表示没有一篇微博符合时间限制，这一行不添加
                if no_doc == 1:
                    logging.error("所有的微博都不符合该时间段" + cluster_id)
                elif no_doc == 0:
                    feature_write.write(feature_line)
                    cluster_write.write(clusterid + "\n")
                    all_clusterid_write.write(clusterid + "\n")
                    words_write.write("\n")
                    all_splited_write.write("\n")
                    text_write.write("\n")
                    all_text_write.write("\n")
                if no_cluster == 1:
                    logging.error("xml中没有话题，id为" + cluster_id)
                id_line = id_read.readline()

            text_write.close()
            words_write.close()
            cluster_write.close()
            id_read.close()
            feature_read.close()
            feature_write.close()
    all_text_write.close()
    all_splited_write.close()
    all_clusterid_write.close()

def constructHotTextAndSplitedWord(conn):
    hottopic_read = open("sources/all_hottopic.txt", mode='r', encoding='utf-8')
    text_write = open("sources/train/hottopic_text.txt", mode='w+', encoding='utf-8')
    splitedword_write = open("sources/train/hottopic_splited.txt", mode='w+', encoding='utf-8')
    clusterToTopicDict = {}
    line = hottopic_read.readline()

    # 加载过滤词
    filter_read = open("sources/filter_words.dic", mode='r', encoding='utf-8')
    filter_words = set()
    write_flag = 0
    for words in filter_read:
        words = words.strip("\n")
        if words in filter_words:
            write_flag = 1
            logging.info("过滤词典中有重复词:%s" % words)
        filter_words.add(words)
    filter_read.close()
    # 出现了重复词 则要更新过滤词表
    if write_flag == 1:
        filter_write = open("sources/filter_words.dic", mode='w+', encoding='utf-8')
        for word in filter_words:
            filter_write.write(word + "\n")
        filter_write.close()

    jieba.load_userdict("sources/jieba_dict.txt")
    word_attribute = ['n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf', 'nt', 'nz', 'nl', 'ng', 'v', 'vd', 'vn',
                      'vf', 'vx', 'vi', 'vl', 'vg', 'a', 'an', 'ad', 'ag', 'al', 'mg']

    # 从数据库中读表情符号
    expression_list = deal_weibo.readExpression(conn)
    while line:
        real_cluster_ids = []
        split_line = line.split("\t")
        timestamp = int(split_line[0]) * 60
        topic_id = split_line[1]
        if topic_id in clusterToTopicDict.keys():
            # 开始解析相对应时间的xml文档
            real_cluster_ids = clusterToTopicDict[topic_id]
        else:
            cluster_ids = conn.queryData("select childTopicid from topicmanual a,topicmanual_topic b "
                                         "where a.id=b.topicid and a.id=" + topic_id)
            for id in cluster_ids:
                real_cluster_ids.append(str(id[0]))
            clusterToTopicDict[topic_id] = real_cluster_ids

        # 求下一个小时的时间戳
        timestamp += 3600
        timeArray = time.localtime(timestamp)
        real_xml_path = "E:/DLTopicWorkspace/RnnTopic/initTopics/" + time.strftime("%Y%m%d%H", timeArray) + "00.xml"
        logging.info(real_xml_path)
        # 开始解析xml文件
        xml = ET.parse(real_xml_path)
        xml_topics = xml.findall("topic")
        for xml_topic in xml_topics:
            clusterid = xml_topic.find("clusterid").text
            # 如果clusterid不是在cluster_ids中，则忽略
            if clusterid not in real_cluster_ids:
                continue
            # 开始获取该话题簇的微博文本
            docs = xml_topic.find("DocMembers")
            for doc in docs.getchildren():
                title = doc.text
                title = deal_weibo.removeExpression(title=title, expression_list=expression_list)
                title = deal_weibo.dealWeiboContent(title=title)
                text_write.write(title + "。")
                title = deal_weibo.removePunctuation(title=title)
                seg_list = pseg.cut(title)  # seg_list是生成器generator类型
                # 去掉过滤词
                words = ""
                for seg in seg_list:
                    if seg.flag not in word_attribute:
                        continue
                    w = seg.word.strip()
                    words += " " + w
                words = words.strip()
                splitedword_write.write(words + " ")

        text_write.write("\n")
        splitedword_write.write("\n")
        line = hottopic_read.readline()

    text_write.close()
    hottopic_read.close()
    splitedword_write.close()

def newConstructHotTextAndSplitedWord(conn):
    """
    同样的道理，对微博文本进行了时间限制，限制当前话题的当前时刻的微博时间只能是当前1小时内
    并且还对话题id和特征进行保存
    :param conn: 
    :return: 
    """
    hottopic_read = open("sources/all_hottopic.txt", mode='r', encoding='utf-8')
    text_write = open("sources/train/hottopic_text.txt", mode='w+', encoding='utf-8')
    splitedword_write = open("sources/train/hottopic_splited.txt", mode='w+', encoding='utf-8')
    feature_write = open("sources/train/hottopic_feature.txt", mode='w+', encoding='utf-8')
    clusterToTopicDict = {}
    line = hottopic_read.readline()

    # 加载过滤词
    filter_read = open("sources/filter_words.dic", mode='r', encoding='utf-8')
    filter_words = set()
    write_flag = 0
    for words in filter_read:
        words = words.strip("\n")
        if words in filter_words:
            write_flag = 1
            logging.info("过滤词典中有重复词:%s" % words)
        filter_words.add(words)
    filter_read.close()
    # 出现了重复词 则要更新过滤词表
    if write_flag == 1:
        filter_write = open("sources/filter_words.dic", mode='w+', encoding='utf-8')
        for word in filter_words:
            filter_write.write(word + "\n")
        filter_write.close()

    jieba.load_userdict("sources/jieba_dict.txt")
    word_attribute = ['n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf', 'nt', 'nz', 'nl', 'ng', 'v', 'vd', 'vn',
                      'vf', 'vx', 'vi', 'vl', 'vg', 'a', 'an', 'ad', 'ag', 'al', 'mg']

    # 从数据库中读表情符号
    expression_list = deal_weibo.readExpression(conn)
    while line:
        real_cluster_ids = []
        split_line = line.split("\t")
        timestamp = int(split_line[0]) * 60
        topic_id = split_line[1]
        if topic_id in clusterToTopicDict.keys():
            # 开始解析相对应时间的xml文档
            real_cluster_ids = clusterToTopicDict[topic_id]
        else:
            cluster_ids = conn.queryData("select childTopicid from topicmanual a,topicmanual_topic b "
                                         "where a.id=b.topicid and a.id=" + topic_id)
            for id in cluster_ids:
                real_cluster_ids.append(str(id[0]))
            clusterToTopicDict[topic_id] = real_cluster_ids

        # 求下一个小时的时间戳
        next_timestamp = timestamp + 3600
        timeArray = time.localtime(next_timestamp)
        real_xml_path = "initTopics/" + time.strftime("%Y%m%d%H", timeArray) + "00.xml"
        logging.info(real_xml_path)
        # 开始解析xml文件
        xml = ET.parse(real_xml_path)
        xml_topics = xml.findall("topic")
        no_doc = 1
        for xml_topic in xml_topics:
            clusterid = xml_topic.find("clusterid").text
            # 如果clusterid不是在cluster_ids中，则忽略
            if clusterid not in real_cluster_ids:
                continue
            # 开始获取该话题簇的微博文本
            docs = xml_topic.find("DocMembers")
            for doc in docs.getchildren():
                title = doc.text
                doc_time = str(doc.get("day"))[0:19]
                doc_timestamp = time.mktime(time.strptime(doc_time, '%Y-%m-%d %H:%M:%S'))
                # 如果微博时间不在当前3个小时的时间段内，则不予加入计算
                if doc_timestamp < timestamp - 7200 or doc_timestamp > next_timestamp:
                    continue
                no_doc = 0
                title = deal_weibo.removeExpression(title=title, expression_list=expression_list)
                title = deal_weibo.dealWeiboContent(title=title)
                text_write.write(title + "<sssss>")
                title = deal_weibo.removePunctuation(title=title)
                seg_list = pseg.cut(title)  # seg_list是生成器generator类型
                # 去掉过滤词
                words = ""
                for seg in seg_list:
                    if seg.flag not in word_attribute:
                        continue
                    w = seg.word.strip()
                    words += " " + w
                words = words.strip()
                splitedword_write.write(words + " ")
        if no_doc == 0:
            feature_write.write(line.strip()+"\n")
            text_write.write("\n")
            splitedword_write.write("\n")
        line = hottopic_read.readline()

    text_write.close()
    hottopic_read.close()
    splitedword_write.close()
    feature_write.close()

def constructNegativeTextAndSplitedWord(conn):
    negative_read = open("sources/select_negative.txt", mode='r', encoding='utf-8')
    splitedword_write = open("sources/train/negative_splited.txt", mode='w+', encoding='utf-8')
    text_write = open("sources/train/negative_text.txt", mode='w+', encoding='utf-8')
    line = negative_read.readline()

    # 加载过滤词
    filter_read = open("sources/filter_words.dic", mode='r', encoding='utf-8')
    filter_words = set()
    write_flag = 0
    for words in filter_read:
        words = words.strip("\n")
        if words in filter_words:
            write_flag = 1
            logging.info("过滤词典中有重复词:%s" % words)
        filter_words.add(words)
    filter_read.close()
    # 出现了重复词 则要更新过滤词表
    if write_flag == 1:
        filter_write = open("sources/filter_words.dic", mode='w+', encoding='utf-8')
        for word in filter_words:
            filter_write.write(word + "\n")
        filter_write.close()

    jieba.load_userdict("sources/jieba_dict.txt")
    word_attribute = ['n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf', 'nt', 'nz', 'nl', 'ng', 'v', 'vd', 'vn',
                      'vf', 'vx', 'vi', 'vl', 'vg', 'a', 'an', 'ad', 'ag', 'al', 'mg']
    # 从数据库中读表情符号
    expression_list = deal_weibo.readExpression(conn)

    while line:
        line_split = line.split("\t")
        topic_id = line_split[1]
        xml_path = "E:/DLTopicWorkspace/RnnTopic/initTopics/" + line_split[0].strip() + ".xml"
        logging.info(xml_path)
        # 开始解析xml文件
        xml = ET.parse(xml_path)
        xml_topics = xml.findall("topic")
        for xml_topic in xml_topics:
            clusterid = xml_topic.find("clusterid").text
            # 如果clusterid不等于clusterid中，则忽略
            if clusterid != topic_id:
                continue

            # 开始获取该话题簇的微博文本
            docs = xml_topic.find("DocMembers")
            for doc in docs.getchildren():
                title = doc.text
                title = deal_weibo.removeExpression(title=title, expression_list=expression_list)
                title = deal_weibo.dealWeiboContent(title=title)
                text_write.write(title+"。")
                title = deal_weibo.removePunctuation(title=title)
                seg_list = pseg.cut(title)  # seg_list是生成器generator类型
                # 去掉过滤词
                words = ""
                for seg in seg_list:
                    if seg.flag not in word_attribute:
                        continue
                    w = seg.word.strip()
                    words += " " + w
                words = words.strip()
                splitedword_write.write(words + " ")
            break
        text_write.write("\n")
        splitedword_write.write("\n")
        line = negative_read.readline()

    splitedword_write.close()
    text_write.close()
    negative_read.close()

def newConstructNegativeTextAndSplitedWord(conn):
    """
    同样的道理，对微博文本进行了时间限制，限制当前话题的当前时刻的微博时间只能是当前1小时内
    并且还对话题id和特征进行保存
    :param conn: 
    :return: 
    """
    negative_read = open("sources/all_negative.txt", mode='r', encoding='utf-8')
    splitedword_write = open("sources/train/all_negative_splited.txt", mode='w+', encoding='utf-8')
    text_write = open("sources/train/all_negative_text.txt", mode='w+', encoding='utf-8')
    feature_write = open("sources/train/all_negative_feature.txt", mode='w+', encoding='utf-8')
    line = negative_read.readline()

    # 加载过滤词
    filter_read = open("sources/filter_words.dic", mode='r', encoding='utf-8')
    filter_words = set()
    write_flag = 0
    for words in filter_read:
        words = words.strip("\n")
        if words in filter_words:
            write_flag = 1
            logging.info("过滤词典中有重复词:%s" % words)
        filter_words.add(words)
    filter_read.close()
    # 出现了重复词 则要更新过滤词表
    if write_flag == 1:
        filter_write = open("sources/filter_words.dic", mode='w+', encoding='utf-8')
        for word in filter_words:
            filter_write.write(word + "\n")
        filter_write.close()

    jieba.load_userdict("sources/jieba_dict.txt")
    word_attribute = ['n', 'nr', 'nr1', 'nr2', 'nrj', 'nrf', 'ns', 'nsf', 'nt', 'nz', 'nl', 'ng', 'v', 'vd', 'vn',
                      'vf', 'vx', 'vi', 'vl', 'vg', 'a', 'an', 'ad', 'ag', 'al', 'mg']
    # 从数据库中读表情符号
    expression_list = deal_weibo.readExpression(conn)

    while line:
        line_split = line.split("\t")
        topic_id = line_split[1]
        file_name = line_split[0].strip()
        threshold = 100
        if file_name.find("0000") != -1 or file_name.find("0100") != -1:
            threshold = 7700
            if file_name.find("07010000") != -1 or file_name.find("07010100") != -1:
                threshold = 707700
        xml_path = "initTopics/" + file_name + ".xml"
        logging.info(xml_path)
        # 开始解析xml文件
        xml = ET.parse(xml_path)
        xml_topics = xml.findall("topic")
        no_doc = 1
        for xml_topic in xml_topics:
            clusterid = xml_topic.find("clusterid").text
            # 如果clusterid不等于clusterid中，则忽略
            if clusterid != topic_id:
                continue

            # 开始获取该话题簇的微博文本
            docs = xml_topic.find("DocMembers")
            for doc in docs.getchildren():
                title = doc.text
                doc_time = int(str(doc.get("day")).replace(":", "").replace("-", "").replace(" ", "")[0:12])
                # 如果微博时间不在当前1个小时时间段内，则不予加入计算
                if int(file_name) - doc_time > threshold or doc_time > int(file_name):
                    continue
                no_doc = 0
                title = deal_weibo.removeExpression(title=title, expression_list=expression_list)
                title = deal_weibo.dealWeiboContent(title=title)
                text_write.write(title+"<sssss>")
                title = deal_weibo.removePunctuation(title=title)
                seg_list = pseg.cut(title)  # seg_list是生成器generator类型
                # 去掉过滤词
                words = ""
                for seg in seg_list:
                    if seg.flag not in word_attribute:
                        continue
                    w = seg.word.strip()
                    words += " " + w
                words = words.strip()
                splitedword_write.write(words + " ")
            break
        if no_doc == 0:
            feature_write.write(line.strip()+"\n")
            text_write.write("\n")
            splitedword_write.write("\n")
        line = negative_read.readline()

    splitedword_write.close()
    text_write.close()
    negative_read.close()
    feature_write.close()


if __name__ == '__main__':
    conn = database_util.ConnMysql("59.77.233.198", 3306, "root", "mysql_fzu_118", "HotTopic")
    conn.connectMysql()
    logging.basicConfig(filename="logs/new_construct_data.log", format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)

    # newConstructHotTextAndSplitedWord(conn)
    newConstructNegativeTextAndSplitedWord(conn)
    # newConstructTestTextAndSplitedWord(conn)
    # newestConstructTestTextAndSplistedWord(conn)

    conn.closeMysql()

