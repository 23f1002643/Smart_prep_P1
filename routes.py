from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Account, db, Courses, Assessment
from datetime import datetime
#from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Create a Blueprint for routes
auth = Blueprint('auth', __name__)

# Helper Decorator for Admin Routes
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Unauthorized access!', 'error')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

@auth.route('/login', methods=['GET', 'POST'])
@auth.route('/')
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Account.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['role'] = user.role
            session.permanent = True  # Keep session active for configured duration
            flash('Logged in successfully!', 'success')
            return redirect(url_for('auth.dashboard'))

        flash('Invalid username or password', 'error')
    return render_template('login.html')

# Registration Route
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')

        # Check if username is already taken
        if Account.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('auth.register'))

        # Create new user with hashed password
        new_user = Account(
            username=username,
            password=password,
            full_name=full_name,
            qualification=qualification,
            dob=datetime.strptime(dob, '%Y-%m-%d'),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# Logout Route
@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))

# Dashboard Route
@auth.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = Account.query.get(session['user_id'])
    
    if user.role == 'admin':
        return render_template('admin/dashboard.html')
    
    # If not admin, show user dashboard
    quizzes = Assessment.query.all()
    return render_template('user/dashboard.html', quizzes=quizzes)

# Admin - Manage Subjects Route
@auth.route('/admin/subjects', methods=['GET', 'POST'])
@admin_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        new_subject = Courses(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')

    subjects = Courses.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

