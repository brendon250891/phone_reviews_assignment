import matplotlib.pyplot as plt
import matplotlib.dates as plt_dates
import numpy as np
import sqlite3
import datetime

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
        select strftime('%m', r.review_date) || "-" || substr(strftime('%Y', r.review_date), 3, 4) as date, count() 
        from reviews r join items i on i.asin = r.asin where i.brand = ? group by date 
        order by strftime('%Y', r.review_date), strftime('%m', r.review_date)
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
        select strftime('%m', r.review_date) || "-" || substr(strftime('%Y', r.review_date), 3, 4) as date, 
        avg(r.rating) from reviews r join items i on r.asin = i.asin where i.brand = ? and strftime('%Y', r.review_date)
        between '2017' and '2019' group by date order by strftime('%Y', r.review_date), strftime('%m', r.review_date)
    """
    for name in run_database_query(get_brand_names_query):
        monthly_averages = run_database_query(get_brand_monthly_averages_query, tuple(name))
        top_five_brands_average_rating[name[0]] = create_n_dimensional_array(len(monthly_averages[0]), monthly_averages)
    return top_five_brands_average_rating


def get_reviews_against_average_rating_for_product_titles():
    product_title_average_rating_query = """
        select i.total_reviews, avg(r.rating) from items i join reviews r on r.asin = i.asin group by i.title
        order by i.total_reviews
        """
    return run_database_query(product_title_average_rating_query)


def create_n_dimensional_array(n, data):
    """ Creates and returns an n-dimensional array """
    nd_array = np.zeros(shape=(n, len(data)), dtype='object')
    for i in range(len(data)):
        for j in range(n):
            if j == 0:
                nd_array[j][i] = datetime.datetime.strptime(data[i][j], '%m-%y')
            else:
                nd_array[j][i] = data[i][j]
    return nd_array


def datetime_string_to_datetime(dates):
    for d in dates:
        d = datetime.datetime.strptime(d, '%m-%y')
    return dates


def find_min_max_date(data):
    min = max = None
    for values in data.values():
        for date in values[0]:
            if min == None and max == None:
                min = max = date.year
            else:
                if date.year < min:
                    min = date.year
                if date.year > max:
                    max = date.year
    return min, max


def find_min_max_reviews(data):
    min = max = None
    for values in data:
        if min == None and max == None:
            min = max = values[1]
        else:
            if values[1] < min:
                min = values[1]
            if values[1] > max:
                max = values[1]
    return min, max


def generate_plot(plot, data, plot_title, x_label, y_label):
    for value in data.values():
        plot.plot(value[0], value[1])
    plot.set_title(plot_title)
    plot.set_xlabel(x_label)
    plot.set_ylabel(y_label)
    plot.tick_params(axis='x', labelsize=6, rotation=90)
    min_max_date = find_min_max_date(data)
    plot.set_xlim(datetime.date(min_max_date[0] - 1, 1, 1), datetime.date(min_max_date[1] + 1, 1, 1))
    plot.xaxis.set_major_locator(plt_dates.YearLocator())
    plot.xaxis.set_minor_locator(plt_dates.MonthLocator())
    plot.legend(data.keys())
    plot.xaxis_date()
    plot.xaxis.set_major_formatter(plt_dates.DateFormatter('%Y'))


def generate_scatter_plot(plot, data, plot_title, x_label, y_label):
    for value in data:
        plot.plot(value[0], value[1])
    min_max = find_min_max_reviews(data)
    plot.set_xlim(min_max[0], min_max[1], 10)
    plot.tick_params(axis='x', labelsize=6)
    plot.set_title(plot_title)
    plot.set_xlabel(x_label)
    plot.set_ylabel(y_label)


generate_plot(plt.subplot(3, 1, 1), get_top_three_brands_total_reviews(), "Top Three Brands Total Reviews", "Date", "No. of Reviews")
generate_plot(plt.subplot(3, 1, 2), get_top_five_brands_average_rating_per_month_2017_2019(), "Top 5 Brands Average Monthly Rating 2017-2019", "Date", "Avg Rating")
generate_scatter_plot(plt.subplot(3, 1, 3), get_reviews_against_average_rating_for_product_titles(), "Brand Title's Average Rating vs Review", "Reviews", "Average Rating")
plt.subplots_adjust(hspace=0.75)
plt.show()
