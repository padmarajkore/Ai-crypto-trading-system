"""Freqtrade REST API wrappers exposed as ADK tools."""

import os
from typing import Any, Dict, Optional

from freqtrade_client import FtRestClient


class FreqtradeClientError(Exception):
    """Custom exception raised for Freqtrade client errors."""


def _get_client() -> FtRestClient:
    """Initialize and return the Freqtrade REST client."""
    try:
        username = os.environ["FREQTRADE_USERNAME"]
        password = os.environ["FREQTRADE_PASSWORD"]
    except KeyError as exc:
        raise FreqtradeClientError(f"Missing required env var: {exc.args[0]}") from exc

    # Default to 8081 if not set, as that's what we configured
    base_url = os.getenv("FREQTRADE_API_URL", "http://127.0.0.1:8081").rstrip("/")
    
    return FtRestClient(
        serverurl=base_url,
        username=username,
        password=password,
    )


def _safe_call(fn) -> Dict[str, Any]:
    try:
        result = fn()
        # If result is None or empty, return error
        if result is None:
            return {"status": "error", "message": "API returned None"}
        return result
    except Exception as exc:
        import traceback
        error_details = traceback.format_exc()
        return {
            "status": "error", 
            "message": f"{type(exc).__name__}: {str(exc)}",
            "details": error_details
        }


def freqtrade_ping() -> Dict[str, Any]:
    """Check connectivity to the Freqtrade bot."""
    client = _get_client()
    return _safe_call(client.ping)


def freqtrade_pause_bot() -> Dict[str, Any]:
    """Pause trading activity."""
    client = _get_client()
    # FtRestClient doesn't have a direct pause method, but it has stopbuy
    # Using stopbuy as a proxy for pausing new entries
    return _safe_call(client.stopbuy)


def freqtrade_resume_bot() -> Dict[str, Any]:
    """Resume trading activity."""
    client = _get_client()
    # FtRestClient uses reload_config to reset stopbuy
    return _safe_call(client.reload_config)


def freqtrade_stop_bot() -> Dict[str, Any]:
    """Stop the bot entirely."""
    client = _get_client()
    return _safe_call(client.stop)


def freqtrade_get_open_trades() -> Dict[str, Any]:
    """Fetch currently open trades."""
    client = _get_client()
    return _safe_call(client.status)


def freqtrade_get_balance() -> Dict[str, Any]:
    """Retrieve wallet balances."""
    client = _get_client()
    return _safe_call(client.balance)


def freqtrade_get_performance() -> Dict[str, Any]:
    """Return per-pair performance stats."""
    client = _get_client()
    return _safe_call(client.performance)


def freqtrade_force_enter(
    pair: str,
    side: str,
    rate: Optional[float] = None,
    amount: Optional[float] = None,
    enter_tag: Optional[str] = None
) -> Dict[str, Any]:
    """Force entering a trade via the REST API.

    Args:
        pair: Trading pair, e.g. "BTC/USDT"
        side: "long" or "short"
        rate: Optional limit price
        amount: Optional stake amount
        enter_tag: Optional descriptive tag
    """
    client = _get_client()
    return _safe_call(lambda: client.forceenter(
        pair=pair,
        side=side,
        price=rate,
        stake_amount=amount,
        enter_tag=enter_tag
    ))


def freqtrade_force_exit(
    tradeid: str,
    ordertype: str = "market",
    amount: Optional[float] = None
) -> Dict[str, Any]:
    """Force exit a trade.

    Args:
        tradeid: Trade ID to exit
        ordertype: "market" or "limit"
        amount: Optional amount to exit
    """
    client = _get_client()
    return _safe_call(lambda: client.forceexit(
        tradeid=tradeid,
        ordertype=ordertype,
        amount=amount
    ))


def freqtrade_get_klines(
    pair: str,
    timeframe: str,
    limit: int = 100
) -> Dict[str, Any]:
    """Fetch OHLCV data (candles) for a pair.

    Args:
        pair: Trading pair, e.g. "BTC/USDT"
        timeframe: Timeframe, e.g. "5m", "1h", "1d"
        limit: Number of candles to fetch (default 100)
    """
    client = _get_client()
    return _safe_call(lambda: client.pair_candles(
        pair=pair,
        timeframe=timeframe,
        limit=limit
    ))


def freqtrade_get_whitelist() -> Dict[str, Any]:
    """Get the list of whitelisted pairs."""
    client = _get_client()
    return _safe_call(client.whitelist)


def freqtrade_get_market_status() -> Dict[str, Any]:
    """Get the current market status (exchange status)."""
    client = _get_client()
    # Using health as a proxy for market status check
    return _safe_call(client.health)


def freqtrade_get_profit() -> Dict[str, Any]:
    """Get the bot's profit statistics."""
    client = _get_client()
    return _safe_call(client.profit)
