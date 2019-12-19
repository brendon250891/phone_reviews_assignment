#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 12:53:54 2019

@author: brendon
"""

import sqlite3
import openpyxl


def create_database():
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
                           review_id int auto_increment not null,
                           asin char(10) not null,
                           name varchar(255) not null,
                           rating char(1) not null,
                           review_date date not null,
                           verified boolean not null,
                           title varchar(255) not null,
                           body varchar(255), 
                           helpful_vote varchar(4) not null,
                           constraint reviews_pk primary key (review_id)
                           constraint reviews_fk foreign key (asin) references items(asin)
                           )"""
    cursor.execute(create_reviews_table)
    
def database_test():
    connection = sqlite3.connect('review_data.db')
    cursor = connection.cursor()
    for record in cursor.execute('select * from items'):
        print(record)

create_database()
database_test()
wb = openpyxl.load_workbook('reviews.xlsx')