import time
import json
import requests
import pandas as pd
from threading import Thread, Event
from stock_app.models import Stock, PriceHistory
import yfinance as yf
from utils.db_utils import db

class StockUpdater:
    def __init__(self, app, interval=600):
        self.app = app
        self.interval = interval
        self.stop_event = Event()
        self.thread = None

    def get_stock_symbols(self):
        core_stocks = [
            # US Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'INTC', 'AMD',
            'PYPL', 'CSCO', 'QCOM', 'ADBE', 'CRM', 'AVGO', 'TXN', 'ORCL', 'IBM', 'UBER',
            
            # US Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB',
            
            # US Consumer
            'WMT', 'PG', 'KO', 'PEP', 'MCD', 'NKE', 'SBUX', 'TGT', 'HD', 'LOW',
            
            # Indian Blue Chips
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'WIPRO.NS',
            
            # Additional sectors
            'DIS', 'V', 'MA', 'UNH', 'JNJ', 'XOM', 'CVX', 'BA', 'GE'
        ]
        return core_stocks

    def initialize_stocks(self):
        with self.app.app_context():
            from trading_app.models import Trade
            
            Trade.query.delete()
            db.session.commit()
            
            PriceHistory.query.delete()
            db.session.commit()
            
            Stock.query.delete()
            db.session.commit()
            
            symbols = self.get_stock_symbols()
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.fast_info
                    
                    new_stock = Stock(
                        ticker=symbol,
                        name=symbol,
                        price=info.last_price if hasattr(info, 'last_price') else 0,
                        change=0,
                        volume=info.volume if hasattr(info, 'volume') else 0
                    )
                    db.session.add(new_stock)
                    db.session.commit()
                    print(f"Added {symbol} successfully")
                    
                except Exception as e:
                    print(f"Skipping {symbol}: {str(e)}")
                    continue

    def add_historical_data(self, stock, ticker):
        try:
            history = ticker.history(period='1y')
            for date, row in history.iterrows():
                price_history = PriceHistory(
                    stock_id=stock.id,
                    date=date,
                    open_price=row['Open'],
                    high_price=row['High'],
                    low_price=row['Low'],
                    close_price=row['Close'],
                    volume=row['Volume']
                )
                db.session.add(price_history)
            db.session.commit()
        except Exception as e:
            print(f"Error adding history for {stock.ticker}: {str(e)}")

    def update_stock_prices(self):
        with self.app.app_context():
            stocks = Stock.query.all()
            for stock in stocks:
                if self.stop_event.is_set():
                    break
                try:
                    ticker = yf.Ticker(stock.ticker)
                    
                    historical_data = ticker.history(period='1mo')
                    
                    if not historical_data.empty:
                        latest_price = historical_data['Close'].iloc[-1]
                        stock.change = latest_price - stock.price
                        stock.price = latest_price
                        stock.volume = historical_data['Volume'].iloc[-1]
                    
                    for date, row in historical_data.iterrows():
                        existing_history = PriceHistory.query.filter_by(
                            stock_id=stock.id,
                            date=date
                        ).first()
                        
                        if not existing_history:
                            price_history = PriceHistory(
                                stock_id=stock.id,
                                date=date,
                                open_price=row['Open'],
                                high_price=row['High'],
                                low_price=row['Low'],
                                close_price=row['Close'],
                                volume=row['Volume']
                            )
                            db.session.add(price_history)
                    
                    db.session.commit()
                    print(f"Updated {stock.ticker} with historical data")
                    
                except Exception as e:
                    print(f"Error updating {stock.ticker}: {str(e)}")
                    db.session.rollback()
    def run(self):
        with self.app.app_context():
            if Stock.query.count() == 0:
                self.initialize_stocks()
                
        while not self.stop_event.is_set():
            try:
                self.update_stock_prices()
                time.sleep(self.interval)
            except Exception as e:
                print(f"Stock update error: {str(e)}")
                time.sleep(5)

    def start(self):
        self.thread = Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()

def start_stock_updater(app, interval=600):
    updater = StockUpdater(app, interval)
    updater.start()
    return updater
