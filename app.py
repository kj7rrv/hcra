from flask import Flask, request, Response
import os
import requests
import base64
#import hcapi
app = Flask(__name__)

@app.route('/client')
def client():
    with open('client.html') as f:
        return f.read()
