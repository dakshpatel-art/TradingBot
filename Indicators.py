from pyti.smoothed_moving_average import smoothed_moving_average as sma
from pyti.exponential_moving_average import exponential_moving_average as ema
from pyti.bollinger_bands import  lower_bollinger_band as lbb
from pyti.bollinger_bands import upper_bollinger_band as ubb

def ComputeIchimokuCloud(df) :
    
    nine_period_high = df['high'].rolling(window=9).max()
    nine_period_low = df['low'].rolling(window=9).min()
    df['tenkansen'] = (nine_period_high + nine_period_low)/2
    
    period26_high = df['high'].rolling(window=26).max()
    period26_low = df['low'].rolling(window=26).min()
    df['tenkansen'] = (period26_high + period26_low)/2

    df['senkou_a'] = ((df['tenkansen'] + df['kijusen'])/2).shift(26)

    period52_high = df['high'].rolling(window = 52).max()
    period52_low = df['low'].rolling(window = 52).min()
    df['senkou_b'] = ((period52_high + period52_low) / 2).shift(52)

    df['chikouspan'] = df['close'].shift(-26)

    return df

class Indicators :
    
    INDICATORS_DICT = {
        "sma": sma,
		"ema": ema,
		"lbb": lbb,
		"ubb": ubb,
		"ichimoku": ComputeIchimokuCloud,
    }

    @staticmethod
    def AddIndicator(df, indicator_name, col_names, args) :
        try : 
            if indicator_name == "ichimoku" :
                df = ComputeIchimokuCloud(df)
            else :
                df[col_name] = Indicators.INDICATORS_DICT[indicator_name]

        except Exception as e :
            print("\n <<< Exception Raised >>>"+indicator_name)
            print(e)


