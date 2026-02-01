from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List


@dataclass(frozen=True)
class TimeRange:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.start.tzinfo != timezone.utc or self.end.tzinfo != timezone.utc:
            raise ValueError('TimeRange start/end must be timezone-aware UTC datetimes')
        if self.end <= self.start:
            raise ValueError('TimeRange end must be after start')

    @classmethod
    def from_dates(cls, start_date: str, end_date: str) -> 'TimeRange':
        start = _parse_utc_midnight(start_date)
        end = _parse_utc_midnight(end_date)
        return cls(start=start, end=end)

    def start_iso(self) -> str:
        return _format_utc_iso(self.start)

    def end_iso(self) -> str:
        return _format_utc_iso(self.end)


@dataclass(frozen=True)
class Candle:
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    @property
    def date(self) -> str:
        return datetime.utcfromtimestamp(self.time).strftime('%Y-%m-%d')

    def to_dict(self) -> dict:
        return {
            'date': self.date,
            'time': self.time,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
        }


@dataclass(frozen=True)
class Series:
    asset: str
    quote: str
    granularity: int
    candles: List[Candle]

    def to_history(self) -> dict:
        return {
            'product': f'{self.asset}-{self.quote}',
            'granularity': self.granularity,
            'candles': [candle.to_dict() for candle in self.candles],
        }


def normalize_coinbase_candles(candles: Iterable[Iterable]) -> List[Candle]:
    normalized = []
    for index, candle in enumerate(candles):
        if not isinstance(candle, (list, tuple)) or len(candle) < 6:
            raise ValueError(f'Invalid candle format at index {index}: {candle}')
        try:
            time_epoch = int(candle[0])
            low = float(candle[1])
            high = float(candle[2])
            open_price = float(candle[3])
            close = float(candle[4])
            volume = float(candle[5])
        except (TypeError, ValueError) as error:
            raise ValueError(f'Invalid candle values at index {index}: {candle}') from error
        normalized.append(
            Candle(
                time=time_epoch,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
            )
        )
    normalized.sort(key=lambda entry: entry.time)
    return normalized


def _parse_utc_midnight(date_value: str) -> datetime:
    return datetime.strptime(date_value, '%Y-%m-%d').replace(tzinfo=timezone.utc)


def _format_utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
