import csv
import pandas as pd
from config import mayer_ranges
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime, timedelta


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

def generate_mayer_values(source_file, output_file):
    print("Generating Mayer values...")

    mayer_ranges.sort(reverse=True)

    df = pd.read_csv(source_file, skiprows=0)

    df = df.reset_index(drop=True)

    mayer_labels = []
    for mayer_range in mayer_ranges:
        mayer_label = 'Mayer_' + str(mayer_range)
        mayer_labels.append(mayer_label)
        df[mayer_label] = df['Spot']/df['Spot'].rolling(window=(mayer_range + 1)).mean()

    df = df.round(4)
    df.to_csv(output_file, index=False)
    print(f'Created "{output_file}".')

def write_data_to_worksheet(csv_filename, worksheet_name, yesterday):
    data = import_csv_as_list(csv_filename)
    worksheet = google_client.open(workbook_name).worksheet(worksheet_name)
    gsheet_col_names = get_list_of_col_name_from_gsheet(worksheet_name)

    print(f'Checking compatability of "{csv_filename}" with "{worksheet_name}"...')
    okay_to_upload = True
    for i in range(len(data[0])):
        if(data[0][i] != gsheet_col_names[i]):
            okay_to_upload = False
            print(f'Column names "{data[0][i]}" and "{gsheet_col_names[i]}" differ; ' +
                  f'data will not be uploaded to "{worksheet_name}".')
            break;

    if (okay_to_upload):
        dates_from_gsheet = get_list_of_dates_from_gsheet(worksheet_name)
        most_recent_date_in_gsheet = dates_from_gsheet[-1]
        if most_recent_date_in_gsheet < yesterday:
            print(f'Most recent date from Google workbook "{worksheet_name}": {most_recent_date_in_gsheet}')
            missing_gsheet_dates = get_date_range(get_day_after(most_recent_date_in_gsheet), yesterday)
            first_empty_row_index = len(dates_from_gsheet) + 1
            print('Writing missing data to GSheet...')
            for missing_date in missing_gsheet_dates:
                for row in mayer_values_from_csv:
                    if row[0] == missing_date:
                        formatted_row = format_row(row)
                        print(formatted_row)
                        worksheet.insert_row(formatted_row, first_empty_row_index)
                        sleep(2) # don't anger the Google gods
                        first_empty_row_index += 1
            print(f'Updated "{workbook_name}" with {len(missing_gsheet_dates)} record(s).')
        else:
            print(f'Most recent date in "{workbook_name}" ({most_recent_date_in_gsheet}) ' + \
              f'is not before yesterday ({yesterday}); no data are missing.')