import csv
import pandas
from coinbase.wallet.client import Client

from utils import generate_mayer_values, write_data_to_worksheet, get_yesterday
from time import sleep

# Local settings
price_data_csv = 'price_data.csv'
mayer_values_csv = 'output-data/mayer_values.csv'
day_ratios_csv = 'output-data/day_ratios.csv'

# Coinbase settings
coinbase_client = Client('<KEY_NOT_NEEDED>', '<SECRET_NOT_NEEDED>') # key/secret not needed for get_spot_price()
currency_pair = 'BTC-USD'

def import_csv_as_list(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))

def get_most_recent_date(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))[-1][0]

def get_spot_price_for_date(date):
    price_data = coinbase_client.get_spot_price(currency_pair = currency_pair, date = date)
    return price_data['amount']

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

    worksheet_name = "Mayer Multiples"
    # mayer_values_from_csv = import_csv_as_list(mayer_values_csv)

    write_data_to_worksheet(mayer_values_csv, worksheet_name, yesterday)
