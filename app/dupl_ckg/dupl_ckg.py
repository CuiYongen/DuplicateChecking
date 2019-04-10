# coding=utf-8

'''
    准备工作
'''

import codecs
import numpy as np
import os
import jieba
import jieba.analyse

db_data = []
db_hash = []
db_doc_idx = {}

def hammingDis(simhash1, simhash2):  # 计算汉明距离
    t1 = '0b' + simhash1
    t2 = '0b' + simhash2
    n = int(t1, 2) ^ int(t2, 2)
    i = 0
    while n:
        n &= (n-1)
        i += 1
    # print("hammingDis() executed!")
    return i

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
    
def simhash(content):
    seg = jieba.cut(content)  # 分词
    jieba.analyse.set_stop_words('./app/dupl_ckg/stopwords.txt')  # 去除停用词
    keyWord = jieba.analyse.extract_tags(
       '|'.join(seg), topK=20, withWeight=True, allowPOS=())
        # 在这里对 jieba 的 tfidf.py 进行了修改
        # 将 tags = sorted(freq.items(), key=itemgetter(1), reverse=True) 修改成 tags = sorted(freq.items(), key=itemgetter(1,0), reverse=True)
        # 即先按照权重排序，再按照词排序
    keyList = []
    strKeyWord = ''
    keyCount = 0
    for feature, weight in keyWord:  # 对关键词进行 hash
        strKeyWord += str(feature) + ':' + str(weight) + ' '
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
        keyCount += 1
        if keyCount <= 5:
            strKeyWord = ''
    list1 = np.sum(np.array(keyList), axis=0)
    if(keyList == []):  # 编码读不出来
        return strKeyWord, '00'
    simhash = ''
    for i in list1:  # 权值转换成 hash 值
        if(i > 0):
            simhash = simhash + '1'
        else:
            simhash = simhash + '0'
    # print("simhash() executed!")
    return strKeyWord, simhash

    
'''
    建立数据库
'''
    
def db_build():
    print("db_build() starting …")
    prepath = './docs'
    doc_name = os.listdir(prepath)
    global db_data, db_hash  # 全局变量
    db_data = []
    db_hash = []
    count = 0
    for name in doc_name:
        print(count, '\t', name)
        count += 1
        txt = np.loadtxt(codecs.open(os.path.join(prepath, name), encoding=u'gb18030',errors='ignore')
                        , dtype=np.str, delimiter="\r\n", encoding='gb18030')
        txt = np.char.replace(txt, '\\u3000', '')
        txt = np.char.replace(txt, '\\u3000\\u3000', '')    
        for paragraph in txt:
            if paragraph == '' or paragraph == ' ' or paragraph.find(' ') != -1 or paragraph[0].isdigit():
                continue
            strKeyWord, shash = simhash(paragraph)
            if strKeyWord == '':
                continue
            db_data.append([name, paragraph, strKeyWord])
            db_hash.append(shash)
    print("db_build() executed!")

'''
    存储数据库至本地，以便之后使用
'''
def db_save():
    print("db_save() starting …")
    global db_data, db_hash  # 全局变量
    db_data = np.array(db_data)
    db_hash = np.array(db_hash)
    np.save("./app/dupl_ckg/db_data.npy", db_data)
    np.save("./app/dupl_ckg/db_hash.npy", db_hash)
    print("db_save() executed!")

'''
    论文查重 - 准备工作
'''

from collections import OrderedDict
import numpy as np

def get_db_doc_idx(db_data):
    # print("get_db_doc_idx() starting …")
    global db_doc_idx  # 全局变量
    db_doc_idx = {}  # 初始化 db_doc_idx
    for i in range(len(db_data)): 
        arr = db_data[i]
        if arr[0] not in db_doc_idx.keys():
            db_doc_idx[arr[0]] = [i]
        else:
            db_doc_idx[arr[0]].append(i)
    # print("get_db_doc_idx() executed!")
    return db_doc_idx

