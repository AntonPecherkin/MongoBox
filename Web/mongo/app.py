# -*- coding: utf-8 -*-
import base64
import datetime
import os
import shutil
import sys
import json
import struct
from time import sleep
from flask import Flask
from flask import request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login = "Test"

@app.route("/addnewdoc")
def addnewdoc():
    return render_template('addnewdoc.html')

@app.route("/share", methods=['POST'])
def sharepage():
    doc = request.form['Doc']
    docname = request.form['Docname']
    owner = request.form['Owner']
    return render_template('share.html', doc=doc, docname=docname, owner=owner)

@app.route("/sharedoc", methods=['POST'])
def sharedoc():
    global login
    upload = 0
    share = 1
    login = request.form['Owner']
    time = request.form['Time']
    user = request.form['User']
    doc = request.form['Doc']
    docname = request.form['Docname']
    owner = request.form['Owner']
    return render_template('main.html', share=share, upload=upload, time=time, user=user, login=login, doc=doc, docname=docname, owner=owner)

@app.route("/upload", methods=['POST'])
def uploadfile():
    upload = 1
    share = 0
    file = request.files['file']
    basedir = os.path.abspath(os.path.dirname(__file__))
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename)) 
    prefix = """data:image/jpg;base64,"""
    upload_file = basedir + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename
    with open(upload_file, "rb") as imageFile:
        img = imageFile.read()
        plot_bytes_encode = str(base64.b64encode(img))
        plot_bytes_encode = plot_bytes_encode[0:-1]
        plot_bytes_encode_fin = plot_bytes_encode[2:]
        imageBase64 = prefix + plot_bytes_encode_fin #+ base64.b64encode(imageFile.read()).decode('utf8')
    return render_template("main.html", share=share, login=login, upload=upload, filename=filename, imageBase64=imageBase64)
    
@app.route("/main", methods=['POST'])
def mainpage():
    global login
    upload  = 0
    share = 0
    login = request.form['login']
    return render_template('main.html', upload=upload, share=share, login=login)


@app.route("/")
def startpage():
    prefix = """data:image/jpg;base64,"""
    with open("1.jpg", "rb") as imageFile:
        img = imageFile.read()
        plot_bytes_encode = str(base64.b64encode(img))
        plot_bytes_encode = plot_bytes_encode[0:-1]
        plot_bytes_encode_fin = plot_bytes_encode[2:]
        imageBase64 = prefix + plot_bytes_encode_fin #+ base64.b64encode(imageFile.read()).decode('utf8')
    print (imageBase64)
    return render_template('index.html', imageBase64=imageBase64)


if __name__ == '__main__':
    app.run(debug=True, host="livedemo.su", port=3000)


