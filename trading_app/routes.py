# trading_app/routes.py
from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from .models import Trade
from user_app.models import Portfolio, User  # Import User model to modify balance
from stock_app.models import Stock
from utils.db_utils import db
from flask_login import login_required, current_user

trading_app = Blueprint('trading_app', __name__, template_folder='templates')

@trading_app.route('/trade', methods=['GET', 'POST'])
@login_required
def trade():
    if request.method == 'GET':
        stocks = Stock.query.all()
        portfolio = Portfolio.query.filter_by(user_id=current_user.id).all()
        return render_template('trade.html', stocks=stocks, portfolio=portfolio)
    
    stock_id = request.form.get('stock_id')
    action = request.form.get('action')
    shares = int(request.form.get('shares'))
    
    if not stock_id:
        flash('Please select a stock')
        return redirect(url_for('trading_app.trade'))
        
    stock = Stock.query.filter_by(id=stock_id).first_or_404()
    total_amount = stock.price * shares
    
    try:
        if action == 'buy':
            if total_amount > current_user.balance:
                flash('Insufficient funds')
                return redirect(url_for('trading_app.trade'))
                
            current_user.balance -= total_amount
            
            db.session.commit()  
            
            portfolio_item = Portfolio.query.filter_by(
                user_id=current_user.id,
                stock=stock.ticker
            ).first()
            
            if portfolio_item:
                new_shares = portfolio_item.shares + shares
                portfolio_item.avg_price = ((portfolio_item.avg_price * portfolio_item.shares) +
                                          (stock.price * shares)) / new_shares
                portfolio_item.shares = new_shares
            else:
                portfolio_item = Portfolio(
                    user_id=current_user.id,
                    stock=stock.ticker,
                    shares=shares,
                    avg_price=stock.price
                )
                db.session.add(portfolio_item)
                
        elif action == 'sell':
            portfolio_item = Portfolio.query.filter_by(
                user_id=current_user.id,
                stock=stock.ticker
            ).first()
            
            if not portfolio_item or portfolio_item.shares < shares:
                flash('Insufficient shares')
                return redirect(url_for('trading_app.trade'))
                
            current_user.balance += total_amount
            
            db.session.commit()  
            
            portfolio_item.shares -= shares
            
            if portfolio_item.shares == 0:
                db.session.delete(portfolio_item)
        
        # Record the trade
        trade = Trade(
            user_id=current_user.id,
            stock_id=stock.id,
            shares=shares,
            price=stock.price,
            trade_type=action
        )
        db.session.add(trade)
        db.session.commit()
        
        flash(f'Successfully {action}ed {shares} shares of {stock.ticker}')
        return redirect(url_for('user_app.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Trade failed: {str(e)}')
        return redirect(url_for('trading_app.trade'))
