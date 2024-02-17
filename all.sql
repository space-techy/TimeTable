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