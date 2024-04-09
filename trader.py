from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import numpy as np


class Trader:

    A = np.array([[1, 1], [0, 1]])
    B = np.array([[0.5], [1]])
    C = np.array([[1, 0]])
    Q = np.array([[0.0001, 0], [0, 0.0001]])
    R = np.array([[0.01]])
    x0 = np.array([[5.03954329e03], [-2.32747656e-01]])
    P0 = np.eye(2)
    x = x0
    P = P0
    filtered_prices: List = []

    def get_mid(self, order_depth: OrderDepth):
        if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
            return 0
        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
        print("Best bid: " + str(best_bid) + ", Best ask: " + str(best_ask))
        return (best_bid * best_bid_amount + best_ask * best_ask_amount * -1) / (
            best_ask_amount * -1 + best_bid_amount
        )

    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            if product != "STARFRUIT":
                acceptable_price = 10000
            else:
                z = self.get_mid(order_depth)
                x_pred = np.dot(self.A, self.x)
                P_pred = np.dot(np.dot(self.A, self.P), self.A.T) + self.Q

                # Update
                y = z - np.dot(self.C, x_pred)
                S = np.dot(np.dot(self.C, P_pred), self.C.T) + self.R
                K = np.dot(np.dot(P_pred, self.C.T), np.linalg.inv(S))
                self.x = x_pred + np.dot(K, y)
                self.P = P_pred - np.dot(np.dot(K, self.C), P_pred)
                self.filtered_prices.append(self.x[0, 0])
                acceptable_price = self.filtered_prices[-1]

            print("Acceptable price : " + str(acceptable_price))
            print(
                "Buy Order depth : "
                + str(len(order_depth.buy_orders))
                + ", Sell order depth : "
                + str(len(order_depth.sell_orders))
            )

            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) < acceptable_price:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))

            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) > acceptable_price:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))

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

# print(Trader.get_mid(trader, order_depths["AMETHYSTS"])

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
