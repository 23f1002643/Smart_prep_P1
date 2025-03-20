from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Account, Courses, Assessment
from datetime import datetime
import config

# Flask app setup
app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
print("Database initialized.")
# Checking if admin exist in the database or not
def check_admin():
    with app.app_context():
        admin = Account.query.filter_by(username='admin').first()
        if not admin:
            admin = Account(
                username='admin',
                f_name='Quiz',
                l_name='Master',
                pwd='admin123',
                edu_qul='12th',
                mobile_no='1234567890',
                dob=datetime.strptime('2000-01-01', '%Y-%m-%d').date(),
                email='admin@quizmaster',
                role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin account created.")

# Routes

# @app.route('/login', methods=['GET', 'POST'])
# @app.route('/')
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         print('username:', username)
#         print('password:', password)

#         user = Account.query.filter_by(username=username).first()
#         if user and user.pwd == password:
#             session['user_id'] = user.id
#             session['role'] = user.role
#             session.permanent = True
#             flash('Logged in successfully!', 'success')
#             return redirect(url_for('dashboard'))

#         flash('Invalid username or password', 'error')
#     return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        edu_qul = request.form.get('edu_qul')
        dob = request.form.get('dob')

        if Account.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))

        new_user = Account(
            username=username,
            pwd=password,
            f_name=f_name,
            l_name=l_name,
            edu_qul=edu_qul,
            dob=datetime.strptime(dob, '%Y-%m-%d').date(),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
# @app.route('/')
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Get username from form
        password = request.form.get('password')  # Get password from form

        user = Account.query.filter_by(username=username).first()  
        if user and user.pwd == password:
            session['user_id'] = user.id
            session['role'] = user.role
            session.permanent = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = Account.query.get(session['user_id'])
    
    if user.role == 'admin':
        return render_template('admin/dashboard.html')
    
    quizzes = Assessment.query.all()
    return render_template('user/dashboard.html', quizzes=quizzes)

@app.route('/admin/subjects', methods=['GET', 'POST'])
def manage_subjects():
    """Admin page - No restriction now!"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        new_subject = Courses(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')

    subjects = Courses.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

# Runing the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        check_admin()
        print("Setup Complete!")
    app.run(debug=True)
