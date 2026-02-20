"""
AuditAI - Price Feed Tool

Tool for fetching real-time token/cryptocurrency price data.
Uses public APIs (e.g., CoinGecko) to retrieve price information.
"""

from __future__ import annotations
from typing import Any
import httpx
from src.tools.base import BaseTool

class PriceFeedTool(BaseTool):
    """Fetches real-time cryptocurrency price data."""

    name = "price_feed"
    description = (
        "Fetches real-time price data for a cryptocurrency token. "
        "Input: {'token': 'bitcoin'} or {'token': 'ethereum'}. "
        "Returns current price, 24h change, market cap, and volume."
    )

    def __init__(self, api_url: str = "https://api.coingecko.com/api/v3") -> None:
        self.api_url = api_url

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Fetch price data for a given token.

        Args:
            input_data: Must contain 'token' key with the token ID.
                        e.g., {'token': 'bitcoin'}

        Returns:
            Price data including current price, change, market cap.
        """
        token = input_data.get("token", "").lower().strip()
        if not token:
            raise ValueError("Missing 'token' in input_data")

        currency = input_data.get("currency", "usd").lower()

        try:
            response = httpx.get(
                f"{self.api_url}/simple/price",
                params={
                    "ids": token,
                    "vs_currencies": currency,
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            if token not in data:
                raise ValueError(f"Token '{token}' not found")

            token_data = data[token]
            return {
                "token": token,
                "currency": currency,
                "price": token_data.get(f"{currency}"),
                "price_change_24h_pct": token_data.get(f"{currency}_24h_change"),
                "market_cap": token_data.get(f"{currency}_market_cap"),
                "volume_24h": token_data.get(f"{currency}_24h_vol"),
            }

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch price data: {e}") from e
