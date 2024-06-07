from flask import *
import mysql.connector as mysql
from flask_login import UserMixin,  login_user, logout_user, LoginManager, login_required, current_user
from datetime import timedelta
from user_helper import User
import openpyxl
import ast
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
        cursor.execute("SELECT id,year,sem FROM all_timetables ORDER BY year DESC")
        sems_table = cursor.fetchall()
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
        try:
            cursor.execute(insert_query, ( year, sem.upper(), sem_year))
            cursor.execute(create_query)
            conn.commit()
            return redirect("/assign_slots")
        except:
            conn.rollback()
            error = "TimeTable Already Exists!"
            return render_template("main_body.html",error = error)
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
            conn.commit()
            return redirect("/add_subjects")
        except:
            cursor.execute("SELECT DISTINCT(class) FROM divisions WHERE department = %s", (CURR_BRANCH,))
            class_sub = cursor.fetchall()
            cursor.execute("SELECT * FROM subjects")
            subjects = cursor.fetchall()
            return render_template("add_subjects.html", class_sub = class_sub,error = "Subjects Already Exists or Given Data is wrong!", subjects = subjects)
    else:
        cursor.execute("SELECT DISTINCT(class) FROM divisions WHERE department = %s", (CURR_BRANCH,))
        class_sub = cursor.fetchall()
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
        return render_template("add_subjects.html",class_sub = class_sub,subjects = subjects)


@app.route("/add_faculty", methods=["GET", "POST"])
@login_required
def add_faculty():
    if request.method == "POST":
        facinit = request.form.get("faculty_initials")
        facname = request.form.get("faculty_name")
        facdes = request.form.get("faculty_designation")
        facqual = request.form.get("faculty_qualification")
        facshdep = request.form.get("shared_dep")
        facdep = CURR_BRANCH
        facInfo = ( facinit, facname, facdes, facqual, facdep,facshdep)
        facQuery = "INSERT INTO faculty( facinit, facname, facdes, facqual, facdep,facshdep) VALUES(%s,%s,%s,%s,%s,%s)"
        try:
            cursor.execute(facQuery, facInfo)
            conn.commit()
            return redirect("/add_faculty")
        except:
            fac_query = f"SELECT * FROM faculty WHERE facdep = '{CURR_BRANCH}' OR facshdep = '{CURR_BRANCH}'"
            cursor.execute(fac_query)
            faculties = cursor.fetchall()
            return render_template("add_faculty.html", error = "Faculty Already Exists or Input Given was Invalid!" ,faculties = faculties)
    else:
        fac_query = f"SELECT * FROM faculty WHERE facdep = '{CURR_BRANCH}' OR facshdep = '{CURR_BRANCH}'"
        cursor.execute(fac_query)
        faculties = cursor.fetchall()
        return render_template("add_faculty.html", faculties = faculties)
    


@app.route("/add_room", methods=["GET", "POST"])
@login_required
def add_room():
    if request.method == "POST":
        roomno = request.form.get("room_no")
        roomdesc = request.form.get("room_desc")
        roomshdp = request.form.get("shared_dep")
        roomdep = CURR_BRANCH
        roomInfo = ( roomno, roomdesc, roomdep, roomshdp)
        roomQuery = "INSERT INTO rooms( roomno, roomdes, roomdep, roomshdep) VALUES(%s,%s,%s,%s)"
        try:
            cursor.execute( roomQuery, roomInfo)
            conn.commit()
            return redirect("/add_room")
        except:
            room_query = f"SELECT * FROM rooms WHERE roomdep = '{CURR_BRANCH}' OR roomshdep = '{CURR_BRANCH}'"
            cursor.execute(room_query)
            rooms = cursor.fetchall()
            return render_template("add_room.html", error = "Room Already Exists! Or Incorrect Data!" , rooms = rooms)
    else:
        room_query = f"SELECT * FROM rooms WHERE roomdep = '{CURR_BRANCH}' OR roomshdep = '{CURR_BRANCH}'"
        cursor.execute(room_query)
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
        class_coll = year + " " + course+ " " + department
        div_para = (year, course, department, batch, divisions,class_coll)
        div_insert = "INSERT INTO divisions( year, course, department, batch, no_of_div,class) VALUES( %s, %s, %s, %s, %s,%s)"
        try:
            cursor.execute(div_insert, div_para)
            conn.commit()
            return redirect("/add_div")
        except:
            cursor.execute("SELECT * FROM divisions")
            div_table = cursor.fetchall()
            return render_template("add_div.html", error = "Batch with No. of Divisions is already added!", div_table = div_table)
    else:
        cursor.execute("SELECT * FROM divisions")
        div_table = cursor.fetchall()
        return render_template("add_div.html", div_table = div_table)





