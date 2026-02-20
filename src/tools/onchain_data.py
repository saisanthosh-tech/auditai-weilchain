"""
AuditAI - On-Chain Data Tool

Tool for querying on-chain data from the Weilchain blockchain.
Retrieves information such as wallet balances, transaction history,
applet data, and blockchain stats.
"""

from __future__ import annotations
from typing import Any
# Uncomment when Weilchain/Weilliptic SDK becomes available
# import weilliptic

from src.tools.base import BaseTool

class OnchainDataTool(BaseTool):
    """Queries on-chain data from the Weilchain blockchain."""

    name = "onchain_data"
    description = (
        "Queries on-chain data from the Weilchain blockchain. "
        "Input: {'query_type': 'balance', 'address': '0x...'} or "
        "{'query_type': 'transaction', 'tx_hash': '0x...'}. "
        "Returns blockchain data such as balances, transactions, and applet info."
    )

    def __init__(self, rpc_url: str | None = None) -> None:
        self.rpc_url = rpc_url
        # TODO: Initialize Weilchain RPC client (when SDK available)
        # self.client = weilliptic.Client(rpc_url=self.rpc_url)

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Query on-chain data based on the query type.

        Args:
            input_data: Must contain 'query_type' key.
                Supported types:
                - 'balance': Get wallet balance. Requires 'address'.
                - 'transaction': Get transaction details. Requires 'tx_hash'.
                - 'applet_info': Get applet details. Requires 'applet_id'.
                - 'block': Get block info. Requires 'block_number'.

        Returns:
            On-chain data based on the query type.
        """
        query_type = input_data.get("query_type", "").strip()
        if not query_type:
            raise ValueError("Missing 'query_type' in input_data")

        handlers = {
            "balance": self._get_balance,
            "transaction": self._get_transaction,
            "applet_info": self._get_applet_info,
            "block": self._get_block,
        }
        handler = handlers.get(query_type)
        if handler is None:
            raise ValueError(
                f"Unknown query_type: '{query_type}'. "
                f"Supported: {list(handlers.keys())}"
            )
        return handler(input_data)

    def _get_balance(self, input_data: dict[str, Any]) -> dict[str, Any]:
        address = input_data.get("address", "").strip()
        if not address:
            raise ValueError("Missing 'address' for balance query")

        # TODO: Implement actual balance fetch once SDK is available
        # balance = self.client.get_balance(address)
        # return {"address": address, "balance": balance, "currency": "WUSD"}
        return {
            "address": address,
            "balance": None,
            "currency": "WUSD",
            "note": "Weilchain SDK integration pending",
        }

    def _get_transaction(self, input_data: dict[str, Any]) -> dict[str, Any]:
        tx_hash = input_data.get("tx_hash", "").strip()
        if not tx_hash:
            raise ValueError("Missing 'tx_hash' for transaction query")

        # TODO: Implement actual transaction details fetch
        return {
            "tx_hash": tx_hash,
            "details": None,
            "note": "Weilchain SDK integration pending",
        }

    def _get_applet_info(self, input_data: dict[str, Any]) -> dict[str, Any]:
        applet_id = input_data.get("applet_id", "").strip()
        if not applet_id:
            raise ValueError("Missing 'applet_id' for applet info query")

        # TODO: Implement actual applet info fetch
        return {
            "applet_id": applet_id,
            "info": None,
            "note": "Weilchain SDK integration pending",
        }

    def _get_block(self, input_data: dict[str, Any]) -> dict[str, Any]:
        block_number = input_data.get("block_number")
        if block_number is None:
            raise ValueError("Missing 'block_number' for block query")

        # TODO: Implement actual block info fetch
        return {
            "block_number": block_number,
            "info": None,
            "note": "Weilchain SDK integration pending",
        }
