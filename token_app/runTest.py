#!/usr/bin/python

import os
import google.auth
from google.auth import jwt
from google.oauth2 import service_account
from google.oauth2 import id_token
from google.auth import exceptions
from google.auth import transport
import google_auth_httplib2

import google.auth.transport.requests
import requests


""" 
print "++++++++++++++  mint and verify id_token for a service_account ++++++++++++++++"


svc_account_json_file ='svc_account.json'
audience = 'api.endpoints.YOUR_PROJECT.cloud.goog'
additional_claims = {'X-Goog-Authenticated-User-ID': 'accounts.google.com:112312312312382', 'X-Goog-Authenticated-User-Email': 'user1@esodemoapp2.com'}

svc_creds = service_account.Credentials.from_service_account_file(svc_account_json_file)
jwt_creds = jwt.Credentials.from_signing_credentials(svc_creds, audience=audience, additional_claims=additional_claims )

svc_account_name = svc_creds._service_account_email
request = google.auth.transport.requests.Request()
jwt_creds.refresh(request)
idt = jwt_creds.token
print 'id_token: ' + idt
print id_token.verify_token(idt,request, certs_url='https://www.googleapis.com/service_accounts/v1/metadata/x509/' + svc_account_name)
 """
 
print '+++++++++++ Access Endpoints using token ++++++++++++ '

#_HOST = 'http://localhost:8080'
_HOST = " https://api.endpoints.YOUR_PROJECT.cloud.goog"

idt = "IAP_ISSUED_TOKEN_HERE"
print 'id_token: ' + idt

id = 7777

print '-------------- list'
response = requests.get(_HOST+  '/todos', headers={'Authorization': 'Bearer ' + idt})
print response.text


print '-------------- put'
body = {
    'id': id,
    'task': 'some task'
}
response = requests.post(_HOST+ '/todos', headers={'Authorization': 'Bearer ' + idt }, json = body )
print response.text


print '-------------- list'
response = requests.get(_HOST+ '/todos', headers={'Authorization': 'Bearer ' + idt})
print response.text


print '-------------- get'
response = requests.get(_HOST + '/todos/' + str(id), headers={'Authorization': 'Bearer ' + idt})
print response.text


print '-------------- delete'
response = requests.delete( _HOST+ '/todos/' + str(id), headers={'Authorization': 'Bearer ' + idt})
print response.text

print '-------------- list'
response = requests.get(_HOST+ '/todos', headers={'Authorization': 'Bearer ' + idt})
print response.text

print '--------------------------------------------------------------------------'