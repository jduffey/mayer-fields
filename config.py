mayer_ranges = []
[mayer_ranges.append(i) for i in range(600, 1501, 50)]
[mayer_ranges.append(i) for i in range(300, 601, 10)]
[mayer_ranges.append(i) for i in range(50, 301, 5)]
[mayer_ranges.append(i) for i in range(20, 50, 2)]
[mayer_ranges.append(i) for i in range(1, 20, 1)]

day_ratio_ranges = []
[day_ratio_ranges.append(i) for i in range(1, 401)]

coin_vars = {
    'BTC': {
        'price_data': 'price-data/BTC_price_data.csv',
        'mayer_values': 'output-data/BTC_mayer_values.csv',
        'day_ratios': 'output-data/BTC_day_ratios.csv',
        'currency_pair': 'BTC-USD',
        'gsheet_mayer_values': 'BTC Mayer Multiples',
        'gsheet_day_ratios': 'BTC Day Ratios'
    },
    'ETH': {
        'price_data': 'price-data/ETH_price_data.csv',
        'mayer_values': 'output-data/ETH_mayer_values.csv',
        'day_ratios': 'output-data/ETH_day_ratios.csv',
        'currency_pair': 'ETH-USD',
        'gsheet_mayer_values': 'ETH Mayer Multiples',
        'gsheet_day_ratios': 'ETH Day Ratios'
    }
}
