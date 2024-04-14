from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import numpy as np
import pandas as pd
from math import ceil, floor

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

    star_cache_bid = []  # limit of 4
    star_cache_ask = []  # limit of 4
    orch_cache = np.array([])
    orch_limit = 20
    star_limit = 4
    position_limits = {"AMETHYSTS": 20, "STARFRUIT": 20, "ORCHIDS": 100}
    t = 0

    def __init__(self) -> None:
        self.strategies = {
            "AMETHYSTS": self.handle_amethysts,
            "STARFRUIT": self.handle_starfruit,
            "ORCHIDS": self.handle_orchids,
        }

    def get_mid_bid(self, order_depth: OrderDepth):
        sum = 0
        count = 0
        for bid, amount in order_depth.buy_orders.items():
            sum += bid * amount
            count += amount
        return sum / count

    def get_mid_ask(self, order_depth: OrderDepth):
        sum = 0
        count = 0
        for ask, amount in order_depth.sell_orders.items():
            sum += ask * amount * -1
            count += amount * -1
        return sum / count

    def calc_next(self):
        coef_bid = [0.68898749, 0.22587252, 0.06184055, 0.02223278]
        coef_ask = [0.64999519, 0.23712433, 0.06647112, 0.04528404]
        if len(self.star_cache_bid) < self.star_limit:
            return [100000, -100000]
        output_bid = 5.39362451
        output_ask = 5.69797192

        for i in range(len(coef_bid)):
            output_bid += coef_bid[i] * self.star_cache_bid[i]
        for i in range(len(coef_ask)):
            output_ask += coef_ask[i] * self.star_cache_ask[i]

        return [
            output_ask - 3,
            output_bid + 3 - 2 * bool(self.t > 370 and self.t < 560),
        ]

    def handle_starfruit(self, state: TradingState):
        order_depth: OrderDepth = state.order_depths["STARFRUIT"]
        product = "STARFRUIT"
        orders: List[Order] = []
        nxt = self.calc_next()
        acceptable_price = nxt

        self.star_cache_bid.append(self.get_mid_bid(order_depth))
        self.star_cache_ask.append(self.get_mid_ask(order_depth))

        logger.print("Star cache bid : " + str(self.star_cache_bid))
        logger.print("Star cache ask : " + str(self.star_cache_ask))

        if len(self.star_cache_bid) > self.star_limit:
            self.star_cache_bid.pop(0)
        if len(self.star_cache_ask) > self.star_limit:
            self.star_cache_ask.pop(0)
        logger.print("Acceptable price : " + str(acceptable_price))
        logger.print(
            "Buy Order depth : "
            + str(len(order_depth.buy_orders))
            + ", Sell order depth : "
            + str(len(order_depth.sell_orders))
        )

        pos = self.position[product]

        osell = sorted(order_depth.sell_orders.items())
        for price, mnt in osell:
            logger.print("current position: " + str(self.position[product]))
            logger.print("BUY", "Price: " + str(price), "Position: " + str(pos))
            if price <= acceptable_price[1] and pos < self.position_limits[product]:
                buy_amount = min(-mnt, self.position_limits[product] - pos)
                pos += buy_amount
                logger.print("BUY", str(buy_amount) + "x", price)
                orders.append(Order(product, price, buy_amount))

        # buy_margin = list(order_depth.sell_orders.items())[0][0] + 1
        # sell_margin = list(order_depth.buy_orders.items())[0][0] - 1

        # bid = int(min(buy_margin, acceptable_price[1]))
        # ask = int(max(sell_margin, acceptable_price[0]))

        # if pos < self.position_limits[product]:
        #     buy_amount = self.position_limits[product] - pos
        #     orders.append(Order(product, bid, buy_amount))
        #     print("BUY", str(buy_amount) + "x", bid)
        #     pos += buy_amount

        pos = self.position[product]

        obuy = sorted(order_depth.buy_orders.items(), reverse=True)
        for price, mnt in obuy:
            logger.print("current position: " + str(self.position[product]))
            logger.print("SELL", "Price: " + str(price), "Position: " + str(pos))
            if price >= acceptable_price[0] and pos > -self.position_limits[product]:
                sell_amount = max(-mnt, -pos - self.position_limits[product])
                pos += sell_amount
                logger.print("SELL", str(sell_amount) + "x", price)
                orders.append(Order(product, price, sell_amount))

        # if pos > -self.position_limits[product]:
        #     sell_amount = -pos - self.position_limits[product]
        #     orders.append(Order(product, ask, sell_amount))
        #     pos += sell_amount
        #     print("SELL", str(sell_amount) + "x", ask)

        return orders

    def handle_amethysts(self, state: TradingState):
        order_depth: OrderDepth = state.order_depths["AMETHYSTS"]
        product = "AMETHYSTS"
        orders: List[Order] = []
        ps = 15
        pos = state.position.get(product, 0)
        osell = order_depth.sell_orders
        obuy = order_depth.buy_orders

        if len(osell) > 0:
            best_ask = min(osell.keys())
            if best_ask <= 9999:
                best_ask_amount = osell[best_ask]
            else:
                best_ask_amount = 0
        else:
            best_ask_amount = 0

        if len(obuy) > 0:
            best_bid = max(obuy.keys())
            if best_bid >= 10001:
                best_bid_amount = obuy[best_bid]
            else:
                best_bid_amount = 0
        else:
            best_bid_amount = 0

        if pos - best_ask_amount > self.position_limits[product]:
            best_ask_amount = pos - self.position_limits[product]
            open_ask_amount = 0
        else:
            open_ask_amount = pos - ps - best_ask_amount

        if pos - best_bid_amount < -self.position_limits[product]:
            best_bid_amount = pos + self.position_limits[product]
            open_bid_amount = 0
        else:
            open_bid_amount = pos + ps - best_bid_amount

        open_ask_amount = min(0, open_ask_amount)
        open_bid_amount = max(0, open_bid_amount)

        logger.print("best_ask_amount", best_ask_amount)
        if best_ask_amount < 0:
            logger.print("BUY", product, str(-best_ask_amount) + "x", best_ask)
            orders.append(Order(product, best_ask, -best_ask_amount))

        logger.print("open_ask_amount", open_ask_amount)
        if open_ask_amount < 0:
            logger.print("BUY", product, str(-open_ask_amount) + "x", 10003)
            orders.append(Order(product, 9997, -open_ask_amount))

        logger.print("best_bid_amount", best_bid_amount)
        if best_bid_amount > 0:
            logger.print("SELL", product, str(best_bid_amount) + "x", best_bid)
            orders.append(Order(product, best_bid, -best_bid_amount))

        logger.print("open_bid_amount", open_bid_amount)
        if open_bid_amount > 0:
            logger.print("SELL", product, str(open_bid_amount) + "x", 10003)
            orders.append(Order(product, 10003, -open_bid_amount))

        return orders

    def handle_orchids(self, state: TradingState):
        product = "ORCHIDS"
        order_depth: OrderDepth = state.order_depths[product]
        orders: List[Order] = []
        conversions = 0

        best_ask, best_ask_amount = sorted(order_depth.sell_orders.items())[0]
        best_bid, best_bid_amount = sorted(
            order_depth.buy_orders.items(), reverse=True
        )[0]
        pos = state.position.get(product, 0)

        if len(self.orch_cache) < self.orch_limit:
            self.orch_cache = np.append(self.orch_cache, (best_ask + best_bid) / 2)
            return [], 0

        acceptable_price = pd.Series(self.orch_cache).ewm(alpha=0.01).mean().values[-1]
        logger.print("Acceptable price : " + str(acceptable_price))

        self.orch_cache = np.append(self.orch_cache, (best_ask + best_bid) / 2)
        self.orch_cache = np.delete(self.orch_cache, 0)

        if pos == 0:
            orders.append(
                Order(
                    product,
                    floor(acceptable_price - 1),
                    self.position_limits[product] - pos,
                )
            )
            orders.append(
                Order(
                    product,
                    ceil(acceptable_price + 1),
                    -self.position_limits[product] - pos,
                )
            )
        if pos < 0:
            orders.append(
                Order(
                    product,
                    floor(acceptable_price),
                    self.position_limits[product] - pos,
                )
            )
            orders.append(
                Order(
                    product,
                    ceil(acceptable_price + 2),
                    -self.position_limits[product] - pos,
                )
            )
        if pos > 0:
            orders.append(
                Order(
                    product,
                    floor(acceptable_price - 2),
                    self.position_limits[product] - pos,
                )
            )
            orders.append(
                Order(
                    product,
                    ceil(acceptable_price),
                    -self.position_limits[product] - pos,
                )
            )

        obs = state.observations.conversionObservations[product]
        bidPrice = obs.bidPrice
        askPrice = obs.askPrice

        print("Bid Price: ", bidPrice)
        print("Ask Price: ", askPrice)
        transportFees = obs.transportFees
        exportTariff = obs.exportTariff
        importTariff = obs.importTariff
        sunlight = obs.sunlight
        humidity = obs.humidity

        logger.print("Bid Price: " + str(bidPrice))
        logger.print("Ask Price: " + str(askPrice))

        # if pos < 0:
        #     conversions = -pos - 1
        #     orders.append(Order(product, best_ask - 1, -pos - 1))

        # if pos > 0:
        #     conversions = self.position_limits[product] - pos
        #     orders.append(
        #         Order(product, best_ask - 1, self.position_limits[product] - pos - 1)
        #     )

        return orders, conversions

    def run(self, state: TradingState):
        self.t = state.timestamp / 100

        result = {}
        conversions = 0
        for product in state.order_depths:
            print("Product: ", product)
            orders = []
            if product == "ORCHIDS":
                orders, conversions = self.strategies[product](state)
            # else:
            #     orders = self.strategies[product](state)
            result[product] = orders

        traderData = ""

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

# print(Trader.get_mid_bid(trader, order_depths["AMETHYSTS"]))
# print(Trader.get_mid_ask(trader, order_depths["AMETHYSTS"]))

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
