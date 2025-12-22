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
    return render_template('dashboard.html')

@user_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))