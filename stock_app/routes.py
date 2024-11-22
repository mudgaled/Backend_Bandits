# stocks_app/routes.py
from flask import Blueprint, render_template, jsonify, request
from .models import Stock
import yfinance as yf
stocks_app = Blueprint('stocks_app', __name__, template_folder='templates')

@stocks_app.route('/')
def stocks():
    stocks = Stock.query.all()
    return render_template('stocks.html', stocks=stocks)

@stocks_app.route('/view/<ticker>', methods=['GET'])
def stock_detail(ticker):
    stock = Stock.query.filter_by(ticker=ticker).first_or_404()
    yf_stock = yf.Ticker(ticker)
    daily_data = yf_stock.history(period='1d')
    monthly_data = yf_stock.history(period='1mo')
    stock.day_low = daily_data['Low'].iloc[-1]
    stock.day_high = daily_data['High'].iloc[-1]
    stock.month_low = monthly_data['Low'].min()
    stock.month_high = monthly_data['High'].max()

    price_history = []
    for date, row in monthly_data.iterrows():
        price_history.append({
            'date': date.strftime('%Y-%m-%d'),
            'open_price': row['Open'],
            'high_price': row['High'],
            'low_price': row['Low'],
            'close_price': row['Close']
        })
    
    return render_template('stock_detail.html', 
                         stock=stock, 
                         price_history=price_history)
@stocks_app.route('/history')
def stock_history():
    ticker = request.args.get('ticker')
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")  # Fetches 1 month of daily historical data

    data = {
        "dates": hist.index.strftime('%Y-%m-%d').tolist(),
        "prices": hist['Close'].tolist()
    }
    return jsonify(data)
@stocks_app.route('/test')
def test_route():
    return "Test successful!"

