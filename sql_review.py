import sqlite3

DATABASE_NAME = 'review_data.db'


def distinctive_product_titles_in_alphabetical_order():
    """ Retrieves distinct product titles with at least one review and prints the in alphabetical order. """
    connection = sqlite3.connect(DATABASE_NAME)
    titles = connection.cursor().execute("""
        select distinct i.title from items i 
        join reviews r on r.asin = i.asin
        where i.total_reviews >= '1' 
        order by lower(i.title) asc
        """)
    for title in titles:
        print(title)


def create_review_summary_table():
    pass


distinctive_product_titles_in_alphabetical_order()