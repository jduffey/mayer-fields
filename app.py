from config import coin_vars
import printer
import utils
import pandas as pd
import numpy as np
import coinbase_utils
import google_utils


if __name__ == '__main__':

    yesterday = utils.get_yesterday()
    coins = [('BTC', 5), ('ETH', 1)]

    for coin in coins:
        coin_name = coin[0]
        printer.initiating_workflow(coin_name)

        currency_pair = f'{coin_name}-USD'
        price_data = coin_vars[coin_name]['price_data']
        mayer_values = coin_vars[coin_name]['mayer_values']
        day_ratios = coin_vars[coin_name]['day_ratios']

        try:
            current_price = coinbase_utils.get_current_price(currency_pair)
            coinbase_utils.update_price_data(price_data, currency_pair, yesterday, current_price)
            utils.generate_mayer_values(price_data, mayer_values)
            utils.generate_day_ratios(price_data, day_ratios)
            google_utils.write_data_to_worksheet(mayer_values, coin_vars[coin_name]['gsheet_mayer_values'], yesterday)
            google_utils.write_data_to_worksheet(day_ratios, coin_vars[coin_name]['gsheet_day_ratios'], yesterday)
        except Exception as error:
            printer.exception_encountered(error, coin_name)
            printer.hint_vpn()

    target_sma_ratio_min = 2.4
    target_sma_ratio_step = 0.1
    target_sma_ratios = [target_sma_ratio_min + target_sma_ratio_step * x for x in range(11)]

    for coin in coins:
        utils.find_mayer_prices(coin)
        google_utils.write_time_updated(coin[0])
