import mysql.connector
from mysql.connector import errorcode

# Database configuration
DB_CONFIG = {
    'user': 'your_username',  # Replace with your database username
    'password': 'your_password',  # Replace with your database password
    'host': 'localhost',  # Change if your MySQL server is on a different host
}

CREATE_DATABASE = "CREATE DATABASE IF NOT EXISTS trading_app;"
USE_DATABASE = "USE trading_app;"

CREATE_USER_TABLE = """
CREATE TABLE IF NOT EXISTS User (
    userid INT PRIMARY KEY AUTO_INCREMENT,
    PAN VARCHAR(10) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL,
    dmatid VARCHAR(20) NOT NULL UNIQUE,
    age INT CHECK (age >= 0),
    name VARCHAR(100) NOT NULL
);
"""

CREATE_PORTFOLIO_TABLE = """
CREATE TABLE IF NOT EXISTS Portfolio (
    pid INT PRIMARY KEY AUTO_INCREMENT,
    userid INT,
    networth DECIMAL(15, 2) NOT NULL,
    FOREIGN KEY (userid) REFERENCES User(userid) ON DELETE CASCADE
);
"""

CREATE_STOCKS_TABLE = """
CREATE TABLE IF NOT EXISTS Stocks (
    stockid INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(100) NOT NULL
);
"""
CREATE_STOCK_PRICE_TABLE = """
CREATE TABLE IF NOT EXISTS stock_price (
  id INT AUTO_INCREMENT PRIMARY KEY,
  stock_id INT,
  date DATE NOT NULL,
  open DECIMAL(10, 2) NOT NULL,
  high DECIMAL(10, 2) NOT NULL,
  low DECIMAL(10, 2) NOT NULL,
  close DECIMAL(10, 2) NOT NULL,
  adjusted_close DECIMAL(10, 2) NOT NULL,
  volume INT NOT NULL,
  FOREIGN KEY (stock_id) REFERENCES stock (id)
);
"""

CREATE_TRADES_TABLE = """
CREATE TABLE IF NOT EXISTS Trades (
    tradeid INT PRIMARY KEY AUTO_INCREMENT,
    userid INT,
    stockid INT,
    trade_type ENUM('Buy', 'Sell') NOT NULL,
    trade_price DECIMAL(10, 2) NOT NULL,
    trade_date_time DATETIME NOT NULL,
    FOREIGN KEY (userid) REFERENCES User(userid) ON DELETE CASCADE,
    FOREIGN KEY (stockid) REFERENCES Stocks(stockid) ON DELETE CASCADE
);
"""

CREATE_PORTFOLIO_STOCKS_TABLE = """
CREATE TABLE IF NOT EXISTS PortfolioStocks (
    portfolio_id INT,
    stock_id INT,
    quantity INT NOT NULL,
    PRIMARY KEY (portfolio_id, stock_id),
    FOREIGN KEY (portfolio_id) REFERENCES Portfolio(pid) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stockid) ON DELETE CASCADE
);
"""

def create_database_and_tables():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(CREATE_DATABASE)

        cursor.execute(USE_DATABASE)

        cursor.execute(CREATE_USER_TABLE)
        cursor.execute(CREATE_PORTFOLIO_TABLE)
        cursor.execute(CREATE_STOCKS_TABLE)
        cursor.execute(CREATE_STOCK_PRICE_TABLE)
        cursor.execute(CREATE_TRADES_TABLE)
        cursor.execute(CREATE_PORTFOLIO_STOCKS_TABLE)

        print("Database and tables created successfully.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_database_and_tables()
