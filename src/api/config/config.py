class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    password = ''

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mariadb+pymysql://root:1234@localhost:3308/waiketapay1'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/waiketapay1_tst?charset=utf8mb4'
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost:3308/waiketapay1_tst'
    SQLALCHEMY_ECHO = False

SECRET_KEY = '1eee1f901a67e938e53f91db4fa0edd491247391a358d5a1'
SECURITY_PASSWORD_SALT = '80f631ca7b03e56eecace36c1a7ed80d4e90865f4a2b0f8f'

MAIL_DEFAULT_SENDER = 'deanmajaya77@gmail.com'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = 'deanmajaya77@gmail.com'
MAIL_PASSWORD = '77detista'
MAIL_USE_TLS = False
MAIL_USE_SSL = True

UPLOAD_FOLDER = 'C:/Users/huawei/author-manager/src/images'