from flask import Flask, request, abort, logging
from flask_restplus import Api, Resource, fields
from flask.logging import default_handler
from flask_cors import CORS

from functools import wraps

import logging, sys, os
import pprint
import base64
import json
import requests as prequests
import jwt
from jwt.exceptions import MissingRequiredClaimError, InvalidAudienceError, InvalidIssuerError, InvalidAlgorithmError

from google.oauth2 import id_token
from google.auth import transport
import google.auth.transport.requests
from google.auth.transport import requests

IAP_URL = os.getenv('IAP_URL', "https://YOUR_IAP_PROJECT.appspot.com")
JWT_ISSUER = os.getenv('JWT_ISSUER', "YOUR_IAP_PROJECT@appspot.gserviceaccount.com")
JWT_AUDIENCE = os.getenv('JWT_AUDIENCE', "api.endpoints.YOUR_ENDPOINTS_PROJECT.cloud.goog")

app = Flask(__name__)
cors = CORS(app, resources={r"/todos*": {
      "origins": IAP_URL,
      "allow_headers": ["Authorization", "Content-Type", "X-My-Custom-Header"],
      "methods": ["GET", "POST", "PUT", "DELETE"]
    }
})


hdlr = logging.StreamHandler(sys.stdout)
#formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#hdlr.setFormatter(formatter)
app.logger.addHandler(hdlr) 
app.logger.setLevel(logging.DEBUG)

app.logger.removeHandler(default_handler)

AUTHORIZATION_HEADER = 'Authorization'
ENDPOINTS_HEADER = 'X-Endpoint-API-UserInfo'
IAP_CLAIMS=['X-Goog-Authenticated-User-ID', 'X-Goog-Authenticated-User-Email']

certs_url='https://www.googleapis.com/service_accounts/v1/metadata/x509/' + JWT_ISSUER

api = Api(app, version='1.0', title='TodoMVC API',  description='A simple TodoMVC API')

def auth_required(f):
    @wraps(f)
    def check_authorization(*args, **kwargs):
        if request.headers.get(AUTHORIZATION_HEADER):
            dec = base64.b64decode(request.headers.get(AUTHORIZATION_HEADER))
            app.logger.debug("X-Endpoint-API-UserInfo: " + dec)
            
            # verify atleast the issuer was sent
            #if JWT_ISSUER != json.loads(dec).get('issuer'):
            #  app.logger.error("id_token not issued by " + JWT_ISSUER)
            #  api.abort(500, "id_token not issued by " + JWT_ISSUER)

            token = request.headers.get('Authorization')
            app.logger.debug("Authorization: " + str(token))
            token = token.split(' ')[1]

            try:
                # verification of JWT Headers; most of the values should be checked by ESP;
                # The following reverifies the JWT
                # also use pyjwt here  parse out and decode the JWT (not verify)

                #kid = jwt.get_unverified_header(token).get('kid')
                #r = prequests.get(certs_url)
                #public_key = r.json().get(kid)
                #from cryptography import x509
                #from cryptography.hazmat.backends import default_backend
                #cert = x509.load_pem_x509_certificate(public_key.encode(), default_backend())
                options = {
                    'verify_signature': False,
                    'verify_exp': True,
                    'verify_nbf': False,
                    'verify_iat': True,
                    'verify_aud': True,
                    'require_exp': True,
                    'require_iat': False,
                    'require_nbf': False
                }
                #decoded_jwt = jwt.decode(token,key=cert.public_key(), algorithms=['RS256'],audience=JWT_AUDIENCE, issuer=JWT_ISSUER, options=options)
                decoded_jwt = jwt.decode(token,audience=JWT_AUDIENCE, issuer=JWT_ISSUER, options=options)

                for claim in IAP_CLAIMS:
                  app.logger.info("Decoded IAP headers: : {}, VALUE  {} ".format(claim, decoded_jwt.get(claim)))

            except (MissingRequiredClaimError, InvalidAudienceError, InvalidIssuerError, InvalidAlgorithmError)  as e:
              api.abort(500, str(e))
            
            # verificaiton isn't necessary since ESP will verify JWT signature, timestamp, issuer, audience
            # previous step validated JWT already
            #r = requests.Request()
            #jwt_verified = id_token.verify_token(token,r, certs_url=certs_url)
            app.logger.debug("User verification complete")
        else:
            api.abort(401, AUTHORIZATION_HEADER + ' header required')
        return f(*args, **kwargs)
    return check_authorization

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readOnly=True, description='The task id'),
    'task': fields.String(required=True, description='The task details')
})

class TodoDAO(object):
    def __init__(self):
        self.todos = {}

    def get(self, id):
        if (id in self.todos):        
           return self.todos[id]
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self,data):
        id = data['id']
        if (id in self.todos):
            api.abort(409, "Todo {} already exists".format(str(id)))
        self.todos[id] = data
        return data

    def update(self, id, data):
        if (id in self.todos):
          self.todo[id] = data
          return data
        api.abort(404, "Todo {} doesn't exist".format(id))

    def delete(self, id):
        if (id in self.todos):
          del self.todos[id]
          return
        api.abort(404, "Todo {} doesn't exist".format(id))

DAO = TodoDAO()


@ns.route('')
class TodoList(Resource):
    @ns.doc('list_todos')
    @ns.marshal_with(todo, envelope='items')
    @auth_required
    def get(self):
        '''List all resources'''     
        return list(DAO.todos.values())

    @ns.doc('create_todo')
    @ns.marshal_with(todo, code=201)
    @auth_required
    def post(self):
        '''Create a given resource'''        
        return DAO.create(api.payload), 201

@ns.route('/<int:id>')
class Todo(Resource):
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    @ns.response(404, 'Todo not found')
    @auth_required
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    @auth_required
    def delete(self, id):
        '''Delete a given resource'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.response(404, 'Todo not found')
    @ns.marshal_with(todo)
    @auth_required
    def put(self, id):
        '''Update a given resource'''        
        return DAO.update(id, api.payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50051, debug=False,  threaded=True)
