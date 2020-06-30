import csv
import pandas as pd
from coinbase.wallet.client import Client
from utils import generate_mayer_values, generate_day_ratios,\
                  write_data_to_worksheet, get_yesterday,\
                  get_date_range, get_day_after
from config import coin_vars

coinbase_client = Client('<KEY_NOT_NEEDED>', '<SECRET_NOT_NEEDED>')


def import_csv_as_list(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))


def get_most_recent_date(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))[-1][0]


def get_spot_price_for_date(currency_pair, date):
    price_data = coinbase_client.get_spot_price(currency_pair=currency_pair, date=date)
    return price_data['amount']


def get_price_dict_for_dates(currency_pair, dates):
    dates_and_prices = {}
    for date in dates:
        price = get_spot_price_for_date(currency_pair, date)
        dates_and_prices[date] = price
        print(f'{date}: ${price}')
    print()
    return dates_and_prices


def append_data_to_csv(csv_filename, data):
    with open(csv_filename, 'a') as f:
        for key in data.keys():
            f.write("%s,%s\n"%(key, data[key]))


def remove_last_row_from_csv(csv_filename):
    df = pd.read_csv(csv_filename, skiprows=0)
    df.drop(df.tail(1).index,inplace=True)
    df.to_csv(csv_filename, index=False)


def update_price_data(price_data_csv, currency_pair, yesterday):
    price_data_from_csv = import_csv_as_list(price_data_csv)
    most_recent_date_in_price_data = price_data_from_csv[-1][0]
    if most_recent_date_in_price_data == "NOW":
        most_recent_date_in_price_data = price_data_from_csv[-2][0]
        remove_last_row_from_csv(price_data_csv)
    if most_recent_date_in_price_data < yesterday:
        print(f'Most recent date in "{price_data_csv}": {most_recent_date_in_price_data}')
        print('Gathering missing price data...\n')
        missing_price_dates = get_date_range(get_day_after(most_recent_date_in_price_data), yesterday)
        missing_price_data = get_price_dict_for_dates(currency_pair, missing_price_dates)
        append_data_to_csv(price_data_csv, missing_price_data)
        print(f'Updated "{price_data_csv}" with {len(missing_price_data)} record(s).\n')
    else:
        print(f'Most recent date in "{price_data_csv}" ({most_recent_date_in_price_data}) ' + \
              f'is not before yesterday ({yesterday}); no data are missing.\n')
    now_price = coinbase_client.get_spot_price(currency_pair=currency_pair)['amount']
    print('Current: ${:,.2f}\n'.format(float(now_price)))
    with open(price_data_csv,'a') as fd:
        fd.write(f'NOW, {now_price}')


if __name__ == '__main__':

    yesterday = get_yesterday()

    coins = ['BTC', 'ETH']
    for coin in coins:
        price_data = coin_vars[coin]['price_data']
        currency_pair = coin_vars[coin]['currency_pair']
        mayer_values = coin_vars[coin]['mayer_values']
        day_ratios = coin_vars[coin]['day_ratios']

        try:
            update_price_data(price_data, currency_pair, yesterday)
            generate_mayer_values(price_data, mayer_values)
            generate_day_ratios(price_data, day_ratios)
            write_data_to_worksheet(mayer_values, coin_vars[coin]['gsheet_mayer_values'], yesterday)
            write_data_to_worksheet(day_ratios, coin_vars[coin]['gsheet_day_ratios'], yesterday)
        except Exception as error:
            print(f'!! EXCEPTION encountered while attempting workflow for {coin}:\n{error}\n')
