import config
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime, timezone
import printer
import utils
from time import sleep


workbook_name = config.google_workbook_name
google_client_secret = config.google_client_secret
google_client_scope = config.google_client_scope
creds = ServiceAccountCredentials.from_json_keyfile_name(google_client_secret, google_client_scope)
google_client = gspread.authorize(creds)


def get_list_of_dates_from_gsheet(workbook_name, worksheet_name):
    return google_client.open(workbook_name).worksheet(worksheet_name).col_values(1)


def get_list_of_col_name_from_gsheet(worksheet_name):
    return google_client.open(workbook_name).worksheet(worksheet_name).row_values(1)


def write_target_sma_values(coin, values):
    worksheet_name = f'{coin[0]}_Target_SMA'
    print(f'Updating values in {worksheet_name}...')
    worksheet = google_client.open(workbook_name).worksheet(worksheet_name)
    worksheet.clear()
    worksheet.update('A1:B14', values)


def write_time_updated(coin_name):
    worksheet_name = f'Dashboard{coin_name}'
    worksheet = google_client.open(workbook_name).worksheet(worksheet_name)
    utc_now = datetime.now(timezone.utc)
    utc_now_formatted = utc_now.strftime('%Y-%m-%d %H:%M:%S %p')
    current_time = [[f'Updated: {utc_now_formatted} UTC']]
    worksheet.update('A1', current_time)


def write_updating_notice(coin_name):
    worksheet_name = f'Dashboard{coin_name}'
    worksheet = google_client.open(workbook_name).worksheet(worksheet_name)
    utc_now = datetime.now(timezone.utc)
    utc_now_formatted = utc_now.strftime('%Y-%m-%d %H:%M:%S %p')
    current_time = [[f'Notice - Updating... {utc_now_formatted} UTC']]
    worksheet.update('A1', current_time)


def write_data_to_worksheet(csv_filename, worksheet_name, yesterday):
    data = utils.import_csv_as_list(csv_filename)
    worksheet = google_client.open(workbook_name).worksheet(worksheet_name)
    gsheet_col_names = get_list_of_col_name_from_gsheet(worksheet_name)

    printer.check_compatibility_of_price_data_with_worksheet(csv_filename, workbook_name)
    okay_to_upload = True
    for i in range(len(data[0])):
        if data[0][i] != gsheet_col_names[i]:
            okay_to_upload = False
            printer.data_differ_no_upload(data, gsheet_col_names, workbook_name)
            break

    if okay_to_upload:
        dates_from_gsheet = get_list_of_dates_from_gsheet(workbook_name, worksheet_name)
        if dates_from_gsheet[-1] == 'NOW':
            worksheet.delete_row(len(dates_from_gsheet))
            dates_from_gsheet = get_list_of_dates_from_gsheet(workbook_name, worksheet_name)
        most_recent_date_in_gsheet = dates_from_gsheet[-1]
        first_empty_row_index = len(dates_from_gsheet) + 1

        if most_recent_date_in_gsheet < yesterday:
            printer.most_recent_date_from_worksheet(worksheet_name, most_recent_date_in_gsheet)
            missing_gsheet_dates = utils.get_date_range(utils.get_day_after(most_recent_date_in_gsheet), yesterday)
            printer.writing_data_to_worksheet(worksheet_name)
            for missing_date in missing_gsheet_dates:
                for row in data:
                    if row[0] == missing_date:
                        formatted_row = utils.format_row(row)
                        print(formatted_row[0:2])
                        worksheet.insert_row(formatted_row, first_empty_row_index)
                        sleep(2) # don't anger the Google API gods
                        first_empty_row_index += 1
            # TODO: if price data cannot be retrieved and this step is allowed to continue
            #       it will still report that n records have been updated
            printer.updated_worksheet(worksheet_name, missing_gsheet_dates)
        else:
            printer.most_recent_date_in_worksheet_not_before_yesterday(worksheet_name, most_recent_date_in_gsheet, yesterday)

        price_now_row = utils.format_row(data[-1])
        worksheet.insert_row(price_now_row, first_empty_row_index)