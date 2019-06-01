# ORM库，参考 https://github.com/Pingze-github/mango/blob/master/mango.py
# 宗旨：
# API尽量贴合mongo原生pymongo
# 转换pymongo的字典为对象
# 具有简单的校验，
# 可管理index

from flask import Flask, jsonify, request, abort,url_for,render_template,redirect
from time import time
from bson.objectid import ObjectId
from bson.json_util import dumps
from pymongo import MongoClient, errors

global connection
global db

# ****** connect *******

def connect(database, ip='127.0.0.1', port=27017, username=None, password=None):
    global connection, db
    connection = MongoClient(ip, port, username=username, password=password, authSource=database)
    db = connection[database]
    return connection, db

class Todo(object):
    @classmethod
    def create_doc(cls, content):
        return {
            'content': content,
            'created_at': time(),
            'is_finished': False,
            'finished_at': None
        }

class CreateMethod(object):
    @classmethod
    # def create_mdb(cls, idx, name, paragraph, strKeyWord, shash):
    def create_lib(cls, idx, name, paragraph, shash):
        return {
            'idx': idx,
            'name': name,
            'paragraph': paragraph,
            # 'strKeyWord': strKeyWord,
            'shash': shash
        }

    @classmethod
    def create_idx(cls, idx, name):
        return {
            'idx': idx,
            'name': name
        }

    @classmethod
    def create_details(cls, idx_a, idx_b, name_a, parag_a, name_b, parag_b, hamming_dis):
        return {
            'idx_a': idx_a,
            'idx_b': idx_b,
            'name_a': name_a,
            'parag_a': parag_a,
            'name_b': name_b,
            'parag_b': parag_b,
            'hamming_dis': hamming_dis
        }

    @classmethod
    def create_sum(cls, idx_a, idx_b, name_a, name_b, dupl_with_b, plagiarism_rate):
        return {
            'idx_a': idx_a,
            'idx_b': idx_b,
            'name_a': name_a,
            'name_b': name_b,
            'dupl_with_b': dupl_with_b,
            'plagiarism_rate': plagiarism_rate
        }