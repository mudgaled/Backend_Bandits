from flask import Blueprint, render_template, redirect, request, url_for, flash
from .models import User, Portfolio
from stock_app.models import Stock
from utils.db_utils import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

user_app = Blueprint('user_app', __name__, template_folder='templates')

@user_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_app.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user_app.dashboard'))
        flash('Invalid username or password')
    
    return render_template('login.html')

@user_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password_hash = generate_password_hash(request.form['password'])
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_app.login'))
    return render_template('signup.html')

@user_app.route('/logout')
def logout():
    logout_user() 
    return redirect(url_for('user_app.login'))

@user_app.route('/dashboard')
@login_required  
def dashboard():

    user = current_user
    portfolio = Portfolio.query.filter_by(user_id=user.id).all()

    stocks = {}
    all_stocks = Stock.query.all()
    for stock in all_stocks:
        stocks[stock.ticker] = stock

    return render_template('dashboard.html', user=user, portfolio=portfolio, stocks=stocks)
