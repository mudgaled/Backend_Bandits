class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/social_media_app_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPDATE_INTERVAL = 600

    SECRET_KEY = 'your_secret_key_here'

class ProductionConfig(DevelopmentConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@prod_db/production_db'

class TestingConfig(DevelopmentConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/test_db'

