def check_compatibility_of_price_data_with_worksheet(csv_filename, worksheet_name):
    print(f'Checking compatability of "{csv_filename}" with "{worksheet_name}"...\n')


def created_directory(output_data_dir):
    print(f'Creating "{output_data_dir}" directory.\n')


def created_file(output_file):
    print(f'Created "{output_file}".\n')


def current_price(coin, current_price):
    print(f'Current price of {coin}: '
           '${:,.2f}\n'.format(float(current_price)))


def data_differ_no_upload(data, gsheet_col_names, worksheet_name):
    print(f'Column names "{data[0][i]}" and "{gsheet_col_names[i]}" differ; '
          f'data will not be uploaded to "{worksheet_name}".\n')


def date_and_price(date, price):
    print(f'{date}: ${price}')


def exception_encountered(error, coin):
    print(f'!! EXCEPTION encountered while attempting workflow for {coin}:\n{error}\n')


def gathering_missing_price_data(price_data_csv, most_recent_date_in_price_data):
    print(f'Most recent date in "{price_data_csv}": {most_recent_date_in_price_data}\n'
          f'Gathering missing price data...\n')


def generating_day_ratios():
    print("Generating day ratios...")


def generating_mayer_values():
    print("Generating Mayer values...")


def initiating_workflow(coin):
    print(f'=== Initiating workflow for {coin} ===\n')


def most_recent_date_from_worksheet(worksheet_name, most_recent_date_in_gsheet):
    print(f'Most recent date from Google workbook "{worksheet_name}": {most_recent_date_in_gsheet}')


def most_recent_date_in_worksheet_not_before_yesterday(worksheet_name, most_recent_date_in_gsheet, yesterday):
    print(f'Most recent date in "{worksheet_name}" ({most_recent_date_in_gsheet}) '
          f'is not before yesterday ({yesterday}); no data are missing.\n')


def no_data_missing_from_price_data(price_data_csv, most_recent_date_in_price_data, yesterday):
    print(f'Most recent date in "{price_data_csv}" ({most_recent_date_in_price_data}) ' + \
              f'is not before yesterday ({yesterday}); no data are missing.\n')


def updated_price_data(price_data_csv, missing_price_data):
    print(f'Updated "{price_data_csv}" with {len(missing_price_data)} record(s).\n')


def updated_worksheet(worksheet_name, missing_gsheet_dates):
    print(f'Updated "{worksheet_name}" with {len(missing_gsheet_dates)} record(s).\n')


def writing_data_to_worksheet(worksheet_name):
    print(f'Writing missing data to "{worksheet_name}"...')


# TODO: Fix -- this is printing on exceptions not related to this hint
def hint_vpn():
    print(f'HINT: Are you on a VPN or attempting to connect from a deny-listed IP address?')
