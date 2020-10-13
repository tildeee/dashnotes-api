from flask import Flask, make_response
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
import jwt
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

CORS(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    username = db.Column(db.String())
    auth_provider = db.Column(db.String())
    auth_id = db.Column(db.String())
    avatar_url = db.Column(db.String())

    notes = db.relationship('Note', backref='user')

    def __init__(self, name, auth_provider, auth_id, username, avatar_url):
        self.name = name
        self.auth_provider = auth_provider
        self.auth_id = auth_id
        self.username = username
        self.avatar_url = avatar_url

    def __repr__(self):
        return f"<User name: {self.name}, username: {self.username}, auth_provider: {self.auth_provider}>"

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return f"<Note {self.body}>"


@app.route('/auth/callback/gh/<code>', methods=['POST'])
def github_callback(code):
    r = requests.post('https://github.com/login/oauth/access_token', params={
        "client_id": os.environ.get("GITHUB_CLIENT_ID"),
        "client_secret": os.environ.get("GITHUB_CLIENT_SECRET"),
        "code": code
    }, headers={
        "Accept": "application/json"
    })
    auth_r = r.json()
    access_token = auth_r['access_token']

    user_details = requests.get('https://api.github.com/user', headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }).json()

    user = User.query.filter_by(auth_provider="GITHUB", auth_id=str(user_details['id'])).first()

    if user is None:
        user = User(
            name=user_details['name'],
            auth_provider="GITHUB",
            auth_id=user_details['id'],
            username=user_details['login'],
            avatar_url=user_details['avatar_url'],
        )
        db.session.add(user)
        db.session.commit()

    auth_code = jwt.encode({"auth_id": user.auth_id, "auth_provider": user.auth_provider}, os.environ.get("SECRET"), algorithm='HS256')

    return jsonify(name=user.name,
        username=user.username,
        avatar_url=user.avatar_url,
        auth_code=auth_code.decode('UTF-8'))

@app.route('/users')
def get_user_details():
    auth_header = request.headers.get('Authorization')
    token = auth_header.replace("Bearer ", "")
    decoded_token = jwt.decode(token, os.environ.get("SECRET"), algorithms=['HS256'])

    user = User.query.filter_by(auth_provider=decoded_token['auth_provider'], auth_id=str(decoded_token['auth_id'])).first()
    user_stickies = [
         {
             "id": sticky.id,
             "body": sticky.body,
             "user_id": sticky.user.id,
             "username": sticky.user.name
         } for sticky in user.notes
     ]
    return jsonify(name=user.name,
        username=user.username,
        avatar_url=user.avatar_url,
        stickies=user_stickies)

@app.route('/stickies', methods=['GET'])
def handle_stickies():
    stickies = Note.query.all()
    results = [
        {
            "id": sticky.id,
            "body": sticky.body,
            "username": sticky.user.name
        } for sticky in stickies
    ]
    response = make_response({"message": "ok", "stickies": results})
    return response

@app.route('/my-stickies', methods=['POST', 'GET'])
def handle_my_stickies():
    if request.method == 'POST':
        data = request.get_json()

        auth_header = request.headers.get('Authorization')
        token = auth_header.replace("Bearer ", "")
        decoded_token = jwt.decode(token, os.environ.get("SECRET"), algorithms=['HS256'])

        user = User.query.filter_by(auth_provider=decoded_token['auth_provider'], auth_id=str(decoded_token['auth_id'])).first()

        new_sticky = Note(body=data['body'])
        user.notes.append(new_sticky)

        db.session.add(new_sticky)
        db.session.commit()

        new_sticky_data = {
            "id": new_sticky.id,
            "body": new_sticky.body,
            "user_id": new_sticky.user.id,
            "username": new_sticky.user.name
        }
        return {"message": f"sticky {new_sticky.body} by {new_sticky.user.name} has been created successfully.", "sticky": new_sticky_data}
    elif request.method == 'GET':
        auth_header = request.headers.get('Authorization')
        token = auth_header.replace("Bearer ", "")
        decoded_token = jwt.decode(token, os.environ.get("SECRET"), algorithms=['HS256'])

        user = User.query.filter_by(auth_provider=decoded_token['auth_provider'], auth_id=str(decoded_token['auth_id'])).first()

        stickies = user.notes

        results = [
            {
                "id": sticky.id,
                "body": sticky.body,
                "user_id": sticky.user.id,
                "username": sticky.user.name
            } for sticky in stickies
        ]
        response = make_response({"message": "ok", "stickies": results})
        return response

@app.route('/stickies/<sticky_id>', methods=['DELETE', 'GET'])
def handle_sticky(sticky_id):
    sticky = Note.query.get_or_404(sticky_id)

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