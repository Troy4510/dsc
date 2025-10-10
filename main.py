from flask import  Flask, request, session, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import random
import datetime
import config

app = Flask(__name__, template_folder = 'app/templates', static_folder = 'app/static')
app.config['SECRET_KEY'] = config.app_key
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)
#app.config['PERMANENT'] = False #при закрыти браузера
upload_folder = './main/app/static/avatars'

if not os.path.exists(upload_folder):
    print(f'создание папки загрузки ')
    os.makedirs(upload_folder)
    
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    ava_link = db.Column(db.String(100), default = 'default.png')

    def __init__(self, name, password, email, privileges, ava_link):
        self. name = name
        self.password = password
        self.email = email
        self.privileges = privileges
        self.ava_link = ava_link
    
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
'''
def createdb():
    db.create_all()
    return 'DB created'
'''
     
@login_manager.user_loader
def loading_user(user_id):
    x = db.session.get(Users, int(user_id))
    return x

@app.route('/')
@app.route('/index.html')
def index():
    val =[]
    print(request.user_agent)
    val.append(request.remote_addr)
    val.append(request.user_agent)
    #print(val)
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
            return redirect('/admin/1')    
        
        
    return render_template('login.html', message = 'ВХОД:', mod_message = "Введите данные для аутентификации")


@app.route('/user/')
@login_required
def check_result():
    if os.path.exists(app.config['UPLOAD_FOLDER'] + '/' + current_user.ava_link):
        #print(f'аватар найден {app.config['UPLOAD_FOLDER'] + '/' + current_user.ava_link}')
        #print(os.listdir(app.config['UPLOAD_FOLDER']))
        ava = current_user.ava_link
        #print(current_user.ava_link)
    else:
        #print(f'аватар не найден {app.config['UPLOAD_FOLDER'] + '/' + current_user.ava_link}')
        #print(os.listdir(app.config['UPLOAD_FOLDER']))
        ava = 'default.png'
        print(ava)
    
    if not current_user.isblocked:
        msg = f'СТРАНИЦА ПОЛЬЗОВАТЕЛЯ: {current_user.name}, СТАТУС: {current_user.privileges}'
        return render_template('user.html', message = msg, avatar = ava)
    else:
        msg = f'ПОЛЬЗОВАТЕЛЬ {current_user.name} ЗАБЛОКИРОВАН, ОБРАТИТЕСЬ К АДМИНИСТРАТОРУ'
        return render_template('blocked.html', message = msg, avatar = ava)

@app.route('/admin/<page>', methods=['post',  'get'])
@login_required
def adm_page(page):
    records = Users.query.order_by(Users.id).all()
    current_page = int(page)
    if current_page < 1: current_page = 1
    max_records = len(records)
    pages_count = int(max_records/10)+1
    if current_page > pages_count: current_page = pages_count
    start_reading = current_page * 10 - 10
    '''
    #print(start_reading)
    #print(f"page = {page}")
    #print(max_page)
    #print(pages_count) 
    #отбросить дроби и прибавить 1
    #дальше от 0 до 9(если есть), и от 10 до 19 (если есть) и т.д.
    records1 = Users.query.order_by(Users.id).offset(0).limit(10).all()
    print(len(records1))
    print(records1)
    records2 = Users.query.order_by(Users.id).offset(10).limit(10).all()
    print(len(records2))
    print(records2)
    for i in range(0, 10):pass
    '''
    
    if current_user.privileges == 'admin':
        msg = f'ROOT_NAME: {current_user.name}, <br> STATUS: {current_user.privileges}'
        ava = '/static/avatars/' + current_user.ava_link
        listX = Users.query.order_by(Users.id).offset(start_reading).limit(10).all()
        #print(len(listX))
        users_values = []
        for userX in listX:
            users_values.append(userX)
        #print(users_values[0].name)
        return render_template('admin.html', message = msg, avatar = ava, users_values = users_values,
                               max_page = pages_count, page_num = current_page)
    else: return 'НЕТ ДОСТУПА'

