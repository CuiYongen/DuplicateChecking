# coding=utf-8

#导入模板模块
from flask import render_template, flash
from app import app
import os
import shutil

import sys
sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/web_mod")
import web_mod

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    web_mod.upload_file()
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():	# 用户上传文件时，根据 ID 或时间生成用户个人文件夹，用于保存论文和查重结果。用户可单独访问个人网址，相当于登陆功能
    web_mod.upload_file() 
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    UPLOAD_PATH = r'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/lib/'
    return send_from_directory(UPLOAD_PATH, filename)

'''
'''

sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/dupl_ckg")
import dupl_ckg

# 使用 npy 模式下的查看结果
# @app.route('/result')
# def result():
#     content = web_mod.read_file()
#     return render_template('result.html', uid=uid, content=content)

@app.route('/result')
def result():
    paper_a = mdb.idx.find_one({'idx':0})
    name_a = paper_a['name']
    file_name_temp = mdb.sum.find().sort([('dupl_with_b', -1)])
    file_name = []
    file_name_counter = 1
    for i in file_name_temp:
        file_name.append([file_name_counter, i['name_b'], i['dupl_with_b'], round(i['plagiarism_rate'],2)])
        file_name_counter += 1
    name_b = file_name[0][1]
    result_temp = mdb.details.find().sort([('hammingDis',-1)])
    result_details = []
    for i in result_temp:
        result_details.append([i['parag_a'], i['parag_b']])
    return render_template('result.html', file_name=file_name, result_details=result_details, name_a=name_a, name_b=name_b)

    
@app.route('/init')
def init():
    dupl_ckg.init(path='lib')
    return redirect('/')

@app.route('/reset_lib')
def reset_lib():
    mongo.drop_database("test")
    shutil.rmtree(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/lib', False)
    os.mkdir(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/lib')
    return redirect('/')

@app.route('/reset_check')
def reset_check():
    shutil.rmtree(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/check', False)
    os.mkdir(r'C:/Users/Administrator/Documents/duplicateChecking/Flask/docs/check')
    return redirect('/')

@app.route('/test')
def test():
    file_name_temp = mdb.sum.find().sort([('dupl_with_b', -1)])
    file_name = []
    file_name_counter = 1
    for i in file_name_temp:
        file_name.append([file_name_counter, i['name_b'], i['dupl_with_b'], round(i['plagiarism_rate'],2)])
        file_name_counter += 1
    result_temp = mdb.details.find().sort([('hammingDis',-1)])
    result_details = []
    for i in result_temp:
        result_details.append([i['parag_a'], i['parag_b']])
    return render_template('result.html', uid='0001', file_name=file_name, result_details=result_details)

@app.route('/result_all')
def result_all():
    dupl_ckg.result_all(paper_name='', hamming_dis_threshold=3)
    return redirect('result')
    
@app.route('/test/generate')
def test_generate():
    content = web_mod.generate(uid='')
    return render_template('result.html', uid='1', content=content)
    # return render_template('test.html', func_name='generate')
    
@app.route('/test/read')
def test_read():
    content = web_mod.read_file()
    return render_template('result.html', uid='0010', content=content)

@app.route('/test/time')
def test_time():
    clock_0 = time()
    # s1 = '0001001001001000000100100100100000010010010010000001001001001000'
    # s2 = '1000010000100001100001000010000110000100001000011000010000100001'
    s1 = '0010001000100010'
    s2 = '0010001000100011'
    for i in range(1,10000000):
        # dupl_ckg.hammingDis(s1, s2)
        if s1 == s2:
            return s1
    clock_1 = time()
    print('success! time = ', clock_1-clock_0)
    return render_template('test.html', func_name='time')

import numpy as np
@app.route('/test/test')
def test_test():
    file_tmp = open(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/result/1.txt", "r")
    txt_to_calculate = file_tmp.read().strip()
    length = len(txt_to_calculate)
    print(txt_to_calculate)
    print(length)
    file_tmp.close()
    return render_template('test.html', func_name='test')


#=========================================

#=========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uid_imput = request.form.get('userid')
        password_imput = request.form.get('password')
        if uid_imput == '' or password_imput == '':
            print("输入不完整！")
        user = mdb.user.find_one({'uid':uid_imput})
        if password_imput == user['password']:
            print("登陆成功！")
            return redirect(url_for('index'))
        else:
            print("密码错误！")
        # if user is not None and request.form['password'] == user['password']:
        #     curr_user = web_mod.User()
        #     curr_user.id = user_id
        #     login_user(curr_user)  # 通过Flask-Login的login_user方法登录用户
        #     return redirect(url_for('index'))
        # print('Wrong username or password!')

    # GET 请求
    return render_template('login.html')

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return 'Logged out successfully!'

'''
测试 pymongo
'''

sys.path.append(r"C:/Users/Administrator/Documents/duplicateChecking/Flask/app/flk_mdb")
import flk_mdb
import pymongo
from flask import request, redirect, url_for
from flk_mdb import Todo
from time import time

mongo = pymongo.MongoClient('127.0.0.1', 27017)
mdb = mongo.test

@app.route('/test/create_index')
def test_create_index():
    mdb.all.create_index([("name", pymongo.TEXT)])
    # mdb.all.create_index([("name", pymongo.ASCENDING)])
    return render_template('test.html', func_name='create_index')

@app.route('/test/get_index')
def test_get_index():
    # mdb.all.get_index()
    return render_template('test.html', func_name='get_index')

@app.route('/todo/',methods=['GET'])
def mdb_index():
    todosss = mdb.list.find({})
    return  render_template('mdb_index.html',todos=todosss)

@app.route('/todo/', methods=['POST'])
def mdb_add():
    content = request.form.get('content', None)
    if not content:
        abort(400)
    mdb.list.insert(Todo.create_doc(content))
    return redirect('/todo/')

@app.route('/todo/<content>/finished')
def mdb_finish(content):
    result = mdb.list.update_one(
        {'content':content}, 
        {'$set': {
            'is_finished': True,
            'finished_at': time()
            }
        }
    )
    return redirect('/todo/')

@app.route('/todo/<content>')
def mdb_delete(content):
    result = mdb.list.delete_one(
        {'content':content}
    )
    return redirect('/todo/')

''' Flask + Vue 测试 '''

@app.route('/todovue')
def index_todovue():
    return render_template('formdata_vue.html')
