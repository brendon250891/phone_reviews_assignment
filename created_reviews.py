#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 12:53:54 2019

@author: brendon
"""

import sqlite3
import openpyxl
import re
import datetime

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
    print("Creating database...")
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
    seed(ITEMS_EXCEL, 'insert into items values(?,?,?,?,?,?,?,?,?)')
    seed(REVIEWS_EXCEL, 'insert into reviews values(NULL,?,?,?,?,?,?,?,?)')


def create_items_table(cursor):
    create_items_table = """
                       create table items(
                           asin char(10) not null,
                           brand varchar(30) not null,
                           title varchar(255) not null,
                           url varchar(150) not null,
                           image varchar(100) not null,
                           rating varchar(3) not null,
                           review_url varchar(60) not null,
                           total_reviews varchar(4) not null,
                           price decimal(5,2) default 0.0,
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
                           helpful_vote varchar(4),
                           constraint reviews_pk primary key (review_id)
                           constraint reviews_fk foreign key (asin) references items(asin)
                           )"""
    cursor.execute(create_reviews_table)


def seed(excel_file, query):
    data = openpyxl.load_workbook(excel_file)
    records_to_seed = prompt_for_number_of_records(data.active.max_row - 1)
    print("Seeding " + excel_file + "...")
    connection = sqlite3.connect(DATABASE_NAME)
    for row in data.active.iter_rows(min_row=2, max_row=records_to_seed + 1):
        row_values = []
        for cell in row:
            cell.value = check_for_formatting(str(cell.value))
            row_values.append(cell.value)
        connection.cursor().execute(query, tuple(row_values))
    connection.commit()
    connection.close()


def check_for_formatting(value):
    """ Fixes some formatting issues in the data sets.
        1. Some items have multiple prices so the first value is used.
        2. Converts the date column in the reviews dataset to be of type datetime.
    """
    if value.startswith('$'):
        return value[1:value.find(',')]
    elif re.search(", 20[0-9]{2}$", value) and len(value) <= 18:
        year = value[-4:]
        day = value[value.find(' ') + 1: value.find(',')]
        month = month_str_to_int(value[:value.find(' ')].lower())
        return datetime.date(int(year), int(month), int(day))
    else:
        return value


def month_str_to_int(month):
    return {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12}[month]


def prompt_for_number_of_records(row_count):
    while True:
        user_input = input("There are " + str(row_count) + " rows of data\nEnter the number of rows you wish "
                                                           "to seed or press enter to seed all: ")
        if user_input == "":
            return row_count
        try:
            user_input = int(user_input)
            if 0 < int(user_input) <= row_count:
                return user_input
        except ValueError:
            int(input("Incorrect input. Enter a valid number or press enter to seed all: "))


def get_database_info():
    connection = sqlite3.connect(DATABASE_NAME)
    tables = connection.execute("select name from sqlite_master where type = 'table' order by name").fetchall()
    print("Database contains " + str(len(tables)) + " tables:")
    for table in tables:
        number_of_records = connection.execute('select count(*) from {}'.format(table[0])).fetchone()
        print(table[0] + ": " + str(number_of_records[0]) + " records")


# Tries to open the database if it already exists otherwise creates and seeds the database.
if not file_exists(DATABASE_NAME):
    if file_exists(ITEMS_EXCEL) and file_exists(REVIEWS_EXCEL):
        create_database()
    else:
        print("Database Creation Failed.\nData Files Not Found.")
else:
    print("Error: Database already exists.")
    get_database_info()
    while True:
        selection = input("Do you want to re-create and seed (Y/N): ")
        if selection.lower() == 'y':
            create_database()
            break
        elif selection.lower() == 'n':
            print("Exiting...")
            break
        else:
            print("Invalid Selection")
