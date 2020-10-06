from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:postgres@localhost:5432/dashnotes_api"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class UsersModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String())

    def __init__(self, nickname):
        self.nickname = nickname

    def __repr__(self):
        return f"<User {self.nickname}>"

class StickiesModel(db.Model):
    __tablename__ = 'stickies'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String())

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return f"<Sticky {self.body}>"


@app.route('/')
def hello():
    return {
        "hello": "world"
    }

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
        results = [
            {
                "id": sticky.id,
                "body": sticky.body
            } for sticky in stickies
        ]
        return {"stickies": results}
    return {"lol": "something else"}

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