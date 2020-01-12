import created_reviews as cr

TABLE_NAME = "review_summary"
OUTPUT_FILE = "sql_review_output.txt"


def create_review_summary_table():
    """ Creates the review summary table. """
    print("Creating table '{0}'...".format(TABLE_NAME))
    cr.run_database_query("drop table if exists review_summary;")
    cr.run_database_query("""
        create table review_summary(
            title varchar(255) not null,
            brand varchar(30) not null,
            average_rating decimal(1,1) not null,
            total_reviews integer not null,
            constraint review_summary_pk primary key (title),
            constraint valid_review_summary check (average_rating between 0.0 and 5.0 and total_reviews >= 0)
        );
    """)


def get_distinctive_product_titles_with_at_least_one_review_in_2019_ordered_alphabetically():
    """ Retrieves distinct product titles with at least one review and prints the in alphabetical order.

        Returns:
            Array: The data retrieved from the database.
    """
    product_titles = cr.run_database_query("""
        select distinct i.title, i.brand, i.rating, i.total_reviews from items i join reviews r on r.asin = i.asin
        where strftime('%Y', r.review_date) = '2019'
        group by i.title
        order by lower(i.title) asc;
        """)
    return product_titles


def insert_information_into_review_summary_table(product_information):
    """ Inserts the data retrieved from a query into the review_summary table.

        Args:
            product_information (Array): Data retrieved from the database to be inserted into the review_summary table.
    """
    print("Inserting '{0}' records into table '{1}'...".format(len(product_information), TABLE_NAME))
    cr.run_database_query("insert into review_summary values(?, ?, ?, ?)", product_information, False)


def get_product_with_one_or_more_reviews_order_by_rating_desc():
    """ Gets the products with one or more reviews in 2019 ordered by rating descending.

        Returns:
            Array: The data retrieved from the database.
    """
    products = cr.run_database_query("""
        select i.title, i.rating from items i join reviews r on r.asin = i.asin
        where strftime('%Y', r.review_date) = '2019' group by i.title
        order by i.rating desc;
    """)
    return products


def select_display_option():
    """ Prompts the user with options on how they wish the data to be displayed. """
    print("Select how you wish to display distinctive products ordered by title and average rating in descending order.")
    print("\t1. Print to the console.\n\t2. Write to a text file.\n")
    selection_made = False
    while not selection_made:
        user_input = input("Selection: ")
        try:
            value = int(user_input)
            if value == 1:
                display_data()
            elif value == 2:
                display_data(True)
            selection_made = True
        except ValueError:
            print("Invalid selection")


def display_data(write_to_file=False):
    """ Prints the data to the console or a file based on user selection.

        Args:
            write_to_file (bool, optional): Default is false which writes to the console, True if the user wants to
                write data to a file.
    """
    products_alphabetically = get_distinctive_product_titles_with_at_least_one_review_in_2019_ordered_alphabetically()
    products_by_average = get_product_with_one_or_more_reviews_order_by_rating_desc()
    if write_to_file:
        with open(OUTPUT_FILE, 'w') as file:
            file.seek(0)
            file.write("Products with at least 1 review in 2019 ordered by title alphabetically:\n")
            for index in range(len(products_alphabetically)):
                file.write("{0}. {1}\n".format(index + 1, products_alphabetically[index][0]))
            file.write("\nProducts with at least 1 review in 2019 ordered by average rating descending:\n")
            for index in range(len(products_by_average)):
                file.write("{0}. {1}, {2}\n".format(index + 1, products_by_average[index][0], products_by_average[index][1]))
    else:
        print("Products with at least 1 review in 2019 ordered alphabetically by title:\n")
        for index in range(len(products_alphabetically)):
            print("{0}. {1}".format(index + 1, products_alphabetically[index][0]))
        print("\nProducts with at least 1 review in 2019 ordered by average rating descending:\n")
        for index in range(len(products_by_average)):
            print("{0}. {1}, {2}".format(index + 1, products_by_average[index][0], products_by_average[index][1]))


if __name__ == "__main__":
    """ Executed when the file is run. If the review_summary table doesn't exist then it is created and data written, 
    otherwise the user is prompted with options to proceed. """
    tables = cr.get_database_info()
    review_summary_exists = False
    for table in tables:
        if table[0] == TABLE_NAME:
            review_summary_exists = True
    if not review_summary_exists:
        create_review_summary_table()
        product_titles = get_distinctive_product_titles_with_at_least_one_review_in_2019_ordered_alphabetically()
        insert_information_into_review_summary_table(product_titles)
    else:
        print("The table '{0}' already exists in the database '{1}'".format(TABLE_NAME, cr.DATABASE_NAME))
        selected_option = False
        while not selected_option:
            user_input = input("Do you want to remake and re-seed the table {0} (y/n): ".format(TABLE_NAME)).lower()
            if user_input == 'y':
                create_review_summary_table()
                product_titles = get_distinctive_product_titles_with_at_least_one_review_in_2019_ordered_alphabetically()
                insert_information_into_review_summary_table(product_titles)
                selected_option = True
            elif user_input == 'n':
                print("Nothing was done")
                selected_option = True
    select_display_option()