@app.route("/import_file", methods=["GET"])
@login_required
def import_check():
    im_query = "SELECT DISTINCT(class) FROM divisions"
    im_timetable_query = "SELECT year_sem FROM all_timetables"
    cursor.execute(im_query)
    im_res = cursor.fetchall()
    cursor.execute(im_timetable_query)
    im_time_res = cursor.fetchall()
    return render_template("import_excel.html",class_batch = im_res, year_sem = im_time_res)



@app.route("/import_excel", methods=[ "GET", "POST"])
def import_excel():
    if request.method == "POST":
        imp_class = request.form.get("import_class")
        imp_batch = request.form.get("import_batch")
        imp_year_sem = request.form.get("import_year_sem")
        if "import_file" not in request.files:
            return (jsonify({"message": "No file part"}), 400)
        import_file = request.files["import_file"]
        if(import_file.filename == ""):
            return(jsonify({"message": "No Selected File"}), 400)
        wb = openpyxl.load_workbook(import_file)
        ws = wb.active
        days_col = "ABCDEF"
        for row in range(1,ws.max_row):
            if(row == 1):
                continue
            for col in range(len(days_col)):
                if(days_col[col] == "A"):
                    continue
                curr_cell = days_col[col] + str(row)
                if(ws[curr_cell].value is None):
                    continue
                curr_cell_val = ast.literal_eval(ws[curr_cell].value)
                curr_cell_value = curr_cell_val
                if(type(curr_cell_val[0]) == str):
                    imp_sub = curr_cell_val[0]
                    imp_sub_type = curr_cell_val[1]
                    imp_room = curr_cell_val[2]
                    imp_fac = curr_cell_val[3]
                    imp_div = curr_cell_val[4]
                    imp_slot = days_col[col-1] + str(row - 1)
                    imp_day = ws[days_col[col]+"1"].value
                    imp_time = ws["A"+ str(row)].value
                    if(len(imp_div) > 0):
                        imp_batch_col = imp_div
                        imp_div = imp_div[0]
                    else:
                        imp_batch_col = "NO"
                    check_div_query = f"SELECT * FROM { imp_year_sem }  WHERE class = %s AND slot = %s AND batch = %s AND division = %s AND branch = %s"
                    check_all_query = f"SELECT * FROM { imp_year_sem } WHERE class = %s AND subject = %s AND slot = %s AND faculty = %s AND room = %s AND batch = %s AND branch = %s AND division = %s"
                    check_fac_query = f"SELECT * FROM { imp_year_sem } WHERE slot = %s AND ( (faculty LIKE %s) OR (faculty LIKE %s) OR (faculty LIKE %s) OR (faculty LIKE %s))"
                    check_room_query = f"SELECT * FROM { imp_year_sem } WHERE slot = %s AND room = %s"
                    check_div_para = ( imp_class, imp_slot,imp_batch_col, imp_div, CURR_BRANCH)
                    check_all_para = ( imp_class, imp_sub, imp_slot, imp_fac, imp_room, imp_batch_col, CURR_BRANCH, imp_div)
                    check_fac_para = ( imp_slot, f"{imp_fac}", f"%/{imp_fac}",f"{imp_fac}/%",f"%/{imp_fac}/%")
                    check_room_para = ( imp_slot, imp_room)
                    cursor.execute(check_div_query,check_div_para)
                    check_div_res = cursor.fetchall()
                    cursor.execute(check_all_query,check_all_para)
                    check_all_res = cursor.fetchall()
                    cursor.execute(check_fac_query,check_fac_para)
                    check_fac_res = cursor.fetchall()
                    cursor.execute(check_room_query,check_room_para)
                    check_room_res = cursor.fetchall()
                    if((len(check_div_res) > 0) or (len(check_all_res) > 0) or (len(check_fac_res) > 0) or (len(check_room_res) > 0)):
                        continue
                        # return(jsonify({"message": "Data is Already given for a batch"}), 400)
                    imp_insert_query = f"INSERT INTO {imp_year_sem}(class,subject,type,slot,day,time,faculty,room,batch,branch,division) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
                    imp_insert_para = ( imp_class, imp_sub, imp_sub_type, imp_slot, imp_day, imp_time, imp_fac, imp_room, imp_batch_col, CURR_BRANCH, imp_div)
                    try:
                        cursor.execute( imp_insert_query, imp_insert_para)
                        conn.commit()
                    except:
                        error = "Cannot Insert Data"
                        return (jsonify({"message": error}), 200)
                elif(type(curr_cell_val[0]) == tuple):
                    cur_cell_va = curr_cell_value
                    for curr_cell_val in cur_cell_va:
                        imp_sub = curr_cell_val[0]
                        imp_sub_type = curr_cell_val[1]
                        imp_room = curr_cell_val[2]
                        imp_fac = curr_cell_val[3]
                        imp_div = curr_cell_val[4]
                        imp_slot = days_col[col-1] + str(row - 1)
                        imp_day = ws[days_col[col]+"1"].value
                        imp_time = ws["A"+ str(row)].value
                        if(len(imp_div) > 0):
                            imp_batch_col = imp_div
                            imp_div = imp_div[0]
                        else:
                            imp_batch_col = "NO"
                        check_div_query = f"SELECT * FROM { imp_year_sem }  WHERE class = %s AND slot = %s AND batch = %s AND division = %s AND branch = %s"
                        check_all_query = f"SELECT * FROM { imp_year_sem } WHERE class = %s AND subject = %s AND slot = %s AND faculty = %s AND room = %s AND batch = %s AND branch = %s AND division = %s"
                        check_fac_query = f"SELECT * FROM { imp_year_sem } WHERE slot = %s AND ( (faculty LIKE %s) OR (faculty LIKE %s) OR (faculty LIKE %s) OR (faculty LIKE %s))"
                        check_room_query = f"SELECT * FROM { imp_year_sem } WHERE slot = %s AND room = %s"
                        check_div_para = ( imp_class, imp_slot,imp_batch_col, imp_div, CURR_BRANCH)
                        check_all_para = ( imp_class, imp_sub, imp_slot, imp_fac, imp_room, imp_batch_col, CURR_BRANCH,imp_div)
                        check_fac_para = ( imp_slot, f"{imp_fac}", f"%/{imp_fac}",f"{imp_fac}/%",f"%/{imp_fac}/%")
                        check_room_para = ( imp_slot, imp_room)
                        cursor.execute(check_div_query,check_div_para)
                        check_div_res = cursor.fetchall()
                        cursor.execute(check_all_query,check_all_para)
                        check_all_res = cursor.fetchall()
                        cursor.execute(check_fac_query,check_fac_para)
                        check_fac_res = cursor.fetchall()
                        cursor.execute(check_room_query,check_room_para)
                        check_room_res = cursor.fetchall()
                        if((len(check_div_res) > 0) or (len(check_all_res) > 0) or (len(check_fac_res) > 0) or (len(check_room_res) > 0)):
                            # return(jsonify({"message": "Data is Already given for a batch"}), 400)
                            continue
                        imp_insert_query = f"INSERT INTO {imp_year_sem}(class,subject,type,slot,day,time,faculty,room,batch,branch,division) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
                        imp_insert_para = ( imp_class, imp_sub, imp_sub_type, imp_slot, imp_day, imp_time, imp_fac, imp_room, imp_batch_col, CURR_BRANCH, imp_div)
                        try:
                            cursor.execute( imp_insert_query, imp_insert_para)
                            conn.commit()
                        except:
                            error = "Cannot Insert Data"
                            return (jsonify({"message": error}), 200)
                else:
                    return(jsonify({"message": "Excel Data in wrong type"}), 400)  
        return(jsonify({"message": "Successfully Uploaded Data"}), 200)
    else:
        return redirect("/")






