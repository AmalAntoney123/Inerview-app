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
        if email == 'admin@gmail.com':
            return redirect(url_for('user.admin_dashboard'))
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

@user_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session['user'] != 'admin@gmail.com':
        return redirect(url_for('user.signin'))
    
    # Mock data for admin dashboard
    admin_data = {
        'user': {'fullname': 'Admin', 'email': 'admin@gmail.com'},
        'stats': {
            'total_users': 100,
            'active_sessions': 25,
            'system_health': 'Good'
        },
        'recent_activities': [
            {'action': 'New user registered', 'user': 'john@example.com', 'time': '2 hours ago'},
            {'action': 'Interview session completed', 'user': 'jane@example.com', 'time': '4 hours ago'},
            {'action': 'System backup completed', 'user': 'System', 'time': '1 day ago'}
        ],
        'users': [
            {'name': 'John Doe', 'email': 'john@example.com', 'status': 'Active', 'last_login': '2025-12-22'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'status': 'Active', 'last_login': '2025-12-21'},
            {'name': 'Bob Johnson', 'email': 'bob@example.com', 'status': 'Inactive', 'last_login': '2025-12-15'}
        ],
        'analytics': {
            'user_growth': [10, 25, 40, 60, 80, 100],
            'session_stats': [12, 19, 15, 25, 22, 30, 28]
        },
        'system_events': [
            {'time': '10:00', 'title': 'System Maintenance', 'type': 'Scheduled', 'color': 'bg-primary'},
            {'time': '14:00', 'title': 'Backup Completed', 'type': 'Automated', 'color': 'bg-success'}
        ]
    }
    
    return render_template('admin_dashboard.html', **admin_data)

@user_bp.route('/interviews')
def interviews():
    if 'user' not in session:
        return redirect(url_for('user.signin'))
    
    # Get user data
    user_data = users_collection.find_one({'email': session['user']})
    
    # Mock data for interviews
    interviews_data = {
        'user': user_data,
        'past_interviews': [
            {
                'id': 1,
                'title': 'Software Engineer Interview',
                'company': 'Google',
                'date': 'Dec 20, 2025',
                'duration': '45 min',
                'score': 8.5,
                'status': 'completed'
            },
            {
                'id': 2,
                'title': 'Frontend Developer Interview',
                'company': 'Meta',
                'date': 'Dec 18, 2025',
                'duration': '30 min',
                'score': 7.2,
                'status': 'completed'
            },
            {
                'id': 3,
                'title': 'Data Scientist Interview',
                'company': 'Amazon',
                'date': 'Dec 15, 2025',
                'duration': '50 min',
                'score': 9.1,
                'status': 'completed'
            }
        ],
        'current_interview': None  # For active interview
    }
    
    return render_template('interviews.html', **interviews_data)

@user_bp.route('/dashboard_content')
def dashboard_content():
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
        ]
    }
    
    return render_template('dashboard-content.html', **dashboard_data)

@user_bp.route('/interviews_content')
def interviews_content():
    if 'user' not in session:
        return redirect(url_for('user.signin'))
    
    # Get user data
    user_data = users_collection.find_one({'email': session['user']})
    
    # Mock data for interviews
    interviews_data = {
        'user': user_data,
        'past_interviews': [
            {
                'id': 1,
                'title': 'Software Engineer Interview',
                'company': 'Google',
                'date': 'Dec 20, 2025',
                'duration': '45 min',
                'score': 8.5,
                'status': 'completed'
            },
            {
                'id': 2,
                'title': 'Frontend Developer Interview',
                'company': 'Meta',
                'date': 'Dec 18, 2025',
                'duration': '30 min',
                'score': 7.2,
                'status': 'completed'
            },
            {
                'id': 3,
                'title': 'Data Scientist Interview',
                'company': 'Amazon',
                'date': 'Dec 15, 2025',
                'duration': '50 min',
                'score': 9.1,
                'status': 'completed'
            }
        ],
        'current_interview': None  # For active interview
    }
    
    return render_template('interviews-content.html', **interviews_data)

@user_bp.route('/tasks_content')
def tasks_content():
    if 'user' not in session:
        return redirect(url_for('user.signin'))
    
    # Get user data
    user_data = users_collection.find_one({'email': session['user']})
    
    # Mock data for tasks
    tasks_data = {
        'user': user_data,
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
        ]
    }
    
    return render_template('tasks-content.html', **tasks_data)

@user_bp.route('/settings_content')
def settings_content():
    if 'user' not in session:
        return redirect(url_for('user.signin'))
    
    # Get user data
    user_data = users_collection.find_one({'email': session['user']})
    
    return render_template('settings-content.html', user=user_data)

@user_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))