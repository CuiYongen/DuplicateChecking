# coding=utf-8

import codecs
import numpy as np
import jieba
import jieba.analyse
from collections import OrderedDict
import os
import pymongo

import sys
sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/flk_mdb")
from flk_mdb import *

mongo = pymongo.MongoClient('127.0.0.1', 27017)
mdb = mongo.test

# 计算汉明距离
def hammingDis(simhash1, simhash2):
    t1 = '0b' + simhash1
    t2 = '0b' + simhash2
    n = int(t1, 2) ^ int(t2, 2)
    i = 0
    while n:
        n &= (n-1)
        i += 1
    # print("hammingDis() executed!")
    return i

# 哈希函数
def string_hash(source):
    if source == '':
        return 0
    else:
        x = ord(source[0]) << 7
        m = 1000003
        mask = 2 ** 128 - 1
        for c in source:
            x = ((x * m) ^ ord(c)) & mask
        x ^= len(source)
        if x == -1:
            x = -2
        x = bin(x).replace('0b', '').zfill(64)[-64:]
    # print("string_hash() executed!")
    return str(x)

# Simhash 算法
def simhash(content):
    jieba.analyse.set_stop_words('./app/dupl_ckg/stopwords.txt')  # 去除停用词
    keyWord = jieba.analyse.extract_tags(
        content, topK=20, withWeight=True, allowPOS=())  # 根据 TD-IDF 提取关键词，并按照权重排序
    if len(keyWord) < 6:  # 少于5个词放弃这个句子
        return ''
    keyList = []
    # strKeyWord = ''
    for feature, weight in keyWord:  # 对关键词进行 hash
        # strKeyWord += str(feature) + ':' + str(weight) + ' '
        weight = int(weight * 20)
        feature = string_hash(feature)
        temp = []
        for i in feature:
            if(i == '1'):
                temp.append(weight)
            else:
                temp.append(-weight)
        # print(temp)
        keyList.append(temp)
    list1 = np.sum(np.array(keyList), axis=0)
    if(keyList == []):  # 编码读不出来
        # return strKeyWord, '00'
        return '00'
    simhash = ''
    for i in list1:  # 权值转换成 hash 值
        if(i > 0):
            simhash = simhash + '1'
        else:
            simhash = simhash + '0'
    # return strKeyWord, simhash
    return simhash

import time

# 建立数据库
def db_build():
    print("db_build() starting …")
    clock_0 = time.time()
    PATH_lib = 'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/lib'
    doc_name = os.listdir(PATH_lib)
    counter_doc = 0
    for name in doc_name:
        print(counter_doc, '\t', name)
        counter_doc += 1
        mdb.idx.insert(CreateMethod.create_idx(counter_doc, name))
        txt = np.loadtxt(codecs.open(os.path.join(PATH_lib, name), encoding=u'gb18030',errors='ignore')
                        , dtype=np.str, delimiter="\r\n", encoding='gb18030')
        for paragraph in txt:
            paragraph = paragraph.replace('\u3000', '').replace('\t', '').replace('  ', '').replace('\r', ' ')  # 去除全角空格和制表符，换行替换为空格
            # if paragraph == '' or paragraph == ' ' or paragraph[0].isdigit():
            if paragraph == '' or paragraph == ' ':
                continue
            # strKeyWord, shash = simhash(paragraph)
            shash = simhash(paragraph)
            # if strKeyWord == '':
                # continue
            if shash == '':
                continue
            # mdb.test0.insert(CreateMethod.create_mdb(name, paragraph, strKeyWord, shash))  # 保存到 MongoDB
            mdb.all.insert(CreateMethod.create_lib(counter_doc, name, paragraph, shash))
    clock_1 = time.time()
    print("【buildtime】【", clock_1-clock_0, '】') 
    print("db_build() executed!")

