mayer_ranges = []
[mayer_ranges.append(i) for i in range(600, 1501, 50)]
[mayer_ranges.append(i) for i in range(300, 601, 10)]
[mayer_ranges.append(i) for i in range(50, 301, 5)]
[mayer_ranges.append(i) for i in range(20, 50, 2)]
[mayer_ranges.append(i) for i in range(1, 20, 1)]

day_ratio_ranges = []
[day_ratio_ranges.append(i) for i in range(1, 401)]

coins_info = [
    ['price-data/BTC_price_data.csv', 'output-data/BTC_mayer_values.csv',\
     'output-data/BTC_day_ratios.csv', 'BTC-USD',\
     'BTC Mayer Multiples', 'BTC Day Ratios'],
    ['price-data/ETH_price_data.csv', 'output-data/ETH_mayer_values.csv',\
     'output-data/ETH_day_ratios.csv', 'ETH-USD',\
     'ETH Mayer Multiples', 'ETH Day Ratios']\
]
