from flask import Flask, render_template
from config import Config
from user import user_bp
from interview import interview_bp

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(user_bp)
app.register_blueprint(interview_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
