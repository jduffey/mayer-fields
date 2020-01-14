import csv
from coinbase.wallet.client import Client
from utils import generate_mayer_values, generate_day_ratios,\
                  write_data_to_worksheet, get_yesterday,\
                  get_date_range, get_day_after
from config import price_data_csv, mayer_values_csv, day_ratios_csv,\
                   currency_pair

coinbase_client = Client('<KEY_NOT_NEEDED>', '<SECRET_NOT_NEEDED>')

def import_csv_as_list(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))

def get_most_recent_date(csv_filename):
    with open(csv_filename, 'r') as f:
        return list(csv.reader(f))[-1][0]

def get_spot_price_for_date(date):
    price_data = coinbase_client.get_spot_price(currency_pair = currency_pair, date = date)
    return price_data['amount']

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
    generate_day_ratios(price_data_csv, day_ratios_csv)

    write_data_to_worksheet(mayer_values_csv, "Mayer Multiples", yesterday)
    write_data_to_worksheet(day_ratios_csv, "Day Ratios", yesterday)
