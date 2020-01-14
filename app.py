import csv
import gspread
import pandas
from coinbase.wallet.client import Client
from datetime import datetime, timedelta
from generate_mayer_values import generate_mayer_values
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep

# Local settings
price_data_csv = 'price_data.csv'
mayer_values_csv = 'output-data/mayer_values.csv'
day_ratios_csv = 'output-data/day_ratios.csv'
google_client_secret_json = 'creds/client_secret.json'

# Google settings
workbook_name = "Mayer Fields Data"
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(google_client_secret_json, scope)
google_client = gspread.authorize(creds)

# Coinbase settings
coinbase_client = Client('<KEY_NOT_NEEDED>', '<SECRET_NOT_NEEDED>') # key/secret not needed for get_spot_price()
currency_pair = 'BTC-USD'

def import_csv_as_list(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))

def get_most_recent_date(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))[-1][0]

def get_list_of_dates_from_gsheet(worksheet_name):
    return google_client.open(workbook_name).worksheet(worksheet_name).col_values(1)

def get_list_of_col_name_from_gsheet(worksheet_name):
    return google_client.open(workbook_name).worksheet(worksheet_name).row_values(1)

def get_spot_price_for_date(date):
    price_data = coinbase_client.get_spot_price(currency_pair = currency_pair, date = date)
    return price_data['amount']

def get_yesterday():
    return datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')

def get_day_after(date):
    date_formatted = datetime.strptime(date, '%Y-%m-%d')
    return datetime.strftime(date_formatted + timedelta(1), '%Y-%m-%d')

def get_date_range(start_date, end_date):
    return [date.strftime('%Y-%m-%d') for date in pandas.date_range(start_date, end_date)]

def get_price_dict_for_dates(dates):
    dates_and_prices = {}
    for date in dates:
        price = get_spot_price_for_date(date)
        dates_and_prices[date] = price
        print(f'{date}: ${price}')
    return dates_and_prices

def append_data_to_csv(csv_filename, data):
    with open(price_data_csv, 'a') as f:
        for key in missing_price_data.keys():
            f.write("%s,%s\n"%(key,missing_price_data[key]))

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


if __name__ == '__main__':

    price_data_from_csv = import_csv_as_list(price_data_csv)
    most_recent_date_in_price_data = price_data_from_csv[-1][0]

    yesterday = get_yesterday()

    if most_recent_date_in_price_data < yesterday:

        print(f'Most recent date in "{price_data_csv}": {most_recent_date_in_price_data}')
        print('Gathering missing price data...')

        missing_price_dates = get_date_range(get_day_after(most_recent_date_in_price_data), yesterday)

        missing_price_data = get_price_dict_for_dates(missing_price_dates)

        append_data_to_csv(price_data_csv, missing_price_data)
        print(f'Updated "{price_data_csv}" with {len(missing_price_data)} record(s).')

    else:
        print(f'Most recent date in "{price_data_csv}" ({most_recent_date_in_price_data}) ' + \
              f'is not before yesterday ({yesterday}); no data are missing.')

    generate_mayer_values(price_data_csv, mayer_values_csv)

    '''
    Google Sheets write code is below
    '''

    # Mayer values
    worksheet_name = "Mayer Multiples"
    mayer_values_from_csv = import_csv_as_list(mayer_values_csv)

    worksheet = google_client.open(workbook_name).worksheet(worksheet_name)
    gsheet_col_names = get_list_of_col_name_from_gsheet(worksheet_name)
    print(f'Checking compatability of "{mayer_values_csv}" with "{worksheet_name}"...')

    okay_to_upload = True
    for i in range(len(mayer_values_from_csv[0])):
        if(mayer_values_from_csv[0][i] != gsheet_col_names[i]):
            okay_to_upload = False
            print(f'Column names "{mayer_values_from_csv[0][i]}" and "{gsheet_col_names[i]}" differ; ' +
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
