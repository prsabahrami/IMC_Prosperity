from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import numpy as np


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
        print("Best bid: " + str(best_bid) + ", Best ask: " + str(best_ask))
        return (best_bid * best_bid_amount + best_ask * best_ask_amount * -1) / (
            best_ask_amount * -1 + best_bid_amount
        )

    def calc_next(self):
        coefs = [0.3417687, 0.2610691, 0.2077068, 0.1889884]
        if len(self.star_cache) < self.star_limit:
            return [float("inf"), -float("inf")]
        output = 2.3564944
        for i in range(len(coefs)):
            output += coefs[i] * self.star_cache[i]
        return [output + 1, output - 1]

    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
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
                print("Star cache: " + str(self.star_cache))

                if len(self.star_cache) > self.star_limit:
                    self.star_cache.pop(0)
            print("Acceptable price : " + str(acceptable_price))
            print(
                "Buy Order depth : "
                + str(len(order_depth.buy_orders))
                + ", Sell order depth : "
                + str(len(order_depth.sell_orders))
            )

            # if len(order_depth.sell_orders) != 0:
            #     best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            #     if int(best_ask) < acceptable_price[1]:
            #         print("BUY", str(-best_ask_amount) + "x", best_ask)
            #         buy_amount = min(
            #             -best_ask_amount, self.position_limits[product] - self.position[product]
            #         )
            #         self.position[product] += buy_amount
            #         print("BUY", str(buy_amount) + "x", best_ask)
            #         orders.append(Order(product, best_ask, buy_amount))

            # if len(order_depth.buy_orders) != 0:
            #     best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            #     if best_bid > acceptable_price[0]:  # sell
            #         print("current position: " + str(self.position[product]))
            #         # newpos = self.position[product] - (-mnt)
            #         # sell_amount = -mnt
            #         # if newpos < -self.position_limits[product]:
            #         #     sell_amount += newpos
            #         #     newpos = -self.position_limits[product]
            #         # self.position[product] = newpos
            #         sell_amount = max(
            #             -best_bid_amount, -self.position[product] - self.position_limits[product]
            #         )
            #         self.position[product] += sell_amount
            #         print("SELL", str(sell_amount) + "x", best_bid)
            #         orders.append(Order(product, best_bid, sell_amount))

            for price, mnt in order_depth.buy_orders.items():
                if price > acceptable_price[0]:  # sell
                    print("current position: " + str(self.position[product]))
                    sell_amount = max(
                        -mnt, -self.position[product] - self.position_limits[product]
                    )
                    self.position[product] += sell_amount
                    print("SELL", str(sell_amount) + "x", price)
                    orders.append(Order(product, price, sell_amount))
            for price, mnt in order_depth.sell_orders.items():
                if price < acceptable_price[1]:
                    print("current position: " + str(self.position[product]))
                    buy_amount = min(
                        -mnt, self.position_limits[product] - self.position[product]
                    )
                    self.position[product] += buy_amount
                    print("BUY", str(buy_amount) + "x", price)
                    orders.append(Order(product, price, buy_amount))

            result[product] = orders

        traderData = ""

        conversions = 1
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
