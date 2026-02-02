from dataclasses import dataclass
from datetime import datetime, timezone
import math
import numbers
from typing import List

DATE_FORMAT = "%Y-%m-%d"
ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def parse_utc_date(date_str: str) -> datetime:
    try:
        parsed = datetime.strptime(date_str, DATE_FORMAT)
    except ValueError as exc:
        raise ValueError(f"Invalid date '{date_str}', expected format {DATE_FORMAT}") from exc
    return parsed.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class TimeRange:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo != timezone.utc or self.end.tzinfo != timezone.utc:
            raise ValueError("TimeRange start and end must be UTC datetimes")
        if self.end <= self.start:
            raise ValueError("TimeRange end must be after start")

    @classmethod
    def from_dates(cls, start_date: str, end_date: str) -> "TimeRange":
        return cls(start=parse_utc_date(start_date), end=parse_utc_date(end_date))

    def start_iso(self) -> str:
        return self.start.strftime(ISO_DATE_FORMAT)

    def end_iso(self) -> str:
        return self.end.strftime(ISO_DATE_FORMAT)

    def contains_epoch(self, epoch_seconds: int) -> bool:
        if isinstance(epoch_seconds, bool) or not isinstance(epoch_seconds, numbers.Real):
            raise ValueError("epoch_seconds must be a numeric timestamp")
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
            "date": self.date,
            "time": self.time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@dataclass(frozen=True)
class Series:
    asset: str
    quote: str
    granularity: int
    candles: List[Candle]

    @property
    def product(self) -> str:
        return f"{self.asset}-{self.quote}"

    def to_history(self) -> dict:
        return {
            "product": self.product,
            "granularity": self.granularity,
            "candles": [candle.to_dict() for candle in self.candles],
        }


def parse_coinbase_candles(payload) -> List[Candle]:
    if payload is None or not isinstance(payload, list):
        raise ValueError("Candle payload must be a list")

    candles = []
    for index, candle in enumerate(payload):
        if not isinstance(candle, (list, tuple)):
            raise ValueError(f"Candle at index {index} must be list-like")
        if len(candle) < 6:
            raise ValueError(f"Candle at index {index} must have 6 values")

        time_epoch, low, high, open_price, close, volume = candle[:6]
        time_epoch = _parse_epoch_seconds(time_epoch, index)
        low = _parse_numeric_value(low, "low", index)
        high = _parse_numeric_value(high, "high", index)
        open_price = _parse_numeric_value(open_price, "open", index)
        close = _parse_numeric_value(close, "close", index)
        volume = _parse_numeric_value(volume, "volume", index)

        candles.append(
            Candle(
                time=time_epoch,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
            )
        )

    candles.sort(key=lambda item: item.time)
    return candles


def _parse_epoch_seconds(value, index: int) -> int:
    epoch_value = _parse_numeric_value(value, "time", index)
    if not float(epoch_value).is_integer():
        raise ValueError(f"Candle at index {index} has non-integer epoch time")
    return int(epoch_value)


def _parse_numeric_value(value, label: str, index: int) -> float:
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(f"Candle at index {index} has non-numeric {label}")

    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValueError(f"Candle at index {index} has invalid {label}")
    return numeric_value
