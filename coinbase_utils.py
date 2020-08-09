from coinbase.wallet.client import Client
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import printer
import utils


coinbase_client = Client('<KEY_NOT_NEEDED>', '<SECRET_NOT_NEEDED>')


def get_current_price(currency_pair):
    return coinbase_client.get_spot_price(currency_pair=currency_pair)['amount']


def get_spot_price_for_date(currency_pair, date):
    price_data = coinbase_client.get_spot_price(currency_pair=currency_pair, date=date)
    return price_data['amount']


def get_price_dict_for_dates(currency_pair, dates):
    dates_and_prices = {}
    for date in dates:
        price = get_spot_price_for_date(currency_pair, date)
        dates_and_prices[date] = price
        printer.date_and_price(date, price)
    return dates_and_prices


'''
The coinbase_utils-dependent parts of this method should be split out and the rest moved to utils.
Need to pass in missing_price_dates and missing_price_data.
'''
def update_price_data(price_data_csv, currency_pair, yesterday, now_price):
    most_recent_date_in_price_data = utils.get_most_recent_date(price_data_csv)
    if most_recent_date_in_price_data[0] == 'NOW':
        actual_most_recent_date = most_recent_date_in_price_data[1]
        utils.remove_last_row_from_csv(price_data_csv)
    else:
        actual_most_recent_date = most_recent_date_in_price_data[0]
        print(f'ACTUAL MOST RECENT DATE: {actual_most_recent_date}')
    if actual_most_recent_date < yesterday:
        printer.gathering_missing_price_data(price_data_csv, actual_most_recent_date)
        day_after = utils.get_day_after(actual_most_recent_date)
        print(f'DAY AFTER: {day_after}')
        missing_price_dates = utils.get_date_range(day_after, yesterday)
        print(f'MISSING PRICE DATES: {missing_price_dates}')
        # Move this line
        missing_price_data = get_price_dict_for_dates(currency_pair, missing_price_dates)
        utils.append_data_to_csv(price_data_csv, missing_price_data)
        printer.updated_price_data(price_data_csv, missing_price_data)
    else:
        printer.no_data_missing_from_price_data(price_data_csv, actual_most_recent_date, yesterday)

    coin = currency_pair[:3]
    printer.current_price(coin, now_price)
    with open(price_data_csv, 'a') as fd:
        fd.write(f'NOW,{now_price}')