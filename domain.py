from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class TimeRange:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError('TimeRange boundaries must be timezone-aware (UTC).')
        if self.end <= self.start:
            raise ValueError('TimeRange end must be after start.')


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
        return datetime.fromtimestamp(self.time, tz=timezone.utc).strftime('%Y-%m-%d')

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

    def sorted(self) -> 'Series':
        return Series(
            asset=self.asset,
            quote=self.quote,
            granularity=self.granularity,
            candles=sorted(self.candles, key=lambda candle: candle.time),
        )

    def to_dict(self) -> dict:
        return {
            'product': f'{self.asset}-{self.quote}',
            'granularity': self.granularity,
            'candles': [candle.to_dict() for candle in self.candles],
        }


def parse_coinbase_candles(payload: Iterable[Sequence[float]]) -> List[Candle]:
    candles: List[Candle] = []
    for entry in payload:
        if entry is None or len(entry) < 6:
            continue
        time_epoch, low, high, open_, close, volume = entry[:6]
        candles.append(
            Candle(
                time=int(time_epoch),
                open=float(open_),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=float(volume),
            )
        )
    return candles
