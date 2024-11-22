import yfinance as yf
from datetime import datetime
from utils.db_utils import db
from stock_app.models import Stock, PriceHistory
from app import app
import time
import pandas as pd
from sqlalchemy import text


def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'name': info.get('longName', ''),
            'price': info.get('currentPrice', 0.0),
            'volume': info.get('volume', 0)
        }
    except:
        return {
            'name': ticker,
            'price': 0.0,
            'volume': 0
        }


def refresh_stocks():
    with app.app_context():
        stock_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX',
            'INTC', 'AMD', 'PYPL', 'CSCO', 'QCOM', 'ADBE', 'CRM', 'AVGO',
            'TXN', 'ORCL', 'IBM', 'UBER', 'JPM', 'BAC', 'WFC', 'GS', 'MS',
            'C', 'AXP', 'BLK', 'SCHW', 'USB', 'WMT', 'PG', 'KO', 'PEP',
            'MCD', 'NKE', 'SBUX', 'TGT', 'HD', 'LOW', 'RELIANCE.NS', 'TCS.NS',
            'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS', 'SBIN.NS',
            'BHARTIARTL.NS', 'ITC.NS', 'WIPRO.NS', 'DIS', 'V', 'MA', 'UNH',
            'JNJ', 'XOM', 'CVX', 'BA', 'CAT', 'GE'
        ]
        
        for ticker in stock_tickers:
            print(f"Processing {ticker}")
            try:
                db.session.execute(
                    text("DELETE FROM stock WHERE ticker = :ticker"),
                    {'ticker': ticker}
                )
                
                info = get_stock_info(ticker)
                db.session.execute(
                    text("""
                        INSERT INTO stock (ticker, name, price, `change`, volume)
                        VALUES (:ticker, :name, :price, :change, :volume)
                    """),
                    {
                        'ticker': ticker,
                        'name': info['name'],
                        'price': info['price'],
                        'change': 0,
                        'volume': info['volume']
                    }
                )
                db.session.commit()
                print(f"Added {ticker} successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding {ticker}: {str(e)}")
            time.sleep(1)
        
        print("Stock refresh completed!")

def populate_price_history():
    with app.app_context():
        stocks = Stock.query.all()
        print(f"\nProcessing price history for {len(stocks)} stocks")
        
        for stock in stocks:
            print(f"\nFetching data for {stock.ticker}")
            
            try:
                data = yf.download(stock.ticker, period="2y", interval="1d", progress=False)
                if data.empty:
                    continue
                
                PriceHistory.query.filter_by(stock_id=stock.id).delete()
                
                for index, row in data.iterrows():
                    price = PriceHistory(
                        stock_id=stock.id,
                        date=index.to_pydatetime(),
                        open_price=float(row['Open'].iloc[0]),
                        high_price=float(row['High'].iloc[0]),
                        low_price=float(row['Low'].iloc[0]),
                        close_price=float(row['Close'].iloc[0]),
                        volume=int(row['Volume'].iloc[0])
                    )
                    db.session.add(price)
                
                db.session.commit()
                print(f"Added price history for {stock.ticker}")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error with {stock.ticker}: {str(e)}")
            
            time.sleep(1)

if __name__ == "__main__":
    refresh_stocks()
    populate_price_history()
