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
CURR_YEAR_SEM = ""
CURR_BRANCH = ""

@app.before_request
def load_user():
    g.CURR_USER = session.get("username")
    global CURR_BRANCH
    CURR_BRANCH = session.get("username")


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
        result = cursor.fetchall()
        if(len(result) > 0):
            user_log = User(result[0][1])
            login_user(user_log)
            session["username"] = username
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
        session["username"] = username
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
        return render_template("main_body.html", sems_table = sems_table)
    else:
        cursor.execute("SELECT id,year,sem FROM all_timetables")
        sems_table = cursor.fetchall()
        print(sems_table)
        return render_template("main_body.html", sems_table = sems_table)



@app.route("/create_timetable", methods=["GET", "POST"])
@login_required
def create_timetable():
    if request.method == "POST":
        year = request.form.get("year_session")
        sem = request.form.get("sem").lower()
        sem_year = sem + "_" + year
        global CURR_YEAR_SEM 
        CURR_YEAR_SEM = sem_year
        insert_query = "INSERT INTO all_timetables( year, sem, year_sem) VALUES ( %s, %s, %s)"
        create_query = f"""CREATE TABLE {sem_year}(
            id SERIAL,
            class VARCHAR(250) NOT NULL,
            subject VARCHAR(500) NOT NULL,
            slot VARCHAR(50) NOT NULL,
            day VARCHAR(250) NOT NULL,
            time VARCHAR(250) NOT NULL,
            faculty VARCHAR(250) NOT NULL,
            room VARCHAR(250) NOT NULL,
            batch VARCHAR(200) NOT NULL,
            type VARCHAR(100) NOT NULL,
            branch VARCHAR(250) NOT NULL,
            division VARCHAR(250) NOT NULL
        )"""
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

