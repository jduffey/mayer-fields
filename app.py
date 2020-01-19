import csv
import pandas as pd
from coinbase.wallet.client import Client
from utils import generate_mayer_values, generate_day_ratios,\
                  write_data_to_worksheet, get_yesterday,\
                  get_date_range, get_day_after
from config import BTC_price_data_csv, BTC_mayer_values_csv,\
                   BTC_day_ratios_csv, BTC_currency_pair,\
                   ETH_price_data_csv, ETH_mayer_values_csv,\
                   ETH_day_ratios_csv, ETH_currency_pair

coinbase_client = Client('<KEY_NOT_NEEDED>', '<SECRET_NOT_NEEDED>')

def import_csv_as_list(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))

def get_most_recent_date(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))[-1][0]

def get_spot_price_for_date(currency_pair, date):
    price_data = coinbase_client.get_spot_price(currency_pair=currency_pair, date = date)
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


if __name__ == '__main__':

    print()
    price_data_from_csv = import_csv_as_list(BTC_price_data_csv)
    most_recent_date_in_price_data = price_data_from_csv[-1][0]

    yesterday = get_yesterday()

    if most_recent_date_in_price_data == "NOW":
        most_recent_date_in_price_data = price_data_from_csv[-2][0]
        remove_last_row_from_csv(BTC_price_data_csv)

    if most_recent_date_in_price_data < yesterday:

        print(f'Most recent date in "{BTC_price_data_csv}": {most_recent_date_in_price_data}')
        print('Gathering missing price data...\n')

        missing_price_dates = get_date_range(get_day_after(most_recent_date_in_price_data), yesterday)

        missing_price_data = get_price_dict_for_dates(BTC_currency_pair, missing_price_dates)

        append_data_to_csv(BTC_price_data_csv, missing_price_data)
        print(f'Updated "{BTC_price_data_csv}" with {len(missing_price_data)} record(s).\n')

    else:
        print(f'Most recent date in "{BTC_price_data_csv}" ({most_recent_date_in_price_data}) ' + \
              f'is not before yesterday ({yesterday}); no data are missing.\n')

    now_price = coinbase_client.get_spot_price(currency_pair=BTC_currency_pair)['amount']
    print('BTC current: ${:,.2f}\n'.format(float(now_price)))
    with open(BTC_price_data_csv,'a') as fd:
        fd.write(f'NOW, {now_price}')

    generate_mayer_values(BTC_price_data_csv, BTC_mayer_values_csv)
    generate_day_ratios(BTC_price_data_csv, BTC_day_ratios_csv)

    write_data_to_worksheet(BTC_mayer_values_csv, "BTC Mayer Multiples", yesterday)
    write_data_to_worksheet(BTC_day_ratios_csv, "BTC Day Ratios", yesterday)


    # ETH below

    print()
    price_data_from_csv = import_csv_as_list(ETH_price_data_csv)
    most_recent_date_in_price_data = price_data_from_csv[-1][0]

    yesterday = get_yesterday()

    if most_recent_date_in_price_data == "NOW":
        most_recent_date_in_price_data = price_data_from_csv[-2][0]
        remove_last_row_from_csv(ETH_price_data_csv)

    if most_recent_date_in_price_data < yesterday:

        print(f'Most recent date in "{ETH_price_data_csv}": {most_recent_date_in_price_data}')
        print('Gathering missing price data...\n')

        missing_price_dates = get_date_range(get_day_after(most_recent_date_in_price_data), yesterday)

        missing_price_data = get_price_dict_for_dates(ETH_currency_pair, missing_price_dates)

        append_data_to_csv(ETH_price_data_csv, missing_price_data)
        print(f'Updated "{ETH_price_data_csv}" with {len(missing_price_data)} record(s).\n')

    else:
        print(f'Most recent date in "{ETH_price_data_csv}" ({most_recent_date_in_price_data}) ' + \
              f'is not before yesterday ({yesterday}); no data are missing.\n')

    now_price = coinbase_client.get_spot_price(currency_pair=ETH_currency_pair)['amount']
    print('ETH current: ${:,.2f}\n'.format(float(now_price)))
    with open(ETH_price_data_csv,'a') as fd:
        fd.write(f'NOW, {now_price}')

    generate_mayer_values(ETH_price_data_csv, ETH_mayer_values_csv)
    generate_day_ratios(ETH_price_data_csv, ETH_day_ratios_csv)

    write_data_to_worksheet(ETH_mayer_values_csv, "ETH Mayer Multiples", yesterday)
    write_data_to_worksheet(ETH_day_ratios_csv, "ETH Day Ratios", yesterday)
