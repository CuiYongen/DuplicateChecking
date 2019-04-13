# coding=utf-8

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

'''
    检查文件合法性
'''

ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

'''
    上传文件
'''

def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
        if file and allowed_file(file.filename):
            filename = file.filename  # 安全获取：secure_filename(file.filename)
            UPLOAD_PATH = os.path.join(os.getcwd(), "./docs", filename)  # 返回上级目录，进入 /docs
            file.save(UPLOAD_PATH)
        # return render_template('./result/user_xxx.html', uid='')
        
'''
    读取文件
'''

def read_file():
    file = open(r'C:\Users\Administrator\Documents\duplicateChecking\Flask\result\0010.txt')
    content = ''
    for line in file:
        content += line
        content += '<br>'
    file.close()
    return content
    

'''
    为每个用户生成结果
'''

import sys
sys.path.append(r"C:\Users\Administrator\Documents\duplicateChecking\Flask\app\dupl_ckg")
import dupl_ckg

def generate(uid):
    
    print(os.getcwd())
    # os.chdir(r'C:\Users\Administrator\Documents\duplicateChecking\Flask\result')	# 切换到 result 文件夹，保存查重结果
    GENERATE_PATH = r'C:\Users\Administrator\Documents\duplicateChecking\Flask\result'
    uid = "test"
    result_file_name = uid + '.txt'
    
    # dupl_ckg.result_sim('', GENERATE_PATH, result_file)
    # dupl_ckg.result_details('', '', GENERATE_PATH, result_file)
    content = dupl_ckg.result_all('', GENERATE_PATH, result_file_name)
    
    return content
    