# 单篇与数据库相似度
def result_all(paper_name, hamming_dis_threshold):
    print("get_sim() starting …")
    clock_0 = time.time()
    paper_name = 'GS1521FC1-何岩-康龙化成公司固定资产管理系统的设计与实施-云计算 - 第1次修改.txt'
    name_a = paper_name
    paper_a = mdb.idx.find_one({'name':name_a})
    idx_a = paper_a['idx']
    TEMP_a_parag = []
    a_parag = mdb.all.find({'idx':idx_a})
    for i in a_parag:  # 保存待检测的段落和哈希
        TEMP_a_parag.append([i['paragraph'], i['shash']])
    TEMP_name_idx = []
    name_idx = mdb.idx.find({'idx':{'$ne':idx_a}})
    for i in name_idx:  # 生成名字索引
        TEMP_name_idx.append([i['idx'], i['name']])
    for idx_b, name_b in TEMP_name_idx:
        TEMP_b_parag = []
        b_parag = mdb.all.find({'idx':idx_b})
        for i in b_parag:  # 保存样本的段落和哈希
            TEMP_b_parag.append([i['paragraph'], i['shash']])
        sim_count = 0
        parag_same = []
        for a_parag, a_shash in TEMP_a_parag:
            for b_parag, b_shash in TEMP_b_parag:
                # counter_b += 1
                ham_dis = hammingDis(a_shash, b_shash)
                if ham_dis < hamming_dis_threshold:
                    sim_count += 1
                    parag_same.append([a_parag, b_parag, ham_dis])
                    # print('【item: ', item, '】【item_er')
        print('【', name_b, '】【', sim_count, '】')
        if sim_count > 5:
            for parag_a, parag_b, ham_dis in parag_same:
                # print(parag_a, '//', parag_b)
                mdb.details.insert(CreateMethod.create_details(idx_a, idx_b, name_a, parag_a, name_b, parag_b, ham_dis))
            mdb.sum.insert(CreateMethod.create_sum(idx_a, idx_b, name_a, name_b, sim_count))
    dupl_sum = mdb.sum.find().sort([('dupl_with_b',-1)])
    for i in dupl_sum:
        print('【', i['name_b'], '】【', i['dupl_with_b'], '】')
    clock_1 = time.time()
    print("【checktime】【", clock_1-clock_0, '】')
    print("get_sim() executed!")


''' old 函数，基于 npy 运行 '''

db_data = []
db_hash = []
db_doc_idx = {}

