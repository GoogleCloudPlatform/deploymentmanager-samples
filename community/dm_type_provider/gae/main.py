from flask import Flask, request, abort
from flask_restplus import Api, Resource, fields
from functools import wraps

import logging
import pprint

app = Flask(__name__)
app.config['DEBUG'] = True

API_KEY_NAME='X-API-KEY'
API_KEY_VALUE='foo'

authorizations = {
    'ApiKeyAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': API_KEY_NAME
    }
}

api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
    authorizations=authorizations,
    security={"ApiKeyAuth" : []}
)

def auth_required(f):
    @wraps(f)
    def check_authorization(*args, **kwargs):
        if request.headers.get(API_KEY_NAME) == API_KEY_VALUE:
            logging.info("Authorization Key: " + API_KEY_VALUE)
        else:
            api.abort(401, API_KEY_NAME + ' header required')
        return f(*args, **kwargs)
    return check_authorization

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readOnly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details')
})

parser = api.parser()
parser.add_argument(API_KEY_NAME, location='headers', required=True)

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
@ns.expect(parser)
class TodoList(Resource):
    @ns.doc('list_todos')
    @ns.marshal_with(todo, envelope='items')
    @auth_required
    def get(self):
        '''List all resources'''        
        return list(DAO.todos.values())

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    @auth_required
    def post(self):
        '''Create a given resource'''        
        return DAO.create(api.payload), 201

@ns.route('/<int:id>')
@ns.expect(parser)
class Todo(Resource):
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    @ns.param('id', 'The task identifier')
    @ns.response(404, 'Todo not found')
    @auth_required
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    @ns.param('id', 'The task identifier')
    @auth_required
    def delete(self, id):
        '''Delete a given resource'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.response(404, 'Todo not found')
    @ns.param('id', 'The task identifier')
    @ns.marshal_with(todo)
    @auth_required
    def put(self, id):
        '''Update a given resource'''        
        return DAO.update(id, api.payload)

#class LoggingMiddleware(object):
#    def __init__(self, app):
#        self._app = app
#
#    def __call__(self, environ, resp):
#        errorlog = environ['wsgi.errors']
#        pprint.pprint(('REQUEST', environ), stream=errorlog)
#
#        def log_response(status, headers, *args):
#            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
#            return resp(status, headers, *args)
#        return self._app(environ, log_response)

#if __name__ == '__main__':
    #context = ('server.crt','server.key')
    #app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    #app.run(host='0.0.0.0', port=8081, debug=True,  threaded=True, ssl_context=context)
