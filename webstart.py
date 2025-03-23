from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__, template_folder = 'app/templates', static_folder = 'app/static')
main_folder = './main/'

@app.route('/')
@app.route('/index.html')
def index():
   return render_template('index.html')

@app.route('/user/<int:user_id>/')
def user_profile(user_id):
    return "Profile page of user #{}".format(user_id)

@app.route('/login/')
def register_user():
   text = 'ВХОД В DSChat:'
   return render_template('login.html', message = text, addr = request.remote_addr, cli = request.user_agent)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5050, debug=True)