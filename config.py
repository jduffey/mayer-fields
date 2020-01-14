mayer_ranges = []
[mayer_ranges.append(i) for i in range(600, 1501, 50)]
[mayer_ranges.append(i) for i in range(300, 601, 10)]
[mayer_ranges.append(i) for i in range(50, 301, 5)]
[mayer_ranges.append(i) for i in range(20, 50, 2)]
[mayer_ranges.append(i) for i in range(1, 20, 1)]

day_ratio_ranges = []
[day_ratio_ranges.append(i) for i in range(1, 401)]

price_data_csv = 'price_data.csv'
mayer_values_csv = 'output-data/mayer_values.csv'
day_ratios_csv = 'output-data/day_ratios.csv'

currency_pair = 'BTC-USD'
