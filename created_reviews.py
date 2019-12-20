#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 12:53:54 2019

@author: brendon
"""

import sqlite3
import openpyxl

# Store file names in constants
DATABASE_NAME = "review_data.db"
ITEMS_EXCEL = "items.xlsx"
REVIEWS_EXCEL = "reviews.xlsx"


def file_exists(filename):
    """ Checks to see if the database file already exists"""
    try:
        open(filename)
        return True
    except FileNotFoundError:
        return False


def create_database():
    """ """
    connection = sqlite3.connect('review_data.db')
    cursor = connection.cursor()
    drop_items_table = "drop table if exists items;"
    drop_reviews_table = "drop table if exists reviews;"
    cursor.execute(drop_items_table)
    cursor.execute(drop_reviews_table)
    create_items_table(cursor)
    create_reviews_table(cursor)
    connection.commit()
    connection.close()


def create_items_table(cursor):
    create_items_table = """
                       create table items(
                           asin char(10) not null,
                           brand varchar(10) not null,
                           title varchar(255) not null,
                           url varchar(150) not null,
                           image varchar(100) not null,
                           rating varchar(3) not null,
                           review_url varchar(60) not null,
                           total_reviews varchar(4) not null,
                           price decimal(5,2),
                           constraint items_pk primary key (asin),
                           constraint valid_price check (price > 0.0)
                           );"""
    cursor.execute(create_items_table)


def create_reviews_table(cursor):
    create_reviews_table = """
                       create table reviews(
                           review_id integer,
                           asin char(10) not null,
                           name varchar(255) not null,
                           rating char(1) not null,
                           review_date date not null,
                           verified boolean not null,
                           title varchar(255) not null,
                           body varchar(100000), 
                           helpful_vote varchar(4) not null,
                           constraint reviews_pk primary key (review_id)
                           constraint reviews_fk foreign key (asin) references items(asin)
                           )"""
    cursor.execute(create_reviews_table)


def seed_items(excel_file):
    data = openpyxl.load_workbook(excel_file)
    for row in data.active.iter_rows(min_row=2):
        insert_statement = """insert into items 
        VALUES("{asin}", "{brand}", '{title}', "{url}", "{image}", "{rating}", "{review_url}", "{total_reviews}", "{price}")
        """
        insert_command = insert_statement.format(asin=row[0].value, brand=row[1].value, title=row[2].value,
                                                 url=row[3].value, image=row[4].value, rating=row[5].value,
                                                 review_url=row[6].value, total_reviews=row[7].value, price=row[8].value)
        database_insert(insert_command)


def seed_reviews(excel_file):
    data = openpyxl.load_workbook(excel_file)
    for row in data.active.iter_rows(min_row=2):
        insert_statement = """insert into reviews
        VALUES(NULL, "{asin}", '{name}', "{rating}", "{review_date}", "{verified}", '{title}', '{body}', "{helpful_votes}")
        """
        insert_command = insert_statement.format(asin=row[0].value, name=row[1].value, rating=row[2].value,
                                                 review_date=row[3].value, verified=row[4].value, title=row[5].value,
                                                 body=row[6].value, helpful_votes=row[7].value)
        database_insert(insert_command)


def database_insert(command):
    database_connection = sqlite3.connect(DATABASE_NAME)
    database_connection.cursor().execute(command)
    database_connection.commit()
    database_connection.close()


# Tries to open the database if it already exists otherwise creates and seeds the database.
if not file_exists(DATABASE_NAME):
    print("Creating database...")
    if file_exists(ITEMS_EXCEL) and file_exists(REVIEWS_EXCEL):
        create_database()
        print("Seeding " + ITEMS_EXCEL + "...")
        seed_items(ITEMS_EXCEL)
        print("Seeding " + REVIEWS_EXCEL + "...")
        seed_reviews(REVIEWS_EXCEL)
    else:
        print("Data Files Not Found")
else:
    print("Connecting to database...")
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()
