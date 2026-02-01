import coinbase_utils


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
