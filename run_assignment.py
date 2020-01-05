import created_reviews
import sql_review
import excel_review
import numpy_review

SELECTIONS = ["Create and Seed Database", "Create and Insert Excel Data", "Generate Plots"]

for i in range(len(SELECTIONS)):
    print(str(i + 1) + ". " + SELECTIONS[i])

while True:
    try:
        selected_option = int(input("Selection:"))
        if not 1 <= selected_option <= len(SELECTIONS):
            raise(ValueError("Invalid Selection"))
        else:
            if selected_option == 1:
                created_reviews.create_database()
            elif selected_option == 2:
                excel_review.create_new_workbook()
            else:
                numpy_review.get_top_five_brands_average_rating_per_month_2017_2019()
    except ValueError:
        print("Invalid Selection")
