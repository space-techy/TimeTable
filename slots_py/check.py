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



# course_year = "FY"
# course = "B. Tech"
# course_department = "COMP"
# course_batch = "B"


# div_para = (course_year, course,course_department,course_batch)
# div_query = "SELECT no_of_div FROM divisions WHERE year = %s AND course = %s AND department = %s AND batch = %s"
# cursor.execute(div_query, div_para)
# div_res = cursor.fetchall()
# print(div_res[0][0])

# slots = ["B4"]
# search_query = "SELECT day,time FROM time_slots WHERE slots_name = %s"
# cursor.execute(search_query, (slots[0],))
# time_slots = cursor.fetchall()[0]
# print(time_slots)

# This is for checking tuples in list are equal or not!
# l1 = [("FY B. Tech COMP","English","Tuesday","HNN","B203","L","COMP","B1","B"),("FY B. Tech COMP","English","Tuesday","HNN","B203","L","COMP","B3","B"),("FY B. Tech COMP","English","Tuesday","HNN","B203","L","COMP","B2","B")]
# l1 = sorted(l1)
# l2 = [("FY B. Tech COMP","English","Tuesday","HNN","B203","L","COMP","B1","B"),("FY B. Tech COMP","English","Tuesday","HNN","B203","L","COMP","B2","B"),("FY B. Tech COMP","English","Tuesday","HNN","B203","L","COMP","B3","B")]
# # print(l1)
# if(l1 == l2):
#     print("Equal")
# else:
#     print("Not Equal")


