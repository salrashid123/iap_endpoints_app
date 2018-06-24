import logging
import os
import sys
import logging
import json
import time
import pprint
import traceback

from google.appengine.ext import webapp

from apiclient.discovery import build
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import GoogleCredentials

import urllib,urllib2, httplib
from urllib2 import URLError, HTTPError
import random

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from google.auth import app_engine
from google.appengine.api import app_identity
from google.appengine.api import urlfetch

from datetime import datetime, timedelta

from flask import Flask, render_template, request, abort, Response

app = Flask(__name__)

my_appId = os.getenv('APPLICATION_ID')[2:]
svc_account = my_appId + '@appspot.gserviceaccount.com'

@app.route('/getIdToken', methods=['GET'])
def getIdToken():
  iap_jwt = None
  iap_userId = None
  iap_email = None

  audience = 'api.endpoints.YOUR_PROJECT.cloud.goog'

  # TODO: verify jWT signature: https://cloud.google.com/iap/docs/signed-headers-howto
  if 'x-goog-iap-jwt-assertion' in request.headers:
    iap_jwt = request.headers['x-goog-iap-jwt-assertion']

  if 'X-Goog-Authenticated-User-Id' in request.headers:
    iap_userId = request.headers['X-Goog-Authenticated-User-Id']
  else:
    logging.error("X-Goog-Authenticated-User-Id not found")
    abort(500)    

  if 'X-Goog-Authenticated-User-Email' in request.headers:
    iap_email = request.headers['X-Goog-Authenticated-User-Email']
  
  cc = GoogleCredentials.get_application_default()
  iam_scopes = 'https://www.googleapis.com/auth/iam https://www.googleapis.com/auth/cloud-platform'
  if cc.create_scoped_required():
    cc = cc.create_scoped(iam_scopes)
  http = cc.authorize(httplib2.Http())
  service = build(serviceName='iam', version= 'v1',http=http)
  resource = service.projects()   
  now = int(time.time())
  exptime = now + 3600  
  claim =('{"iss":"%s",'
          '"aud":"%s",'
          '"sub":"%s",'          
          '"X-Goog-Authenticated-User-ID":"%s",'
          '"X-Goog-Authenticated-User-Email":"%s",'         
          '"exp":%s,'
          '"iat":%s}') %(svc_account,audience,svc_account,iap_userId,iap_email,exptime,now)
  slist = resource.serviceAccounts().signJwt(name='projects/' + my_appId + '/serviceAccounts/' + svc_account, body={'payload': claim })
  resp = slist.execute()   
  signed_jwt = resp['signedJwt'] 
  return signed_jwt
  

@app.route('/', methods=['GET'])
def index():
  try:
    logging.info('Got Headers {} '.format(request.headers))

    iap_jwt = None
    iap_userId = None
    iap_email = None

    # TODO: verify jWT signature: https://cloud.google.com/iap/docs/signed-headers-howto
    if 'x-goog-iap-jwt-assertion' in request.headers:
      iap_jwt = request.headers['x-goog-iap-jwt-assertion']

    if 'X-Goog-Authenticated-User-Id' in request.headers:
      iap_userId = request.headers['X-Goog-Authenticated-User-Id']

    if 'X-Goog-Authenticated-User-Email' in request.headers:
      iap_email = request.headers['X-Goog-Authenticated-User-Email']

    return render_template('index.html', iap_userId=iap_userId, iap_email=iap_email, iap_jwt=iap_jwt)
  except Exception as e:
    logging.error("Error: " + str(e))
    abort(500)

@app.errorhandler(500)
def server_error(e):
  logging.exception('An error occurred during a request.')
  return 'An internal error occurred.', 500
