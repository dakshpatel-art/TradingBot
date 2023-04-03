import pandas as pd
from decimal import Decimal, getcontext

class StrategyEvaluator:

    def __init__(self,strategy_function, strategy_setting:dict= \
    {'indicators':['low_boll','fast_sma', 'slow_sma']}):
        self.strategy = strategy_function
        self.settings = strategy_settings
        self.buy_times = []
        self.sell_times = []

        self.profitable_symbol = 0
        self.unprofitable_symbol = 0

        self.comoplete_strating_balance = 0
        self.complete_resulting_balance = 0

        self.profits_list =[]
        self.results = dict()

    def backtest(self,
    model,
    starting_balance:float = 100,
    initial_profits:float = 1.045,
    initial_stop_loss:float = 0.85,
    incremental_profits:float = 1.04,
    incremetal_stop_loss:float = 0.975):
        
        if initial_stop_loss >= 1 or initial_stop_loss <=0:
            AssertionError("initial_stop_loss should be between 0 and 1!")

        if initial_profits <= 1:
            AssertionError("initial_profits should be greater than 1!")        

        df = model.df
        buy_times = []
        sell_times = []

        last_buy = None

        getcontext().prec = 30

        resulting_balance = Decimal(starting_balance)
        stop_loss = Decimal(initial_stop_loss)
        profit_target = Decimal(initial_profits)
        buy_price = 0

        for i in range(0,len(df['close']) - 1):
            if last_buy is None:
                strategy_result = self.strategy(model.df, i)

                if strategy_result:
                    buy_price = Decimal(strategy_result)
                    last_buy ={
                        "index" : i,
                        "price" : buy_price
                    }
                    buy_times.append([df['time'][i], buy_price])

                    stop_loss = Decimal(initial_stop )
                    profit_target = Decimal(initial_profits)

            elif last_buy is not None and i > last_buy["index"] + 1:
                # Yes (we already bought) so check whether the price has hit
                # Either the stop loss price OR the target price

                stop_loss_price = last_buy["price"] * stop_loss
                next_target_price = last_buy["price"] * profit_target

                if df['low'][i] < stop_loss_price:
                    #  If price went below our stop_loss, we sold at that point
                    sell_times.append([df['time'][i], stop_loss_price])
                    resulting_balance = resulting_balance * (stop_loss_price / buy_price)

                    last_buy = None
                    buy_price = Decimal(0)

                elif df['high'][i] > next_target_price:
                    # If price went above our target, it means we increased our stop loss
                    # and set our next target
                    last_buy = {
                        "index" : i,
                        "price" : Decimal(next_target_price)
                    }

                    stop_loss = Decimal(incremental_stop_loss)
                    profit_target = Decimal(incremental_profits)

        self.results[model.symbol] = dict(
            returns = round(Decimal(100.0) * (resulting_balance/Decimal(starting_balance) - Decimal(1.0)),3),
            buy_times = buy_times,
            sell_times = sell_times
        )

        if resulting_balance > starting_balance:
            self.profitable_symbol = self.profitable_symbol + 1
        elif resulting_balance < starting_balance:
            self.unprofitable_symbol = self.unprofitable_symbol + 1

        return resulting_balance

    def evaluate(self, model):
        last_entry = len(model.df['close']) - 1
        return self.strategy(model.df, last_entry)

    def updateResults(self, starting_balance, resulting_balance):
        self.comoplete_strating_balance = self.comoplete_strating_balance + starting_balance
        self.complete_resulting_balance = self.complete_resulting_balance + resulting_balance

    def printResults(self):
        print(self.strategy.__name__+" STATS: ")
        print("Profitable Symbols: "+str(self.profitable_symbol))
        print("Unprofitable Symbols: "+str(self.unprofitable_symbol))

        if len(self.profits_list) > 0:
            profitability = Decimal(100.0) * (self.complete_resulting_balance/self.comoplete_strating_balance - Decimal(1.0))
            print("overall Profits : " + str(round(sum(self.profits_list),2)))
            print(" Least Profitable Trade: "+ str(round(min(self.profits_list),2)))
            print(" Most Profitable Trade : " + str(round(max(self.profits_list),2)))
            print("With an initial balance of "+ str(round(self.complete_starting_balance) + \
                " and a Final balance of "+ str(round(self.complete_resulting_balance, 2))))
            print("The Profitability is "+ str(round(profitability, 2))+"%")
         
    