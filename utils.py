import csv
from datetime import datetime, timedelta, timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from os import path, mkdir
import pandas as pd
from time import sleep
import google_utils

import config
import printer


workbook_name = config.google_workbook_name
google_client_secret = config.google_client_secret
google_client_scope = config.google_client_scope
creds = ServiceAccountCredentials.from_json_keyfile_name(google_client_secret, google_client_scope)
google_client = gspread.authorize(creds)


# tested
def import_csv_as_list(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))


# tested
def get_yesterday():
    return datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')


# tested
def get_date_range(start_date, end_date):
    return [date.strftime('%Y-%m-%d') for date in pd.date_range(start_date, end_date)]


# tested
def get_day_after(date):
    date_formatted = datetime.strptime(date, '%Y-%m-%d')
    return datetime.strftime(date_formatted + timedelta(1), '%Y-%m-%d')


# tested
def format_row(unformatted_row):
    formatted_row = []
    formatted_row.append(unformatted_row[0])
    formatted_row.append('${:,.2f}'.format(float(unformatted_row[1])))
    for i in range(2, len(unformatted_row)):
        if unformatted_row[i] != '':
            formatted_row.append(float(unformatted_row[i]))
        else: # avoid ValueError
            formatted_row.append(unformatted_row[i])
    return formatted_row


# tested
def create_output_dir(output_dir):
    if not path.exists(output_dir):
        mkdir(output_dir)
        printer.created_directory(output_dir)


# tested... partially? To what extent should we test the actaul values?
def generate_mayer_values(source_file, output_file):
    create_output_dir('output-data/')
    printer.generating_mayer_values()

    config.mayer_ranges.sort(reverse=True)
    df = pd.read_csv(source_file, skiprows=0)
    df = df.reset_index(drop=True)

    mayer_labels = []
    for mayer_range in config.mayer_ranges:
        mayer_label = f'Mayer_{str(mayer_range)}'
        mayer_labels.append(mayer_label)
        df[mayer_label] = df['Spot']/df['Spot'].rolling(window=(mayer_range + 1)).mean()

    df = df.round(4)
    df.to_csv(output_file, index=False)
    printer.created_file(output_file)


# TODO: test this
def generate_day_ratios(source_file, output_file):
    create_output_dir('output-data/')
    printer.generating_day_ratios()

    config.day_ratio_ranges.sort(reverse=True)
    df = pd.read_csv(source_file, skiprows=0)
    df = df.reset_index(drop=True)

    day_ratio_labels = []
    for day_ratio in config.day_ratio_ranges:
        day_ratio_label = f'Ratio_{str(day_ratio)}'
        day_ratio_labels.append(day_ratio_label)
        df[day_ratio_label] = df['Spot'] / df['Spot'].shift(day_ratio)

    df = df.round(4)
    df.to_csv(output_file, index=False)
    printer.created_file(output_file)


# tested
def append_data_to_csv(csv_filename, data):
    with open(csv_filename, 'a') as f:
        for key in data.keys():
            f.write(f'{key},{data[key]}\n')


# tested
def remove_last_row_from_csv(csv_filename):
    df = pd.read_csv(csv_filename, skiprows=0)
    df.drop(df.tail(1).index, inplace=True)
    df.to_csv(csv_filename, index=False)


def get_most_recent_date(price_data_csv):
    price_data_from_csv = import_csv_as_list(price_data_csv)
    most_recent_date = price_data_from_csv[-1][0]
    if most_recent_date == 'NOW':
        return ('NOW', price_data_from_csv[-2][0])
    else:
        return (price_data_from_csv[-1][0],)


def find_mayer_prices(coin):
    sma_pairs = [(200, [2.4 + 0.1 * x for x in range(14)])]
    coin_name = coin[0]
    price_step = coin[1]

    now_date = 'NOW'

    for sma_pair in sma_pairs:
        sma_day_range = sma_pair[0]
        target_sma_ratios = sma_pair[1]
        print(f'\nSMA Day Range: {sma_day_range}\n--------------')
        print(f'Target SMA ratios: {target_sma_ratios}')
        sma_ratio_value = 0
        csv_filename = f'price-data/{coin_name}_price_data.csv'
        original_df = pd.read_csv(csv_filename, skiprows=0)
        current_price = original_df.loc[original_df.index.max()]['Spot']
        guess_price = current_price - current_price % price_step
        df = original_df.copy()
        df.loc[df.index.max() + 1] = [now_date, guess_price]
        current_sma_ratios = df['Spot']/df['Spot'].rolling(window=(sma_day_range + 1)).mean()
        current_sma_ratio = current_sma_ratios[current_sma_ratios.index.max()]
        print(f'Current price rounded down to nearest ${price_step}: ${guess_price}')
        print(f'Current SMA ratio: {current_sma_ratio}\n')

        all_target_sma_prices = []
        for target_sma_ratio in target_sma_ratios:
           while sma_ratio_value < target_sma_ratio:
               df = original_df.copy()
               # Drop existing NOW value so that the testing NOW value can take its place
               df.drop(df.tail(1).index,inplace=True)

               df.loc[df.index.max() + 1] = [now_date, guess_price]

               sma_values = df['Spot']/df['Spot'].rolling(window=(sma_day_range + 1)).mean()

               sma_ratio_value = sma_values[sma_values.index.max()]

               if target_sma_ratio <= sma_ratio_value:
                   print(f'{coin_name}: ${guess_price}: {sma_ratio_value}')
                   all_target_sma_prices.append([guess_price, sma_ratio_value])

               guess_price += price_step

        google_utils.write_target_sma_values(coin, all_target_sma_prices)
