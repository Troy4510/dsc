from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask import request
from flask import render_template
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, template_folder = 'app/templates', static_folder = 'app/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://dsc_user:484827548@localhost/dsc_base'
db = SQLAlchemy(app)

#dialect+driver://username:password@host:port/database
#'postgresql+psycopg2://root:pass@localhost/my_db'

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    privileges = db.Column(db.String(5), nullable=False)
    isBlocked = db.Column(db.Boolean, default=False)
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/createdb/')
def createdb():
    db.create_all()
    return 'DB created'

@app.route('/create-admin/')
def makeroot():
    adm1 = 'troy'
    hash1 = generate_password_hash('dedmoroz')
    email1 = 'troy@xzgde.ru'
    privileges1 = 'admin'
    adm1 = Users(name=adm1, password=hash1, email=email1, privileges=privileges1)
    db.session.add_all([adm1])
    db.session.commit()
    return 'admin1 created'

@app.route('/create-user/')
def makeuser():
    name1 = 'test'
    hash1 = generate_password_hash('test')
    email1 = 'test@test.ru'
    privileges1 = 'user'
    usr1 = Users(name=name1, password=hash1, email=email1, privileges=privileges1)
    db.session.add_all([usr1])
    db.session.commit()
    return f'user {name1} added'



if __name__ == '__main__':
    #print(db.session.get(Users, 3).id)
    #print(db.session.query(Users).filter_by(id = current_user))
     app.run(host='127.0.0.1', port=5050, debug=True)