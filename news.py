import pandas as pd
import numpy as np
import yfinance as yf

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, r2_score
from sklearn.metrics import mean_poisson_deviance, mean_gamma_deviance, accuracy_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

def technical_analysis(ticker,ip):

    ticker_name = ticker
    market = ip
    if market == "y" or market == "Y": ticker_name = ticker_name + ".NS"

    ticker = yf.download(ticker_name, start="2022-01-01")

    ticker.reset_index(inplace=True)
    ticker.rename(columns={"Date":"date", "Open":"open", "High":"high", "Low":"low", "Close":"close"}, inplace=True)

    ticker.dropna()
    ticker.date = pd.to_datetime(ticker.date)

    print("------------------------------------------------------------------")

    print("Starting date: ",ticker.iloc[0][0])
    print("Ending date: ", ticker.iloc[-1][0])
    print("Duration: ", ticker.iloc[-1][0]-ticker.iloc[0][0])

    print("------------------------------------------------------------------")

    closedf = ticker[['date','close','Volume']]

    close_stock = closedf.copy()
    del closedf['date']
    scaler=MinMaxScaler(feature_range=(0,1))
    closedf=scaler.fit_transform(np.array(closedf).reshape(-1,1))

    training_size=int(len(closedf)*0.65)
    test_size=len(closedf)-training_size
    train_data,test_data=closedf[0:training_size,:],closedf[training_size:len(closedf),:1]


    def create_dataset(dataset, time_step=1):
        dataX, dataY = [], []
        for i in range(len(dataset)-time_step-1):
            a = dataset[i:(i+time_step), 0]   ###i=0, 0,1,2,3-----99   100
            dataX.append(a)
            dataY.append(dataset[i + time_step, 0])
        return np.array(dataX), np.array(dataY)

    time_step = 15
    X_train, y_train = create_dataset(train_data, time_step)
    X_test, y_test = create_dataset(test_data, time_step)

    regressor = XGBRegressor()
    regressor.fit(X_train, y_train)

    train_predict=regressor.predict(X_train)
    test_predict=regressor.predict(X_test)

    train_predict = train_predict.reshape(-1,1)
    test_predict = test_predict.reshape(-1,1)

    train_predict = scaler.inverse_transform(train_predict)
    test_predict = scaler.inverse_transform(test_predict)
    original_ytrain = scaler.inverse_transform(y_train.reshape(-1,1))
    original_ytest = scaler.inverse_transform(y_test.reshape(-1,1))

    print("Train data explained variance regression score:", explained_variance_score(original_ytrain, train_predict))
    print("Test data explained variance regression score:", explained_variance_score(original_ytest, test_predict))



def sentimental_analysis(ticker):

    finwiz_url = "https://finviz.com/quote.ashx?t="
    news_tables = {}
    url = finwiz_url + (ticker)

    req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
    response = urlopen(req)
    html = BeautifulSoup(response, features="lxml")

    news_table = html.find(id='news-table')
    news_table_tr = news_table.find_all('tr')

    parsed_news = []

    for x in news_table.findAll('tr'):
        text = x.a.get_text()
        date_scrape = x.td.text.split()
        if len(date_scrape) == 1:
            time = date_scrape[0]
        else:
            date = date_scrape[0]
            time = date_scrape[1]
        parsed_news.append([ date, time, text])

    vader = SentimentIntensityAnalyzer()
    columns = ['date', 'time', 'headline']
    parsed_and_scored_news = pd.DataFrame(parsed_news, columns=columns)
    scores = parsed_and_scored_news['headline'].apply(vader.polarity_scores).tolist()
    scores_df = pd.DataFrame(scores)
    parsed_and_scored_news = parsed_and_scored_news.join(scores_df, rsuffix='_right')
    parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date
    print(parsed_and_scored_news.head(1))


technical_analysis('AMZN','N')
sentimental_analysis('AMZN')