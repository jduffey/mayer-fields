import utils

from datetime import date, datetime, timedelta
import re


date_pattern = re.compile('[\\d]{4}-[\\d]{2}-[\\d]{2}')


def test_import_csv_as_list():
    actual = utils.import_csv_as_list('price_data_test.csv')

    assert len(actual) == 3671
    assert actual[0] == ['Date', 'Spot']
    assert actual[-1] == ['NOW', '11126.525']


def test_get_yesterday():
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

    actual = utils.get_date_range(start_date, end_date)

    assert actual == ['2020-02-28', '2020-02-29', '2020-03-01']


def test_get_day_after():
    assert utils.get_day_after('2009-01-03') == '2009-01-04'
    assert utils.get_day_after('2020-02-28') == '2020-02-29'
    assert utils.get_day_after('2020-12-31') == '2021-01-01'


def test_format_row():
    unformatted_row = ['2020-08-01', '1234567.12345', '1.2345', '']
    expected = ['2020-08-01', '$1,234,567.12', 1.2345, '']

    assert utils.format_row(unformatted_row) == expected