import coinbase_utils
import domain


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


def test_get_price_history_parses_and_sorts(monkeypatch):
    candles = [
        [1609545600, 900.0, 1100.0, 950.0, 1000.0, 12.5],
        [1609459200, 800.0, 1000.0, 900.0, 950.0, 10.0],
    ]

    def fake_get(url, params, timeout):
        return FakeResponse(200, candles)

    monkeypatch.setattr(coinbase_utils.requests, 'get', fake_get)

    history = coinbase_utils.get_price_history('BTC', 'USD', '2021-01-01', '2021-01-03')

    assert history['product'] == 'BTC-USD'
    assert history['granularity'] == coinbase_utils.DAILY_GRANULARITY_SECONDS
    assert [entry['time'] for entry in history['candles']] == [1609459200, 1609545600]
    assert history['candles'][0]['date'] == '2021-01-01'
    assert history['candles'][0]['open'] == 900.0
    assert history['candles'][0]['high'] == 1000.0
    assert history['candles'][0]['low'] == 800.0
    assert history['candles'][0]['close'] == 950.0
    assert history['candles'][0]['volume'] == 10.0


def test_get_price_history_builds_day_boundary_params(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured['url'] = url
        captured['params'] = params
        return FakeResponse(200, [])

    monkeypatch.setattr(coinbase_utils.requests, 'get', fake_get)

    coinbase_utils.get_price_history('BTC', 'USD', '2017-01-01', '2017-01-02')

    assert captured['url'].endswith('/products/BTC-USD/candles')
    assert captured['params'] == {
        'start': '2017-01-01T00:00:00Z',
        'end': '2017-01-02T00:00:00Z',
        'granularity': coinbase_utils.DAILY_GRANULARITY_SECONDS,
    }


def test_get_price_history_empty_results(monkeypatch):
    monkeypatch.setattr(
        coinbase_utils.requests,
        'get',
        lambda url, params, timeout: FakeResponse(200, []),
    )

    history = coinbase_utils.get_price_history('ETH', 'USD', '2021-02-01', '2021-02-02')

    assert history['candles'] == []
    assert history.get('error') is None


def test_get_price_history_non_200(monkeypatch):
    call_count = {'count': 0}

    def fake_get(url, params, timeout):
        call_count['count'] += 1
        return FakeResponse(500, {'message': 'server error'})

    monkeypatch.setattr(coinbase_utils.requests, 'get', fake_get)
    monkeypatch.setattr(coinbase_utils.time, 'sleep', lambda *_: None)

    history = coinbase_utils.get_price_history('BTC', 'USD', '2020-01-01', '2020-01-02')

    assert history['error']['status'] == 500
    assert call_count['count'] == coinbase_utils.MAX_RETRIES + 1


def test_get_price_history_invalid_candle_payload(monkeypatch):
    def fake_get(url, params, timeout):
        return FakeResponse(200, [[1609545600, 900.0]])

    monkeypatch.setattr(coinbase_utils.requests, 'get', fake_get)

    history = coinbase_utils.get_price_history('BTC', 'USD', '2021-01-01', '2021-01-02')

    assert history['candles'] == []
    assert 'Invalid candle format' in history['error']['message']


def test_fetch_candles_retries_on_request_exception(monkeypatch):
    call_count = {'count': 0}

    def fake_get(url, params, timeout):
        call_count['count'] += 1
        raise coinbase_utils.requests.RequestException('boom')

    monkeypatch.setattr(coinbase_utils.requests, 'get', fake_get)
    monkeypatch.setattr(coinbase_utils.time, 'sleep', lambda *_: None)

    response, error = coinbase_utils._fetch_candles('BTC-USD', '2021-01-01T00:00:00Z', '2021-01-02T00:00:00Z')

    assert response is None
    assert error['message'] == 'Request failed'
    assert call_count['count'] == coinbase_utils.MAX_RETRIES + 1


def test_get_spot_price_for_date_mismatched_candle_date(monkeypatch):
    def fake_get_price_history(asset, quote, start_date, end_date):
        return {
            'product': f'{asset}-{quote}',
            'granularity': coinbase_utils.DAILY_GRANULARITY_SECONDS,
            'candles': [
                {
                    'date': '2020-01-02',
                    'time': 1577923200,
                    'open': 1,
                    'high': 2,
                    'low': 0.5,
                    'close': 1.5,
                    'volume': 100,
                }
            ],
        }

    monkeypatch.setattr(coinbase_utils, 'get_price_history', fake_get_price_history)

    try:
        coinbase_utils.get_spot_price_for_date('BTC-USD', '2020-01-01')
        assert False, 'Expected ValueError for mismatched candle date'
    except ValueError as error:
        assert 'No candle data available' in str(error)


def test_normalize_coinbase_candles_sorted():
    candles = [
        [1609545600, 900.0, 1100.0, 950.0, 1000.0, 12.5],
        [1609459200, 800.0, 1000.0, 900.0, 950.0, 10.0],
    ]

    normalized = domain.normalize_coinbase_candles(candles)

    assert [entry.time for entry in normalized] == [1609459200, 1609545600]
