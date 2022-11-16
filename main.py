from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

with open('configuration.json', 'r') as c:
    params = json.load(c)["params"]


'''flask app making and starting'''
app = Flask(__name__)
app.secret_key = "College Erp"


if params['local_server']:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contact(db.Model):
    S_No = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), unique=False, nullable=False)
    Phone = db.Column(db.String(12), nullable=False)
    Email = db.Column(db.String(30), nullable=False)
    Message = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)


class Admin(db.Model):
    Admin_id = db.Column(db.String(50), primary_key=True)
    Name = db.Column(db.String(50), unique=False, nullable=False)
    Phone = db.Column(db.String(12), nullable=False)
    Email = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(30), nullable=False)


class Students(db.Model):
    Student_id = db.Column(db.String(50), primary_key=True)
    Name = db.Column(db.String(50), unique=False, nullable=False)
    Phone = db.Column(db.String(12), nullable=False)
    Email = db.Column(db.String(50), nullable=False)
    Pass = db.Column(db.String(30), nullable=False)
    Sem = db.Column(db.String(5), nullable=False)
    Course = db.Column(db.String(50), nullable=False)


class Teachers(db.Model):
    Teacher_id = db.Column(db.String(50), primary_key=True)
    Name = db.Column(db.String(50), unique=False, nullable=False)
    Phone = db.Column(db.String(12), nullable=False)
    Email = db.Column(db.String(50), nullable=False)
    Pass = db.Column(db.String(30), nullable=False)


class Posts(db.Model):
    S_No = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(50), unique=False, nullable=False)
    Written_by = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(3000), nullable=False)
    Date = db.Column(db.String(12), nullable=True)


class Courses(db.Model):
    S_No = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), unique=False, nullable=False)
    img_file = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(10), nullable=False)


