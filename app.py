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
            printer.hint_vpn()


    target_sma_ratio = 2.4
    def find_mayer_price(coin):
        coin_name = coin[0]
        coin_jump = coin[1]
        now_date = 'NOW'
        now_price = 0
        sma200_value = 0

        while sma200_value < target_sma_ratio:
            csv_filename = f'price-data/{coin_name}_price_data.csv'

            df = pd.read_csv(csv_filename, skiprows=0, skipfooter=1)
            df.loc[df.index.max() + 1] = [now_date, now_price]

            sma200_values = df['Spot']/df['Spot'].rolling(window=(200 + 1)).mean()

            sma200_value = sma200_values[sma200_values.index.max()]

            now_price = now_price + coin_jump

        print(f'{coin_name}: ${now_price}: {sma200_value}')

    coins = [('BTC', 50), ('ETH', 5)]
    print(f'=== Price where SMA200 > {target_sma_ratio} ===')
    for coin in coins:
        find_mayer_price(coin)
