# coding=utf-8

#导入模板模块
from flask import render_template
from app import app

@app.route('/')

@app.route('/index')
def index():
	return render_template('index.html')

import sys
sys.path.append(r"C:\Users\Administrator\Documents\duplicateChecking\Flask\app\web_mod")
import web_mod

@app.route('/upload', methods=['GET', 'POST'])
def upload():	# 用户上传文件时，根据 ID 或时间生成用户个人文件夹，用于保存论文和查重结果。用户可单独访问个人网址，相当于登陆功能
    web_mod.upload_file()
    # web_mod.create_result(uid='user_123')
    # 上传文件后就应该开始比对了，这里应该传参 paper_file_name，执行 
    return render_template('upload.html')

sys.path.append(r"C:\Users\Administrator\Documents\duplicateChecking\Flask\app\dupl_ckg")
import dupl_ckg

@app.route('/result')
def result():
    # dupl_ckg.debug_import()  # 测试 dupl_ckg 模块是否导入
    # dupl_ckg.result_sim(paper_file_name='')  # 计算单篇论文与数据库相似度
	# dupl_ckg.result_details(paper_a='', paper_b='')  # 计算两篇论文相似度及详情
    # return render_template('userid.html', userid=, )  # 为每个用户生成结果页（尚未完成）
    uid = '0010'  # 为用户生成唯一 uid
    content = web_mod.read_file()
    return render_template('result.html', uid=uid, content=content)
    
@app.route('/init')
def init():
    dupl_ckg.init()
    return render_template('index.html')

@app.route('/test')
def test():
    # dupl_ckg.result_sim(paper_file_name='')
    return render_template('test.html', func_name='NULL')

@app.route('/test/result_sim')
def test_result_sim():
    dupl_ckg.result_sim(paper_name='', target_file='')
    return render_template('test.html', func_name='result_sim')
    
@app.route('/test/result_details')
def test_result_details():
    dupl_ckg.result_details(paper_name_a='', paper_name_b='')
    return render_template('test.html', func_name='result_details')
    
@app.route('/test/result_all')
def test_result_all():
    dupl_ckg.result_all(paper_name='')
    return render_template('test.html', func_name='result_all')
    
@app.route('/test/generate')
def test_generate():
    content = web_mod.generate(uid='')
    return render_template('result.html', uid='0010', content=content)
    # return render_template('test.html', func_name='generate')
    
@app.route('/test/read')
def test_read():
    content = web_mod.read_file()
    return render_template('result.html', uid='0010', content=content)