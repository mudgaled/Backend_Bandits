import yfinance as yf
from utils.db_utils import db
from stock_app.models import Stock
from app import app
import json

def fetch_and_insert_stocks():
    with app.app_context():
        tickers = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']
        
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d')
            info = stock.info
            
            if not data.empty:
                latest_price = data['Close'].iloc[-1]
                previous_close = info.get('previousClose', latest_price)
                price_change = latest_price - previous_close
                
                # Convert Timestamp objects to string format for JSON serialization
                historical_data = stock.history(period='1mo')['Close']
                historical_dict = {date.strftime('%Y-%m-%d'): price 
                                 for date, price in historical_data.items()}
                
                new_stock = Stock(
                    ticker=ticker,
                    name=info.get('longName', ticker),
                    price=latest_price,
                    change=price_change,
                    price_history=json.dumps(historical_dict)
                )
                
                db.session.add(new_stock)
                db.session.commit()
                print(f"Added {ticker} - {info.get('longName')} with price ${latest_price:.2f} (Change: ${price_change:.2f})")

if __name__ == '__main__':
    fetch_and_insert_stocks()