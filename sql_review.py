import sqlite3

DATABASE_NAME = 'review_data.db'


def get_distinctive_product_titles_in_alphabetical_order():
    """ Retrieves distinct product titles with at least one review and prints the in alphabetical order. """
    connection = sqlite3.connect(DATABASE_NAME)
    products = connection.cursor().execute("""
        select distinct title, brand, rating, total_reviews from items
        where total_reviews >= '1'
        group by title
        order by lower(title) asc;
        """).fetchall()
    connection.close()
    return products


def get_product_with_one_or_more_reviews_order_by_rating_desc():
    connection = sqlite3.connect(DATABASE_NAME)
    products = connection.cursor().execute("""
        select title, rating from items 
        where total_reviews >= '1'
        order by rating desc;    
    """).fetchall()
    connection.close()
    return products


def create_review_summary_table():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.cursor().execute("drop table if exists review_summary;")
    connection.cursor().execute("""
        create table review_summary(
            title varchar(255) not null,
            brand varchar(30) not null,
            average_rating varchar(4) not null,
            total_reviews varchar(4) not null,
            constraint review_summary_pk primary key (title)
        );
        """)
    connection.close()
    seed_review_summary_table(get_distinctive_product_titles_in_alphabetical_order())


def seed_review_summary_table(product_info):
    connection = sqlite3.connect(DATABASE_NAME)
    sql_statement = """
        insert into review_summary
        values('{title}', '{brand}', '{average_rating}', '{total_reviews}')
    """
    for product in get_distinctive_product_titles_in_alphabetical_order():
        sql_command = sql_statement.format(title=product[0], brand=product[1], average_rating=product[2],
                                           total_reviews=product[3])
        connection.execute(sql_command)
        connection.commit()
    connection.close()


def print_database_query_results(title, query_results):
    print(title)
    for product in query_results:
        print(product)
    print("\n\n\n")


print_database_query_results("Distinct Products in Alphabetical Order:",
                             get_distinctive_product_titles_in_alphabetical_order())
create_review_summary_table()
print_database_query_results("Products With One or More Review Ordered By Rating:",
                             get_product_with_one_or_more_reviews_order_by_rating_desc())