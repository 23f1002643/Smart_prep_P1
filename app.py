from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Account, Courses, Assessment, CourseModule, AssessmentProblem, ExamPerformance 
from datetime import datetime, timedelta
import config

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = config.config_settings['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config.config_settings['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.config_settings['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['PERMANENT_SESSION_LIFETIME'] = config.config_settings['PERMANENT_SESSION_LIFETIME']
db.init_app(app)
print("Database initialized.")

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
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

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

        new_sub = Courses(s_name=name, remarks=description)
        db.session.add(new_sub)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('manage_subjects'))

    subjects = Courses.query.all()
    print(subjects)
    return render_template('admin/subjects.html', subjects=subjects)

@app.route('/admin/subjects/delete/<int:sub_id>', methods=['GET','POST'])
def delete_subject(sub_id):
    """Admin panel - remove an existing subject"""
    if request.method != 'POST':
        flash('Invalid request!', 'danger')
        return redirect(url_for('manage_subjects'))

    subject = Courses.query.get(sub_id)
    print(subject)
    if subject is not None:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject successfully removed!', 'success')
    else:
        flash('Subject not found!', 'danger')

    return redirect(url_for('manage_subjects'))

@app.route('/admin/subjects/<int:sub_id>/chapters', methods=['GET', 'POST'])
def add_chapter(sub_id):
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        new_chapter = CourseModule(name=name, description=description, subject_id=sub_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('add_chapter', sub_id=sub_id))

    chapters = CourseModule.query.all()
    return render_template('admin/chapters.html', chapters=chapters, sub_id=sub_id)

@app.route('/admin/subjects/<int:sub_id>/chapters/delete/<int:chap_id>', methods=['GET','POST'])
def delete_chapter(sub_id, chap_id):
    if request.method != 'POST':
        flash('Invalid request!', 'danger')
        return redirect(url_for('add_chapter', sub_id=sub_id)) 

    chapter = CourseModule.query.get(chap_id)
    if chapter is not None:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter successfully removed!', 'success')
        return redirect(url_for('add_chapter', sub_id=sub_id))

    return redirect(url_for('add_chapter', sub_id=sub_id))

@app.route('/admin/subjects/update/<int:sub_id>', methods=['GET', 'POST'])
def update_sub(sub_id):
    subject = Courses.query.get(sub_id)
    print(subject)
    print(sub_id)
    if request.method != 'POST':
        return render_template('admin/update_sub.html', subject=subject)
    subject.s_name = request.form.get('name')
    subject.remarks = request.form.get('description')
    db.session.commit()
    flash('Subject updated successfully!', 'success')
    return redirect(url_for('manage_subjects'))

@app.route('/admin/subjects/<int:sub_id>/chapters/update/<int:chap_id>', methods=['GET', 'POST'])
def update_chap(sub_id, chap_id):
    chapter = CourseModule.query.get(chap_id)
    if request.method != 'POST':
        return render_template('admin/update_chap.html', chapter=chapter, sub_id=sub_id)
    chapter.name = request.form.get('name')
    chapter.description = request.form.get('description')
    db.session.commit()
    flash('Chapter updated successfully!', 'success')
    return redirect(url_for('add_chapter', sub_id=sub_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        check_admin()
        print("Admin Already Exists")
    app.run(debug=True)

