-- This is for creating add subject 

CREATE TABLE subjects(
    subid SERIAL PRIMARY KEY,
    subclass VARCHAR(500) NOT NULL,
    subsem VARCHAR(500) NOT NULL,
    subcode VARCHAR(500) UNIQUE NOT NULL,
    subabb VARCHAR(500) UNIQUE NOT NULL,
    subname VARCHAR(500) UNIQUE NOT NULL,
    sublecture INT NOT NULL,
    subtut INT NOT NULL,
    subprac INT NOT NULL,
    subelective VARCHAR(500) NOT NULL
);


-- This is for creating Add Faculty

CREATE TABLE faculty(
    facid SERIAL PRIMARY KEY,
    facinit VARCHAR(10) NOT NULL,
    facname VARCHAR(500) NOT NULL,
    facdes VARCHAR(500) NOT NULL,
    facqual VARCHAR(500) NOT NULL,
    facshdep VARCHAR(500) NOT NULL
);


-- This is for creating Add Room

CREATE TABLE rooms(
    roomid SERIAL PRIMARY KEY UNIQUE,
    roomno VARCHAR(100) UNIQUE NOT NULL,
    roomdes VARCHAR(500) NOT NULL,
    roomshdep VARCHAR(500) NOT NULL 
);

-- This table is for timetable slots

CREATE TABLE time_slots(
    id SERIAL,
    day VARCHAR(250),
    time VARCHAR(500),
    slots_name VARCHAR(500) UNIQUE PRIMARY KEY
);



-- This table is for storing all the timetables we have made till now every year

CREATE TABLE all_timetables(
    id SERIAL,
    year VARCHAR(500) NOT NULL,
    sem VARCHAR(500) NOT NULL,
    year_sem VARCHAR(500) UNIQUE NOT NULL PRIMARY KEY
);



-- A sample sql code to make year_sem table

CREATE TABLE 'You can give any name'(
    id NOT NULL SERIAL,
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
);