@app.route('/change/<user_id>', methods=['post',  'get'])
@login_required
def change_user(user_id):
    #разобраться с post/get
    if current_user.privileges == 'admin':
        if request.method == 'GET':
            #print('GET METHOD')
            userX = Users.query.filter_by(id=user_id).first()
            if os.path.exists(app.config['UPLOAD_FOLDER'] + '/' + userX.ava_link):
                ava = userX.ava_link
            else: ava = ava = 'default.png'
            return render_template('change.html', avatar = ava,
                                   message = f'ИМЯ: {userX.name}, ID: {userX.id}', user = userX)
        if request.method == 'POST':
            #print('POST METHOD')
            userX = Users.query.filter_by(id=user_id).first()
            curr_id = int(request.form.get('id'))
            new_name = request.form.get('username')
            new_email = request.form.get('email')
            new_privileges = request.form.get('privileges')
            
            if request.form.get('blockstate'): new_blockstate = True
            else: new_blockstate = False
            
            if request.form.get('ava_reset'):
                target1 = userX.ava_link
                if os.path.exists(app.config['UPLOAD_FOLDER'] + '/' + target1) and target1 != 'default.png':
                    os.remove(app.config['UPLOAD_FOLDER'] + '/' + target1) 
                new_ava = 'default.png'
            else:
                new_ava = userX.ava_link
            
            if request.form.get('password') == 'оставить старый':
                Users.query.filter_by(id = curr_id).update({
                    'name': new_name, 'email' : new_email, 
                    'privileges' : new_privileges,
                    'isblocked' : new_blockstate, 'ava_link' : new_ava})
            else:
                new_password = generate_password_hash(request.form.get('password'))
                Users.query.filter_by(id = curr_id).update({
                    'name': new_name, 'password' : new_password, 'email' : new_email, 
                    'privileges' : new_privileges,
                    'isblocked' : new_blockstate, 'ava_link' : new_ava})
            
            db.session.commit()
            return redirect('/admin/1')
        
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
            usr1 = Users(name=username1, password=generate_password_hash(raw_pass),
                         email=email1, privileges=privileges1, ava_link='default.png')
            db.session.add_all([usr1])
            db.session.commit()
            #except: print('error')
            return redirect('/admin/1')
    else: return 'НЕТ ДОСТУПА'
    return render_template('register.html')
    
@app.route('/regnew/', methods=['post','get'])
def try_add_user():
    if request.method == 'POST':
            val_is_ok = True
            pass_check = True
            tmp_name = request.form.get('nickname')
            tmp_email = request.form.get('email')
            tmp_password1 = request.form.get('password1')
            tmp_password2 = request.form.get('password2')
            nick_msg = email_msg = password_msg = 'ok'
            #проверка почты, имени и пароля
            email_check = Users.query.filter_by(email=tmp_email).first()
            '''
            email_test1 = tmp_email.find('@')
            email_test2 = tmp_email.find('.', tmp_email.find('@')) > 2
            email_test3 = tmp_email.find('.', len(tmp_email)-5) < len(tmp_email)-1
            '''
            #(есть символ "@" и он не в начале) &&
            #(символ "@" делит адрес надвое и он единственный) &&
            #(символ "@" не в конце)
            email_test1 = (tmp_email.find('@') > 0) \
                and (len(tmp_email.split('@'))==2)\
                and (tmp_email.rfind('@') != len(tmp_email)-1)
    
            #('.' присутствует) && (минимум 2 символа после '.') &&
            #(между '@' и '.' минимум 2 символа)
            email_test2 = (tmp_email.find('.') > 0) \
                and (tmp_email.rfind('.') < len(tmp_email)-2) \
                and (tmp_email.rfind('.') - tmp_email.rfind('@')>2)
            
            if email_test1==email_test2==True: email_test = True
            else: email_test = False
            name_check = Users.query.filter_by(name=tmp_name).first()
            pass_check = (len(tmp_password1)>5) and (tmp_password1 == tmp_password2)
            if email_check: val_is_ok = False; email_msg = 'такой e-mail уже есть в базе'
            if email_test == False: 
                email_msg = 'неправильно введён email'
                val_is_ok = False
            if name_check: val_is_ok = False; nick_msg = 'придумайте другое имя'
            if len(tmp_name)<4: val_is_ok = False; nick_msg = 'имя слишком короткое (менее 4 символов)'
            if not pass_check: password_msg = 'пароли не совпадают или длинна менее 6 символов'
            if not val_is_ok or not pass_check:
                return render_template('regnew.html', message = 'РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ', 
                            nick_msg = nick_msg, email_msg = email_msg, 
                            password_msg = password_msg, ava_link = 'default.png')
            else:
                usr1 = Users(name=tmp_name, password=generate_password_hash(tmp_password1),
                             email=tmp_email, privileges='user', ava_link = 'default.png')
                db.session.add_all([usr1])
                db.session.commit()
                return 'Пользователь успешно зарегистрирован, <a href = "/login/" /a> ВОЙТИ В СИСТЕМУ'
            
    if request.method == 'GET':
            return render_template('regnew.html', message = 'РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ', 
                                   nick_msg = 'введите имя (минимум 4 символа)',
                                   email_msg = 'введите адрес почты',
                                   password_msg = 'введите пароль (минимум 6 символов)')

