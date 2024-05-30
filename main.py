from flask import *
import mysql.connector as mysql
from flask_login import UserMixin,  login_user, logout_user, LoginManager, login_required, current_user
from datetime import timedelta
from user_helper import User
import os


#Creating instance of Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

#Flask_Login configurations to manage user login
login_manger = LoginManager()
login_manger.init_app(app)
login_manger.login_view = "login"


#LoginManager User loader
@login_manger.user_loader
def load_user(user_id):
    return User(user_id)


#Host and Other info to connect to MySQL server
#This is config to get direct access and you can change user and host and password and also database
config = {
    'host': "localhost",
    'user': "root",
    'password': "root",
    'database': "KJSCE_Timetable",
}

#This is for connecting MySQL connector to python
conn = mysql.connect(**config)
cursor = conn.cursor()


#This variable is created globally so that it can keep track of which timetable we are currently in
curr_year_sem = ""

#This is for users to log in
@app.route("/login", methods=["GET","POST"], endpoint = "login")
def login_page():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_info = (username,password)
        user_login = "SELECT user_id,username,user_password FROM users WHERE username = %s AND user_password = %s"
        cursor.execute(user_login,user_info)
        result = cursor.fetchall()[0][0]
        if(result):
            user_log = User(result)
            login_user(user_log)
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect("/")
        else:
            return redirect("/login")
    else:
        return render_template("login.html")

