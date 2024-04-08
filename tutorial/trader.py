from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import string

Product = str

class Trader:

    prices: Dict[Product, List[int]]
    def __init__(self):
        self.position_limit = {"AMETHYSTS": 20, "STARFRUIT": 20}
        prices = {}
        counts = {}

    def run(self, state: TradingState):

        result = {}

        current_timestamp = state.timestamp

        history_length = 10
        start_trading = 100 * history_length

        order_depth: OrderDepth = state.order_depths["STARFRUIT"]
        
        price = 0
        count = 0

        for trade in state.market_trades["STARFRUIT"]:

            sma = price / count
            
            

                    



