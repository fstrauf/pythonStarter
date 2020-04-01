import backtrader as bt
from datetime import datetime
import pandas as pd
import helper
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo

class firstStrategy(bt.Strategy):
    params = (
        ('maperiod', 21),
        ('printlog', False),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2i' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     order.executed.size))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2i' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          order.executed.size))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # if self.dataclose[0] > self.sma[0]:
            if self.rsi < 30:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            # if self.dataclose[0] < self.sma[0]: 
            if self.rsi > 70:           
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

    def stop(self):
        pnl = round(self.broker.getvalue() - startcash,2)
        print('RSI Period: {} Final PnL: {}'.format(self.params.maperiod, pnl))

class TimingSMASingle(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=8)
        self.outofmarket = True
        self.stratname = 'SMASingleEUR'
        self.invested=False
        self.lastmonth=None

    def notify_order(self, order):
        if order.status == order.Completed:
            pass
        if not order.alive():
            self.order = None  # indicate no order is pending
    def start(self):
        self.order = None
        
    def next(self):
        dt = datetime.fromordinal(int(self.datas[0].datetime[0]))
        mon = dt.month
        
        if self.invested==False: #we are not invested yet
            self.broker.set_cash(10000)
            print("SIN: Set initial cash value to %.2f" % self.broker.get_value())
            self.invested=True
        
        if mon != self.lastmonth: #This is the last trading day of the month and we determine what we order
            # self.broker.add_cash(1000) # what does this do???
            lastclose = self.datas[0].close[0]
            smaval = self.sma[0]
            portfolio_value = self.broker.get_value()
            trading = False
            if (1*smaval) > lastclose and self.outofmarket==False:
                self.order_target_value(target=0.0)
                self.order_target_value(target=portfolio_value) 
                self.outofmarket = True
                trading = True
            if smaval < lastclose and self.outofmarket==True:
                self.order_target_value(target=0.0) 
                self.order_target_value(target=portfolio_value) 
                self.outofmarket = False
                trading = True
            if trading:
                print('SIN %04d - %s - SMA: %.2f; C: %.2f; PF: %.2f' %
                    (len(self), dt.date(), smaval, lastclose, portfolio_value ))
                if self.outofmarket:
                    print("Leaving market on %s" % dt.date())
                else:
                    print("Entering market on %s" % dt.date())
            if trading==False: #We are not trading, just rebalance in case we are in the market:
                if self.outofmarket==False:
                    self.order_target_value(target=portfolio_value-4000.0)
                else:
                    self.order_target_value(target=portfolio_value-4000.0)
            self.lastmonth=dt.month


if __name__ == '__main__':
    startcash=10000
    maperiod=16
    stock='SAP'

    cerebro = bt.Cerebro()
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addstrategy(firstStrategy)

    helper.downloadCSV([stock])
    datapath = '/Users/d062864/Documents/01_code/pythonStarter/data/' + stock + '.csv'
    dataframe = pd.read_csv(datapath, skiprows=0, header=0, parse_dates=True, index_col=0)
    data = bt.feeds.PandasData(dataname=dataframe, fromdate=datetime(2017, 1, 1), todate=datetime(2019, 12, 31))

    cerebro.adddata(data)
    cerebro.broker.setcash(startcash)

    cerebro.run()

    #Get final portfolio Value
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash

    #Print out the final result
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))

    #Finally plot the end results
    b = Bokeh(style='bar', plot_mode='single')
    cerebro.plot(b)