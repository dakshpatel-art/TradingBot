import requests,hashlib,json,decimal,hmac,time
import pandas as pd

binance_keys = {'api_key' : "",'secret_key':""}

class Binance :

    def __init__(self) :

        self.base = 'https://api.binance.com'
        self.endpoints = {"order": '/api/v3/order',
                         "testOrder": '/api/v3/order/test',
                         "allOrders": '/api/v3/allOrders',
                         "klines": '/api/v3/klines',
                         "exchangeInfo": '/api/v3/exchangeInfo'}
        self.headers = {"X-MBX-APIKEY": binance_keys['api_key']}

    def GetTreadingSymbols(self , quoteAssets : list = None ) :
        url = self.base + self.endpoints["exchangeInfo"]
         
        try :
            response = requests.get(url)
            data = json.loads(response.text)
        except Exception as e :
            print("Exception occured while trying url"+url)
            print(e)
            return[]

        symbols_list = []

        for pair in data['symbols'] :
            if pair['status'] == 'TREADING' :
                if quoteAssets != None and pair['quoteAsset'] in quoteAssets :
                    symbols_list.append(pair['symbol'])
        
        return symbols_list

    def GetLongerSymbolData(self, symbol:str, interval:str, limit:int=1000, end_time=False):
        repeat_rounds = 0

        if limit > 1000 :
            repeat_rounds = int(limit/1000)
        
        initial_limit == limit % 1000
        if initial_limit == 0 :
            initial_limit = 1000

        df = self.GetSymbolData(symbol, interval, limit=initial_limit, end_time=end_time)
        while repeat_rounds > 0 :
            df2 = self.GetSymbolData(symbol, interval, limit=1000, eend_time=df['time'[0]]) 
            df = df2.append(df, ignore_index = True)
            repeat_rounds = repeat_rounds - 1

        return df

    def GetSymbolData(self, symbol:str, interval:str, limit:int, end_time:False):
        if limit > 1000 :
            return self.GetLongerSymbolData(symbol, interval, limit. end_time) 

        params = '?&symbol='+symbol+'&interval='+interval+'&limit='+str(limit)
        
        if end_time :
            params = params + '&endTime=' + str(int(end_time))
        
        url = self.base + self.endpoints['klines'] + params

        data = requests.get(url)
        dictionary = json.loads(data.text)
        df = pd.DataFrame.from_dict(dictionary)
        df = df.drop(range(6,12), axis=1)
        col_names = ['time', 'open', 'hign', 'low', 'close', 'volume']
        df.columns = col_names 

        for col in col_names : 
            df[col] = df[col].astype(float)

        df['date'] = pd.to_datetime(df['time']*1000000, infer_datetime_format=True)

        return df

    def PlaceOrder(self, symbol:str, side:str, type:str, quantity:float=0, test:bool=True) :
        params = {'symbol': symbol,
			      'side': side, 			
			      'type': type,				
			      'quoteOrderQty': quantity,
			      'recvWindow': 5000,
			      'timestamp': int(round(time.time()*1000))}
        
        if type != 'MARKET' :
            params['timeInForce'] = 'GTC'
            params['price'] = self.floatToString(price)

        self.signRequest(params)

        url = ''

        if test : 
            url = self.base + self.endpoints['testOrder']
        else :
            url = self.base + self.endpoints['order']

        try :
            response = requests.post(url, params = params, headers=self.headers)
            data = response.text
        except Exception as e :
            print("Exception occured when trying to place on "+ url)
            print(e)
            data = {'code': '-1', 'msg':e}

        return json.loads(data)

    def CancelOrder(self, symbol:str, orderId:str) :
        params = {
            'symbol': symbol,
			'orderId' : orderId,
			'recvWindow': 5000,
			'timestamp': int(round(time.time()*1000))
        }

        self.signRequest(params)

        url = self.base + self.endpoints['order']

        try :
            response = requests.delete(url, params=params, headers=self.headers)
            data = response.text
        except Exception as e :
            print("Exception occured when trying to cancel order on "+ url)
            print(e)
            data = {'code':'-1', 'msg':e}

        return json.loads(data)

    def GetOrderInfo(self, symbol:str, orderId:str):
        params = {
            'symbol': symbol,
			'orderId' : orderId,
			'recvWindow': 5000,
			'timestamp': int(round(time.time()*1000))
        }
        self.signRequest(params)
        url = self.base + self.endpoints['order']

        try :
            response = requests.get(url, params=params, headers=self.headers)
            data = response.text
        except Exception as e :
            print("Exception occurd when trying to get order info on "+url)
            print(e)
            data = {'code':'-1', 'msg':e}

        return json.loads(data)

    def GetAllOrderInfo(self, symbol:str):
        params = {
            'symbol':symbol,
            'timestamp' : int(round(time.time()*1000))
        }

        self.signRequest(params)
        url = self.base + self.endpoints['allOrders']

        try:
            response = requests.get(url, params = params ,headers = self.headers)
            data = response.text
        except Exception as e :
            print("Exception occurd when trying to get info on all orders on "+url)
            print(e)
            data = {'code':-1,'msg':e}

        return json.loads(data)

    def floatToString(self, f:float):
        ctx = decimal.Context()
        ctx.prac = 12 
        d1 = ctx.create_decimal(repr(f))
        return format(d1, 'f')

    def signRequest(self, params:dict) :

        query_string = '&'.join(["{}={}".format(d, params[d]) for d in params])
        signature = hmac.new(binance_keys['secret_key'].encode('utf-8'),query_string.encode('utf-8'),hashlib.sha256)
        params['signature'] = signature.hexdigest()

        