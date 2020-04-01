import pandas as pd
import os

def downloadCSV(tickers=['TSLA', 'MSFT'], fileDir='/Users/d062864/Documents/01_code/pythonStarter/data'):
    for ticker in tickers:
        if not os.path.isfile(fileDir + '/' + ticker + '.csv'): 
            baseUrl = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ticker + '&apikey=Z0KW216UY5S8C6KQ&datatype=csv&outputsize=full'
            df = pd.read_csv(baseUrl,skiprows=0,header=0,parse_dates=True,index_col=0)
            df.rename_axis("Date", axis='index', inplace=True)
            df = df.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'})   
            df=df.sort_values('Date')         
            df.to_csv(fileDir + '/' + ticker + '.csv')