# 建立数据库
def db_build_old(prepath, flag):
    print("db_build_old() starting …")
    doc_name = os.listdir(prepath)
    global db_data, db_hash  # 全局变量
    if flag == '0':
        db_data = []
        db_hash = []
    count = 0
    for name in doc_name:
        count += 1
        print(count, '\t', name)
        txt = np.loadtxt(codecs.open(os.path.join(prepath, name), encoding=u'gb18030',errors='ignore')
                        , dtype=np.str, delimiter="\r\n", encoding='gb18030')
        for paragraph in txt:
            paragraph = paragraph.replace('\u3000', '').replace('\t', '').replace('  ', '').replace('\r', ' ')  # 去除全角空格和制表符，换行替换为空格
            # if paragraph == '' or paragraph == ' ' or paragraph[0].isdigit():
            if paragraph == '' or paragraph == ' ':
                continue
            # strKeyWord, shash = simhash(paragraph)
            shash = simhash(paragraph)
            # if strKeyWord == '':
            if shash == '':
                continue
            # db_data.append([name, paragraph, strKeyWord]) 
            db_data.append([name, paragraph])
            db_hash.append(shash)
        if count % 29 == 0:
            db_build_old(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/check', '1')
            db_save_old(str(count//29))
            db_data = []
            db_hash = []
    print("db_build_old() executed!")

# 存储数据库至本地，以便之后使用
def db_save_old(num):
    print("db_save_old() starting …")
    global db_data, db_hash  # 全局变量
    db_data_to_save = np.array(db_data)
    db_hash_to_save = np.array(db_hash)
    PATH_data = "./app/dupl_ckg/npy/db_data" + num + ".npy"
    PATH_hash = "./app/dupl_ckg/npy/db_hash" + num + ".npy"
    np.save(PATH_data, db_data_to_save)
    np.save(PATH_hash, db_hash_to_save)
    print("db_save_old() executed!")

# 加载本地数据库
def db_load_old(num):
    print("db_load_old() starting …")
    global db_data, db_hash  # 全局变量
    PATH_data = 'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/npy/db_data' + str(num) + '.npy'
    PATH_hash = 'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/npy/db_hash' + str(num) + '.npy'
    db_data = np.load(PATH_data)
    db_hash = np.load(PATH_hash)
    print("db_load_old() executed!", num)

# 生成索引
def get_db_doc_idx(db_data):
    global db_doc_idx  # 全局变量
    db_doc_idx = {}  # 初始化 db_doc_idx
    for i in range(len(db_data)): 
        arr = db_data[i]
        # print(' / ', arr, ' / ')  # 打印测试
        # file_tmp = open(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/get_db_doc_idx.txt', 'a')
        # print('【arr: ', arr, '】【[i]: ', [i], '】【i: ', i, '】', file=file_tmp)
        # file_tmp.close()
        if arr[0] not in db_doc_idx.keys():
            db_doc_idx[arr[0]] = [i]
        else:
            db_doc_idx[arr[0]].append(i)
    # print("get_db_doc_idx() executed!")
    # print(db_doc_idx, '\n')
    return db_doc_idx

# 单篇与论文库相似度排序
def get_sim_old(paper_name, db_doc_idx, db_hash, hamming_dis_threshold=5):
    print("get_sim_old() starting …")
    a_key = paper_name
    doc_name = os.listdir('./docs/lib')
    result_dict = {}
    for b_key in db_doc_idx.keys():
        if a_key == b_key:
            continue
        sim_count = 0
        for a_idx in db_doc_idx[a_key]:
            item = []
            for b_idx in db_doc_idx[b_key]:
                item_result = hammingDis(db_hash[a_idx], db_hash[b_idx])
                if item_result <= hamming_dis_threshold:
                    item.append([a_idx, b_idx])
            # print('\na_key: ', a_key, '\nb_key: ', b_key, '\ndb_doc_idx[a_key]: ', db_doc_idx[a_key], '\ndb_doc_idx[b_key]: ', db_doc_idx[b_key])
            if len(item) > 0:
                sim_count += len(item)
            # print('\na_idx: ', a_idx, '\titem: ', item, '\tsim_count: ', sim_count)
        if sim_count > 5:  # 只保存重复超过5句的文章
            result_dict[b_key] = sim_count
    result_dict = OrderedDict(sorted(result_dict.items(), key=lambda t: t[1], reverse=True))
    print("get_sim_pld() executed!")
    return result_dict

# 两篇相似情况
def get_sim_details_old(paper_name_a, paper_name_b,  db_doc_idx, db_hash, db_data, hamming_dis_threshold=5):
    # print("get_sim_details_old() starting …")
    a_key = paper_name_a
    b_key = paper_name_b
    result_dict = {}
    for a_idx in db_doc_idx[a_key]:
        for b_idx in db_doc_idx[b_key]:
            item_sim = hammingDis(db_hash[a_idx], db_hash[b_idx])
            if item_sim <= hamming_dis_threshold:
                if item_sim not in result_dict.keys():
                    result_dict[item_sim] = []
                result_dict[item_sim].append([db_data[a_idx], db_data[b_idx]])
    result_dict = OrderedDict(sorted(result_dict.items()))
    # print("get_sim_details_old() executed!")
    return result_dict

# 计算单篇论文与存在相似关系的论文的相似度；值越大，越相似
def result_sim_old(paper_name, GENERATE_PATH, target_file):
    print("result_sim_old() starting …")
    global db_doc_idx # 全局变量
    db_doc_idx = get_db_doc_idx(db_data)
    paper_name = 'GS1521FC1-何岩-康龙化成公司固定资产管理系统的设计与实施-云计算 - 第1次修改.txt'
    result_dict = get_sim_old(paper_name, db_doc_idx, db_hash, hamming_dis_threshold=5)
    full_path = GENERATE_PATH + '\\' + target_file
    file = open(full_path, 'a')
    for k,v in result_dict.items():
        print(k, v, file=file)
    file.close()
    print("result_sim_old() executed!")
    return result_dict

# 打印两篇论文的相似情况；hamming distance 越小，越相似
def result_details_old(paper_name_a, paper_name_b, GENERATE_PATH, target_file):
    print("result_details_old() starting …")
    global db_doc_idx  # 全局变量
    db_doc_idx = get_db_doc_idx(db_data)
    # print('\ndb_doc_idx: \n', db_doc_idx, '\n')  # 打印测试
    result_dict_details = get_sim_details_old(paper_name_a, paper_name_b, db_doc_idx, db_hash, db_data, hamming_dis_threshold=6)
    full_path = GENERATE_PATH + '\\' + target_file
    file = open(full_path, 'a')
    print('paper a:', paper_name_a, '\npaper b:', paper_name_b, '\n', file=file)  # 打印标题
    for k in result_dict_details.keys():
        print('hamming distance:', str(k), file=file)
        for a, b in result_dict_details[k]:
            print('-'*100, file=file)
            print('\ta:\t', a[1], file=file)
            print('\tb:\t', b[1], file=file)
        print('', file=file)
    file = file.close()
    print("result_details_old() executed!")

# 结合 result_sim_old 和 result_details_old，按相似度排序，打印相似段落
def result_all_old(paper_name, GENERATE_PATH, target_file_name):
    print("result_details_old() starting …")
    paper_name = 'GS1521FC1-何岩-康龙化成公司固定资产管理系统的设计与实施-云计算 - 第1次修改.txt'
    result_dict = result_sim_old(paper_name, GENERATE_PATH, target_file_name) 
    full_path = GENERATE_PATH + '\\' + target_file_name
    counter = 1
    for paper_name_counter, hamming_dis in result_dict.items():
        target_file = open(full_path, 'a')
        print('■'*100,'\n', file=target_file)
        print('【No.%d】:'%counter, paper_name_counter, '\n', file=target_file)
        target_file = target_file.close()  # 写入 all 部分后需要关闭文件，否则写入顺序会出错
        result_details_old(paper_name, paper_name_counter, GENERATE_PATH, target_file_name)
        counter += 1
    target_file = open(full_path, 'r')
    content = target_file.readlines()
    target_file.close()
    print("result_details_old() executed!")
    return content

# 初始化数据库
def init():  # 仅在论文库更新时再次 db_build() 和 db_save_old() 即可
    print("init() starting …")
    db_build_old(prepath=r'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/lib', flag='0')
    # db_save_old('')
    # db_load_old()
    print("init() executed!")