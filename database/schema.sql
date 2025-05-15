USE DATABASE CULTURAL_DB;
USE SCHEMA CULTURAL_SCHEMA;
USE WAREHOUSE CULTURAL_WH;


CREATE TABLE tourism_stats (
    id INT AUTOINCREMENT PRIMARY KEY,
    state STRING,
    year INT,
    domestic_arrivals INT
);

CREATE OR REPLACE TABLE cultural_sites (
    site_id INT AUTOINCREMENT PRIMARY KEY,
    site_name STRING,
    state STRING,
    art_form STRING,
    seasonality STRING,
    responsible_score FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    image_url STRING,
    describtion STRING
);

SELECT * FROM cultural_sites;