CREATE DATABASE CULTURAL_DB;
USE CULTURAL_DB;

CREATE SCHEMA CULTURAL_SCHEMA;
USE CULTURAL_SCHEMA;

CREATE TABLE cultural_sites (
    site_id INT AUTOINCREMENT PRIMARY KEY,
    site_name STRING,
    state STRING,
    art_form STRING,
    seasonality STRING,
    responsible_score FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    image_url STRING
);

CREATE TABLE tourism_stats (
    id INT AUTOINCREMENT PRIMARY KEY,
    state STRING,
    year INT,
    domestic_arrivals INT
);
