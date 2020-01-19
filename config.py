mayer_ranges = []
[mayer_ranges.append(i) for i in range(600, 1501, 50)]
[mayer_ranges.append(i) for i in range(300, 601, 10)]
[mayer_ranges.append(i) for i in range(50, 301, 5)]
[mayer_ranges.append(i) for i in range(20, 50, 2)]
[mayer_ranges.append(i) for i in range(1, 20, 1)]

day_ratio_ranges = []
[day_ratio_ranges.append(i) for i in range(1, 401)]

BTC_price_data_csv = 'BTC_price_data.csv'
BTC_mayer_values_csv = 'output-data/BTC_mayer_values.csv'
BTC_day_ratios_csv = 'output-data/BTC_day_ratios.csv'
BTC_currency_pair = 'BTC-USD'

ETH_price_data_csv = 'ETH_price_data.csv'
ETH_mayer_values_csv = 'output-data/ETH_mayer_values.csv'
ETH_day_ratios_csv = 'output-data/ETH_day_ratios.csv'
ETH_currency_pair = 'ETH-USD'
