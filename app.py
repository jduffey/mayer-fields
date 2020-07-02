from config import coin_vars
import printer
import utils


if __name__ == '__main__':

    yesterday = utils.get_yesterday()

    coins = ['BTC', 'ETH']
    for coin in coins:
        printer.initiating_workflow(coin)

        price_data = coin_vars[coin]['price_data']
        currency_pair = coin_vars[coin]['currency_pair']
        mayer_values = coin_vars[coin]['mayer_values']
        day_ratios = coin_vars[coin]['day_ratios']

        try:
            utils.update_price_data(price_data, coin, currency_pair, yesterday)
            utils.generate_mayer_values(price_data, mayer_values)
            utils.generate_day_ratios(price_data, day_ratios)
            utils.write_data_to_worksheet(mayer_values, coin_vars[coin]['gsheet_mayer_values'], yesterday)
            utils.write_data_to_worksheet(day_ratios, coin_vars[coin]['gsheet_day_ratios'], yesterday)
        except Exception as error:
            printer.exception_encountered(error, coin)
