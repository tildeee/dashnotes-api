from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from authlib.integrations.flask_client import OAuth
from loginpass import create_flask_blueprint
from loginpass import Twitter, GitHub, Google

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:postgres@localhost:5432/dashnotes_api"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


app.secret_key = 'c1662e05-476a-4ce6-8759-2fcbc99e7c06'


login_manager = LoginManager()
login_manager.init_app(app)
oauth = OAuth(app)

app.config['GITHUB_CLIENT_ID'] = 'Iv1.13f31d855859ad99'
app.config['GITHUB_CLIENT_SECRET'] = '2a6c3f7e7a91c8f9bf5f7cd7a3d0f7d2182d956d'

@login_manager.user_loader
def load_user(user_id):
    return UsersModel.query.get(user_id)

def handle_authorize(remote, raw_token, user_info):
    token = str(raw_token)
    user_gh_id = user_info['sub']
    user = UsersModel.query.filter_by(github_id=user_gh_id).first()
    if user is None:
        new_user = UsersModel(user_info['name'], user_gh_id)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return {"message": f"you did it....... it's new..... {token} ................ {user_info}"}
    else:
        login_user(user)
        return {"message": "you did it....... it's old....."}
    return {"message":f"wow. remote: {remote}, token: {token}, user_info: {user_info}"}

bp = create_flask_blueprint([GitHub], oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return {"message": "you logged out...."}

class UsersModel(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String())
    github_id = db.Column(db.String())

    def __init__(self, nickname, github_id):
        self.nickname = nickname
        self.github_id = github_id

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