@app.route("/edit_or_show_timetable", methods = [ "GET", "POST"])
@login_required
def edorsho():
    if request.method == "POST":
        global CURR_YEAR_SEM
        val = request.form.get("action")
        year_sem_id = request.form.get("year_sem_id")
        query_edit = "SELECT year_sem FROM all_timetables WHERE id = %s"
        cursor.execute(query_edit , (year_sem_id,))
        year_sem = cursor.fetchall()[0][0]
        CURR_YEAR_SEM = year_sem
        if(val == "edit"):
            return redirect("/assign_slots")
        else:
            return redirect ("/show_timetable")
    else:
        return redirect("/")



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
    global CURR_BRANCH
    global CURR_YEAR_SEM
    if request.method == "POST":
        college_class = request.form.get("class")
        division = request.form.get("division")
        subject = request.form.get("subject")
        room = request.form.get("room")
        faculty = request.form.get("faculty")
        mult_faculty = request.form.get("multiple-faculty")
        batch = request.form.get("batch")
        slots = request.form.getlist("slots")
        type_submit = request.form.get("submit-button")
        if(len(mult_faculty) > 0):
            faculty = faculty.strip() + "/" + mult_faculty.strip()
            fac_list = []
            fac_index = 0
            for j in range(len(faculty)):
                if(faculty[j] == "/"):
                    fac_list.append(faculty[fac_index:j])
                    fac_index = j + 1
            fac_list.append(faculty[fac_index:])
            if(len(slots) > 1):
                for curr_fac in fac_list:
                    for slot in slots:
                        fac_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE slot = %s AND ((faculty  LIKE  %s) OR (faculty  LIKE  %s) OR (faculty  LIKE  %s))"
                        fac_para = (slots[0],f"%/{curr_fac}/%",f"%{curr_fac}/%",f"%/{curr_fac}%")
                        cursor.execute(fac_query,fac_para)
                        fac_res = cursor.fetchall()
                        if(len(fac_res >= 1)):
                            query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                            cursor.execute(query)
                            results = cursor.fetchall()
                            return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Faculty is already alloted for that slot!")
            else:
                for curr_fac in fac_list:
                    fac_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE slot = %s AND ((faculty  LIKE  %s) OR (faculty  LIKE  %s) OR (faculty  LIKE  %s))"
                    fac_para = (slots[0],f"%/{curr_fac}/%",f"%{curr_fac}/%",f"%/{curr_fac}%")
                    cursor.execute(fac_query,fac_para)
                    fac_res = cursor.fetchall()
                    if(len(fac_res) >= 1):
                        query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                        cursor.execute(query)
                        results = cursor.fetchall()
                        return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Faculty is already alloted for that slot!")
        else:
            if(len(slots) > 1):
                for slot in slots:
                    fac_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE slot = %s AND  faculty = %s"
                    fac_para = (slot,faculty)
                    cursor.execute(fac_query,fac_para)
                    fac_res = cursor.fetchall()
                    if(len(fac_res >= 1)):
                        query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                        cursor.execute(query)
                        results = cursor.fetchall()
                        return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Faculty is already alloted for that slot!")
            else:
                fac_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE slot = %s AND  faculty = %s"
                fac_para = (slots[0],faculty)
                cursor.execute(fac_query,fac_para)
                fac_res = cursor.fetchall()
                if(len(fac_res) >= 1):
                    query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                    cursor.execute(query)
                    results = cursor.fetchall()
                    return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Faculty is already alloted for that slot!")
        if(len(slots) > 1):
            for slot in slots:
                room_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE room = %s AND slot = %s"
                room_para = (room,slot)
                cursor.execute(room_query,room_para)
                room_res = cursor.fetchall()
                batch_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE slot = %s AND batch = %s AND division = %s AND class = %s"
                batch_para = (slot,batch,division,college_class)
                cursor.execute(batch_query, batch_para)
                batch_res = cursor.fetchall()
                if((len(batch_res) >= 1) or (len(room_res) >= 1)):
                    query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                    cursor.execute(query)
                    results = cursor.fetchall()
                    if(len(room_res) >= 1):
                        return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Room is already alloted for that slot!")
                    elif(len(batch_res) >= 1):
                        return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Batch of that Division is already alloted for that slot!")
                search_query = "SELECT day,time FROM time_slots WHERE slots_name = %s"
                cursor.execute(search_query, (slot,))
                time_slots = cursor.fetchall()[0]
                cursor.execute("SELECT subelective FROM subjects WHERE subabb = %s", (subject,))
                subelective = cursor.fetchall()
                if(subelective == "YES"):
                    type_sub = "E".strip() + type_submit.strip()
                else:
                    type_sub = type_submit
                insert_para = (college_class,subject,slot,time_slots[0],time_slots[1],faculty,room, batch, type_sub, CURR_BRANCH,division)
                insert_query = f"""INSERT INTO {CURR_YEAR_SEM}(class,subject,slot,day,time,faculty,room,batch,type,branch,division) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
            try:
                cursor.execute(insert_query,insert_para)
                conn.commit()
                return redirect("/assign_slots")
            except mysql.errors as error:
                query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                cursor.execute(query)
                results = cursor.fetchall()
                return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results, error = error)
        else:
            room_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE room = %s AND slot = %s"
            room_para = (room,slots[0])
            cursor.execute(room_query,room_para)
            room_res = cursor.fetchall()
            batch_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE slot = %s AND batch = %s AND division = %s AND class = %s"
            batch_para = (slots[0],batch,division,college_class)
            cursor.execute(batch_query, batch_para)
            batch_res = cursor.fetchall()
            if((len(batch_res) >= 1) or (len(room_res) >= 1)):
                query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                cursor.execute(query)
                results = cursor.fetchall()
                if(len(room_res) >= 1):
                    return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Room is already alloted for that slot!")
                elif(len(batch_res) >= 1):
                    return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Batch of that Division is already alloted for that slot!")
            search_query = "SELECT day,time FROM time_slots WHERE slots_name = %s"
            cursor.execute(search_query, (slots[0],))
            time_slots = cursor.fetchall()[0]
            cursor.execute("SELECT subelective FROM subjects WHERE subabb = %s", (subject,))
            subelective = cursor.fetchall()[0]
            if(subelective == "YES"):
                type_sub = "E".strip() + type_submit.strip()
            else:
                type_sub = type_submit
            insert_para = (college_class,subject,slots[0],time_slots[0],time_slots[1],faculty,room, batch, type_sub, CURR_BRANCH,division)
            insert_query = f"""INSERT INTO {CURR_YEAR_SEM}(class,subject,slot,day,time,faculty,room,batch,type,branch,division) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
            try:
                cursor.execute(insert_query,insert_para)
                conn.commit()
                return redirect("/assign_slots")
            except mysql.errors as error:
                query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                cursor.execute(query)
                results = cursor.fetchall()
                return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results, error = error)
    else:
        query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
        cursor.execute(query)
        results = cursor.fetchall()
        return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results)
    


