import created_reviews as cr
import openpyxl
import sqlite3


COMPARISON_EXCEL_WORKBOOK = "comparison.xlsx"
WORKSHEETS = ["reviews per year", "customers"]
REVIEW_HEADINGS = ["Brand", "Product Title", "Year", "Number of Reviews"]
CUSTOMER_HEADINGS = ["Brand", "Percentage of Verified Customers", "Percentage of Each Customer Group"]


def create_new_workbook():
    print("Creating Workbook '{0}'".format(COMPARISON_EXCEL_WORKBOOK))
    comparison_workbook = openpyxl.Workbook()
    comparison_workbook.active.title = WORKSHEETS[0]
    comparison_workbook.create_sheet(WORKSHEETS[1])
    insert_worksheet_headings(comparison_workbook[WORKSHEETS[0]], REVIEW_HEADINGS)
    insert_worksheet_headings(comparison_workbook[WORKSHEETS[1]], CUSTOMER_HEADINGS)
    comparison_workbook.save(COMPARISON_EXCEL_WORKBOOK)


def insert_worksheet_headings(worksheet, headings):
    print("Creating worksheet '{0}'".format(worksheet.title))
    for col in range(1, len(headings) + 1):
        worksheet.cell(row=1, column=col, value="{0}".format(headings[col - 1]))


def write_data_to_workbook(data, sheet_name):
    comparison_workbook = openpyxl.load_workbook(COMPARISON_EXCEL_WORKBOOK)
    if sheet_name not in comparison_workbook.sheetnames:
        comparison_workbook.create_sheet(sheet_name)
    worksheet = comparison_workbook[sheet_name]
    print("Writing '{0}' records into worksheet '{1}'".format(len(data), sheet_name))
    for row in range(2, len(data) + 2):
        for col in range(1, len(data[0]) + 1):
            worksheet.cell(row=row, column=col, value="{0}".format(data[row - 2][col - 1]))
    comparison_workbook.save(COMPARISON_EXCEL_WORKBOOK)
    comparison_workbook.close()


def get_review_yearly_data():
    records = cr.run_database_query("""
        select i.brand, i.title, strftime('%Y', r.review_date) as year, count() from items i 
        join reviews r on r.asin = i.asin group by i.title, year order by i.brand, year""")
    return records


def get_verified_customer_data():
    records = cr.run_database_query("""
        select i.brand, cast(count() as float) / (select count() from reviews where verified = 'True') * 100,
        cast(count() as float) / (select count() from reviews ir join items ii on ii.asin = ir.asin where ii.brand = i.brand) * 100
        from reviews r join items i on i.asin = r.asin where r.verified = 'True' group by i.brand order by count()
    """)
    return records


if __name__ == '__main__':
    if not cr.file_exists(COMPARISON_EXCEL_WORKBOOK):
        create_new_workbook()
        write_data_to_workbook(get_review_yearly_data(), WORKSHEETS[0])
        write_data_to_workbook(get_verified_customer_data(), WORKSHEETS[1])
    else:
        write_data_to_workbook(get_review_yearly_data(), WORKSHEETS[0])
        write_data_to_workbook(get_verified_customer_data(), WORKSHEETS[1])