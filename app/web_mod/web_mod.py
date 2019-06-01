# coding=utf-8

import os
import sys
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/flk_mdb")
import flk_mdb
import pymongo
from flask import request, redirect, url_for
from flk_mdb import Todo
from time import time

mongo = pymongo.MongoClient('127.0.0.1', 27017)
mdb = mongo.test

''' 检查文件合法性 '''

ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

''' 上传文件 '''
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist("file_lib[]")
        for file in files:
            filename = file.filename  # 安全获取：secure_filename(file.filename)
            UPLOAD_PATH = 'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/lib/'+ filename
            file.save(UPLOAD_PATH)
        files = request.files.getlist("file_check[]")
        for file in files:
            filename = file.filename  # 安全获取：secure_filename(file.filename)
            UPLOAD_PATH = 'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/check/'+ filename
            file.save(UPLOAD_PATH)
        mdb.test.remove({})

''' 读取文件 '''
def read_file():
    file = open(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/result/科协学会专家数据库的设计与实施-第4次修改（降重）.txt", "rb")
    # content = ''
    # for line in file:
    #     content += line
    #     content += '<br>'
    file_tmp = open(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg/paragraph.txt', 'a', encoding='gb18030')
    for line in file:
        print('==paragragh: ', line, '==', file=file_tmp)
    file_tmp.close()
    content = file.readlines()
    file.close()
    return content
    

''' 为每个用户生成结果 '''

import sys
sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg")
import dupl_ckg

def generate_old(uid):
    GENERATE_PATH = r'C:/Users/Administrator/Documents/duplicateChecking/Flask/result'
    PATH_lib = 'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/lib'
    dupl_ckg.db_build_old(prepath=PATH_lib, flag='0')
    for i in range(1,45):
        dupl_ckg.db_load_old(i)
        uid = str(i)
        result_file_name = uid + '.txt'
        content = dupl_ckg.result_all_old('', GENERATE_PATH, result_file_name)
    return content


''' 登陆 '''

from flask_login import UserMixin

class User(UserMixin):
    pass

users = [
    {'id':'Tom', 'username': 'Tom', 'password': '111111'},
    {'id':'Michael', 'username': 'Michael', 'password': '123456'}
]

def query_user(user_id):
    for user in users:
        if user_id == user['id']:
            return user

# from flask_login import LoginManager

# login_manager = LoginManager()
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'
# login_manager.login_message = 'Access denied.'
# login_manager.init_app(app)

# @login_manager.user_loader
# def load_user(user_id):
#     if query_user(user_id) is not None:
#         curr_user = User()
#         curr_user.id = user_id
#         return curr_user