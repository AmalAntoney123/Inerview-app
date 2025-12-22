from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt
from config import Config

load_dotenv()

# MongoDB connection for users
client = MongoClient(
    Config().MONGO_URI,
    tlsAllowInvalidCertificates=True
)
db = client['interview_app']
users_collection = db['users']

# User Blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required.')
            return redirect(url_for('user.signin'))
        
        user = users_collection.find_one({'email': email})
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            flash('Invalid email or password.')
            return redirect(url_for('user.signin'))
        
        # Successful login, set session
        session['user'] = email
        return redirect(url_for('user.dashboard'))
    
    return render_template('signin.html')

@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        # Basic validation
        if not fullname or not email or not password:
            flash('All required fields must be filled.')
            return redirect(url_for('user.signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('user.signup'))
        
        # Check if user exists
        if users_collection.find_one({'email': email}):
            flash('User with this email already exists.')
            return redirect(url_for('user.signup'))
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Save user
        user_data = {
            'fullname': fullname,
            'email': email,
            'phone': phone,
            'password': hashed_password
        }
        users_collection.insert_one(user_data)
        
        flash('Signup successful! Please sign in.')
        return redirect(url_for('user.signin'))
    
    return render_template('signup.html')

@user_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('user.signin'))
    
    # Get user data from database
    user_data = users_collection.find_one({'email': session['user']})
    
    # Mock data for now - in a real app, this would come from the database
    dashboard_data = {
        'user': user_data,
        'stats': {
            'interviews_completed': 5,
            'average_score': 4.2,
            'practice_time': '12h',
            'achievements': 3
        },
        'practice_areas': [
            {
                'name': 'Technical Interviews',
                'sessions': 10,
                'progress': 85,
                'color': 'purple'
            },
            {
                'name': 'Behavioral Practice',
                'sessions': 12,
                'progress': 78,
                'color': 'teal'
            },
            {
                'name': 'System Design Sessions',
                'sessions': 8,
                'progress': 92,
                'color': 'orange'
            }
        ],
        'upcoming_interviews': [
            {
                'title': 'Software Engineer Interview',
                'company': 'Google Inc.',
                'type': 'Technical Round',
                'date': 'Tomorrow 2:00 PM'
            },
            {
                'title': 'Product Manager Interview',
                'company': 'Amazon',
                'type': 'Behavioral Round',
                'date': 'Dec 28, 10:00 AM'
            }
        ],
        'today_tasks': [
            {
                'title': 'Behavioral Interview',
                'description': 'Prepare STAR method examples',
                'color': 'teal',
                'completed': False
            },
            {
                'title': 'System Design',
                'description': 'Design scalable architecture',
                'color': 'purple',
                'completed': False
            },
            {
                'title': 'Technical Coding',
                'description': 'Array problems practice',
                'color': 'orange',
                'completed': True
            }
        ],
        'calendar_events': [
            {
                'time': '10:00',
                'title': 'Technical Interview',
                'company': 'Google Inc',
                'color': 'teal'
            },
            {
                'time': '13:20',
                'title': 'Behavioral Round',
                'company': 'Amazon',
                'color': 'orange'
            }
        ]
    }
    
    return render_template('dashboard.html', **dashboard_data)

@user_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))