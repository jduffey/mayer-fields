import gspread
from oauth2client.service_account import ServiceAccountCredentials

import config
import google_utils

TEST_WORKBOOK = 'Mayer Fields Test'

google_client_secret = config.google_client_secret
google_client_scope = config.google_client_scope
creds = ServiceAccountCredentials.from_json_keyfile_name(google_client_secret, google_client_scope)
google_client = gspread.authorize(creds)


def reset_google_test_workbook():
    worksheet_name = 'test_sheet_1'
    worksheet = google_client.open(TEST_WORKBOOK).worksheet(worksheet_name)
    worksheet.clear()

    a1, b1 = 'a1', 'b1'
    a2, b2 = 'a2', 'b2'
    a3, b3 = 'a3', 'b3'
    values = [[a1, b1], [a2, b2], [a3, b3]]

    worksheet.update('A1:B3', values)


def test_get_list_of_dates_from_gsheet():
    reset_google_test_workbook()

    worksheet_name = 'test_sheet_1'

    actual = google_utils.get_list_of_dates_from_gsheet(TEST_WORKBOOK, worksheet_name)

    assert actual == ['a1', 'a2', 'a3']
