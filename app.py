from flask import Flask, render_template, Blueprint

app = Flask(__name__)

# User Blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/signin')
def signin():
    return render_template('signin.html')

@user_bp.route('/signup')
def signup():
    return render_template('signup.html')

app.register_blueprint(user_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
