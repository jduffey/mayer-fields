import coinbase_utils
import google_utils
import printer
import utils
from config import coin_vars
import sys

def update_target_mayer_value_price_and_updated_dashboard(coin_name):
    google_utils.write_updating_notice(coin_name)
    utils.find_mayer_prices(coin_name)
    google_utils.write_time_updated(coin_name)


if __name__ == '__main__':
    google_utils.format_sheets()
    sys.exit()

    yesterday = utils.get_yesterday()
    coins = ['BTC', 'ETH']

    for coin in coins:
        printer.initiating_workflow(coin)

        currency_pair = f'{coin}-USD'
        price_data = coin_vars[coin]['price_data']
        mayer_values = coin_vars[coin]['mayer_values']
        day_ratios = coin_vars[coin]['day_ratios']

        try:
            current_price = coinbase_utils.get_current_price(currency_pair)
            coinbase_utils.update_price_data(price_data, currency_pair, yesterday, current_price)
            utils.generate_mayer_values(price_data, mayer_values)
            utils.generate_day_ratios(price_data, day_ratios)
            google_utils.write_data_to_worksheet(mayer_values, coin_vars[coin]['gsheet_mayer_values'], yesterday)
            google_utils.write_data_to_worksheet(day_ratios, coin_vars[coin]['gsheet_day_ratios'], yesterday)
            update_target_mayer_value_price_and_updated_dashboard(coin)
        except Exception as error:
            printer.exception_encountered(error, coin)
            printer.hint_vpn()