@app.route("/")
def index():
    post = Posts.query.filter_by().all()
    return render_template('index.html', post=post)


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        message = request.form.get("message")
        entry = Contact(Name=name, Phone=phone, Email=email, Message=message, Date=datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html')


@app.route("/course")
def course():
    courses = Courses.query.filter_by().all()
    return render_template('course.html', courses=courses)


@app.route("/login", methods=['POST', 'GET'])
def login():
    username = request.form.get('email')
    password = request.form.get('pass')
    category = request.form.get('category')
    email = "@"
    passw = "@"
    idd = ""
    if category == "admin":
        try:
            admin = Admin.query.filter_by(Email=username).first()
            email = admin.Email
            passw = admin.Password
            idd = admin.Admin_id
        except Exception as e:
            print(e)
    elif category == "student":
        try:
            student = Students.query.filter_by(Email=username).first()
            email = student.Email
            passw = student.Pass
            idd = student.Student_id
        except Exception as e:
            print(e)
    elif category == "teacher":
        try:
            teacher = Teachers.query.filter_by(Email=username).first()
            email = teacher.Email
            passw = teacher.Pass
            idd = teacher.Teacher_id
        except Exception as e:
            print(e)
    if request.method == "POST":
        if username == email and password == passw:
            if category == "admin":
                session['user'] = params["admin_session"]
            if category == "student":
                session['user'] = params["student_session"]
            if category == "teacher":
                session['user'] = params["teacher_session"]
            return redirect('/dashboard/' + category + '/' + idd)
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route("/dashboard/admin/<string:adminid>", methods=['POST', 'GET'])
def admindashboard(adminid):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    if 'user' in session and session['user'] == params["admin_session"]:
        if request.method == "POST":
            admin.Name = request.form.get('adminname')
            admin.Phone = request.form.get('adminphone')
            admin.Email = request.form.get('adminemail')
            admin.Password = request.form.get('adminpass')
            db.session.commit()
            return redirect('/dashboard/admin/' + admin.Admin_id)
        return render_template("admindashboard.html", admin=admin)


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/login")


@app.route("/admin/<string:adminid>/editcourse")
def editcourse(adminid):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    courses = Courses.query.filter_by().all()
    if 'user' in session and session['user'] == params["admin_session"]:
        return render_template('editcourse.html', courses=courses, admin=admin)


@app.route("/admin/<string:adminid>/editcourse/<string:s_no>", methods=['POST', 'GET'])
def courseediting(adminid, s_no):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    course = Courses.query.filter_by(S_No=s_no).first()
    if 'user' in session and session['user'] == params["admin_session"]:
        if request.method == "POST":
            course.course_name = request.form.get("coursename")
            course.img_file = request.form.get("courseimg")
            course.category = request.form.get("coursecategory")
            db.session.commit()
            return redirect('/admin/' + admin.Admin_id + '/editcourse/' + str(course.S_No))
        return render_template('courseediting.html', course=course, admin=admin)


@app.route("/admin/<string:adminid>/viewcontact")
def viewcontact(adminid):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    contacts = Contact.query.filter_by().all()
    if 'user' in session and session['user'] == params["admin_session"]:
        return render_template('viewcontact.html', admin=admin, contacts=contacts)


@app.route("/admin/<string:adminid>/editpost")
def editpost(adminid):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    posts = Posts.query.filter_by().all()
    if 'user' in session and session['user'] == params["admin_session"]:
        return render_template('editpost.html', posts=posts, admin=admin)


@app.route("/admin/<string:adminid>/editpost/<string:s_no>", methods=['POST', 'GET'])
def postediting(adminid, s_no):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    post = Posts.query.filter_by(S_No=s_no).first()
    if 'user' in session and session['user'] == params["admin_session"]:
        if request.method == "POST":
            post.Title = request.form.get("posttitle")
            post.content = request.form.get("postcontent")
            post.Written_by = request.form.get("postwrittenby")
            db.session.commit()
            return redirect('/admin/' + admin.Admin_id + '/editpost/' + str(post.S_No))
        return render_template('postediting.html', post=post, admin=admin)


@app.route("/admin/<string:adminid>/editstudent")
def editstudent(adminid):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    students = Students.query.filter_by().all()
    if 'user' in session and session['user'] == params["admin_session"]:
        return render_template('editstudent.html', students=students, admin=admin)


@app.route("/admin/<string:adminid>/editstudent/<string:studid>", methods=['POST', 'GET'])
def studentediting(adminid, studid):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    student = Students.query.filter_by(Student_id=studid).first()
    if 'user' in session and session['user'] == params["admin_session"]:
        if request.method == "POST":
            student.Student_id = request.form.get("studid")
            student.Name = request.form.get("name")
            student.Phone = request.form.get("phone")
            student.Email = request.form.get("email")
            student.Pass = request.form.get("pass")
            student.Sem = request.form.get("sem")
            student.Course = request.form.get("course")
            db.session.commit()
            return redirect('/admin/' + admin.Admin_id + '/editstudent/' + student.Student_id)
        return render_template('studentediting.html', student=student, admin=admin)


@app.route("/admin/<string:adminid>/addstudent", methods=['POST', 'GET'])
def addstudent(adminid):
    admin = Admin.query.filter_by(Admin_id=adminid).first()
    if 'user' in session and session['user'] == params["admin_session"]:
        if request.method == "POST":
            student_id = request.form.get("studid")
            name = request.form.get("name")
            phone = request.form.get("phone")
            email = request.form.get("email")
            passs = request.form.get("pass")
            sem = request.form.get("sem")
            course = request.form.get("course")
            entry = Students(Student_id=student_id, Name=name, Phone=phone, Email=email, Pass=passs, Sem=sem, Course=course)
            db.session.add(entry)
            db.session.commit()
            return redirect('/admin/' + admin.Admin_id + '/editstudent')
        return render_template("addstudent.html", admin=admin)


@app.route("/dashboard/student/<string:studid>", methods=['POST', 'GET'])
def studentdashboard(studid):
    student = Students.query.filter_by(Student_id=studid).first()
    if 'user' in session and session['user'] == params["student_session"]:
        if request.method == "POST":
            student.Name = request.form.get('studentname')
            student.Phone = request.form.get('studentphone')
            student.Email = request.form.get('studentemail')
            student.Pass = request.form.get('studentpass')
            db.session.commit()
            return redirect('/dashboard/student/' + student.Student_id)
        return render_template("studentdashboard.html", student=student)


@app.route("/dashboard/teacher/<string:teacherid>", methods=['POST', 'GET'])
def teacherdashboard(teacherid):
    teacher = Teachers.query.filter_by(Teacher_id=teacherid).first()
    if 'user' in session and session['user'] == params["teacher_session"]:
        if request.method == "POST":
            teacher.Name = request.form.get('teachername')
            teacher.Phone = request.form.get('teacherphone')
            teacher.Email = request.form.get('teacheremail')
            teacher.Pass = request.form.get('teacherpass')
            db.session.commit()
            return redirect('/dashboard/teacher/' + teacher.Teacher_id)
        return render_template("teacherdashboard.html", teacher=teacher)


app.run(debug=True)
