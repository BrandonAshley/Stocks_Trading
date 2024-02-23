#Add a directory at line ---118
#Change interval and period see yfinance documentation for interval and periods

import pandas as pd
import numpy as np
import talib
import yfinance as yf
import alpaca_trade_api as tradeapi
import pandas_ta as ta
import matplotlib.pyplot as plt
import backtrader as bt
import re
import itertools

buy_sell_events = []
class TradingStrategy:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = pd.DataFrame()
        self.data_profit=pd.DataFrame()
        self.consecutive_signals=6
        self.signal_columns = {}
        self.interval="5m"
        self.period="5d"#"1mo"
        
    def get_data(self):
        df = yf.download(self.symbol, interval=self.interval, period=self.period)
        if len(df)<200:
            raise Exception("DataFrame length is less than 200.")
        
        df.reset_index(inplace=True)
        #print(df.info())
        if 'Date' in df.columns:
            df['Datetime']=df['Date']
        
        
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df.set_index('Datetime', inplace=True)
        return df
    
    def set_data(self, df):
        self.data= df
        
    #Indicator signals    
    def RSI(self,col,Low,High):
        if col< Low:
            return 1  # Buy signal
        elif col > High:
            return -1  # Sell signal
    
    def RSI_SMA(self,row,rsi,sma):
        if row[rsi] < 5 and (row['Close']>row[sma]):
            return 1  # Buy signal
        elif row[rsi] > 95 and (row['Close']<row[sma]):
            return -1  # Sell signal
        
    def EMA(self,row,low,medium,high): 
    
        if (row[low] > row[medium]) and (row[low] > row[high]) and (row[medium] > row[high]) and (row['direction_14_3']==1 or row['direction_100_2']==1): #can remove one of the directions
            return 1
        if (row[low] > row[medium]) and (row[low] < row[high]) and (row[medium] < row[high]) and (row['direction_14_3']==-1 or row['direction_100_2']==1 ):
            return -1
    
    def stoch(self,df,col):
        if df[col] < 20 and df['direction_100_2']==1:
            return 1  # Buy signal
        elif df[col] > 80 and df['direction_100_2']==-1:
            return -1  # Sell signal
    
    def MADC_RSI_SMA(self,df):
        if (df['RSI']>50) and (df['Close']>df['200_SMA']) and (df['MACD_signal']==1):
            return 1 
        elif (df['Close']<df['200_SMA']) and (df['RSI']<50) and (df['MACD_signal']==-1):
            return -1
    
    def Donchian(self,row,l,m,u):
        if row['High']>=row[u]and (row['Close']>row['SMA_200']):
            return 1 
        elif row['Low']<=row[l]and (row['Close']<row['SMA_200']):
            return -1        
        
    def create_data_information(self): #create information for the dataframe
        #Super_trends
        self.data[['SUPERT_14_3', 'direction_14_3', 'long_14_3', 'short_14_3']] = ta.supertrend(self.data['High'], self.data['Low'], self.data['Close'], length=14, multiplier=3)
        self.data[['SUPERT_100_2', 'direction_100_2', 'long_100_2', 'short_100_2']] = ta.supertrend(self.data['High'], self.data['Low'], self.data['Close'], length=100, multiplier=2)
        
        #RSI
        timePeriods=[2,8,11,14,21]
        for i in timePeriods:
            self.data[f'RSI_{i}']=talib.RSI(self.data['Close'], i)
            
        periods=[5,10,20,50,100,200]
        for i in periods:
            self.data[f'SMA_{i}']=self.data['Close'].rolling(window=i).mean()
            self.data[f'ema_{i}']=talib.EMA(self.data['Close'], timeperiod=i)

        stock_periods=[[5,3,3],[6,3,3],[13,8,8],[15,3,3]]
        
        for f,s,si in stock_periods:
            self.data[f'stock_k_{f}_{s}_{si}'], _ = talib.STOCH(self.data['High'], self.data['Low'], self.data['Close'], fastk_period=f, slowk_period=s, slowd_period=si)
        
        stock_periods=[[12,26,9],[24,52,9],[19,39,9]]
        for f,s,si in stock_periods:
            self.data[f'MACD_{f}_{s}_{si}'], self.data[f'Signal_{f}_{s}_{si}'], _ = talib.MACD(self.data['Close'], fastperiod=f, slowperiod=s, signalperiod=si)
        
        self.data['Prev_Close'] = self.data['Close'].shift(1)
        self.data['OBV'] = 0
        self.data.loc[self.data['Close'] > self.data['Prev_Close'], 'OBV'] = self.data['Volume']
        self.data.loc[self.data['Close'] < self.data['Prev_Close'], 'OBV'] = -self.data['Volume']
        self.data['OBV'] = self.data['OBV'].cumsum()
        
        stock_periods=[[20,20],[40,50],[100,100]]
        
        for l,u in stock_periods:
            self.data[[f'dcl_{l}_{u}',f'dcm_{l}_{u}',f'dcu_{l}_{u}']]=self.data.ta.donchian(lower_length = l, upper_length = u)
    
        self.data.to_csv(fr"....")
       

    def Strategy_combined_decision(self):
        self.data=self.get_data()
        self.create_data_information()

        return self.data
        
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'AMD', 'NFLX', 'PYPL', 'IBM', 'GS']#]#
ListofDF=[]
for s in symbols:
    strategy = TradingStrategy(s) 
    data=strategy.Strategy_combined_decision()
    ListofDF.append(data)

