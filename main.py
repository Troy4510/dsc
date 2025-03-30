from flask import  Flask, request, session, render_template, flash, redirect  #, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
#import datetime

app = Flask(__name__, template_folder = 'app/templates', static_folder = 'app/static')
app.config['SECRET_KEY'] = '48_obezyan_v_jopu_sunuli_banan'
#app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://dsc_user:484827548@localhost/dsc_base'

db = SQLAlchemy(app) #передаем sql-алхимику экземпляр приложения
login_manager = LoginManager(app) #передаем логин-мененджеру экземпляр приложени

class Users(db.Model): #класс для алхимика и flask-login
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    privileges = db.Column(db.String(5), nullable=False)

    def __init__(self, name, password, email, privileges):
        self. name = name
        self.password = self.set_password(password)
        self.email = email
        
    def set_password(self, password):
        return self.password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authentificated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymus(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
     
@login_manager.user_loader
def loading_user(user_id):
    #return Users.query.get(int(user_id))
    return db.session.get(Users, int(user_id))

@app.route('/')
@app.route('/index.html')
def index():
   return render_template('index.html')

@app.route('/login/', methods=['post',  'get'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Users.query.filter_by(email=username).first()
        #user = db.session.get(Users).filter_by(email=username).first()
        print(user.privileges)
        if not user or not user.check_password(password):
            flash('неверные данные аутентификации')
            return render_template('login.html', message = 'AUTH FAILED')
        
        login_user(user)
        
        if user.privileges == 'user':
            return redirect('/check/')
        elif user.privileges == 'admin':
            return redirect('/admin')    
        
        
    return render_template('login.html', message = 'LOGIN PAGE')


@app.route('/check/')
@login_required
def check_result():
    #print(dir(current_user))
    #print(db.session.get(Users, 3).id)
    #print(db.session.query(Users).filter_by(id = current_user))
    msg = f'USERNAME: {current_user.name}, STATUS: {current_user.privileges}'
    return render_template('check.html', message = msg)


@app.route('/admin/')
@login_required
def adm_page():
    msg = f'ROOT_NAME: {current_user.name}, STATUS: {current_user.privileges}'
    return render_template('admin.html', message = msg)  


if __name__ == "__main__":
    app.run(host='192.168.0.10', port=5050, debug=True)