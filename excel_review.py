from created_reviews import file_exists
import openpyxl

COMPARISON_EXECL_WORKBOOK = "comparison.xlsx"


def create_new_workbook():
    comparison_workbook = openpyxl.Workbook()
    comparison_workbook.create_sheet("reviews per year")


if not file_exists(COMPARISON_EXECL_WORKBOOK):
    create_new_workbook()
else:
    print("Workbook Already Exists")