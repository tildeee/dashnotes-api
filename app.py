from flask import Flask, make_response
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

CORS(app)

class UsersModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    username = db.Column(db.String())
    auth_provider = db.Column(db.String())
    auth_id = db.Column(db.String())
    avatar_url = db.Column(db.String())

    def __init__(self, name, auth_provider, auth_id, username, avatar_url):
        self.name = name
        self.auth_provider = auth_provider
        self.auth_id = auth_id
        self.username = username
        self.avatar_url = avatar_url

    def __repr__(self):
        return f"<User {self.nickname}>"

class StickiesModel(db.Model):
    __tablename__ = 'stickies'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String())
    username = db.Column(db.String())

    def __init__(self, body, username):
        self.body = body
        self.username = username

    def __repr__(self):
        return f"<Sticky {self.body}>"


@app.route('/')
def hello():
    return {
        "hello": "world"
    }

@app.route('/whatever/github/<code>', methods=['POST'])
def whatever_github(code):
    r = requests.post('https://github.com/login/oauth/access_token', params={
        "client_id": os.environ.get("GITHUB_CLIENT_ID"),
        "client_secret": os.environ.get("GITHUB_CLIENT_SECRET"),
        "code": code
    }, headers={
        "Accept": "application/json"
    })
    print(r)
    auth_r = r.json()
    print("omaskfj;alsdkjflaskdjf")
    print(auth_r)
    access_token = auth_r['access_token']
    user_details = requests.get('https://api.github.com/user', headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }).json()

    user = UsersModel.query.filter_by(auth_provider="GITHUB", auth_id=str(user_details['id'])).first()

    if user is None:
        user = UsersModel(
            name=user_details['name'],
            auth_provider="GITHUB",
            auth_id=user_details['id'],
            username=user_details['login'],
            avatar_url=user_details['avatar_url'],
        )

    return jsonify(name=user.name,
        username=user.username,
        avatar_url=user.avatar_url)

@app.route('/authenticate/<code>', methods=['GET'])
def authenticate(code):
    print(code)
    response = make_response({"authenticate": f"{code}"})
    print(response)
    return response

@app.route('/stickies', methods=['POST', 'GET'])
def handle_stickies():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_sticky = StickiesModel(body=data['body'])
            db.session.add(new_sticky)
            db.session.commit()
            return {"message": f"sticky {new_sticky.body} has been created successfully."}
        else:
            return {"lol":"not json"}
    elif request.method == 'GET':
        stickies = StickiesModel.query.all()
        auth_header = request.headers.get('Authorization')
        results = [
            {
                "id": sticky.id,
                "body": sticky.body,
                "username": sticky.username
            } for sticky in stickies
        ]
        response = make_response({"message": "ok", "stickies": results})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/my-stickies', methods=['POST', 'GET'])
def handle_my_stickies():
    if request.method == 'POST':
        if request.is_json:
            print(f"heaedersrsrasdfasdfasfd {request.headers}")
            auth_header = request.headers.get('Authorization')
            username = auth_header[7:]
            data = request.get_json()
            new_sticky = StickiesModel(body=data['body'], username=username)
            db.session.add(new_sticky)
            db.session.commit()
            return {"message": f"sticky {new_sticky.body} by {new_sticky.username} has been created successfully."}
        else:
            return {"lol":"not json"}
    elif request.method == 'GET':
        auth_header = request.headers.get('Authorization')
        username = auth_header.replace("Bearer ", "")
        stickies = StickiesModel.query.filter_by(username=username)
        results = [
            {
                "id": sticky.id,
                "body": sticky.body,
                "auth_header": auth_header,
                "username": sticky.username
            } for sticky in stickies
        ]
        response = make_response({"message": "ok", "stickies": results})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/stickies/<sticky_id>', methods=['DELETE', 'GET'])
def handle_sticky(sticky_id):
    sticky = StickiesModel.query.get_or_404(sticky_id)

    if request.method == 'GET':
        response = {
            "id": sticky.id,
            "body": sticky.body
        }
        return {"message": "success", "sticky": response}
    elif request.method == 'DELETE':
        db.session.delete(sticky)
        db.session.commit()
        return {"message": f"Sticky {sticky.body} has been successfully deleted."}
    return {"lol": "boooo"}

if __name__ == '__main__':
    app.run(debug=True)