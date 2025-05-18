from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from projectx_sdk.endpoints import BaseService
from projectx_sdk.models.order import (
    Order,
    OrderCancellationResponse,
    OrderModificationResponse,
    OrderPlacementResponse,
    OrderSearchResponse,
)
from projectx_sdk.utils.constants import OrderSide, OrderType


class OrderService(BaseService):
    """Service for order-related endpoints."""

    def search(
        self, account_id: int, start_timestamp: datetime, end_timestamp: Optional[datetime] = None
    ) -> List[Order]:
        """
        Search for orders based on criteria.

        Args:
            account_id: The account ID to filter orders by
            start_timestamp: The start of the date/time range (inclusive)
            end_timestamp: The end of the date/time range (inclusive, optional)

        Returns:
            A list of orders matching the criteria
        """
        data = {
            "accountId": account_id,
            "startTimestamp": start_timestamp.isoformat(),
        }

        if end_timestamp:
            data["endTimestamp"] = end_timestamp.isoformat()

        response = self._client.post("Order/search", json=data)
        search_response = OrderSearchResponse.model_validate(response)
        return search_response.orders

    def search_open(self, account_id: int) -> List[Order]:
        """
        Search for open (active) orders for an account.

        Args:
            account_id: The account ID for which to retrieve open orders

        Returns:
            A list of currently open orders
        """
        data = {"accountId": account_id}

        response = self._client.post("Order/searchOpen", json=data)
        search_response = OrderSearchResponse.model_validate(response)
        return search_response.orders

    def place(
        self,
        account_id: int,
        contract_id: str,
        order_type: Union[OrderType, int],
        side: Union[OrderSide, int],
        size: int,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        custom_tag: Optional[str] = None,
        linked_order_id: Optional[int] = None,
    ) -> int:
        """
        Place a new order.

        Args:
            account_id: The ID of the account to place the order in
            contract_id: The ID of the contract/instrument to trade
            order_type: The order type (market, limit, etc.)
            side: The side of the order (buy or sell)
            size: The quantity of the order
            limit_price: The limit price (for limit orders)
            stop_price: The stop price (for stop orders)
            trail_price: The trailing amount (for trailing stops)
            custom_tag: A custom tag or note for the order
            linked_order_id: ID of a linked order for advanced strategies

        Returns:
            The order ID of the newly placed order
        """
        # Convert enum to int if needed
        if isinstance(order_type, OrderType):
            order_type = int(order_type)
        if isinstance(side, OrderSide):
            side = int(side)

        data = {
            "accountId": account_id,
            "contractId": contract_id,
            "type": order_type,
            "side": side,
            "size": size,
            "limitPrice": limit_price,
            "stopPrice": stop_price,
            "trailPrice": trail_price,
            "customTag": custom_tag,
            "linkedOrderId": linked_order_id,
        }

        response = self._client.post("Order/place", json=data)
        placement_response = OrderPlacementResponse.model_validate(response)
        return placement_response.order_id

    def cancel(self, account_id: int, order_id: int) -> bool:
        """
        Cancel an open order.

        Args:
            account_id: The account ID which the order belongs to
            order_id: The unique ID of the order to cancel

        Returns:
            True if cancellation was successful, False otherwise
        """
        data = {"accountId": account_id, "orderId": order_id}

        response = self._client.post("Order/cancel", json=data)
        cancellation_response = OrderCancellationResponse.model_validate(response)
        return cancellation_response.success

    def modify(
        self,
        account_id: int,
        order_id: int,
        size: Optional[int] = None,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
    ) -> bool:
        """
        Modify an existing open order.

        Args:
            account_id: The account ID which the order belongs to
            order_id: The ID of the order to modify
            size: The new size (quantity) for the order
            limit_price: The new limit price
            stop_price: The new stop price
            trail_price: The new trail price

        Returns:
            True if modification was successful, False otherwise
        """
        data = {"accountId": account_id, "orderId": order_id}

        # Only include fields that are being modified
        if size is not None:
            data["size"] = size
        if limit_price is not None:
            data["limitPrice"] = limit_price
        if stop_price is not None:
            data["stopPrice"] = stop_price
        if trail_price is not None:
            data["trailPrice"] = trail_price

        response = self._client.post("Order/modify", json=data)
        modification_response = OrderModificationResponse.model_validate(response)
        return modification_response.success