# 单篇与数据库相似度
def get_sim(paper_name, db_doc_idx, db_hash, hamming_dis_threshold=5):
    # print("get_sim() starting …")
    a_key = paper_name
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
            if len(item) > 0:
                sim_count += len(item)
        if sim_count > 0:
            result_dict[b_key] = sim_count
    
    result_dict = OrderedDict(sorted(result_dict.items(), key=lambda t: t[1], reverse=True))
    
    # print("get_sim() executed!")
    return result_dict

# 两篇相似情况
def get_sim_details(paper_name_a, paper_name_b,  
                    db_doc_idx, db_hash, db_data, hamming_dis_threshold=5,
                    print_details='short'):
    # print("get_sim_details() starting …")
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
    
    # full_path = GENERATE_PATH + '\\' + target_file
    # file = open(full_path, 'a')
    
    # if print_details == 'short':
        # print('paper a:', paper_name_a, '\npaper b:', paper_name_b, '\n', file=file)  # 打印标题
        # for k in result_dict.keys():
            # print('hamming distance:', str(k), file=file)
            # for a, b in result_dict[k]:
                # print('-'*100, file=file)
                # print('\ta:\t', a[1], file=file)
                # print('\tb:\t', b[1], file=file)
            # print('', file=file)
    
    # file = file.close()
    
    # print("get_sim_details() executed!")
    return result_dict

'''
    论文查重 - 加载本地数据库
'''
def db_load():
    print("db_load() starting …")
    global db_data, db_hash  # 全局变量
    db_data = np.load(r'C:\Users\Administrator\Documents\duplicateChecking\Flask\app\dupl_ckg\db_data.npy')
    db_hash = np.load(r'C:\Users\Administrator\Documents\duplicateChecking\Flask\app\dupl_ckg\db_hash.npy')
    print("db_load() executed!")

'''
    计算单篇论文与数据库中论文的相似度
    # 仅得数存在相似关系的论文的相关数据，值越大，越相似
'''
def result_sim(paper_name, GENERATE_PATH, target_file):
    print("result_sim() starting …")
    
    global db_doc_idx # 全局变量
    db_doc_idx = get_db_doc_idx(db_data)
    paper_name = '重庆有线广告管理系统的设计与实施GS1321154刘冉.txt'
    result_dict = get_sim(paper_name, db_doc_idx, db_hash, hamming_dis_threshold=5)
    
    full_path = GENERATE_PATH + '\\' + target_file
    file = open(full_path, 'a')
    
    for k,v in result_dict.items():
        print(k, v, file=file)
        
    file.close()
    
    print("result_sim() executed!")
    return result_dict

'''
    输出并打印两篇论文的相似情况
    # hamming distance 越小，越相似
'''
def result_details(paper_name_a, paper_name_b, GENERATE_PATH, target_file):
    print("result_details() starting …")
    
    global db_doc_idx  # 全局变量
    db_doc_idx = get_db_doc_idx(db_data)
    result_dict_details = get_sim_details(paper_name_a, paper_name_b, db_doc_idx, db_hash, db_data, hamming_dis_threshold=6)
    
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
    
    print("result_details() executed!")


'''
    按相似度排序，打印相似段落
'''

def result_all(paper_name, GENERATE_PATH, target_file_name):
    print("result_details() starting …")
    
    paper_name = '重庆有线广告管理系统的设计与实施GS1321154刘冉.txt'
    result_dict = result_sim(paper_name, GENERATE_PATH, target_file_name) 
    full_path = GENERATE_PATH + '\\' + target_file_name
    
    counter = 1
    for paper_name_counter, hamming_dis in result_dict.items():
        target_file = open(full_path, 'a')
        print('■'*100,'\n', file=target_file)
        print('【No.%d】:'%counter, paper_name_counter, '\n', file=target_file)
        target_file = target_file.close()  # 写入 all 部分后需要关闭文件，否则写入顺序会出错
        
        result_details(paper_name, paper_name_counter, GENERATE_PATH, target_file_name)
        counter += 1
        
    target_file = open(full_path, 'r')
    content = target_file.readlines()
    target_file.close()
    
    print("result_details() executed!")
    return content
    
'''
    初始化数据库
'''

def init():
    print("init() starting …")
    # db_build()  # 仅在论文库更新时再次 db_build() 和 db_save() 即可
    # db_save()
    db_load()
    print("init() executed!")