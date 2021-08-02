from flask_sqlalchemy import SQLAlchemy
from app import App
from os import path
from flask import request, jsonify
from datetime import datetime, timedelta
from security import hash, match_passwords
import jwt
from functools import wraps

todos =  App(f'{path.dirname(__file__)}/config.ini')
db = SQLAlchemy(todos.app)

class TodoModel(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    todo = db.Column(db.String(80))
    timestamp = db.Column(db.String(80))

    def __init__(self, todo, timestamp):
        self.todo = todo
        self.timestamp = timestamp

    def json(self):
        return {'id': self.id, 'todo': self.todo, 'timestamp': self.timestamp}

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(80)) 
    timestamp = db.Column(db.String(80))

    def __init__(self, username, password, timestamp):
        self.username = username
        self.password = password
        self.timestamp = timestamp

    def json(self):
        return {'id': self.id, 'username': self.username, 'password': self.password, 'timestamp': self.timestamp}

db.create_all()

def authenticate(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing'}), 401
        try:
            data = jwt.decode(token, todos.app.config['SECRET_KEY'])
            user = UserModel.query.filter_by(id = data['id']).first()
        except:
            return jsonify({'message' : 'Token is invalid'}), 401
        return func(user, *args, **kwargs)
    return decorated

@todos.app.route('/register', methods = ['POST'])
def register():
    try:
        request_data = request.get_json()
        username = request_data['username']
        password = request_data['password']
        password = hash(password)
        timestamp = datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        input = UserModel(username, password, timestamp)
        db.session.add(input)
        db.session.commit()
        return {'user': input.json()}
    except Exception as e:
        return {"response": e}, 500

@todos.app.route('/login', methods = ['POST'])
def login():
    try:
        request_data = request.get_json()
        username = request_data['username']
        password = request_data['password']
        user = UserModel.query.filter_by(username = username).first()
        if user:
            user = user.json()
            if match_passwords(password, user['password']):
                token = jwt.encode(
                    {
                        'id': user['id'],
                        'exp': datetime.utcnow() + timedelta(minutes = 30)
                    },
                    todos.app.config['SECRET_KEY']
                )
                token = str(token, 'utf-8')
                return {'access-token': token}
            return {'message': 'Password is incorrect.'}, 401
        return {'message': 'User not found'}, 404
    except Exception as e:
        return {"response": e}, 500

@todos.app.route('/todo', methods = ['POST'])
def post():
    try:
        request_data = request.get_json()
        todo = request_data['todo']
        timestamp = datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        input = TodoModel(todo, timestamp)
        db.session.add(input)
        db.session.commit()
        return {'todo': input.json()}
    except Exception as e:
        return {"response": e}, 500

@todos.app.route('/todos', methods = ['GET'])
@authenticate
def get_todos():
    try:
        todos = TodoModel.query.all()
        if todos:
            return {'todos': list(map(lambda x: x.json(), todos))}, 200
        return {'message': 'Items not found'}, 404
    except Exception as e:
        return {'response': e}
    

@todos.app.route('/todo/<string:id>', methods = ['GET'])
@authenticate
def get_todo(id):
    try:
        todo = TodoModel.query.filter_by(id=id).first()
        if todo:
            return {'todo': todo.json()}, 200
        return {'message': 'Item not found'}, 404
    except Exception as e:
        return {'response': e}

@todos.app.route('/todo/<string:id>', methods = ['PUT'])
@authenticate
def update_todo(id):
    try:
        request_data = request.get_json()
        todo = TodoModel.query.get(id)
        if todo:
            todo.todo = request_data['todo']
            todo.timestamp = datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
            db.session.add(todo)
            db.session.commit()
            return {'todo': todo.json()}, 200
        return {'message': 'Item not found'}, 404
    except Exception as e:
        return {'message': e}

@todos.app.route('/todo/<string:id>', methods = ['DELETE'])
@authenticate
def delete_todo(id):
    try:
        todo = TodoModel.query.get(id)
        if todo:
            db.session.delete(todo)
            db.session.commit()
            return {'message': 'Item Deleted'}, 200
        return {'message': 'Item not found'}, 404
    except Exception as e:
        return {'message': e}

todos.app.run(host = todos.parms['endpoint_host'], port = todos.parms['endpoint_port'])