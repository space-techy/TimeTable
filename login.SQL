-- This SQL file is for all the commands we used to make the database named KJSCE_Timetable
-- MySQL connector is used in python

CREATE DATABASE KJSCE_Timetable;

USE KJSCE_Timetable;

-- Users Table containing info about login users
CREATE TABLE IF NOT EXISTS users(
    user_id INT AUTO_INCREMENT UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email_id VARCHAR(100) UNIQUE NOT NULL,
    user_password VARCHAR(100) NOT NULL,
    college_name VARCHAR(100) NOT NULL
);