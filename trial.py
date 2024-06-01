tq = "FHS/JJK/RHS"
l1 = []
i = 0
for j in range(len(tq)):
    if(tq[j] == "/"):
        faculty = tq[i:j]
        i = j + 1
        l1.append(faculty)
l1.append(tq[i:])
print(l1)