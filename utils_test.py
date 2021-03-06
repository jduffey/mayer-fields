import os
import re
import uuid
from datetime import date, datetime

import pandas as pd

import utils


sandbox_csv = 'test_sandbox.csv'


def test_import_csv_as_list():
    actual = utils.import_csv_as_list('price_data_test.csv')

    assert len(actual) == 3671
    assert actual[0] == ['Date', 'Spot']
    assert actual[-1] == ['NOW', '11126.525']


def test_get_yesterday():
    date_pattern = re.compile('[\\d]{4}-[\\d]{2}-[\\d]{2}')
    today = datetime.strftime(datetime.now(), '%Y-%m-%d')

    actual = utils.get_yesterday()

    tod = today.split('-')
    yst = actual.split('-')
    d0 = date(int(tod[0]), int(tod[1]), int(tod[2]))
    d1 = date(int(yst[0]), int(yst[1]), int(yst[2]))
    delta = d1 - d0

    assert delta.days == -1
    assert date_pattern.match(actual)


def test_get_date_range():
    start_date = '2020-02-28'
    end_date = '2020-03-01'

    assert utils.get_date_range(start_date, end_date) == ['2020-02-28', '2020-02-29', '2020-03-01']


def test_get_day_after():
    assert utils.get_day_after('2009-01-03') == '2009-01-04'
    assert utils.get_day_after('2020-02-28') == '2020-02-29'
    assert utils.get_day_after('2020-12-31') == '2021-01-01'


def test_format_row():
    unformatted_row = ['2020-08-01', '1234567.12345', '1.2345', '']
    expected = ['2020-08-01', '$1,234,567.12', 1.2345, '']

    assert utils.format_row(unformatted_row) == expected


def test_create_output_dir():
    dir_name = uuid.uuid4()
    test_dir = f'{dir_name}/'

    utils.create_output_dir(test_dir)

    if os.path.isdir(test_dir):
        os.removedirs(test_dir)
    else:
        assert os.path.isdir(test_dir)


# TODO: this tests the csv was created, need a test/method to verify values are correct(???)
# or need to extract the actual calculation part of the method?
def test_generate_mayer_values():
    source_file = 'price_data_test.csv'
    output_file = 'expected_mayer_values.csv'

    utils.generate_mayer_values(source_file, output_file)

    actual = utils.import_csv_as_list(output_file)

    assert len(actual) == 3671
    assert actual[0][0] == 'Date'
    assert actual[0][134] == 'Mayer_1'
    assert actual[3670][0] == 'NOW'
    assert actual[3670][134] == '0.9787'


def test_get_most_recent_date():
    assert utils.get_most_recent_date('price_data_test.csv') == tuple(['NOW', '2020-08-01'])
    assert utils.get_most_recent_date('price_data_test_2.csv') == tuple(['2010-07-17'])


def test_find_target_sma_ratio_price():
    prev_daily_prices = [10, 10, 10]
    target_sma_ratio = 2.4

    actual = utils.find_target_sma_ratio_price(prev_daily_prices, target_sma_ratio)

    assert actual == 45


def test_get_previous_prices_for_sma_range():
    sma_range = 200
    data = [x for x in range(1, sma_range + 1)]
    df = pd.DataFrame(data, columns=['Spot'])

    actual = utils.get_previous_prices_for_sma_range(df, sma_range)

    assert actual == [x for x in range(1, sma_range)]


def test_append_data_to_csv():
    key = str(uuid.uuid4())
    val = str(uuid.uuid4())
    data = {key: val}

    utils.append_data_to_csv(sandbox_csv, data)

    actual = utils.import_csv_as_list(sandbox_csv)

    assert actual[-1][0] == key
    assert actual[-1][1] == val

    reset_sandbox_csv()


def test_remove_last_row_from_csv():
    utils.remove_last_row_from_csv(sandbox_csv)

    actual = utils.import_csv_as_list(sandbox_csv)

    assert len(actual) == 1
    assert actual[0] == ['KEY', 'VALUE']

    reset_sandbox_csv()


def reset_sandbox_csv():
    os.remove(sandbox_csv)
    with open(sandbox_csv, 'a') as f:
        f.write('KEY,VALUE\n')
        f.write('a,b\n')
