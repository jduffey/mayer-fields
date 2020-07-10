from coinbase.wallet.client import Client
import csv
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from os import path, mkdir
import pandas as pd
from time import sleep

from config import mayer_ranges, day_ratio_ranges
import printer


workbook_name = "Mayer Fields Data"
google_client_secret_json = 'creds/client_secret.json'
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(google_client_secret_json, scope)
google_client = gspread.authorize(creds)
coinbase_client = Client('<KEY_NOT_NEEDED>', '<SECRET_NOT_NEEDED>')


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


def create_output_dir():
    output_data_dir = "output-data/"
    if not path.exists(output_data_dir):
        mkdir(output_data_dir)
        printer.created_directory(output_data_dir)


def generate_mayer_values(source_file, output_file):
    create_output_dir()
    printer.generating_mayer_values()

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
    printer.created_file(output_file)


def generate_day_ratios(source_file, output_file):
    create_output_dir()
    printer.generating_day_ratios()

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
    printer.created_file(output_file)


def write_data_to_worksheet(csv_filename, worksheet_name, yesterday):
    data = import_csv_as_list(csv_filename)
    worksheet = google_client.open(workbook_name).worksheet(worksheet_name)
    gsheet_col_names = get_list_of_col_name_from_gsheet(worksheet_name)

    printer.check_compatibility_of_price_data_with_worksheet(csv_filename, workbook_name)
    okay_to_upload = True
    for i in range(len(data[0])):
        if data[0][i] != gsheet_col_names[i]:
            okay_to_upload = False
            printer.data_differ_no_upload(data, gsheet_col_names, workbook_name)
            break

    if okay_to_upload:
        dates_from_gsheet = get_list_of_dates_from_gsheet(worksheet_name)
        if dates_from_gsheet[-1] == 'NOW':
            worksheet.delete_row(len(dates_from_gsheet))
            dates_from_gsheet = get_list_of_dates_from_gsheet(worksheet_name)
        most_recent_date_in_gsheet = dates_from_gsheet[-1]
        first_empty_row_index = len(dates_from_gsheet) + 1

        if most_recent_date_in_gsheet < yesterday:
            printer.most_recent_date_from_worksheet(worksheet_name, most_recent_date_in_gsheet)
            missing_gsheet_dates = get_date_range(get_day_after(most_recent_date_in_gsheet), yesterday)
            printer.writing_data_to_worksheet(worksheet_name)
            for missing_date in missing_gsheet_dates:
                for row in data:
                    if row[0] == missing_date:
                        formatted_row = format_row(row)
                        print(formatted_row[0:2])
                        worksheet.insert_row(formatted_row, first_empty_row_index)
                        sleep(2) # don't anger the Google API gods
                        first_empty_row_index += 1
            # TODO: if price data cannot be retrieved and this step is allowed to continue
            #       it will still report that n records have been updated
            printer.updated_worksheet(worksheet_name, missing_gsheet_dates)
        else:
            printer.most_recent_date_in_worksheet_not_before_yesterday(worksheet_name, most_recent_date_in_gsheet, yesterday)

        price_now_row = format_row(data[-1])
        worksheet.insert_row(price_now_row, first_empty_row_index)


def get_most_recent_date(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))[-1][0]


def get_spot_price_for_date(coinbase_client, currency_pair, date):
    price_data = coinbase_client.get_spot_price(currency_pair=currency_pair, date=date)
    return price_data['amount']


def get_price_dict_for_dates(currency_pair, dates):
    dates_and_prices = {}
    for date in dates:
        price = get_spot_price_for_date(coinbase_client, currency_pair, date)
        dates_and_prices[date] = price
        printer.date_and_price(date, price)
    return dates_and_prices


def append_data_to_csv(csv_filename, data):
    with open(csv_filename, 'a') as f:
        for key in data.keys():
            f.write(f'{key},{data[key]}\n')


def remove_last_row_from_csv(csv_filename):
    df = pd.read_csv(csv_filename, skiprows=0)
    df.drop(df.tail(1).index, inplace=True)
    df.to_csv(csv_filename, index=False)


def update_price_data(price_data_csv, coin, currency_pair, yesterday):
    price_data_from_csv = import_csv_as_list(price_data_csv)
    most_recent_date_in_price_data = price_data_from_csv[-1][0]
    if most_recent_date_in_price_data == "NOW":
        most_recent_date_in_price_data = price_data_from_csv[-2][0]
        remove_last_row_from_csv(price_data_csv)
    if most_recent_date_in_price_data < yesterday:
        printer.gathering_missing_price_data(price_data_csv, most_recent_date_in_price_data)
        missing_price_dates = get_date_range(get_day_after(most_recent_date_in_price_data), yesterday)
        missing_price_data = get_price_dict_for_dates(currency_pair, missing_price_dates)
        append_data_to_csv(price_data_csv, missing_price_data)
        printer.updated_price_data(price_data_csv, missing_price_data)
    else:
        printer.no_data_missing_from_price_data(price_data_csv, most_recent_date_in_price_data, yesterday)

    now_price = coinbase_client.get_spot_price(currency_pair=currency_pair)['amount']
    printer.current_price(coin, now_price)
    with open(price_data_csv, 'a') as fd:
        fd.write(f'NOW,{now_price}')
