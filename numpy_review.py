import matplotlib.pyplot as plt
import matplotlib.dates as matdates
import numpy as np
import sqlite3
import datetime
import openpyxl

DATABASE_NAME = "review_data.db"


def run_database_query(query, params=None):
    connection = sqlite3.connect(DATABASE_NAME)
    query_results = None
    if params is not None:
        query_results = connection.execute(query, params).fetchall()
    else:
        query_results = connection.execute(query).fetchall()
    connection.close()
    return query_results

def get_top_three_brands_total_reviews():
    """ Gets the top three brands total reviews by first getting the names and then getting the monthly reviews for
    each"""
    top_three_brand_reviews = {}
    top_three_brands_query = """
        select i.brand from items i join reviews r on r.asin = i.asin group by i.brand order by count() desc limit 3
    """
    monthly_reviews_query = """
        select strftime('%m-%Y', r.review_date) as date, count() from reviews r join items i on i.asin = r.asin 
        where i.brand = ? group by date order by strftime('%Y', r.review_date), strftime('%m', r.review_date)
    """
    for brand in run_database_query(top_three_brands_query):
        monthly_reviews = run_database_query(monthly_reviews_query, tuple(brand))
        top_three_brand_reviews[brand[0]] = create_n_dimensional_array(len(monthly_reviews[0]), monthly_reviews)
    return top_three_brand_reviews


def get_top_five_brands_average_rating_per_month_2017_2019():
    """ Gets the top five brands average rating per month from 2017-2019 for the top five rated brands during that
    period."""
    top_five_brands_average_rating = {}
    get_brand_names_query = """
        select i.brand from items i join reviews r on r.asin = i.asin where strftime('%Y', r.review_date) between 
        '2017' and '2019' group by i.brand order by avg(r.rating) desc limit 5
    """
    get_brand_monthly_averages_query = """
        select avg(r.rating) as average, strftime('%m-%Y', r.review_date) as 
        month_year from reviews r join items i on r.asin = i.asin where i.brand = ? and strftime('%Y', r.review_date)
        between '2017' and '2019' group by month_year order by strftime('%Y', r.review_date), 
        strftime('%m', r.review_date)
    """
    for name in run_database_query(get_brand_names_query):
        monthly_averages = run_database_query(get_brand_monthly_averages_query, tuple(name))
        top_five_brands_average_rating[name[0]] = create_n_dimensional_array(len(monthly_averages[0]), monthly_averages)
    return top_five_brands_average_rating


def reviews_against_average_rating_for_product_titles():
    connection = sqlite3.connect(DATABASE_NAME)
    review_against_average = connection.execute("""
        select i.title, i.total_reviews, avg(r.rating) from items i join reviews r on r.asin = i.asin group by i.title
        """).fetchall()
    connection.close()


def create_n_dimensional_array(n, data):
    """ Creates and returns an n-dimensional array """
    nd_array = np.zeros(shape=(n, len(data)), dtype='object')
    for i in range(len(data)):
        for j in range(n):
            nd_array[j][i] = data[i][j]
    return nd_array


""" Need to plot """

for key, value in get_top_five_brands_average_rating_per_month_2017_2019().items():
    print(key + " : " + str(value))