@app.route("/show_timetable", methods=["GET","POST"])
@login_required
def show_timetable():
    if request.method == "POST":
        sel_class = request.form.get("sel_class")
        sel_room = request.form.get("sel_room")
        sel_fac = request.form.get("sel_fac")
        if(sel_class):
            course_year = sel_class[0:2]
            course_batch = sel_class[-1]
            course = sel_class[3:10]
            course_department = CURR_BRANCH
            div_para = (course_year, course,course_department,course_batch)
            div_query = "SELECT no_of_div FROM divisions WHERE year = %s AND course = %s AND department = %s AND batch = %s"
            cursor.execute(div_query, div_para)
            div_res = cursor.fetchall()
            no_of_div = div_res[0][0]
            time_slots = ["8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00","12:00-1:00", "1:00-2:00", "2:00-3:00", "3:00-4:00", "4:00-5:00", "5:00-6:00", "6:00-7:00"]
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            # Now we are working on the part of adding colspan for days
            day_colspan = {}
            total_columns = 0
            for day in days:
                day_query = f"SELECT batch FROM {CURR_YEAR_SEM} WHERE division = %s AND branch = %s AND day = %s AND batch != 'NO'"
                day_para = ( course_batch, course_department, day)
                cursor.execute( day_query, day_para)
                day_res = cursor.fetchall()
                if(len(day_res) > 0 ):
                    day_colspan[day] = no_of_div
                    total_columns = total_columns + no_of_div
                else:
                    day_colspan[day] = 1
                    total_columns = total_columns + 1
            
            # This code is for creating html table head with colspan
            table_head = "<thead><tr><th>Time/Day</th>"
            for day in days:
                if(day_colspan[day] > 1):
                    table_head = table_head + f"<th colspan={day_colspan[day]}>{day}<th>"
                else:
                    table_head = table_head + f"<th colspan={day_colspan[day]}>{day}<th>"
            table_head  = table_head + "</tr></thead>"

            # Now we are going to create the body of the table
            check_back_row = {}
            table_body = "<tbody>"
            for t in range(len(time_slots)):
                table_body = table_body + f"<tr><td>{time_slots[t]}</td>"
                if(time_slots[t] == "1:00-2:00"):
                    table_body = table_body + f"<td colspan={total_columns}>LUNCH BREAK</td>"
                    continue
                for day in days:
                    if(check_back_row[time_slots[t]] == day):
                        continue
                    curr_time_para = (day,time_slots[t],course_department, course_batch)
                    next_time_para = (day,time_slots[t + 1],course_department, course_batch)
                    time_query = f"SELECT class,subject,day,faculty,room,type,branch,batch,division FROM { CURR_YEAR_SEM } WHERE day = %s AND time = %s AND branch = %s AND division = %s"
                    cursor.execute(time_query, curr_time_para)
                    curr_time_res = cursor.fetchall()
                    cursor.execute(time_query, next_time_para )
                    next_time_res = cursor.fetchall()
                    curr_time_res = sorted(curr_time_res)
                    next_time_res = sorted(next_time_res)
                    rowspan_or_not = False
                    if(curr_time_res == next_time_res):
                        check_back_row[time_slots[t + 1]] = day
                        rowspan_or_not = True
                    data_query = f"SELECT subject,room,faculty,division,batch FROM { CURR_YEAR_SEM } WHERE day = %s AND time = %s AND branch = %s AND division = %s"
                    cursor.execute(data_query, curr_time_para)
                    data_res = cursor.fetchall()
                    if(len(data_res) == 0):
                        if(rowspan_or_not):
                            table_body = table_body + "<td rowspan=2></td>"
                        else:
                            table_body = table_body + "<td rowspan=1></td>"
                    if(len(data_res) > 1):
                        for curr_batch in data_res:
                            if(rowspan_or_not):
                                table_body = table_body + f"""<td rowspan=2 colspan=1>{ curr_batch[0] } 
                                {" "} { curr_batch[1] } {" "} { curr_batch[2] } {" "} { curr_batch[4] }</td>"""
                            else:
                                table_body = table_body + f"""<td rowspan=1 colspan=1>{ curr_batch[0] } 
                                {" "} { curr_batch[1] } {" "} { curr_batch[2] } {" "} { curr_batch[4] }</td>"""
                    else:
                        if(rowspan_or_not):
                            table_body = table_body + f"""<td rowspan=2 colspan={ no_of_div }>{ curr_batch[0] } {" "} { curr_batch[1] } {" "} { curr_batch[2] } {" "} { curr_batch[3] }</td>"""
                        else:
                            table_body = table_body + f"""<td rowspan=1 colspan={ no_of_div }>{ curr_batch[0] } {" "} { curr_batch[1] } {" "} { curr_batch[2] } {" "} { curr_batch[3] }</td>"""
                table_body = table_body + "</tr>"
            table_body = table_body + "</tbody>"
            space_hod = total_columns - 2
            table_foot = f"""<tfoot>
                <tr><td>H.O.D</td><td colspan={space_hod}></td><td>PRINCIPAL</td></tr>
            </tfoot>"""
            complete_table = table_head + table_body + table_foot
            return render_template("show_timetable.html", CURR_YEAR_SEM = CURR_YEAR_SEM, timetable = complete_table)
        elif(sel_room):
            print("In sel room")
        elif(sel_fac):
            print("In sel_fac")
        return render_template("show_timetable.html", CURR_YEAR_SEM = CURR_YEAR_SEM)
    else:
        return render_template("show_timetable.html", CURR_YEAR_SEM = CURR_YEAR_SEM)
    


