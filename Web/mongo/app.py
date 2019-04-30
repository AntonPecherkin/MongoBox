# -*- coding: utf-8 -*-
import base64
import datetime
import os
import shutil
import sys
import json
import struct
import maya
from twisted.logger import globalLogPublisher
from nucypher.characters.lawful import Alice, Bob, Ursula
from nucypher.data_sources import DataSource as Enrico
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import simpleObserver
from umbral.keys import UmbralPublicKey
from time import sleep
from flask import Flask
from flask import request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

# Execute the download script (download_finnegans_wake.sh) to retrieve the book
BOOK_PATH = os.path.join('.', 'finnegans-wake.txt')

# Twisted Logger
globalLogPublisher.addObserver(simpleObserver)

# Temporary file storage
TEMP_FILES_DIR = "{}/examples-runtime-cruft".format(os.path.dirname(os.path.abspath(__file__)))
TEMP_DEMO_DIR = "{}/finnegans-wake-demo".format(TEMP_FILES_DIR)
TEMP_CERTIFICATE_DIR = "{}/certs".format(TEMP_DEMO_DIR)

# Remove previous demo files and create new ones
shutil.rmtree(TEMP_FILES_DIR, ignore_errors=True)
os.mkdir(TEMP_FILES_DIR)
os.mkdir(TEMP_DEMO_DIR)
os.mkdir(TEMP_CERTIFICATE_DIR)

#######################################
# Finnegan's Wake on NuCypher Testnet #
# (will fail with bad connection) #####
#######################################

TESTNET_LOAD_BALANCER = "eu-federated-balancer-40be4480ec380cd7.elb.eu-central-1.amazonaws.com"

##############################################
# Ursula, the Untrusted Re-Encryption Proxy  #
##############################################
ursula = Ursula.from_seed_and_stake_info(host=TESTNET_LOAD_BALANCER,
                                         certificates_directory=TEMP_CERTIFICATE_DIR,
                                         federated_only=True,
                                         minimum_stake=0)



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
    policy_end_datetime = maya.now() + datetime.timedelta(days=5)
    m, n = 2, 3  
    label = b"secret/files/and/stuff"
    ######################################
    # Alice, the Authority of the Policy # 
    ######################################
    ALICE = Alice(network_middleware=RestMiddleware(),
                  known_nodes=[ursula],
                  learn_on_same_thread=True,
                  federated_only=True,
                  known_certificates_dir=TEMP_CERTIFICATE_DIR)      
    BOB = Bob(known_nodes=[ursula],
              network_middleware=RestMiddleware(),
              federated_only=True,
              start_learning_now=True,
              learn_on_same_thread=True,
              known_certificates_dir=TEMP_CERTIFICATE_DIR)

    ALICE.start_learning_loop(now=True)
    policy = ALICE.grant(BOB,
                         label,
                         m=m, n=n,
                         expiration=policy_end_datetime)

    # Alice puts her public key somewhere for Bob to find later...
    alices_pubkey_bytes_saved_for_posterity = bytes(ALICE.stamp)
    # ...and then disappears from the internet.    
    del ALICE
     
    BOB.join_policy(label, alices_pubkey_bytes_saved_for_posterity)
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


