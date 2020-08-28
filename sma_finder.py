import pandas as pd
import utils


def find_mayer_price(coin):
    sma_pairs = [(200, [2.4 + 0.1 * x for x in range(11)])]
    coin_name = coin[0]
    now_date = 'NOW'
    csv_filename = f'price-data/{coin_name}_price_data.csv'
    original_df = pd.read_csv(csv_filename, skiprows=0)

    for sma_pair in sma_pairs:
        sma_day_range = sma_pair[0]
        target_sma_ratios = sma_pair[1]
        print(f'\nSMA Day Range: {sma_day_range}\n--------------')
        print(f'Target SMA ratios: {target_sma_ratios}')
        sma_ratio_value = 0

        current_price = original_df.loc[original_df.index.max()]['Spot']
        # Set initial guess price higher than would be realistic for highest target sma_ratio
        original_guess_price = current_price * 10

        all_target_sma_prices = []
        for target_sma_ratio in target_sma_ratios:
            guess_price = original_guess_price
            guess_step = original_guess_price / 2
            while abs(target_sma_ratio - sma_ratio_value) > 0.00001:
                df = original_df.copy() # Reset df
                add_guess_price_to_df(df, now_date, guess_price)

                sma_ratio_value = get_sma_ratio_value(df, sma_day_range)

                if sma_ratio_value > target_sma_ratio:
                    guess_price = guess_price - guess_step
                else:
                    guess_price = guess_price + guess_step
                guess_step = guess_step / 2
            print(f'{guess_price}: {sma_ratio_value}')
            all_target_sma_prices.append([guess_price, sma_ratio_value])

        print(all_target_sma_prices)


def get_sma_ratio_value(df, sma_day_range):
    sma_values = df['Spot']/df['Spot'].rolling(window=(sma_day_range + 1)).mean()
    return sma_values[sma_values.index.max()]


def add_guess_price_to_df(df, now_date, guess_price):
    df.loc[df.index.max() + 1] = [now_date, guess_price]


def get_current_sma_ratio(df, sma_day_range):
    current_sma_ratios = df['Spot']/df['Spot'].rolling(window=(sma_day_range + 1)).mean()
    return current_sma_ratios[current_sma_ratios.index.max()]


coins = [('BTC', 10)]
for coin in coins:
    coin_name = coin[0]
    find_mayer_price(coin)
