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