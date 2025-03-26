from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Account, Courses, Assessment, CourseModule, AssessmentProblem, ExamPerformance 
from datetime import datetime
import config

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = config.config_settings['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = config.config_settings['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.config_settings['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['PERMANENT_SESSION_LIFETIME'] = config.config_settings['PERMANENT_SESSION_LIFETIME']
db.init_app(app)

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
        print('Bhai admin pehla hi creted hai')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        edu_qul = request.form.get('edu_qul')
        dob = request.form.get('dob')
        mobile_no = request.form.get('mobile_no')
        email = request.form.get('email')

        required_params = [f_name, l_name, pwd, username, email, mobile_no, edu_qul, dob]
        if not all(required_params):
            flash('Please fill all required fields!', 'danger')
            return redirect(url_for('register'))

        if Account.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))

        new_user = Account(
            username=username,
            pwd=pwd,
            f_name=f_name,
            l_name=l_name,
            edu_qul=edu_qul,
            dob=datetime.strptime(dob, '%Y-%m-%d').date(),
            mobile_no=mobile_no,
            email=email,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
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
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
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
    subjects = Courses.query.all()
    today = datetime.today().date()
    print(today)
    return render_template('user/dashboard.html', first_name=user.f_name, subjects=subjects, quizzes=quizzes, today=today)

@app.route('/admin/subjects', methods=['GET', 'POST'])
def manage_subjects():
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

@app.route('/admin/subjects/<int:sub_id>/chapters/<int:chap_id>/quizzes', methods=['GET', 'POST'])
def add_quiz(sub_id, chap_id):
    if request.method == 'POST':
        hours = request.form.get('hours')
        minutes = request.form.get('minutes')
        duration = f"{hours.zfill(2)}:{minutes.zfill(2)}"
        q_name = request.form.get('quiz_name')
        date = request.form.get('quiz_date')
        date = datetime.strptime(date, '%Y-%m-%d').date()
        remarks = request.form.get('remarks')
        print(q_name, date, duration, remarks)
        if not q_name or not date or not remarks:
            flash('Please fill in all the fields!', 'danger')
            return redirect(url_for('add_quiz', sub_id=sub_id, chap_id=chap_id))
        new_quiz = Assessment(q_name=q_name, date_of_quiz=date, time_duration=duration, remarks=remarks, chapter_id=chap_id)
        db.session.add(new_quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('add_quiz', sub_id=sub_id, chap_id=chap_id))

    Assessments = Assessment.query.all()
    return render_template('admin/quiz.html', quizzes=Assessments, sub_id=sub_id, chap_id=chap_id)

@app.route('/admin/subjects/<int:sub_id>/chapters/<int:chap_id>/quizzes/delete/<int:quiz_id>', methods=['GET','POST'])
def remove_quiz(sub_id, chap_id, quiz_id):
    if request.method != 'POST':
        flash('Invalid request!', 'danger')
        return redirect(url_for('add_quiz', sub_id=sub_id, chap_id=chap_id)) 

    quiz = Assessment.query.get(quiz_id)
    if quiz is not None:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz successfully removed!', 'success')
        return redirect(url_for('add_quiz', sub_id=sub_id, chap_id=chap_id))

    return redirect(url_for('add_quiz', sub_id=sub_id, chap_id=chap_id))

@app.route('/admin/subjects/<int:sub_id>/chapters/<int:chap_id>/quizzes/update/<int:quiz_id>', methods=['GET', 'POST'])
def update_quiz(sub_id, chap_id, quiz_id):
    quiz = Assessment.query.get(quiz_id)
    if request.method != 'POST':
        return render_template('admin/update_quiz.html', quiz=quiz, sub_id=sub_id, chap_id=chap_id)
    quiz.q_name = request.form.get('name')
    quiz.date_of_quiz = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    quiz.time_duration = request.form.get('hours') + ":" + request.form.get('minutes')
    quiz.remarks = request.form.get('remarks')
    db.session.commit()
    flash('Quiz updated successfully!', 'success')
    return redirect(url_for('add_quiz', sub_id=sub_id, chap_id=chap_id))

@app.route('/admin/subjects/<int:sub_id>/chapters/<int:chap_id>/quizzes/<int:quiz_id>/questions', methods=['GET', 'POST'])
def add_quest(sub_id, chap_id, quiz_id):    
    if request.method != 'POST':
        questions = AssessmentProblem.query.filter_by(quiz_id=quiz_id).all()
        return render_template('admin/questions.html', sub_id=sub_id, chap_id=chap_id, quiz_id=quiz_id, questions=questions)
    question = request.form.get('statement')
    options = request.form.getlist('options')
    correct_option = request.form.get('cor_opt')
    new_question = AssessmentProblem(quiz_id=quiz_id, statement=question, opt1=options[0], opt2=options[1], opt3=options[2], opt4=options[3], cor_opt=correct_option)
    db.session.add(new_question)
    db.session.commit()
    flash('Question added successfully!', 'success')
    return redirect(url_for('add_quest', sub_id=sub_id, chap_id=chap_id, quiz_id=quiz_id))

@app.route('/admin/subjects/<int:sub_id>/chapters/<int:chap_id>/quizzes/<int:quiz_id>/questions/delete/<int:ques_id>', methods=['GET', 'POST'])
def remove_quest(sub_id, chap_id, quiz_id, ques_id):
    if request.method!= 'POST':
        flash('Invalid request!', 'danger')
        return redirect(url_for('add_quest', sub_id=sub_id, chap_id=chap_id, quiz_id=quiz_id))
    question = AssessmentProblem.query.get(ques_id)
    if question is not None:
        db.session.delete(question)
        db.session.commit()
        flash('Question successfully removed!', 'success')
        return redirect(url_for('add_quest', sub_id=sub_id, chap_id=chap_id, quiz_id=quiz_id))
    return redirect(url_for('add_quest', sub_id=sub_id, chap_id=chap_id, quiz_id=quiz_id))

# Update question
@app.route('/admin/subjects/<int:sub_id>/chapters/<int:chap_id>/quizzes/<int:quiz_id>/questions/update/<int:ques_id>', methods=['GET', 'POST'])
def update_quest(sub_id, chap_id, quiz_id, ques_id):
    question = AssessmentProblem.query.get(ques_id)
    if request.method != 'POST':
        return render_template('admin/update_quest.html', question=question, sub_id=sub_id, chap_id=chap_id, quiz_id=quiz_id)
    question.statement = request.form.get('statement')
    options = request.form.getlist('options')
    question.opt1 = options[0]
    question.opt2 = options[1]
    question.opt3 = options[2]
    question.opt4 = options[3]
    question.cor_opt = request.form.get('cor_opt')
    db.session.commit()
    flash('Question updated successfully!', 'success')
    return redirect(url_for('add_quest', sub_id=sub_id, chap_id=chap_id, quiz_id=quiz_id))

@app.route('/user/quiz/view/<int:quiz_id>', methods=['GET'])
def quiz_info(quiz_id):
    quiz = Assessment.query.get(quiz_id)
    questions = AssessmentProblem.query.filter_by(quiz_id=quiz_id).all()
    return render_template('user/quiz_info.html', quiz=quiz, questions=questions)



@app.route('/user/quiz/start/<int:quiz_id>', methods=['GET', 'POST'])
def start_Assessment(quiz_id):
    if 'user_id' not in session:
        flash("You need to log in to take the quiz.", "warning")
        return redirect(url_for('login'))
    today = datetime.today().date()
    quiz = Assessment.query.get(quiz_id)
    if quiz.date_of_quiz != today: # current date check 
        flash("Quiz is not available today", "warning")
        return redirect(url_for('dashboard'))
    if request.method != 'POST': 
        quiz = Assessment.query.get(quiz_id)
        quest = AssessmentProblem.query.filter_by(quiz_id=quiz_id).all()
        return render_template('user/quiz.html', quiz=quiz, questions=quest)
    
    ans = request.form.to_dict()
    quest = AssessmentProblem.query.filter_by(quiz_id=quiz_id).all()
    Total_Marks = sum(
        1 for question in quest
        if str(question.id) in ans and int(ans[str(question.id)]) == question.cor_opt
    )
    print("Total Marks:", Total_Marks)
    
    latest_score = ExamPerformance(score=Total_Marks, user_id=session['user_id'], quiz_id=quiz_id)
    db.session.add(latest_score)
    db.session.commit()

    flash('Quiz submitted successfully!', 'success')
    return render_template('user/score.html', quiz=quiz, Total_Marks=Total_Marks)

@app.route('/admin/manage_user/<int:user_id>', methods=['GET', 'POST'])
def manage_user(user_id):
    if 'user_id' not in session or session['role']!= 'admin':
        return redirect(url_for('login'))
    users = Account.query.all()
    if request.method == 'POST':
        user_id = request.form.get('user_id') 
        print("User_id:", user_id)  # Debugging

        if user_id is None:
            # flash("Invalid user ID!", "danger")
            return render_template('admin/manage_user.html', users=users)

        user = Account.query.get(user_id)  

        if user:
            user.active = not user.active 
            db.session.commit()
            flash(f'User {user_id} status changed successfully!', 'success')
        else:
            flash(f'User {user_id} not found!', 'danger')

        return redirect(url_for('manage_user', user_id=session['user_id']))  # Redirect to avoid form resubmission

    return render_template('admin/manage_user.html', users=users)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_role = session.get('role')  # Get the role of the logged-in user

    if request.method == 'POST':
        search_query = request.form.get('search')

        if not search_query:
            flash(f'Search "{search_query}" not found!', 'danger')
            return redirect(url_for('search'))  # Redirect if empty search

        # Admin can search everything
        if user_role == 'admin':
            users = Account.query.filter(Account.username.ilike(f'%{search_query}%')).all()
            subjects = Courses.query.filter(Courses.s_name.ilike(f'%{search_query}%')).all()
            quizzes = Assessment.query.filter(Assessment.q_name.ilike(f'%{search_query}%')).all()
            chapters = CourseModule.query.filter(CourseModule.name.ilike(f'%{search_query}%')).all()
            questions = AssessmentProblem.query.filter(AssessmentProblem.statement.ilike(f'%{search_query}%')).all()
        else:
            # Normal user should only see quizzes and subjects
            users = []
            subjects = Courses.query.filter(Courses.s_name.ilike(f'%{search_query}%')).all()
            quizzes = Assessment.query.filter(Assessment.q_name.ilike(f'%{search_query}%')).all()
            chapters = CourseModule.query.filter(CourseModule.name.ilike(f'%{search_query}%')).all()
            questions = []

        return render_template('search.html',
                                users=users,
                                subjects=subjects,
                                quizzes=quizzes,
                                chapters=chapters,
                                questions=questions,
                                user_role=user_role,
                                search_query=search_query)

    return render_template('search.html', user_role=user_role)

@app.route('/user/scores_history')
def scores_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    scores = ExamPerformance.query.filter_by(user_id=session['user_id']).order_by(ExamPerformance.time_of_attempt.desc()).all()
    return render_template('user/scores_history.html', scores=scores)

# make routes for subjects for user 
@app.route('/user/subjects/<int:sub_id>', methods=['GET', 'POST'])
def subjects(sub_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))   
    
    user = Account.query.get(session['user_id'])
    subject = Courses.query.get(sub_id)
    chapters = CourseModule.query.filter_by(subject_id=sub_id).all()
    return render_template('user/view_chapter.html', user=user, subject=subject, chapters=chapters) 

@app.route('/user/chapter/<int:chap_id>', methods=['GET', 'POST'])
def available_quiz(chap_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    chapter = CourseModule.query.get(chap_id)
    if not chapter:
        flash('Chapter not found!', 'danger')
        return redirect(url_for('dashboard'))

    quizzes = Assessment.query.filter_by(chapter_id=chap_id).all()
    return render_template('user/view_quiz.html', quizzes=quizzes, chapter=chapter)






if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        check_admin()
        print("Admin Already Exists")
    app.run(debug=True)

