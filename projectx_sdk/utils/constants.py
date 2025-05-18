"""Constants and enumerations for the ProjectX API."""

from enum import IntEnum


class OrderType(IntEnum):
    """Order types supported by the ProjectX API."""

    LIMIT = 1
    MARKET = 2
    STOP = 4
    TRAILING_STOP = 5
    JOIN_BID = 6
    JOIN_ASK = 7


class OrderSide(IntEnum):
    """Order sides (buy/sell) for the ProjectX API."""

    BUY = 0
    SELL = 1

    # Alternative names for the same values
    BID = 0
    ASK = 1


# URLs for different environments
ENVIRONMENT_URLS = {
    "alphaticks": "gateway-api-alphaticks.s2f.projectx.com",
    "blueguardian": "gateway-api-blueguardian.s2f.projectx.com",
    "blusky": "gateway-api-blusky.s2f.projectx.com",
    "e8x": "gateway-api-e8x.s2f.projectx.com",
    "fundingfutures": "gateway-api-fundingfutures.s2f.projectx.com",
    "thefuturesdesk": "gateway-api-thefuturesdesk.s2f.projectx.com",
    "futureselite": "gateway-api-futureselite.s2f.projectx.com",
    "fxifyfutures": "gateway-api-fxifyfutures.s2f.projectx.com",
    "goatfunded": "gateway-api-goatfunded.s2f.projectx.com",
    "tickticktrader": "gateway-api-tickticktrader.s2f.projectx.com",
    "toponefutures": "gateway-api-toponefutures.s2f.projectx.com",
    "topstepx": "gateway-api-topstepx.s2f.projectx.com",
    "tx3funding": "gateway-api-tx3funding.s2f.projectx.com",
    # Demo environment for testing
    "demo": "gateway-api-demo.s2f.projectx.com",
}

# Real-time WebSocket hub URLs
REALTIME_HUB_URLS = {env: f"wss://gateway-rtc-{env}.s2f.projectx.com" for env in ENVIRONMENT_URLS}

# API Endpoints
ENDPOINTS = {
    "auth": {
        "login_key": "/api/Auth/loginKey",
        "login_app": "/api/Auth/loginApp",
        "validate": "/api/Auth/validate",
    },
    "account": {
        "search": "/api/Account/search",
    },
    "contract": {
        "search": "/api/Contract/search",
        "search_by_id": "/api/Contract/searchById",
    },
    "history": {
        "retrieve_bars": "/api/History/retrieveBars",
    },
    "order": {
        "search": "/api/Order/search",
        "search_open": "/api/Order/searchOpen",
        "place": "/api/Order/place",
        "cancel": "/api/Order/cancel",
        "modify": "/api/Order/modify",
    },
    "position": {
        "search_open": "/api/Position/searchOpen",
        "close_contract": "/api/Position/closeContract",
        "partial_close_contract": "/api/Position/partialCloseContract",
    },
    "trade": {
        "search": "/api/Trade/search",
    },
}
