from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


DATE_FORMAT = '%Y-%m-%d'


def parse_utc_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, DATE_FORMAT).replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class TimeRange:
    start: datetime
    end: datetime

    def contains_epoch(self, epoch_seconds: int) -> bool:
        timestamp = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        return self.start <= timestamp < self.end


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
        return datetime.fromtimestamp(self.time, tz=timezone.utc).strftime(DATE_FORMAT)

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
