import mysql.connector as mysql

config = {
    'host': "localhost",
    'user': "root",
    'password': "root",
    'database': "KJSCE_Timetable",
}

#This is for connecting MySQL connector to python
conn = mysql.connect(**config)
cursor = conn.cursor()

def check_data(imp_year_sem,div_para = None,all_para = None,fac_para = None,room_para = None):
    check_div_query = f"SELECT * FROM { imp_year_sem }  WHERE class = %s AND slot = %s AND batch = %s AND division = %s AND branch = %s"
    check_all_query = f"SELECT * FROM { imp_year_sem } WHERE class = %s AND subject = %s AND slot = %s AND faculty = %s AND room = %s AND batch = %s AND branch = %s AND division = %s"
    check_fac_query = f"SELECT * FROM { imp_year_sem } WHERE slot = %s AND ( (faculty LIKE %s) OR (faculty LIKE %s) OR (faculty LIKE %s) OR (faculty LIKE %s))"
    check_room_query = f"SELECT * FROM { imp_year_sem } WHERE slot = %s AND room = %s"
    if((not div_para) and (not all_para) and (not fac_para) and (room_para)):
        cursor.execute(check_room_query, room_para)
        room_res = cursor.fetchall()
        if(len(room_res) >= 1):
            return "Room is already allotted for that slot!"
        else:
            return False
    if((not div_para) and (not all_para) and (fac_para) and (not room_para)):
        cursor.execute(check_fac_query, fac_para)
        fac_res = cursor.fetchall()
        if(len(fac_res) >= 1):
            return "Faculty is already allotted for that slot!"
        else:
            return False
    if((not div_para) and ( all_para) and (not fac_para) and (not room_para)):
        cursor.fetchall(check_all_query, all_para)
        all_res = cursor.fetchall()
        if(len(all_res) >= 1):
            return "Slot for the id has already been allotted"
        else:
            return False
    if(( div_para) and (not all_para) and (not fac_para) and (not room_para)):
        cursor.fetchall(check_div_query, div_para)
        div_res = cursor.fetchall()
        if(len(div_res) >= 1):
            return "Division with batch is already allotted"
        else:
            return False
    if(( div_para) and ( all_para) and ( fac_para) and ( room_para)):
        cursor.execute(check_div_query,div_para)
        check_div_res = cursor.fetchall()
        cursor.execute(check_all_query,all_para)
        check_all_res = cursor.fetchall()
        cursor.execute(check_fac_query,fac_para)
        check_fac_res = cursor.fetchall()
        cursor.execute(check_room_query,room_para)
        check_room_res = cursor.fetchall()
        if((len(check_div_res) > 0) or (len(check_all_res) > 0) or (len(check_fac_res) > 0) or (len(check_room_res) > 0)):
            return "Some slot is already allotted please check again"
        else:
            return False