import utils

from datetime import date
from datetime import datetime
import re


def test_import_csv_as_list():
    actual = utils.import_csv_as_list('price_data_test.csv')

    assert len(actual) == 3671
    assert actual[0] == ['Date', 'Spot']
    assert actual[-1] == ['NOW', '11126.525']


def test_get_yesterday():
    pattern = re.compile('[\\d]{4}-[\\d]{2}-[\\d]{2}')
    today = datetime.strftime(datetime.now(), '%Y-%m-%d')

    actual = utils.get_yesterday()

    t = today.split('-')
    a = actual.split('-')
    d0 = date(int(t[0]), int(t[1]), int(t[2]))
    d1 = date(int(a[0]), int(a[1]), int(a[2]))
    delta = d1 - d0

    assert delta.days == -1
    assert pattern.match(actual)
