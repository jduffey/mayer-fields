mayer_ranges = []
[mayer_ranges.append(i) for i in range(600, 1501, 50)]
[mayer_ranges.append(i) for i in range(300, 601, 10)]
[mayer_ranges.append(i) for i in range(50, 301, 5)]
[mayer_ranges.append(i) for i in range(20, 50, 2)]
[mayer_ranges.append(i) for i in range(1, 20, 1)]

day_ratio_ranges = []
[day_ratio_ranges.append(i) for i in range(1, 401)]

output_data_dir = "output-data/"
price_data_dir = "price-data/"

coins = ['BTC', 'ETH']

coin_vars = {}
for coin in coins:
    coin_vars.update(
        {coin : {
            'price_data': f'{price_data_dir}{coin}_price_data.csv',
            'mayer_values': f'{output_data_dir}{coin}_mayer_values.csv',
            'day_ratios': f'{output_data_dir}{coin}_day_ratios.csv',
            'gsheet_mayer_values': f'{coin} Mayer Multiples',
            'gsheet_day_ratios': f'{coin} Day Ratios'
        }
    })
