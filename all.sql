-- This is for creating add subject 

CREATE TABLE subjects(
    subid SERIAL PRIMARY KEY,
    subclass VARCHAR(500) NOT NULL,
    subsem VARCHAR(500) NOT NULL,
    subcode VARCHAR(500) UNIQUE NOT NULL,
    subabb VARCHAR(500) NOT NULL,
    subname VARCHAR(500) NOT NULL,
    sublecture INT NOT NULL,
    subtut INT NOT NULL,
    subprac INT NOT NULL,
    subelective VARCHAR(500) NOT NULL,
    subdep VARCHAR(500) NOT NULL
);


-- This is for creating Add Faculty

CREATE TABLE faculty(
    facid SERIAL PRIMARY KEY,
    facinit VARCHAR(10) NOT NULL UNIQUE,
    facname VARCHAR(500) NOT NULL,
    facdes VARCHAR(500) NOT NULL,
    facqual VARCHAR(500) NOT NULL,
    facdep VARCHAR(500) NOT NULL,
    facshdep VARCHAR(500)
);


-- This is for creating Add Room

CREATE TABLE rooms(
    roomid SERIAL PRIMARY KEY UNIQUE,
    roomno VARCHAR(100) UNIQUE NOT NULL,
    roomdes VARCHAR(500) NOT NULL,
    roomdep VARCHAR(500) NOT NULL,
    roomshdep VARCHAR(500) 
);

-- This table is for timetable slots

CREATE TABLE time_slots(
    id SERIAL,
    slots_name VARCHAR(500) UNIQUE PRIMARY KEY,
    day VARCHAR(250),
    time VARCHAR(500),
    slot_time_day VARCHAR(500)
);



-- This table is for storing all the timetables we have made till now every year

CREATE TABLE all_timetables(
    id SERIAL,
    year VARCHAR(500) NOT NULL,
    sem VARCHAR(500) NOT NULL,
    year_sem VARCHAR(500) UNIQUE NOT NULL PRIMARY KEY
);



-- A sample sql code to make year_sem table

CREATE TABLE "your time table name"(
    id PRIMARY KEY UNIQUE NOT NULL,
    class VARCHAR(250) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    slot VARCHAR(50) NOT NULL,
    day VARCHAR(250) NOT NULL,
    time VARCHAR(250) NOT NULL,
    faculty varchar(250) NOT NULL,
    room varchar(250) NOT NULL,
    batch varchar(200) NOT NULL,
    type varchar(100) NOT NULL,
    branch varchar(250) NOT NULL,
    division varchar(250) not null
);


-- Table for creating divisions for a batch

CREATE TABLE divisions(
    id SERIAL NOT NULL,
    year VARCHAR(10) NOT NULL,
    course VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    batch VARCHAR(10) NOT NULL,
    no_of_div INT(10) NOT NULL,
    class VARCHAR(500) NOT NULL
);



UPDATE even_2023_2024 AS main
                JOIN temp_data AS temp ON temp.id = 422
                SET main.class = temp.class, 
                    main.subject = temp.subject, 
                    main.slot = temp.slot, 
                    main.day = temp.day, 
                    main.time = temp.time, 
                    main.faculty = temp.faculty, 
                    main.room = temp.room, 
                    main.batch = temp.batch, 
                    main.type = temp.type, 
                    main.branch = temp.branch, 
                    main.division = temp.division
                WHERE main.id = 421