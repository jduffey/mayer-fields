from datetime import timezone

import domain


def test_parse_utc_date_round_trip():
    parsed = domain.parse_utc_date('2021-01-01')

    assert parsed.tzinfo == timezone.utc
    assert parsed.strftime(domain.DATE_FORMAT) == '2021-01-01'


def test_time_range_contains_epoch():
    time_range = domain.TimeRange.from_dates('2021-01-01', '2021-01-03')

    assert time_range.contains_epoch(1609459200)
    assert not time_range.contains_epoch(1609632000)


def test_parse_coinbase_candles_valid_payload():
    payload = [
        [1609545600, 900.0, 1100.0, 950.0, 1000.0, 12.5],
        [1609459200, 800.0, 1000.0, 900.0, 950.0, 10.0],
    ]

    candles = domain.parse_coinbase_candles(payload)

    assert [candle.time for candle in candles] == [1609459200, 1609545600]
    assert candles[0].open == 900.0
    assert candles[0].high == 1000.0
    assert candles[0].low == 800.0
    assert candles[0].close == 950.0
    assert candles[0].volume == 10.0


def test_parse_coinbase_candles_invalid_payload():
    payload = [
        [1609459200, 800.0, 1000.0, 900.0, 950.0],
    ]

    try:
        domain.parse_coinbase_candles(payload)
        assert False, 'Expected ValueError for invalid candle payload'
    except ValueError as error:
        assert 'index 0' in str(error)
