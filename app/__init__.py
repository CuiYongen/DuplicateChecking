# coding=utf-8

from flask import Flask

#创建app应用,__name__是python预定义变量，被设置为使用本模块.
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

from app import routes
from app import dupl_ckg
from app import web_mod
from app import flk_mdb