#This is for users to Register
@app.route("/register", methods = ["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email_id = request.form.get("email_id")
        college_name = request.form.get("college_name")
        #This is to insert User Info into Database
        user_reg = "INSERT INTO users(username,email_id,user_password,college_name) VALUES (%s,%s,%s,%s)"
        param = (username,email_id,password,college_name)
        cursor.execute(user_reg,param)
        #This is to fetch user id from the database to give user the access to website after logging IN
        user_id_reg = "SELECT user_id FROM users WHERE username = %s"
        cursor.execute(user_id_reg,(username,))
        cur_res = (cursor.fetchall())[0][0]
        user_res = User(cur_res)
        login_user(user_res)
        conn.commit()
        return redirect("/")
    else:
        return render_template("register.html")
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# This routing is for redirecting to login page when you are on Register page
@app.route("/login_redirect", methods = ["GET"])
def login_red():
    return redirect("/login")

#This routing is for redirecting to register page if you are on login page
@app.route("/register_redirect", methods = ["GET"])
def reg_red():
    return redirect("/register")


#This route is for redirecting to our main website page after logging in
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        return render_template("main_body.html")

    else:
        cursor.execute("SELECT year,sem FROM all_timetables")
        sems_table = cursor.fetchall()
        print(sems_table)
        return render_template("main_body.html",sems_table = sems_table)



@app.route("/create_timetable", methods=["GET", "POST"])
@login_required
def create_timetable():
    if request.method == "POST":
        year = request.form.get("year_session")
        sem = request.form.get("sem").lower()
        sem_year = sem + "_" + year
        global curr_year_sem 
        curr_year_sem = sem_year
        insert_query = "INSERT INTO all_timetables( year, sem, year_sem) VALUES ( %s, %s, %s)"
        create_query = f"""CREATE TABLE {sem_year}(
            id SERIAL,
            class VARCHAR(250) NOT NULL,
            subject VARCHAR(500) NOT NULL,
            slot VARCHAR(50) NOT NULL,
            day VARCHAR(250) NOT NULL,
            time VARCHAR(250) NOT NULL,
            faculty varchar(250) NOT NULL,
            room varchar(250) NOT NULL,
            batch varchar(200) NOT NULL,
            type varchar(100) NOT NULL,
            branch varchar(250) NOT NULL
        )"""
        print(sem,year,sem_year)
        print(create_query)
        try:
            cursor.execute(insert_query, ( year, sem.upper(), sem_year))
            cursor.execute(create_query)
            conn.commit()
            return redirect("/assign_slots")
        except mysql.Error as error:
            conn.rollback()
            print("MySQL Error: ", error)
            return render_template("main_body.html")
    else:
        return render_template("main_body.html")



@app.route("/add_subjects", methods=["GET", "POST"])
@login_required
def add_subject():
    if request.method == "POST":
        sub_class = request.form.get("class_sub")
        sub_sem = request.form.get("sem")
        sub_code = request.form.get("sub_code")
        sub_abb = request.form.get("sub_abb")
        sub_name = request.form.get("sub_name")
        subL = request.form.get("total_l")
        subT = request.form.get("total_t")
        subP = request.form.get("total_p")
        subEelective = request.form.get("elective")
        subInfo = (sub_class, sub_sem, sub_code, sub_abb, sub_name, subL, subT, subP, subEelective,)
        subQuery = "INSERT INTO subjects( subclass, subsem, subcode, subabb, subname, sublecture, subtut, subprac, subelective) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(subQuery, subInfo)
            return redirect("/add_subjects")
        except:
            cursor.execute("SELECT * FROM subjects")
            subjects = cursor.fetchall()
            return render_template("add_subjects.html", error = "Faculty Already Exists or Given Data is wrong!", subjects = subjects)
    else:
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
        return render_template("add_subjects.html",subjects = subjects)


@app.route("/add_faculty", methods=["GET", "POST"])
@login_required
def add_faculty():
    if request.method == "POST":
        facinit = request.form.get("faculty_initials")
        facname = request.form.get("faculty_name")
        facdes = request.form.get("faculty_designation")
        facqual = request.form.get("faculty_qualification")
        facshdep = request.form.get("shared_dep")
        facInfo = ( facinit, facname, facdes, facqual, facshdep)
        facQuery = "INSERT INTO faculty( facinit, facname, facdes, facqual, facshdep) VALUES(%s,%s,%s,%s,%s)"
        try:
            cursor.execute(facQuery, facInfo)
            conn.commit()
            return redirect("/add_faculty")
        except:
            cursor.execute("SELECT * FROM faculty")
            faculties = cursor.fetchall()
            return render_template("add_faculty.html", error = "Faculty Already Exists or Input Given was Invalid!" ,faculties = faculties)
    else:
        cursor.execute("SELECT * FROM faculty")
        faculties = cursor.fetchall()
        return render_template("add_faculty.html", faculties = faculties)
    


@app.route("/add_room", methods=["GET", "POST"])
@login_required
def add_room():
    if request.method == "POST":
        roomno = request.form.get("room_no")
        roomdesc = request.form.get("room_desc")
        roomshdp = request.form.get("shared_dep")
        roomInfo = ( roomno, roomdesc, roomshdp)
        roomQuery = "INSERT INTO rooms( roomno, roomdes, roomshdep) VALUES(%s,%s,%s)"
        try:
            cursor.execute( roomQuery, roomInfo)
            conn.commit()
            return redirect("/add_room")
        except mysql.errors as error:
            cursor.execute("SELECT * FROM rooms")
            rooms = cursor.fetchall()
            return render_template("add_room.html", error = error , rooms = rooms)
    else:
        cursor.execute("SELECT * FROM rooms")
        rooms = cursor.fetchall()
        return render_template("add_room.html", rooms = rooms)
    

@app.route("/add_div", methods=[ "GET", "POST"])
@login_required
def add_div():
    if request.method == "POST":
        year = request.form.get("year")
        course = request.form.get("course")
        department = request.form.get("department")
        batch = request.form.get("batch")
        divisions = request.form.get("no_div")
        div_para = (year, course, department, batch, divisions)
        div_insert = "INSERT INTO divisions( year, course, department, batch, no_of_div) VALUES( %s, %s, %s, %s, %s)"
        try:
            cursor.execute(div_insert, div_para)
            conn.commit()
            return redirect("/add_div")
        except mysql.errors as error:
            cursor.execute("SELECT * FROM divisions")
            div_table = cursor.fetchall()
            return render_template("add_div.html", error = error, div_table = div_table)
    else:
        cursor.execute("SELECT * FROM divisions")
        div_table = cursor.fetchall()
        print(div_table)
        return render_template("add_div.html", div_table = div_table)


    

@app.route("/assign_slots", methods=["GET","POST"])
@login_required
def assign_slots():
    if request.method == "POST":
        return render_template("assign.html")
    else:
        return render_template("assign.html")
    


@app.route("/show_timetable", methods=["GET","POST"])
@login_required
def show_timetable():
    if request.method == "POST":
        return render_template("show_timetable.html")
    else:
        return render_template("show_timetable.html")
    


