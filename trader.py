from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import numpy as np
from math import ceil

import json
from datamodel import (
    Listing,
    Observation,
    Order,
    OrderDepth,
    ProsperityEncoder,
    Symbol,
    Trade,
    TradingState,
)
from typing import Any


class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(
        self,
        state: TradingState,
        orders: dict[Symbol, list[Order]],
        conversions: int,
        trader_data: str,
    ) -> None:
        base_length = len(
            self.to_json(
                [
                    self.compress_state(state, ""),
                    self.compress_orders(orders),
                    conversions,
                    "",
                    "",
                ]
            )
        )

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(
            self.to_json(
                [
                    self.compress_state(
                        state, self.truncate(state.traderData, max_item_length)
                    ),
                    self.compress_orders(orders),
                    conversions,
                    self.truncate(trader_data, max_item_length),
                    self.truncate(self.logs, max_item_length),
                ]
            )
        )

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append(
                [listing["symbol"], listing["product"], listing["denomination"]]
            )

        return compressed

    def compress_order_depths(
        self, order_depths: dict[Symbol, OrderDepth]
    ) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append(
                    [
                        trade.symbol,
                        trade.price,
                        trade.quantity,
                        trade.buyer,
                        trade.seller,
                        trade.timestamp,
                    ]
                )

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[: max_length - 3] + "..."


logger = Logger()


class Trader:

    star_cache = []  # limit of 4
    star_limit = 4
    position = {"AMETHYSTS": 0, "STARFRUIT": 0}
    position_limits = {"AMETHYSTS": 20, "STARFRUIT": 20}

    def get_mid(self, order_depth: OrderDepth):
        if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
            return 0
        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
        logger.print("Best bid: " + str(best_bid) + ", Best ask: " + str(best_ask))
        return (best_bid * best_bid_amount + best_ask * best_ask_amount * -1) / (
            best_ask_amount * -1 + best_bid_amount
        )

    def calc_next(self):
        coefs = [0.3417687, 0.2610691, 0.2077068, 0.1889884]
        if len(self.star_cache) < self.star_limit:
            return [100000, -100000]
        output = 2.3564944
        for i in range(len(coefs)):
            output += coefs[i] * self.star_cache[i]
        return [output + 1, output - 1]

    def run(self, state: TradingState):

        for key, val in state.position.items():
            self.position[key] = val

        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            if product != "STARFRUIT":
                acceptable_price = [10000, 10000]
            else:
                nxt = self.calc_next()
                acceptable_price = nxt

                self.star_cache.append(self.get_mid(order_depth))
                logger.print("Star cache: " + str(self.star_cache))

                if len(self.star_cache) > self.star_limit:
                    self.star_cache.pop(0)
            logger.print("Acceptable price : " + str(acceptable_price))
            logger.print(
                "Buy Order depth : "
                + str(len(order_depth.buy_orders))
                + ", Sell order depth : "
                + str(len(order_depth.sell_orders))
            )

            pos = self.position[product]

            for price, mnt in order_depth.sell_orders.items():
                logger.print("current position: " + str(self.position[product]))
                if (
                    price <= acceptable_price[1]
                    or (
                        (self.position[product] < 0)
                        and (price == acceptable_price[1] + 1)
                    )
                ) and pos < self.position_limits[product]:
                    buy_amount = min(-mnt, self.position_limits[product] - pos)
                    pos += buy_amount
                    logger.print("BUY", str(buy_amount) + "x", price)
                    orders.append(Order(product, price, buy_amount))

            buy_margin = list(order_depth.sell_orders.items())[0][0] + 1
            sell_margin = list(order_depth.buy_orders.items())[0][0] - 1

            bid = int(min(buy_margin, acceptable_price[0]))
            ask = int(max(sell_margin, acceptable_price[1]))

            # if pos < self.position_limits[product]:
            #     buy_amount = self.position_limits[product] - pos
            #     orders.append(Order(product, bid, buy_amount))
            #     print("BUY", str(buy_amount) + "x", bid)
            #     pos += buy_amount

            pos = self.position[product]

            for price, mnt in order_depth.buy_orders.items():
                logger.print("current position: " + str(self.position[product]))
                if (
                    price >= acceptable_price[0]
                    or (
                        (self.position[product] > 0)
                        and (price == acceptable_price[0] - 1)
                    )
                ) and pos > -self.position_limits[product]:
                    sell_amount = max(-mnt, -pos - self.position_limits[product])
                    pos += sell_amount
                    logger.print("SELL", str(sell_amount) + "x", price)
                    orders.append(Order(product, price, sell_amount))

            # if pos > -self.position_limits[product]:
            #     sell_amount = -pos - self.position_limits[product]
            #     orders.append(Order(product, ask, sell_amount))
            #     pos += sell_amount
            #     print("SELL", str(sell_amount) + "x", ask)

            # for price, mnt in order_depth.buy_orders.items():
            #     print("current position: " + str(self.position[product]))
            #     if price > acceptable_price[0]:  # sell
            #         sell_amount = max(
            #             -mnt, -self.position[product] - self.position_limits[product]
            #         )
            #         self.position[product] += sell_amount
            #         print("SELL", str(sell_amount) + "x", price)
            #         orders.append(Order(product, price, sell_amount))
            # buy_margin = min(
            #     list(order_depth.buy_orders.items())[0][0] + 1, acceptable_price[0]
            # )
            # if buy_margin != float("inf") and buy_margin != -float("inf"):
            #     buy_margin = ceil(buy_margin)
            # if self.position[product] < self.position_limits[product]:
            #     orders.append(
            #         Order(
            #             product,
            #             buy_margin,
            #             self.position_limits[product] - self.position[product],
            #         )
            #     )
            #     print(
            #         "BUY",
            #         str(self.position_limits[product] - self.position[product]) + "x",
            #         buy_margin,
            #     )
            # self.position[product] += (
            #     self.position_limits[product] - self.position[product]
            # )

            # for price, mnt in order_depth.sell_orders.items():
            #     print("current position: " + str(self.position[product]))
            #     if price < acceptable_price[1]:
            #         buy_amount = min(
            #             -mnt, self.position_limits[product] - self.position[product]
            #         )
            #         self.position[product] += buy_amount
            #         print("BUY", str(buy_amount) + "x", price)
            #         orders.append(Order(product, price, buy_amount))

            # sell_margin = max(
            #     list(order_depth.sell_orders.items())[0][0] - 1, acceptable_price[1]
            # )
            # if sell_margin != float("inf") and sell_margin != -float("inf"):
            #     sell_margin = int(sell_margin)
            # if self.position[product] > -self.position_limits[product]:
            #     orders.append(
            #         Order(
            #             product,
            #             sell_margin,
            #             -self.position[product] - self.position_limits[product],
            #         )
            #     )
            #     print(
            #         "SELL",
            #         str(-self.position[product] - self.position_limits[product]) + "x",
            #         sell_margin,
            #     )

            # self.position[product] -= (
            #     self.position[product] + self.position_limits[product]
            # )

            result[product] = orders

        traderData = ""

        conversions = 1

        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData


