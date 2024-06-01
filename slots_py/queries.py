file1 = open("./slots_py/sql_text.txt", "w")


time_slots = ["8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00","12:00-1:00", "1:00-2:00", "2:00-3:00", "3:00-4:00", "4:00-5:00", "5:00-6:00", "6:00-7:00"]
 
days = { 'A': "Monday", 'B' : "Tuesday", "C": "Wednesday", 'D': "Thursday", 'E':"Friday"}


for i in "ABCDE":
    for j in time_slots:
        if(j == "1:00-2:00"):
            slot = "LB"
        else:
            slot =  i + str(time_slots.index(j) + 1)
            slot_time_day = slot.strip() + "|".strip() + j.strip() + "|".strip() + days[i].strip()
        query1 = f'INSERT INTO time_slots( day, time, slots_name, slot_time_day) VALUES( "{days[i]}", "{j}", "{slot}", "{slot_time_day}");'
        file1.write(query1)
        file1.write("\n")


file1.close()