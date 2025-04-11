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
login_manager = LoginManager(app) #передаем логин-мененджеру экземпляр приложения

class Users(db.Model): #класс для алхимика и flask-login
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    privileges = db.Column(db.String(5), nullable=False)
    isblocked = db.Column(db.Boolean, default=False)

    def __init__(self, name, password, email, privileges):
        self. name = name
        self.password = password
        self.email = email
        self.privileges = privileges
    
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
    val =[]
    print(request.user_agent)
    val.append(request.remote_addr)
    val.append(request.user_agent)
    print(val)
    return render_template('index.html', data = val)
    #return redirect('/login/')
    
@app.route('/login/', methods=['post',  'get'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Users.query.filter_by(email=username).first()
        #user = db.session.get(Users).filter_by(email=username).first()
        #print(user.privileges)
        if not user or not user.check_password(password):
            flash('неверные данные аутентификации')
            return render_template('login.html', message = 'ОШИБКА АУТЕНТИФИКАЦИИ')
        
        login_user(user)
        
        if user.privileges == 'user':
            return redirect('/user/')
        elif user.privileges == 'admin':
            return redirect('/admin')    
        
        
    return render_template('login.html', message = 'LOGIN PAGE')


@app.route('/user/')
@login_required
def check_result():
    if not current_user.isblocked:
        msg = f'СТРАНИЦА ПОЛЬЗОВАТЕЛЯ: {current_user.name},СТАТУС: {current_user.privileges}'
        print(current_user.isblocked)
        return render_template('user.html', message = msg)
    else:
        msg = f'ПОЛЬЗОВАТЕЛЬ {current_user.name} ЗАБЛОКИРОВАН, ОБРАТИТЕСЬ К АДМИНИСТРАТОРУ'
        return render_template('user.html', message = msg)

@app.route('/admin/')
@login_required
def adm_page():
    if current_user.privileges == 'admin':
        msg = f'ROOT_NAME: {current_user.name}, STATUS: {current_user.privileges}'
        listX = Users.query.all()
        users_values = []
        for userX in listX:
            users_values.append(userX)
        print(users_values[0].name)
        return render_template('admin.html', message = msg, users_values = users_values)
    else: return 'НЕТ ДОСТУПА'

@app.route('/change/<user_id>', methods=['post',  'get'])
@login_required
def change_user(user_id):
    #разобраться с post/get
    if current_user.privileges == 'admin':
        if request.method == 'GET':
            #print('GET METHOD')
            userX = Users.query.filter_by(id=user_id).first()
            return render_template('change.html', message = f'ИМЯ: {userX.name}, ID: {userX.id}', user = userX)
        if request.method == 'POST':
            #print('POST METHOD')
            curr_id = int(request.form.get('id'))
            new_name = request.form.get('username')
            new_email = request.form.get('email')
            new_privileges = request.form.get('privileges')
            
            if request.form.get('blockstate'): new_blockstate = True
            else: new_blockstate = False
            
            if request.form.get('password') == 'оставить старый':
                Users.query.filter_by(id = curr_id).update({
                    'name': new_name, 'email' : new_email, 
                    'privileges' : new_privileges, 'isblocked' : new_blockstate})
            else:
                new_password = generate_password_hash(request.form.get('password'))
                Users.query.filter_by(id = curr_id).update({
                    'name': new_name, 'password' : new_password, 'email' : new_email, 
                    'privileges' : new_privileges, 'isblocked' : new_blockstate})
            
            db.session.commit()
            return redirect('/admin')
        
    else: return 'НЕТ ДОСТУПА'

@app.route('/register/', methods=['post',  'get'])
@login_required
def reg_new_user():
    if current_user.privileges == 'admin':
        if request.method == 'POST':
            username1 = request.form.get('username')
            raw_pass = request.form.get('password')
            print(raw_pass)
            email1 = request.form.get('email')
            privileges1 = request.form.get('privileges')
            #try:
            usr1 = Users(name=username1, password=generate_password_hash(raw_pass), email=email1, privileges=privileges1)
            db.session.add_all([usr1])
            db.session.commit()
            #except: print('error')
            return redirect('/admin')
    else: return 'НЕТ ДОСТУПА'
    return render_template('register.html')
    
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5050, debug=True)