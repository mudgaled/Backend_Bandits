import yfinance as yf
from utils.db_utils import db
from stock_app.models import Stock
from user_app.models import User
from trading_app.models import Trade
from user_app.models import Portfolio
from app import app
import json
from datetime import datetime

def create_sample_users():
    users = [
        {'username': 'john_trader', 'password': 'trading123'},
        {'username': 'sarah_invest', 'password': 'invest123'},
        {'username': 'mike_stocks', 'password': 'stocks123'}
    ]
    created_users = []
    
    for user_data in users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            created_users.append(existing_user)
            print(f"User {user_data['username']} already exists")
            continue
            
        # Create new user if doesn't exist
        user = User(username=user_data['username'])
        user.set_password(user_data['password'])
        db.session.add(user)
        created_users.append(user)
        print(f"Created new user: {user_data['username']}")
    
    db.session.commit()
    print(f"Total users available: {len(created_users)}")
    return created_users
def create_sample_portfolios(users):
    portfolios = []
    stocks = ['AAPL', 'GOOGL', 'MSFT']  # Sample stocks
    
    for user in users:
        for stock in stocks:
            # Check if portfolio entry already exists
            existing_portfolio = Portfolio.query.filter_by(
                user_id=user.id,
                stock=stock
            ).first()
            
            if existing_portfolio:
                portfolios.append(existing_portfolio)
                print(f"Portfolio for {user.username} - {stock} already exists")
                continue
            
            # Create new portfolio entry with all required fields
            portfolio = Portfolio(
                user_id=user.id,
                stock=stock,
                shares=100,  # Initial shares
                avg_price=150.0,  # Initial average price
                balance=100000.0  # Initial balance
            )
            db.session.add(portfolio)
            portfolios.append(portfolio)
            print(f"Created new portfolio for {user.username} - {stock}")
    
    db.session.commit()
    print(f"Total portfolio entries: {len(portfolios)}")
    return portfolios


def create_sample_trades(portfolios, stocks):
    trades = []
    with app.app_context():
        for portfolio in portfolios:
            for stock in stocks:
                stock = db.session.merge(stock)
                
                trade = Trade(
                    user_id=portfolio.user_id,  # Using user_id instead of portfolio_id
                    stock_id=stock.id,
                    shares=50,
                    price=stock.price,
                    trade_type='buy',  # Using trade_type instead of type
                    timestamp=datetime.now()
                )
                db.session.add(trade)
                trades.append(trade)
                print(f"Created trade for user {portfolio.user_id} - {stock.ticker}")
        
        db.session.commit()
        print(f"Total trades created: {len(trades)}")
        return trades
def fetch_and_insert_stocks():
    with app.app_context():
        tickers = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']
        created_stocks = []
        
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d')
            info = stock.info
            
            if not data.empty:
                latest_price = float(data['Close'].iloc[-1])
                previous_close = float(info.get('previousClose', latest_price))
                price_change = latest_price - previous_close
                
                historical_data = stock.history(period='1mo')['Close']
                historical_dict = {date.strftime('%Y-%m-%d'): float(price) 
                                 for date, price in historical_data.items()}
                
                # Try to find existing stock
                existing_stock = Stock.query.filter_by(ticker=ticker).first()
                
                if existing_stock:
                    # Update existing stock
                    existing_stock.name = info.get('longName', ticker)
                    existing_stock.price = latest_price
                    existing_stock.change = price_change
                    existing_stock.price_history = json.dumps(historical_dict)
                    created_stocks.append(existing_stock)
                    print(f"Updated {ticker} - {info.get('longName')} with price ${latest_price:.2f}")
                else:
                    # Create new stock
                    new_stock = Stock(
                        ticker=ticker,
                        name=info.get('longName', ticker),
                        price=latest_price,
                        change=price_change,
                        price_history=json.dumps(historical_dict)
                    )
                    db.session.add(new_stock)
                    created_stocks.append(new_stock)
                    print(f"Added {ticker} - {info.get('longName')} with price ${latest_price:.2f}")
                
                db.session.commit()
        
        return created_stocks        
        # Create sample users, portfolios, and trades
def populate_database():
    with app.app_context():
        users = create_sample_users()
        portfolios = create_sample_portfolios(users)
        created_stocks = fetch_and_insert_stocks()
        create_sample_trades(portfolios, created_stocks)
        print("\nDatabase populated successfully!")
        

if __name__ == '__main__':
    populate_database()
        
    print("\nCreated sample users with portfolios and trades!")
