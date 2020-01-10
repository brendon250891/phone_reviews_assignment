import matplotlib.pyplot as plt
import matplotlib.dates as plt_dates
import numpy as np
import datetime
import re
import created_reviews as cr


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
    for brand in cr.run_database_query(top_three_brands_query):
        monthly_reviews = cr.run_database_query(monthly_reviews_query, brand)
        top_three_brand_reviews[brand[0]] = create_n_dimensional_array(len(monthly_reviews[0]), monthly_reviews, is_date=True)
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
    for name in cr.run_database_query(get_brand_names_query):
        monthly_averages = cr.run_database_query(get_brand_monthly_averages_query, name)
        top_five_brands_average_rating[name[0]] = create_n_dimensional_array(len(monthly_averages[0]), monthly_averages, is_date=True)
    return top_five_brands_average_rating


def get_reviews_against_average_rating_for_product_titles():
    product_title_average_rating_query = """
        select i.total_reviews, avg(r.rating) from items i join reviews r on r.asin = i.asin group by i.title
        order by i.total_reviews
        """
    reviews_against_average_rating = cr.run_database_query(product_title_average_rating_query)
    reviews_against_average_rating = create_n_dimensional_array(len(reviews_against_average_rating[0]), reviews_against_average_rating)
    return reviews_against_average_rating


def get_review_body():
    sql_query = """
        select strftime('%Y', review_date), body from reviews
    """
    review_body = cr.run_database_query(sql_query)
    return review_body


def pull_comments_related_to_price(review_body_data):
    review_body_yearly_count = {}
    for body in review_body_data:
        search = re.search("(price|cost|[$]+)", body[1])
        if search:
            if body[0] in review_body_yearly_count:
                review_body_yearly_count[body[0]] += 1
            else:
                review_body_yearly_count[body[0]] = 1
    return review_body_yearly_count


def create_n_dimensional_array(n, data, is_date=False):
    """ Creates and returns an n-dimensional array """
    nd_array = np.zeros(shape=(n, len(data)), dtype='object')
    for i in range(len(data)):
        for j in range(n):
            if j == 0 and is_date:
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
            if min is None and max is None:
                min = max = date.year
            else:
                if date.year < min:
                    min = date.year
                if date.year > max:
                    max = date.year
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
    plot.scatter(data[1], data[0])
    plot.tick_params(axis='x', labelsize=6)
    plot.set_title(plot_title)
    plot.set_xlabel(x_label)
    plot.set_ylabel(y_label)


def plot_last(plot, data, plot_title, x_label, y_label):
    for key, value in sorted(data.items(), key=lambda x: (x[0])):
        plot.plot(key, value)
    plot.set_title(plot_title)
    plot.set_xlabel(x_label)
    plot.set_ylabel(y_label)


if __name__ == "__main__":
    generate_plot(plt.subplot(221), get_top_three_brands_total_reviews(), "Top Three Brands Total Reviews", "Date", "No. of Reviews")
    generate_plot(plt.subplot(222), get_top_five_brands_average_rating_per_month_2017_2019(), "Top 5 Brands Average Monthly Rating 2017-2019", "Date", "Avg Rating")
    generate_scatter_plot(plt.subplot(223), get_reviews_against_average_rating_for_product_titles(), "Brand Title's Average Rating vs Review", "Reviews", "Average Rating")
    plot_last(plt.subplot(224), pull_comments_related_to_price(get_review_body()), "Number of Reviews Relating To The Cost Of A Phone", "Date", "No. of Reviews")
    plt.subplots_adjust(hspace=0.75)
    plt.show()
