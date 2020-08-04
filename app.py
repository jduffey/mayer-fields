from config import coin_vars
import printer
import utils
import pandas as pd
import numpy as np


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

    target_sma_ratio_min = 2.4
    target_sma_ratio_step = 0.1
    target_sma_ratios = [target_sma_ratio_min + target_sma_ratio_step * x for x in range(11)]

    def find_mayer_price(coin):
        sma_pairs = [(200, [2.4 + 0.1 * x for x in range(11)]),
                     (30, [1.2, 1.3, 1.4])]
        coin_name = coin[0]
        coin_step = coin[1]

        now_date = 'NOW'

        for sma_pair in sma_pairs:
            sma_day_range = sma_pair[0]
            target_sma_ratios = sma_pair[1]
            print(f'\nSMA Day Range: {sma_day_range}')
            print(f'Target SMA ratios: {target_sma_ratios}')
            sma_ratio_value = 0
            csv_filename = f'price-data/{coin_name}_price_data.csv'
            original_df = pd.read_csv(csv_filename, skiprows=0)
            now_price = original_df.loc[original_df.index.max()]['Spot']
            now_price = now_price - now_price % coin_step
            df = original_df.copy()
            df.loc[df.index.max() + 1] = [now_date, now_price]
            current_sma_ratios = df['Spot']/df['Spot'].rolling(window=(sma_day_range + 1)).mean()
            current_sma_ratio = current_sma_ratios[current_sma_ratios.index.max()]
            print(f'Current price rounded down to nearest ${coin_step}: ${now_price}')
            print(f'Current SMA ratio: {current_sma_ratio}\n')

            for target_sma_ratio in target_sma_ratios:
                while sma_ratio_value < target_sma_ratio:
                    df = original_df.copy()

                    df.loc[df.index.max() + 1] = [now_date, now_price]

                    sma_values = df['Spot']/df['Spot'].rolling(window=(sma_day_range + 1)).mean()

                    sma_ratio_value = sma_values[sma_values.index.max()]

                    if target_sma_ratio <= sma_ratio_value:
                        print(f'{coin_name}: ${now_price}: {sma_ratio_value}')

                    now_price += coin_step

    coins = [('BTC', 10), ('ETH', 5)]
    for coin in coins:
        coin_name = coin[0]
        coin_step = coin[1]

        find_mayer_price(coin)

        reduce_percentages = np.arange(0.1, 0.51, 0.05).tolist()

        csv_filename = f'price-data/{coin_name}_price_data.csv'
        original_df = pd.read_csv(csv_filename, skiprows=0)
        now_price = original_df.loc[original_df.index.max()]['Spot']

        print(f'\n== Price reduced by %')
        for percentage in reduce_percentages:
            print(f'{int(percentage * 100)}%: ${now_price * (1 - percentage)}')
