from flask import Flask, jsonify, request, abort,url_for,render_template,redirect
from time import time
from bson.objectid import ObjectId
from bson.json_util import dumps

class Todo(object):
    @classmethod
    def create_doc(cls, content):
        return {
            'content': content,
            'created_at': time(),
            'is_finished': False,
            'finished_at': None
        }

class Paper(object):
    @classmethod
    def create_mdb(cls, name, paragraph, strKeyWord, shash):
        return {
            'name': name,
            'paragraph': paragraph,
            'strKeyWord': strKeyWord,
            'shash': shash,
            'created_at': time(),
        }