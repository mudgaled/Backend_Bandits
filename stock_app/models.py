# stocks_app/models.py
from utils.db_utils import db



class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    change = db.Column(db.Float, default=0, nullable=False)
    volume = db.Column(db.BigInteger, default=0, nullable=False)
    
    trades = db.relationship('Trade', backref='stock_trade', lazy=True)  # String reference to avoid circular import
    price_history = db.relationship(
        'PriceHistory', 
        back_populates='stock',
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Stock {self.ticker} - {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "ticker": self.ticker,
            "name": self.name,
            "price": self.price,
            "change": self.change,
            "volume": self.volume,
            "price_history": [ph.to_dict() for ph in self.price_history]
        }

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)

    stock = db.relationship(
        'Stock', 
        back_populates='price_history'
    )

    def __repr__(self):
        return f"<PriceHistory {self.date} for Stock ID {self.stock_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "stock_id": self.stock_id,
            "date": self.date.isoformat(),
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "close_price": self.close_price,
            "volume": self.volume
        }
