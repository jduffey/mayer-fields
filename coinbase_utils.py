from datetime import datetime
import time

import requests
from coinbase.wallet.client import Client

import printer
import utils


coinbase_client = Client('<KEY_NOT_NEEDED>', '<SECRET_NOT_NEEDED>')
COINBASE_EXCHANGE_API_BASE = 'https://api.exchange.coinbase.com'
DAILY_GRANULARITY_SECONDS = 86400
RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BACKOFF_SECONDS = 0.5
REQUEST_TIMEOUT_SECONDS = 10


def get_current_price(currency_pair):
    return coinbase_client.get_spot_price(currency_pair=currency_pair)['amount']


def get_price_history(asset, quote, start_date, end_date):
    product_id = f'{asset}-{quote}'
    start_timestamp = f'{start_date}T00:00:00Z'
    end_timestamp = f'{end_date}T00:00:00Z'

    response, error = _fetch_candles(product_id, start_timestamp, end_timestamp)
    history = {'product': product_id, 'granularity': DAILY_GRANULARITY_SECONDS, 'candles': []}

    if error:
        history['error'] = error
        return history

    try:
        candles = response.json()
    except ValueError:
        history['error'] = {'status': response.status_code, 'message': 'Invalid JSON response'}
        return history

    if not candles:
        return history

    for candle in candles:
        # Coinbase Exchange candle format: [time, low, high, open, close, volume]
        time_epoch = candle[0]
        history['candles'].append({
            'date': datetime.utcfromtimestamp(time_epoch).strftime('%Y-%m-%d'),
            'time': time_epoch,
            'open': candle[3],
            'high': candle[2],
            'low': candle[1],
            'close': candle[4],
            'volume': candle[5],
        })

    history['candles'].sort(key=lambda entry: entry['time'])
    return history


def get_spot_price_for_date(currency_pair, date):
    asset, quote = currency_pair.split('-')
    end_date = utils.get_day_after(date)
    history = get_price_history(asset, quote, date, end_date)
    if history.get('error'):
        raise RuntimeError(f"Failed to fetch price data: {history['error']}")
    if not history['candles']:
        raise ValueError(f'No candle data available for {currency_pair} on {date}')
    if history['candles'][0]['date'] != date:
        raise ValueError(f'No candle data available for {currency_pair} on {date}')
    return history['candles'][0]['close']


def get_price_dict_for_dates(currency_pair, dates):
    dates_and_prices = {}
    for date in dates:
        price = get_spot_price_for_date(currency_pair, date)
        dates_and_prices[date] = price
        printer.date_and_price(date, price)
    return dates_and_prices


# TODO: The coinbase_utils-dependent parts of this method should be split out and the rest moved to utils.
# TODO: Need to pass in missing_price_dates and missing_price_data.
def update_price_data(price_data_csv, currency_pair, yesterday, current_price):
    most_recent_date_in_price_data = utils.get_most_recent_date(price_data_csv)
    if most_recent_date_in_price_data[0] == 'NOW':
        actual_most_recent_date = most_recent_date_in_price_data[1]
        utils.remove_last_row_from_csv(price_data_csv)
    else:
        actual_most_recent_date = most_recent_date_in_price_data[0]
    if actual_most_recent_date < yesterday:
        printer.gathering_missing_price_data(price_data_csv, actual_most_recent_date)
        day_after = utils.get_day_after(actual_most_recent_date)
        missing_price_dates = utils.get_date_range(day_after, yesterday)
        missing_price_data = get_price_dict_for_dates(currency_pair, missing_price_dates)
        utils.append_data_to_csv(price_data_csv, missing_price_data)
        printer.updated_price_data(price_data_csv, missing_price_data)
    else:
        printer.no_data_missing_from_price_data(price_data_csv, actual_most_recent_date, yesterday)

    coin = currency_pair[:3]
    printer.current_price(coin, current_price)
    with open(price_data_csv, 'a') as fd:
        fd.write(f'NOW,{current_price}')


def _fetch_candles(product_id, start_timestamp, end_timestamp):
    url = f'{COINBASE_EXCHANGE_API_BASE}/products/{product_id}/candles'
    params = {
        'start': start_timestamp,
        'end': end_timestamp,
        'granularity': DAILY_GRANULARITY_SECONDS,
    }
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as error:
            return None, {'message': 'Request failed', 'details': str(error)}

        if response.status_code == 200:
            return response, None

        if response.status_code in RETRY_STATUSES and attempt < MAX_RETRIES:
            time.sleep(BACKOFF_SECONDS * (2 ** attempt))
            continue

        return response, {
            'status': response.status_code,
            'message': 'Non-200 response',
            'body': response.text,
        }

    return None, {'message': 'Request retries exhausted'}