@app.route("/get_div", methods = [ "GET", "POST"])
def get_div():
    if request.method == "POST":
        sel_class = request.get_json()
        sel_class = sel_class["sel_class"]
        sub_query = f"SELECT subabb FROM subjects WHERE subclass = %s AND subsem = %s"
        div_query = f"SELECT batch,no_of_div FROM divisions WHERE class = %s"
        room_query = f"SELECT roomno FROM rooms WHERE roomdep = %s OR roomshdep = %s"
        faculty_query = f"SELECT facinit FROM faculty WHERE facdep = %s OR facshdep = %s"
        if(CURR_YEAR_SEM[0] == "O"):
            subsem = "ODD"
        else:
            subsem = "EVEN"
        sub_para = (sel_class, subsem)
        div_para = (sel_class,)
        room_fac_para = (CURR_BRANCH,CURR_BRANCH)
        cursor.execute(sub_query,sub_para)
        sub_res = cursor.fetchall()
        cursor.execute(div_query,div_para)
        div_res = cursor.fetchall()
        cursor.execute(room_query,room_fac_para)
        room_res = cursor.fetchall()
        cursor.execute(faculty_query,room_fac_para)
        faculty_res = cursor.fetchall()

        # This is to send back the data
        send_results = {
            "subjects" : sub_res,
            "divisions" : div_res,
            "rooms" : room_res,
            "faculty" : faculty_res
        }
        return jsonify(send_results)



    

