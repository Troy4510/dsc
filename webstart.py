from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__, template_folder = 'app/templates', static_folder = 'app/static')
main_folder = './main/'

@app.route('/')
@app.route('/index.html')
def index():
   return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5050, debug=True)