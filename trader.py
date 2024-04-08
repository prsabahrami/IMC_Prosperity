from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string



class Trader:
    def __init__(self):
        self.position_limit = {"AMETHYSTS": 20, "STARFRUIT": 20}
        self.prices = {"AMETHYSTS": [], "STARFRUIT": []}
        self.counts = {"AMETHYSTS": [], "STARFRUIT": []}
        self.last_val = -1

    def ma(self,prices,counts):
        sum = 0
        c = 0
        for i in range(len(prices)):
            sum += prices[i] * counts[i]
            c += counts[i]
        return sum / c
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        acc_prices = {'AMETHYSTS': 10000, 'STARFRUIT': 10}
        coef = [4.997108e+03,  1.002812e-01, -6.605642e-04,  1.359603e-06, -1.241079e-09,  4.907114e-13, -5.258202e-17, -7.529245e-21]
		# Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            for price in order_depth.buy_orders.keys():
                quantity = order_depth.buy_orders[price]
                self.prices[product].append(price)
                self.counts[product].append(quantity)
                if len(self.prices[product]) > 10:
                    self.prices[product].pop(0)
                    self.counts[product].pop(0)
                print("Prices: " + str(self.prices[product]))
                print("Counts: " + str(self.counts[product]))
            if len(self.prices[product]) == 10 and product == 'STARFRUIT':
                sma = self.ma(self.prices[product], self.counts[product])
                t = state.timestamp / 100
                acc_prices[product] = coef[0] + coef[1] * t + coef[2] * t ** 2 + coef[3] * t ** 3 + coef[4] * t ** 4 + coef[5] * t ** 5 + coef[6] * t ** 6 + coef[7] * t ** 7
                acc_prices[product] = (acc_prices[product] + sma) / 2
            acceptable_price = acc_prices[product] # Participant should calculate this value
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
    
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
    
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 
        
				# Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData
    
# trader = Trader()

# from datamodel import Listing, OrderDepth, Trade, TradingState

# timestamp = 1100

# listings = {
# 	"AMETHYSTS": Listing(
# 		symbol="AMETHYSTS", 
# 		product="AMETHYSTS", 
# 		denomination= "SEASHELLS"
# 	),
# 	"STARFRUIT": Listing(
# 		symbol="STARFRUIT", 
# 		product="STARFRUIT", 
# 		denomination= "SEASHELLS"
# 	),
# }

# order_depths = {
# 	"AMETHYSTS": OrderDepth(
# 		buy_orders={10: 7, 9: 5},
# 		sell_orders={12: -5, 13: -3}
# 	),
# 	"STARFRUIT": OrderDepth(
# 		buy_orders={142: 3, 141: 5},
# 		sell_orders={144: -5, 145: -8}
# 	),	
# }

# own_trades = {
# 	"AMETHYSTS": [
# 		Trade(
# 			symbol="AMETHYSTS",
# 			price=11,
# 			quantity=4,
# 			buyer="SUBMISSION",
# 			seller="",
# 			timestamp=1000
# 		),
# 		Trade(
# 			symbol="AMETHYSTS",
# 			price=12,
# 			quantity=3,
# 			buyer="SUBMISSION",
# 			seller="",
# 			timestamp=1000
# 		)
# 	],
# 	"STARFRUIT": [
# 		Trade(
# 			symbol="STARFRUIT",
# 			price=143,
# 			quantity=2,
# 			buyer="",
# 			seller="SUBMISSION",
# 			timestamp=1000
# 		),
# 	]
# }

# market_trades = {
# 	"AMETHYSTS": [],
# 	"STARFRUIT": []
# }

# position = {
# 	"AMETHYSTS": 10,
# 	"STARFRUIT": -7
# }

# observations = {}

# traderData = ""

# state = TradingState(
# 	traderData,
# 	timestamp,
#   listings,
# 	order_depths,
# 	own_trades,
# 	market_trades,
# 	position,
# 	observations
# )

# # Test the trader
# trader.run(state)