@app.route('/user_editing/', methods=['post','get'])
@login_required
def user_editing():
    if os.path.exists(app.config['UPLOAD_FOLDER'] + '/' + current_user.ava_link):
        ava = current_user.ava_link
        print(f'файл аватара найден: {app.config['UPLOAD_FOLDER'] + '/' + current_user.ava_link}')
    else: 
        ava = 'default.png'
    userX = Users.query.filter_by(id=current_user.id).first()
    
    if request.method == 'GET':
        if current_user.privileges == 'user':   
            return render_template('user_editing.html', avatar = ava, user = userX)

    if request.method == 'POST':
        #print(request.form)
        tmp_password1 = request.form.get('password1')
        tmp_password2 = request.form.get('password2')
        if tmp_password1 == tmp_password2 == 'оставить старый':
            return redirect ('/user_editing/')
        else:
            pass_check = (len(tmp_password1)>5) and (tmp_password1 == tmp_password2)
            if not pass_check:
                password_msg = 'пароли не совпадают или длинна менее 6 символов'
                return render_template('user_editing.html', avatar = ava,
                                       password_msg = password_msg, user = userX)
                
            if pass_check:
                password_msg = 'пароль успешно изменен'
                new_password = generate_password_hash(tmp_password1)
                Users.query.filter_by(id = current_user.id).update({'password' : new_password})
                db.session.commit()
                return render_template('user_editing.html', avatar = ava,
                                       password_msg = password_msg, user = userX)
    


@app.route('/upload', methods=['POST'])#указан в user_editing.html
@login_required
def upload_file():
    if 'file' not in request.files:
        return 'файл не выбран', 400

    file = request.files['file']
    
    if file.filename == '':
        return 'файл не выбран', 400
    
    #проверка и изменение имени файла и расширения
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ext1 = file.filename.rsplit('.', 1)
        
    if ext1[1] in ALLOWED_EXTENSIONS:
        #print(f'{ext1[1]} в разрешенных расширениях')
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y_%m_%d_%H_%M_%S_")
        new_filename = formatted_date + str(random.randrange(5000)) + '.' + ext1[1]
        #print(f'новое имя файла: {new_filename}')
        file.filename = new_filename
        #print(f'текущий пользователь: {current_user.name}')
        #print(f'текущий пользователь: {current_user.id}')
        #удаление файла старой аватарки и проверка на default
        if current_user.ava_link == 'default.png':
            Users.query.filter_by(id = current_user.id).update({'ava_link' : new_filename})
        else:
            target1 = current_user.ava_link
            print(f'current: "{target1}"')
            if os.path.exists(app.config['UPLOAD_FOLDER'] + '/' + target1):
                os.remove(app.config['UPLOAD_FOLDER'] + '/' + target1)
            Users.query.filter_by(id = current_user.id).update({'ava_link' : new_filename})
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        db.session.commit()
        return redirect('/user_editing/')
    else:
        return f'расширение {ext1[1]} не разрешено'

@app.route("/chat/")
def chatting():
    return render_template('chat.html')

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return render_template('logout.html', ok_message = "Вы успешно вышли из системы")


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5050, debug=True)