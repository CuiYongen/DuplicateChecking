# coding=utf-8

from flask import Flask

#创建app应用,__name__是python预定义变量，被设置为使用本模块.
app = Flask(__name__)

#如果你使用的IDE，在routes这里会报错，因为我们还没有创建呀，为了一会不要再回来写一遍，因此我先写上了
from app import routes

from app import dupl_ckg