# trader = Trader()

# from datamodel import Listing, OrderDepth, Trade, TradingState

# timestamp = 1100

# listings = {
#     "AMETHYSTS": Listing(
#         symbol="AMETHYSTS", product="AMETHYSTS", denomination="SEASHELLS"
#     ),
#     "STARFRUIT": Listing(
#         symbol="STARFRUIT", product="STARFRUIT", denomination="SEASHELLS"
#     ),
# }

# order_depths = {
#     "AMETHYSTS": OrderDepth(buy_orders={10: 7, 9: 5}, sell_orders={12: -5, 13: -3}),
#     "STARFRUIT": OrderDepth(
#         buy_orders={142: 3, 141: 5}, sell_orders={144: -5, 145: -8}
#     ),
# }

# print(Trader.get_mid(trader, order_depths["AMETHYSTS"]))

# own_trades = {
#     "AMETHYSTS": [
#         Trade(
#             symbol="AMETHYSTS",
#             price=11,
#             quantity=4,
#             buyer="SUBMISSION",
#             seller="",
#             timestamp=1000,
#         ),
#         Trade(
#             symbol="AMETHYSTS",
#             price=12,
#             quantity=3,
#             buyer="SUBMISSION",
#             seller="",
#             timestamp=1000,
#         ),
#     ],
#     "STARFRUIT": [
#         Trade(
#             symbol="STARFRUIT",
#             price=143,
#             quantity=2,
#             buyer="",
#             seller="SUBMISSION",
#             timestamp=1000,
#         ),
#     ],
# }

# market_trades = {"AMETHYSTS": [], "STARFRUIT": []}

# position = {"AMETHYSTS": 10, "STARFRUIT": -7}

# observations = {}

# traderData = ""

# state = TradingState(
#     traderData,
#     timestamp,
#     listings,
#     order_depths,
#     own_trades,
#     market_trades,
#     position,
#     observations,
# )

# # Test the trader
# trader.run(state)
