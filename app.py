from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from user_app.routes import user_app
from stock_app.routes import stocks_app
from trading_app.routes import trading_app
from services.stock_updater import StockUpdater, start_stock_updater
from utils.db_utils import db, migrate
from flask_login import LoginManager
from user_app.models import User
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/trading_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-super-secret-key-here'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_app.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(user_app, url_prefix='/user')
app.register_blueprint(stocks_app, url_prefix='/stocks')
app.register_blueprint(trading_app, url_prefix='/trade')

with app.app_context():
    db.create_all()
    updater = StockUpdater(app, interval=300)
    updater.initialize_stocks()  
    updater.start() 
@app.route('/')
def landing():
    return render_template('landing.html')

if __name__ == '__main__':
    app.run(debug=True)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nTerminating both the processes. Alvida!")

