from config import coin_vars
import printer
import utils
import pandas as pd


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


    def find_mayer_price():
        now_date = 'NOW'
        now_price = 0
        sma200_value = 0
        target_sma_ratio = 2.4
        price_jump = 100

        while sma200_value < target_sma_ratio:
            csv_filename = 'price-data/BTC_price_data.csv'

            df = pd.read_csv(csv_filename, skiprows=0, skipfooter=1)
            df.loc[df.index.max() + 1] = [now_date, now_price]

            sma200_values = df['Spot']/df['Spot'].rolling(window=(200 + 1)).mean()

            sma200_value = sma200_values[sma200_values.index.max()]

            print(f'${now_price}: {sma200_value}')

            now_price = now_price + price_jump

    find_mayer_price()