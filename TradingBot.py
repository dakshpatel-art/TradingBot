from StrategyEvaluator import StrategyEvaluator
from Strategies import Strategies
from Binance import Binance
from TradingModel import TradingModel

import json
from decimal import Decimal,getcontext

def BacktestStrategies(symbols = [], interval = '4h', plot=False , strategy_evaluators=[],
                        options = dict(starting_balance=100, initial_profits = 1.01,initial_stop_loss = 0.9,incremental_profits = 1.005,incremental_stop_loss = 0.995)) :

                        coins_tested = 0
                        trade_value = options['starting_balance']

                        for symbol in symbols :
                            print(symbol)
                            model = TradingModel(symbol=symbol, timeframe=interval)
                            for evaluator in strategy_evaluators :
                                resulting_balance = evaluator.backtest(
                                    model,starting_balance = options['starting_balance'],
                                    initial_profits = options['initial_profits'],
                                    initial_stop_loss = options['initial_stop_loss'],
                                    incremental_profits = options['incremental_profits'],
                                    incremental_stop_loss =options['incremental_stop_loss'])

                                if resulting_balance != trade_value :
                                    print(evaluator.strategy.__name__
                                    +": Starting Balance :"+str(trade_value)
                                    +": resulting balance :"+str(round(resulting_balance,2)))

                                    if plot :
                                        model.plotData(
                                            buy_signals = evaluator.results[model.symbol]['buy_times'],
                                            sell_signals = evaluator.results[model.symbol]['sell_times'],
                                            plot_title = evaluator.strategy.__name__+" on "+model.symbol)
                                    
                                    evaluator.profits_list.append(resulting_balance - trade_value)
                                    evaluator.updateResult(trade_value, resulting_balance)

                                coins_tested = coins_tested + 1
                        
                        for evaluator in strategy_evaluators :
                            print("")
                            evaluator.printResults()

strategy_matched_symbol = "\nStrategy Matched Symbol! \
                        \nType 'b' then ENTER to backtest \
                        \nType 'p' then ENTER to place Order \
                        \nType anything willl skip.\n"

ask_place_order = "\nType 'p' if you want to place order \
                    \nOr press anything to skip.\n"  

def EvaluateStrategies(symbols=[], strategy_evaluators=[], interval='1h', options = dict(starting_balance=100, initial_profits = 1.01, initial_stop_loss = 0.9,incremental_profits = 1.005, incremental_stop_loss = 0.995)):
    for symbol in symbols:
        print(symbol)
        model = TradingModel(symbol=symbol, timeframe=interval)
        for evaluator in strategy_evaluators:
            if evaluator in strategy_evaluators :
                print("\n"+evalutor.strategy.__name__+"matched on"+symbol)
                print(strategy_matched_symbol)
                answer = input()

                if answer == 'b' :
                    resulting_balance = evalutor.backtest(
                        model,
                        starting_balance = options['starting_balance'],
                        initial_profits = options['initial_profits'],
                        initial_stop_loss = options['initial_stop_loss'],
                        incremental_profits = options['incremental_profits'],
                        incremental_stop_loss = options['incremental_stop_loss'],
                    )
                    model.plotData(
                        buy_signals = evaluator.results[model.symbol]['buy_times'],
                        sell_signals = evaluator.results[model.symbol]['sell_times'],
                        plot_title = evaluator.strategy.__name__+"matched on "+symbol
                    )
                    print(evaluator.results[model.symbol])
                    print(ask_place_order)
                    answer = input()

                if answer == 'p' :
                    print("\nPlacing order")
                    order_result = model.exchange.PlaceOrder(model.symbol,"BUY","MARKET",quantity=0.02,test=False)
                    if "code" in order_result:
                        print("\nERROR.")
                        print(order_result)

                    else :
                        print("\nSUCCESS.")
                        print(order_result)

opening_text = "\nWelcome to Crypto Bot.\n \
    press 'b' to backtest \n \
    press 'e' to excause the strategies \n \
    press 'q' to quit. "

def Main():

    exchange = Binance()
    symbols = exchange.GetTreadingSymbols(quoteAssets=["ETH"])

    strategy_evaluators = [
        StrategyEvaluator(strategy_function=Strategies.bollStrategy),
        StrategyEvaluator(strategy_function=Strategies.maStrategy),
        StrategyEvaluator(strategy_function=Strategies.ichimokuBullish)
    ]

    print(opening_text)

    answer = input()

    while answer not in ['b','e','q'] :
        print(opening_text)
        answer = input()

    if answer == 'e' :
        EvaluateStrategies(symbols=symbols,interval='5m',strategy_evaluators=strategy_evaluators)
    if answer == 'b' :
        BacktestStrategies(symbols=symbols, interval='5m', plot=True, strategy_evaluators=strategy_evaluators)
    if answer == 'q' :
        print("\nBYE!\n")

if __name__ == '__main__' :
    Main()

