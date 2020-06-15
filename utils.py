import csv
import pandas as pd
from time import sleep
from config import mayer_ranges, day_ratio_ranges
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime, timedelta
from os import path, mkdir


# Google settings
workbook_name = "Mayer Fields Data"
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
google_client_secret_json = 'creds/client_secret.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(google_client_secret_json, scope)
google_client = gspread.authorize(creds)


def get_list_of_dates_from_gsheet(worksheet_name):
    return google_client.open(workbook_name).worksheet(worksheet_name).col_values(1)


def get_list_of_col_name_from_gsheet(worksheet_name):
    return google_client.open(workbook_name).worksheet(worksheet_name).row_values(1)


def import_csv_as_list(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))


def get_yesterday():
    return datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')


def get_date_range(start_date, end_date):
    return [date.strftime('%Y-%m-%d') for date in pd.date_range(start_date, end_date)]


def get_day_after(date):
    date_formatted = datetime.strptime(date, '%Y-%m-%d')
    return datetime.strftime(date_formatted + timedelta(1), '%Y-%m-%d')


def format_row(unformatted_row):
    formatted_row = []
    formatted_row.append(unformatted_row[0])
    formatted_row.append('${:,.2f}'.format(float(unformatted_row[1])))
    for i in range(2, len(unformatted_row)):
        if unformatted_row[i] == '': # skips missing Mayer values
            formatted_row.append(unformatted_row[i])
        else:
            formatted_row.append(float(unformatted_row[i]))
    return formatted_row


def generate_mayer_values(source_file, output_file):
    # TODO: if output file does not exist then create it
    output_data_dir = "output-data/"
    if path.exists(output_data_dir):
        print(f'******* "{output_data_dir}" directory exists.')
    else:
        mkdir(output_data_dir)
        print(f'******* Creating "{output_data_dir}" directory.')
    if path.exists(output_file):
        print(f'******* "{output_file}" exists.')
    else:
        _ = open(output_file, 'x')
        print(f'******* Creating {output_file}')

    print("Generating Mayer values...")

    mayer_ranges.sort(reverse=True)

    df = pd.read_csv(source_file, skiprows=0)

    df = df.reset_index(drop=True)

    mayer_labels = []
    for mayer_range in mayer_ranges:
        mayer_label = f'Mayer_{str(mayer_range)}'
        mayer_labels.append(mayer_label)
        df[mayer_label] = df['Spot']/df['Spot'].rolling(window=(mayer_range + 1)).mean()

    df = df.round(4)
    df.to_csv(output_file, index=False)
    print(f'Created "{output_file}".\n')


def generate_day_ratios(source_file, output_file):
    print("Generating day ratios...")

    day_ratio_ranges.sort(reverse=True)

    df = pd.read_csv(source_file, skiprows=0)

    df = df.reset_index(drop=True)

    day_ratio_labels = []
    for day_ratio in day_ratio_ranges:
        day_ratio_label = f'Ratio_{str(day_ratio)}'
        day_ratio_labels.append(day_ratio_label)
        df[day_ratio_label] = df['Spot'] / df['Spot'].shift(day_ratio)

    df = df.round(4)
    df.to_csv(output_file, index=False)
    print(f'Created "{output_file}".\n')


def write_data_to_worksheet(csv_filename, worksheet_name, yesterday):
    data = import_csv_as_list(csv_filename)
    worksheet = google_client.open(workbook_name).worksheet(worksheet_name)
    gsheet_col_names = get_list_of_col_name_from_gsheet(worksheet_name)

    print(f'Checking compatability of "{csv_filename}" with "{worksheet_name}"...\n')
    okay_to_upload = True
    for i in range(len(data[0])):
        if data[0][i] != gsheet_col_names[i]:
            okay_to_upload = False
            print(f'Column names "{data[0][i]}" and "{gsheet_col_names[i]}" differ; ' +
                  f'data will not be uploaded to "{worksheet_name}".\n')
            break

    if okay_to_upload:
        dates_from_gsheet = get_list_of_dates_from_gsheet(worksheet_name)
        if dates_from_gsheet[-1] == 'NOW':
            worksheet.delete_row(len(dates_from_gsheet))
            dates_from_gsheet = get_list_of_dates_from_gsheet(worksheet_name)
        most_recent_date_in_gsheet = dates_from_gsheet[-1]
        first_empty_row_index = len(dates_from_gsheet) + 1

        if most_recent_date_in_gsheet < yesterday:
            print(f'Most recent date from Google workbook "{worksheet_name}": {most_recent_date_in_gsheet}')
            missing_gsheet_dates = get_date_range(get_day_after(most_recent_date_in_gsheet), yesterday)
            print(f'Writing missing data to "{worksheet_name}"...')
            for missing_date in missing_gsheet_dates:
                for row in data:
                    if row[0] == missing_date:
                        formatted_row = format_row(row)
                        print(formatted_row[0:2])
                        worksheet.insert_row(formatted_row, first_empty_row_index)
                        sleep(2) # don't anger the Google API gods
                        first_empty_row_index += 1
            print(f'Updated "{worksheet_name}" with {len(missing_gsheet_dates)} record(s).\n')
        else:
            print(f'Most recent date in "{worksheet_name}" ({most_recent_date_in_gsheet}) ' + \
              f'is not before yesterday ({yesterday}); no data are missing.\n')

        price_now_row = format_row(data[-1])
        worksheet.insert_row(price_now_row, first_empty_row_index)