@app.route("/assign_slots", methods=["GET","POST"])
@login_required
def assign_slots():
    global CURR_BRANCH
    global CURR_YEAR_SEM
    errorin = ""
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
        check_query = f"SELECT * FROM { CURR_YEAR_SEM }  WHERE class = %s AND slot = %s AND batch = %s AND division = %s AND branch = %s"
        if(len(slots) > 1):
            for slot in slots:
                check_para = (college_class,slot,batch,division, CURR_BRANCH)
                cursor.execute( check_query, check_para)
                check_res = cursor.fetchall()
                if(len(check_res) > 0):
                    errorin = "Batch or Division has already been assigned slots"
                    return redirect("/assign_slots")
        else:
            check_para = (college_class,slots,batch,division, CURR_BRANCH)
            cursor.execute( check_query, check_para)
            check_res = cursor.fetchall()
            if(len(check_res) > 0):
                errorin = "Batch or Division has already been assigned slots"
                return redirect("/assign_slots")
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
                        search_query = "SELECT day,time FROM time_slots WHERE slots_name = %s"
                        cursor.execute(search_query, (slot,))
                        time_slots = cursor.fetchall()[0]
                        cursor.execute("SELECT subelective FROM subjects WHERE subabb = %s", (subject,))
                        subelective = cursor.fetchall()
                        if(subelective == "YES"):
                            type_sub = "E".strip() + type_submit.strip()
                        else:
                            type_sub = type_submit
                        insert_para = (college_class,subject,slot,time_slots[0],time_slots[1],curr_fac,room, batch, type_sub, CURR_BRANCH,division)
                        insert_query = f"""INSERT INTO {CURR_YEAR_SEM}(class,subject,slot,day,time,faculty,room,batch,type,branch,division) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
                        try:
                            cursor.execute(insert_query,insert_para)
                            conn.commit()
                        except:
                            errorin = "Some problem Arised please check the fields again while submitting!"
                            return redirect("/assign_slots")
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
                    search_query = "SELECT day,time FROM time_slots WHERE slots_name = %s"
                    cursor.execute(search_query, (slots,))
                    time_slots = cursor.fetchall()[0]
                    cursor.execute("SELECT subelective FROM subjects WHERE subabb = %s", (subject,))
                    subelective = cursor.fetchall()
                    if(subelective == "YES"):
                        type_sub = "E".strip() + type_submit.strip()
                    else:
                        type_sub = type_submit
                    insert_para = (college_class,subject,slots,time_slots[0],time_slots[1],curr_fac,room, batch, type_sub, CURR_BRANCH,division)
                    insert_query = f"""INSERT INTO {CURR_YEAR_SEM}(class,subject,slot,day,time,faculty,room,batch,type,branch,division) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
                    try:
                        cursor.execute(insert_query,insert_para)
                        conn.commit()
                    except:
                        errorin = "Some problem Arised please check the fields again while submitting!"
                        return redirect("/assign_slots")
        else:
            if(len(slots) > 1):
                for slot in slots:
                    fac_query = f"SELECT * FROM {CURR_YEAR_SEM} WHERE slot = %s AND  faculty = %s"
                    fac_para = (slot,faculty)
                    cursor.execute(fac_query,fac_para)
                    fac_res = cursor.fetchall()
                    if(len(fac_res) >= 1):
                        query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
                        cursor.execute(query)
                        results = cursor.fetchall()
                        return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,error = "Faculty is already alloted for that slot!")
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
                    except:
                        errorin = "Some problem Arised please check the fields again while submitting!"
                        return redirect("/assign_slots")
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
                search_query = "SELECT day,time FROM time_slots WHERE slots_name = %s"
                cursor.execute(search_query, (slots[0],))
                time_slots = cursor.fetchall()[0]
                cursor.execute("SELECT subelective FROM subjects WHERE subabb = %s", (subject,))
                subelective = cursor.fetchall()
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
                except:
                    errorin = "Some problem Arised please check the fields again while submitting!"
                    return redirect("/assign_slots")
            return redirect("/assign_slots")
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
                except:
                    errorin = "Some problem Arised please check the fields again while submitting!"
                    return redirect("/assign_slots")
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
            except:
                errorin = "Some Problem has arised please check input fields  or data again!"
                return redirect("/assign.html")
    else:
        input_class_query = "SELECT DISTINCT(class) FROM divisions WHERE department = %s"
        input_class_para = ( CURR_BRANCH, )
        slots_para = "SELECT slots_name,slot_time_day FROM time_slots"
        cursor.execute(slots_para)
        slots_res = cursor.fetchall()
        cursor.execute(input_class_query, input_class_para)
        input_class_res = cursor.fetchall()
        query = f"SELECT id,class,subject,slot,day,time,faculty,room,division,batch,type FROM { CURR_YEAR_SEM }"
        cursor.execute(query)
        results = cursor.fetchall()
        return render_template("assign.html", CURR_YEAR_SEM = CURR_YEAR_SEM, results = results,slots_res = slots_res, input_class_res = input_class_res,error = errorin)
    


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
                    table_head = table_head + f"<th colspan={day_colspan[day]}>{day}</th>"
                else:
                    table_head = table_head + f"<th colspan={day_colspan[day]}>{day}</th>"
            table_head  = table_head + "</tr></thead>"
            # Now we are going to create the body of the table
            check_back_row = {}
            table_body = "<tbody>"
            for t in range(len(time_slots)):
                table_body = table_body + f"<tr><td>{time_slots[t]}</td>"
                if(time_slots[t] == "1:00-2:00"):
                    table_body = table_body + f'<td colspan={total_columns} style="text-align: center;">LUNCH BREAK</td>'
                    continue
                for day in days:
                    if(time_slots[t] in check_back_row.keys()):
                        if(day in check_back_row[time_slots[t]]):
                            continue
                    time_query = f"SELECT class,subject,day,faculty,room,type,branch,batch,division FROM { CURR_YEAR_SEM } WHERE day = %s AND time = %s AND branch = %s AND division = %s"
                    curr_time_para = (day,time_slots[t],course_department, course_batch)
                    cursor.execute(time_query, curr_time_para)
                    curr_time_res = cursor.fetchall()
                    curr_time_res = sorted(curr_time_res)
                    if((t+1) != len(time_slots)):
                        next_time_para = (day,time_slots[t + 1],course_department, course_batch)
                        cursor.execute(time_query, next_time_para )
                        next_time_res = cursor.fetchall()
                        next_time_res = sorted(next_time_res)
                    rowspan_or_not = False
                    if(next_time_res):
                        if(curr_time_res == next_time_res):
                            if(time_slots[t+1] in check_back_row.keys()):
                                add_day =  check_back_row[time_slots[t + 1]]
                                add_day.append(day)
                                check_back_row[time_slots[t + 1]] = add_day
                                rowspan_or_not = True
                            else:
                                check_back_row[time_slots[t + 1]] = [day]
                                rowspan_or_not = True
                    data_query = f"SELECT subject,room,faculty,division,batch FROM { CURR_YEAR_SEM } WHERE day = %s AND time = %s AND branch = %s AND division = %s"
                    cursor.execute(data_query, curr_time_para)
                    data_res = cursor.fetchall()
                    if(len(data_res) == 0):
                        table_body = table_body + f"<td colspan = {day_colspan[day]}></td>"
                        continue
                    if(len(data_res) > 1):
                        for curr_batch in data_res:
                            if(rowspan_or_not):
                                td = f'<td rowspan=2 colspan=1>{ curr_batch[0] } {" "} { curr_batch[1] } {" "} { curr_batch[2] } {" "} { curr_batch[4] }</td>'
                                table_body = table_body + td
                            else:
                                td = f'<td rowspan=1 colspan=1>{ curr_batch[0] } {" "} { curr_batch[1] } {" "} { curr_batch[2] } {" "} { curr_batch[4] }</td>'
                                table_body = table_body + td
                    else:
                        curr_batch = data_res[0]
                        if(rowspan_or_not):
                            td = f'<td rowspan=2 colspan={ no_of_div }>{ curr_batch[0] } {" "} { curr_batch[1] } {" "} { curr_batch[2] } {" "} { curr_batch[3] }</td>'
                            table_body = table_body + td
                        else:
                            td = f'<td rowspan=1 colspan={ no_of_div }>{ curr_batch[0] } {" "} { curr_batch[1] } {" "} { curr_batch[2] } {" "} { curr_batch[3] }</td>'
                            table_body = table_body + td
                    next_time_res = False
                table_body = table_body + "</tr>"
            table_body = table_body + "</tbody>"
            space_hod = total_columns - 1
            table_foot = f"""<tfoot>
                <tr><td>H.O.D</td><td colspan={space_hod}></td><td>PRINCIPAL</td></tr>
            </tfoot>"""
            complete_table = table_head + table_body + table_foot
            return render_template("show_timetable.html", CURR_YEAR_SEM = CURR_YEAR_SEM, timetable = complete_table)
        elif(sel_room):
            time_slots = ["8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00","12:00-1:00", "1:00-2:00", "2:00-3:00", "3:00-4:00", "4:00-5:00", "5:00-6:00", "6:00-7:00"]
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            table_head = "<thead><tr><th>Time/Day</th>"
            for day in days:
                table_head = table_head + f"<th>{day}</th>"
            table_head = table_head + "</tr></thead>"
            check_back_row = {}
            table_body = "<tbody>"
            for t in range(len(time_slots)):
                table_body = table_body + f"<tr><td>{time_slots[t]}</td>"
                if(time_slots[t] == "1:00-2:00"):
                    table_body = table_body + f'<td colspan=5 style="text-align: center;">LUNCH BREAK</td>'
                    continue
                for day in days:
                    if(time_slots[t] in check_back_row.keys()):
                        if(day in check_back_row[time_slots[t]]):
                            continue
                    time_query = f"SELECT class,subject,faculty,division,batch FROM {CURR_YEAR_SEM} WHERE room = %s AND branch = %s AND day = %s AND time = %s"
                    curr_time_para = ( sel_room, CURR_BRANCH, day, time_slots[t])
                    cursor.execute(time_query, curr_time_para)
                    curr_time_res = cursor.fetchall()
                    curr_time_res = sorted(curr_time_res)
                    if((t+1) != len(time_slots)):
                        next_time_para = ( sel_room, CURR_BRANCH, day, time_slots[t+1])
                        cursor.execute(time_query, next_time_para)
                        next_time_res = cursor.fetchall()
                        next_time_res = sorted(next_time_res)
                    rowspan_or_not = False
                    if(next_time_res):
                        if(curr_time_res == next_time_res):
                            if(time_slots[t+1] in check_back_row.keys()):
                                add_day =  check_back_row[time_slots[t + 1]]
                                add_day.append(day)
                                check_back_row[time_slots[t + 1]] = add_day
                                rowspan_or_not = True
                            else:
                                check_back_row[time_slots[t + 1]] = [day]
                                rowspan_or_not = True  
                    if(len(curr_time_res) == 0):
                        table_body = table_body + f"<td></td>"
                        continue
                    curr_batch = curr_time_res[0]
                    if(rowspan_or_not):
                        if(curr_batch[-1] == "NO"):
                            td = f'<td rowspan=2>{ curr_batch[0] } {" "} { curr_batch[-2] } {" "} { curr_batch[1] } {" "} { curr_batch[2] }</td>'
                            table_body = table_body + td
                        else:
                            td = f'<td rowspan=2>{ curr_batch[0] } {" "} { curr_batch[-1] } {" "} { curr_batch[1] } {" "} { curr_batch[2] }</td>'
                            table_body = table_body + td
                    else:
                        if(curr_batch[-1] == "NO"):
                            td = f'<td rowspan=1>{ curr_batch[0] } {" "} { curr_batch[-2] } {" "} { curr_batch[1] } {" "} { curr_batch[2] }</td>'
                            table_body = table_body + td
                        else:
                            td = f'<td rowspan=1>{ curr_batch[0] } {" "} { curr_batch[-1] } {" "} { curr_batch[1] } {" "} { curr_batch[2] }</td>'
                            table_body = table_body + td
                    next_time_res = False
                table_body = table_body + "</tr>"
            table_body = table_body + "</tbody>"
            complete_table = table_head + table_body
            return render_template("show_timetable.html", CURR_YEAR_SEM = CURR_YEAR_SEM, timetable = complete_table)
        elif(sel_fac):
            time_slots = ["8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00","12:00-1:00", "1:00-2:00", "2:00-3:00", "3:00-4:00", "4:00-5:00", "5:00-6:00", "6:00-7:00"]
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            table_head = "<thead><tr><th>Time/Day</th>"
            for day in days:
                table_head = table_head + f"<th>{day}</th>"
            table_head = table_head + "</tr></thead>"
            check_back_row = {}
            table_body = "<tbody>"
            for t in range(len(time_slots)):
                table_body = table_body + f"<tr><td>{time_slots[t]}</td>"
                if(time_slots[t] == "1:00-2:00"):
                    table_body = table_body + f'<td colspan=5 style="text-align: center;">LUNCH BREAK</td>'
                    continue
                for day in days:
                    if(time_slots[t] in check_back_row.keys()):
                        if(day in check_back_row[time_slots[t]]):
                            continue
                    time_query = f"SELECT class,subject,room,division,batch FROM  { CURR_YEAR_SEM } WHERE faculty = %s AND day = %s AND time = %s AND branch = %s"
                    curr_time_para = ( sel_fac, day, time_slots[t], CURR_BRANCH)
                    cursor.execute(time_query,curr_time_para)
                    curr_time_res = cursor.fetchall()
                    curr_time_res = sorted(curr_time_res)
                    if((t+1) != len(time_slots)):
                        next_time_para = ( sel_fac, day, time_slots[t+1], CURR_BRANCH)
                        cursor.execute(time_query, next_time_para)
                        next_time_res = cursor.fetchall()
                        next_time_res = sorted(next_time_res)
                    rowspan_or_not = False
                    if(next_time_res):
                        if(curr_time_res == next_time_res):
                            if(time_slots[t+1] in check_back_row.keys()):
                                add_day =  check_back_row[time_slots[t + 1]]
                                add_day.append(day)
                                check_back_row[time_slots[t + 1]] = add_day
                                rowspan_or_not = True
                            else:
                                check_back_row[time_slots[t + 1]] = [day]
                                rowspan_or_not = True
                    if(len(curr_time_res) == 0):
                        table_body = table_body + f"<td></td>"
                        continue
                    curr_batch = curr_time_res[0]
                    if(rowspan_or_not):
                        if(curr_batch[-1] == "NO"):
                            td = f'<td rowspan=2>{ curr_batch[0] } {" "} { curr_batch[-2] } {" "} { curr_batch[1] } {" "} { curr_batch[2] }</td>'
                            table_body = table_body + td
                        else:
                            td = f'<td rowspan=2>{ curr_batch[0] } {" "} { curr_batch[-1] } {" "} { curr_batch[1] } {" "} { curr_batch[2] }</td>'
                            table_body = table_body + td
                    else:
                        if(curr_batch[-1] == "NO"):
                            td = f'<td rowspan=1>{ curr_batch[0] } {" "} { curr_batch[-2] } {" "} { curr_batch[1] } {" "} { curr_batch[2] }</td>'
                            table_body = table_body + td
                        else:
                            td = f'<td rowspan=1>{ curr_batch[0] } {" "} { curr_batch[-1] } {" "} { curr_batch[1] } {" "} { curr_batch[2] }</td>'
                            table_body = table_body + td
                    next_time_res = False
                table_body = table_body + "</tr>"
            table_body = table_body + "</tbody>"
            complete_table = table_head + table_body
            return render_template("show_timetable.html", CURR_YEAR_SEM = CURR_YEAR_SEM, timetable = complete_table)
        return render_template("show_timetable.html", CURR_YEAR_SEM = CURR_YEAR_SEM)
    else:
        class_query = "SELECT DISTINCT(class),batch FROM divisions WHERE department = %s"
        room_query = "SELECT roomno FROM rooms WHERE roomdep = %s OR roomshdep = %s"
        fac_query = "SELECT facinit FROM faculty WHERE facdep = %s OR facshdep = %s"
        class_para = (CURR_BRANCH,)
        room_fac_para = (CURR_BRANCH,CURR_BRANCH)
        cursor.execute(class_query, class_para)
        class_res = cursor.fetchall()
        cursor.execute(room_query, room_fac_para)
        room_res = cursor.fetchall()
        cursor.execute(fac_query, room_fac_para)
        fac_res = cursor.fetchall()
        return render_template("show_timetable.html", CURR_YEAR_SEM = CURR_YEAR_SEM, class_res = class_res, room_res = room_res, fac_res = fac_res)
    


